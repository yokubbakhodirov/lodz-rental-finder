import asyncio
import json
import re
from typing import Callable, List, Optional

import httpx

from .models import Listing

SEARCH_URL = "https://www.rentola.pl/wynajem/lodz"
ITEMS_PER_PAGE = 21
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

LD_JSON_RE = re.compile(r'<script type="application/ld\+json">([\s\S]*?)</script>')

OnPage = Callable[[int, int], None]


def _map_rooms(count: Optional[float]) -> Optional[str]:
    if not count:
        return None
    if count <= 1:
        return "one"
    if count == 2:
        return "two"
    if count == 3:
        return "three"
    return "four"


def _hash_id(url: str) -> int:
    """Stable numeric id from a listing URL, scoped to this source only
    (dedupe.py keys by source+id)."""
    h = 0
    for ch in url:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return abs(h)


def _extract_list_items(html: str) -> List[dict]:
    for m in LD_JSON_RE.finditer(html):
        try:
            parsed = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if parsed.get("@type") == "SearchResultsPage":
            return ((parsed.get("mainEntity") or {}).get("itemListElement")) or []
    raise RuntimeError("Rentola: SearchResultsPage JSON-LD not found")


def _parse_item(entry: dict) -> Listing:
    item = entry.get("item") or {}
    offer = item.get("offers") or {}
    apartment = offer.get("itemOffered") or {}
    url = str(item.get("url") or "")
    if not url or not offer.get("price"):
        raise ValueError("Rentola: missing url or price")

    geo = apartment.get("geo") or {}
    floor_size = apartment.get("floorSize") or {}
    bedrooms = apartment.get("numberOfBedrooms") or {}

    return Listing(
        source="rentola",
        id=_hash_id(url),
        title=item.get("name") or "",
        description="",
        price_monthly_pln=float(offer.get("price") or 0),
        rent_extra_pln=0,
        area_m2=floor_size.get("value"),
        rooms=_map_rooms(bedrooms.get("value")),
        floor=None,
        furnished=None,
        # Rentola doesn't expose a verified district name, only street address —
        # left generic so it's never matched against a user's named-district
        # search (see jobs.py).
        district="Łódź",
        lat=geo.get("latitude"),
        lon=geo.get("longitude"),
        photos=[item["image"]] if item.get("image") else [],
        url=url,
        created_time=offer.get("validFrom") or "",
    )


async def fetch_rentola_lodz_listings(
    max_pages: int = 3, on_page: Optional[OnPage] = None
) -> List[Listing]:
    listings: List[Listing] = []

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for page in range(1, max_pages + 1):
            url = SEARCH_URL if page == 1 else f"{SEARCH_URL}?page={page}"
            res = await client.get(url, headers={"User-Agent": USER_AGENT})
            if res.status_code != 200:
                raise RuntimeError(f"Rentola returned {res.status_code} for page={page}")

            items = _extract_list_items(res.text)

            for entry in items:
                try:
                    listings.append(_parse_item(entry))
                except Exception:
                    continue  # skip malformed item

            if on_page:
                on_page(page - 1, len(listings))

            if len(items) < ITEMS_PER_PAGE:
                break
            await asyncio.sleep(0.7)  # polite delay between requests

    return listings
