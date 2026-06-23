import asyncio
import re
from typing import Any, Callable, List, Optional

import httpx

from .models import Listing

API_BASE = "https://www.olx.pl/api/v1/offers"
PAGE_SIZE = 50
LODZ_CITY_ID = 10609
LODZ_REGION_ID = 7
REAL_ESTATE_RENT_CATEGORY_ID = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

OnPage = Callable[[int, int, float], None]


def _param_value(params: list[dict], key: str) -> Optional[dict]:
    p = next((p for p in params if p.get("key") == key), None)
    return p.get("value") if p else None


def _map_rooms(value: Optional[dict]) -> Optional[str]:
    key = (value or {}).get("key")
    return key if key in ("one", "two", "three", "four") else None


def _to_float(value: Any, default: Optional[float] = 0.0) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _photo_url(photo: dict) -> str:
    return str(photo["link"]).replace("{width}x{height}", "720x540")


def _parse_ad(ad: dict) -> Listing:
    params = ad.get("params") or []
    rent_value = _param_value(params, "rent")
    area_value = _param_value(params, "m")
    floor_value = _param_value(params, "floor_select")
    furniture_value = _param_value(params, "furniture")
    rooms_value = _param_value(params, "rooms")
    price_value = _param_value(params, "price")

    description = re.sub(r"<[^>]+>", " ", ad.get("description") or "")
    description = re.sub(r"\s+", " ", description).strip()

    location = ad.get("location") or {}
    district = (location.get("district") or {}).get("name") or "Łódź"
    map_data = ad.get("map") or {}

    return Listing(
        source="olx",
        id=ad["id"],
        title=ad.get("title") or "",
        description=description,
        price_monthly_pln=_to_float((price_value or {}).get("value"), 0.0) or 0.0,
        rent_extra_pln=_to_float((rent_value or {}).get("key"), 0.0) or 0.0,
        area_m2=_to_float((area_value or {}).get("key"), None),
        rooms=_map_rooms(rooms_value),
        floor=(floor_value or {}).get("label"),
        furnished=(furniture_value.get("key") == "yes") if furniture_value else None,
        district=district,
        lat=map_data.get("lat"),
        lon=map_data.get("lon"),
        photos=[_photo_url(p) for p in (ad.get("photos") or [])[:6]],
        url=ad["url"],
        created_time=ad.get("created_time") or "",
    )


async def fetch_lodz_listings(
    max_pages: int = 4, on_page: Optional[OnPage] = None
) -> List[Listing]:
    listings: List[Listing] = []
    total_elements: float = float("inf")

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for page in range(max_pages):
            offset = page * PAGE_SIZE
            if offset >= total_elements:
                break

            url = (
                f"{API_BASE}?offset={offset}&limit={PAGE_SIZE}"
                f"&category_id={REAL_ESTATE_RENT_CATEGORY_ID}"
                f"&region_id={LODZ_REGION_ID}&city_id={LODZ_CITY_ID}&suggest_filters=true"
            )
            res = await client.get(
                url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
            )
            if res.status_code != 200:
                raise RuntimeError(f"OLX API returned {res.status_code} for offset={offset}")

            data = res.json()
            total_elements = (data.get("metadata") or {}).get("total_elements", len(listings))
            ads = data.get("data") or []

            for ad in ads:
                try:
                    listings.append(_parse_ad(ad))
                except Exception:
                    continue  # skip malformed ad

            if on_page:
                on_page(page, len(listings), total_elements)

            if len(ads) < PAGE_SIZE:
                break
            await asyncio.sleep(0.6)  # polite delay between requests

    return listings
