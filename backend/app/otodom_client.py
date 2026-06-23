import asyncio
import json
import re
from typing import Callable, List, Optional

import httpx

from .models import Listing

SEARCH_URL = "https://www.otodom.pl/pl/wyniki/wynajem/mieszkanie/lodzkie/lodz/lodz/lodz"
ITEMS_PER_PAGE = 36
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

ROOMS_MAP = {
    "ONE": "one",
    "TWO": "two",
    "THREE": "three",
    "FOUR": "four",
    "FIVE": "four",
    "MORE": "four",
}

NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>([\s\S]*?)</script>'
)

OnPage = Callable[[int, int, float], None]


def _extract_next_data(html: str) -> dict:
    m = NEXT_DATA_RE.search(html)
    if not m:
        raise RuntimeError("Otodom: __NEXT_DATA__ not found in page")
    return json.loads(m.group(1))


def _district_name(item: dict) -> str:
    locations = (((item.get("location") or {}).get("reverseGeocoding") or {}).get("locations")) or []
    district = next((loc for loc in locations if loc.get("locationLevel") == "district"), None)
    if district and district.get("name"):
        return district["name"]
    return (((item.get("location") or {}).get("address") or {}).get("city") or {}).get("name") or "Łódź"


def _parse_item(item: dict) -> Listing:
    if item.get("transaction") != "RENT" or not item.get("href"):
        raise ValueError("Not a rental listing (promoted development ad)")

    href = str(item["href"]).replace("[lang]", "pl")
    images = item.get("images") or []
    rooms_number = item.get("roomsNumber")

    return Listing(
        source="otodom",
        id=item["id"],
        title=item.get("title") or "",
        description=re.sub(r"\s+", " ", item.get("shortDescription") or "").strip(),
        price_monthly_pln=(item.get("totalPrice") or {}).get("value") or 0,
        rent_extra_pln=(item.get("rentPrice") or {}).get("value") or 0,
        area_m2=item.get("areaInSquareMeters"),
        rooms=ROOMS_MAP.get(rooms_number) if rooms_number else None,
        floor=str(item["floorNumber"]) if item.get("floorNumber") is not None else None,
        furnished=None,
        district=_district_name(item),
        lat=None,
        lon=None,
        photos=[img.get("medium") for img in images[:6] if img.get("medium")],
        url=f"https://www.otodom.pl/{href}",
        created_time=item.get("createdAtFirst") or item.get("dateCreated") or "",
    )


async def fetch_otodom_lodz_listings(
    max_pages: int = 3, on_page: Optional[OnPage] = None
) -> List[Listing]:
    listings: List[Listing] = []
    total_elements: float = float("inf")

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for page in range(1, max_pages + 1):
            if (page - 1) * ITEMS_PER_PAGE >= total_elements:
                break

            url = SEARCH_URL if page == 1 else f"{SEARCH_URL}?page={page}"
            res = await client.get(url, headers={"User-Agent": USER_AGENT})
            if res.status_code != 200:
                raise RuntimeError(f"Otodom returned {res.status_code} for page={page}")

            data = _extract_next_data(res.text)
            search_ads = (
                ((data.get("props") or {}).get("pageProps") or {}).get("data") or {}
            ).get("searchAds") or {}
            items = search_ads.get("items") or []
            total_elements = (search_ads.get("pagination") or {}).get("totalItems", len(listings))

            for item in items:
                try:
                    listings.append(_parse_item(item))
                except Exception:
                    continue  # skip malformed item

            if on_page:
                on_page(page - 1, len(listings), total_elements)

            if not items:
                break
            await asyncio.sleep(0.7)  # polite delay between requests

    return listings
