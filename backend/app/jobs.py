import asyncio
import time
import uuid
from typing import Dict, Optional

from .brief_parser import parse_brief
from .dedupe import dedupe_listings
from .models import FunnelStats, Job, ScanLogEntry
from .olx_client import fetch_lodz_listings
from .otodom_client import fetch_otodom_lodz_listings
from .polish_text import fold_polish
from .rentola_client import fetch_rentola_lodz_listings
from .score import score_and_rank

JOBS: Dict[str, Job] = {}
JOB_TTL_SECONDS = 30 * 60


def _log(job: Job, source: str, message: str) -> None:
    job.log.append(ScanLogEntry(ts=int(time.time() * 1000), source=source, message=message))


def get_job(job_id: str) -> Optional[Job]:
    return JOBS.get(job_id)


def create_scan_job(raw_text: str) -> Job:
    brief = parse_brief(raw_text)
    job = Job(id=str(uuid.uuid4()), status="scanning", brief=brief, funnel=FunnelStats())
    JOBS[job.id] = job

    async def evict() -> None:
        await asyncio.sleep(JOB_TTL_SECONDS)
        JOBS.pop(job.id, None)

    async def run() -> None:
        try:
            await _run_scan(job)
        except Exception as err:  # noqa: BLE001 - surface any scan failure to the job
            job.status = "error"
            job.error = str(err)
            _log(job, "system", f"Scan failed: {job.error}")

    asyncio.create_task(run())
    asyncio.create_task(evict())

    return job


async def _run_scan(job: Job) -> None:
    _log(job, "olx.pl", "Connecting to OLX.pl Łódź rentals...")
    _log(job, "otodom.pl", "Connecting to Otodom.pl Łódź rentals...")
    _log(job, "rentola.pl", "Connecting to Rentola.pl Łódź rentals...")

    async def safe_otodom():
        try:
            return await fetch_otodom_lodz_listings(
                max_pages=3,
                on_page=lambda idx, fetched, total: _log(
                    job, "otodom.pl", f"Page {idx + 1} fetched · {fetched}/{total} listings seen"
                ),
            )
        except Exception as err:  # noqa: BLE001 - keep scan alive if a source is down
            _log(job, "otodom.pl", f"Source unavailable, skipping: {err}")
            return []

    async def safe_rentola():
        try:
            return await fetch_rentola_lodz_listings(
                max_pages=3,
                on_page=lambda idx, fetched: _log(
                    job, "rentola.pl", f"Page {idx + 1} fetched · {fetched} listings seen"
                ),
            )
        except Exception as err:  # noqa: BLE001 - keep scan alive if a source is down
            _log(job, "rentola.pl", f"Source unavailable, skipping: {err}")
            return []

    olx_listings, otodom_listings, rentola_listings = await asyncio.gather(
        fetch_lodz_listings(
            max_pages=4,
            on_page=lambda idx, fetched, total: _log(
                job, "olx.pl", f"Page {idx + 1} fetched · {fetched}/{total} listings seen"
            ),
        ),
        safe_otodom(),
        safe_rentola(),
    )

    listings = [*olx_listings, *otodom_listings, *rentola_listings]
    job.funnel.scanned = len(listings)
    _log(
        job,
        "system",
        f"Scan complete: {len(olx_listings)} from OLX.pl + {len(otodom_listings)} from "
        f"Otodom.pl + {len(rentola_listings)} from Rentola.pl = {len(listings)} total",
    )

    deduped = dedupe_listings(listings)
    job.funnel.deduped = len(deduped)
    _log(job, "dedupe", f"Removed {len(listings) - len(deduped)} duplicate/cross-posted listings")

    brief = job.brief

    def in_budget(listing) -> bool:
        if not brief.budget_pln:
            return True
        return (listing.price_monthly_pln + listing.rent_extra_pln) <= brief.budget_pln * 1.15

    budget_filtered = [listing for listing in deduped if in_budget(listing)]

    if not brief.districts:
        district_filtered = budget_filtered
    else:
        def matches_district(listing) -> bool:
            # Rentola listings have no verified district name, so they can't be
            # matched against a specific named-district search (see rentola_client.py).
            if listing.source == "rentola":
                return False
            listing_district = fold_polish(listing.district)
            return any(fold_polish(d) in listing_district for d in brief.districts)

        district_filtered = [listing for listing in budget_filtered if matches_district(listing)]

    job.funnel.matched = len(district_filtered)
    district_note = f" and in {'/'.join(brief.districts)}" if brief.districts else ""
    _log(job, "filter", f"{len(district_filtered)} listings within budget{district_note}")

    _log(job, "scoring", "Scoring listings (budget, rooms, district, renovation)...")
    ranked = score_and_rank(district_filtered, brief)

    shortlist = [listing for listing in ranked if listing.tier != "poor"]
    job.funnel.shortlist = len(shortlist)
    _log(job, "scoring", f"{len(shortlist)} listings made the shortlist")

    job.results = ranked
    job.status = "done"
    _log(job, "system", "Done.")
