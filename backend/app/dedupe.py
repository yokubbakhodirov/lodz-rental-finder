from typing import List

from .models import Listing


def dedupe_listings(listings: List[Listing]) -> List[Listing]:
    seen_ids: set[str] = set()
    seen_signatures: set[str] = set()
    result: List[Listing] = []

    for listing in listings:
        id_key = f"{listing.source}:{listing.id}"
        if id_key in seen_ids:
            continue

        # Cross-posted listings (same flat, different source/title wording)
        # share price+district+area.
        area_key = listing.area_m2 if listing.area_m2 is not None else "?"
        signature = f"{listing.price_monthly_pln}|{listing.district}|{area_key}"
        if signature in seen_signatures:
            continue

        seen_ids.add(id_key)
        seen_signatures.add(signature)
        result.append(listing)

    return result
