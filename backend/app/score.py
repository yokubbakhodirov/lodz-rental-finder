from typing import List

from .models import Brief, Listing, ScoreBreakdown, ScoredListing, Tier

RENOVATION_KEYWORDS = [
    "wyremontowan",
    "nowe mieszkanie",
    "nowy budynek",
    "po remoncie",
    "wysoki standard",
    "nowoczesn",
    "deweloperski",
]

POOR_CONDITION_KEYWORDS = ["do remontu", "stary", "wymaga remontu", "zaniedban"]

ROOM_KEY_TO_COUNT = {"one": 1, "two": 2, "three": 3, "four": 4}


def score_budget_fit(listing: Listing, budget_pln: int | None) -> float:
    if not budget_pln:
        return 7.0
    total = listing.price_monthly_pln + listing.rent_extra_pln
    if total <= budget_pln:
        slack = (budget_pln - total) / budget_pln
        return min(10.0, 8 + slack * 4)
    over = (total - budget_pln) / budget_pln
    return max(0.0, 8 - over * 20)


def score_room_fit(listing: Listing, wanted_rooms: int | None) -> float:
    if not wanted_rooms:
        return 7.0
    actual = ROOM_KEY_TO_COUNT.get(listing.rooms) if listing.rooms else None
    if actual is None:
        return 5.0
    if actual == wanted_rooms:
        return 10.0
    return max(0.0, 10 - abs(actual - wanted_rooms) * 3)


def score_district_fit(listing: Listing, districts: List[str]) -> float:
    if not districts:
        return 7.0
    return 10.0 if listing.district in districts else 3.0


def score_renovation_fit(listing: Listing) -> float:
    text = f"{listing.title} {listing.description}".lower()
    has_good = any(kw in text for kw in RENOVATION_KEYWORDS)
    has_poor = any(kw in text for kw in POOR_CONDITION_KEYWORDS)
    if has_good and not has_poor:
        return 9.0
    if has_poor:
        return 3.0
    if listing.furnished:
        return 6.5
    return 5.5


def tier_for(score: float) -> Tier:
    if score >= 8.5:
        return "premium"
    if score >= 7:
        return "good"
    if score >= 5.5:
        return "average"
    return "poor"


def score_listing(listing: Listing, brief: Brief) -> ScoredListing:
    budget_fit = score_budget_fit(listing, brief.budget_pln)
    room_fit = score_room_fit(listing, brief.rooms)
    district_fit = score_district_fit(listing, brief.districts)
    renovation_fit = score_renovation_fit(listing)

    score = budget_fit * 0.35 + room_fit * 0.25 + district_fit * 0.2 + renovation_fit * 0.2

    return ScoredListing(
        **listing.model_dump(),
        score=round(score, 1),
        score_breakdown=ScoreBreakdown(
            budget_fit=round(budget_fit, 1),
            room_fit=round(room_fit, 1),
            district_fit=round(district_fit, 1),
            renovation_fit=round(renovation_fit, 1),
        ),
        tier=tier_for(score),
    )


def score_and_rank(listings: List[Listing], brief: Brief) -> List[ScoredListing]:
    scored = [score_listing(listing, brief) for listing in listings]
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored
