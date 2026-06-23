from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


RoomKey = Literal["one", "two", "three", "four"]
ListingSource = Literal["olx", "otodom", "rentola"]
Tier = Literal["premium", "good", "average", "poor"]
JobStatus = Literal["scanning", "done", "error"]


class Brief(CamelModel):
    raw_text: str
    budget_pln: Optional[int] = None
    rooms: Optional[int] = None
    districts: List[str] = Field(default_factory=list)
    wants_renovated: bool = False


class Listing(CamelModel):
    source: ListingSource
    id: int
    title: str
    description: str
    price_monthly_pln: float
    rent_extra_pln: float = 0
    area_m2: Optional[float] = None
    rooms: Optional[RoomKey] = None
    floor: Optional[str] = None
    furnished: Optional[bool] = None
    district: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    photos: List[str] = Field(default_factory=list)
    url: str
    created_time: str = ""


class ScoreBreakdown(CamelModel):
    budget_fit: float
    room_fit: float
    district_fit: float
    renovation_fit: float


class ScoredListing(Listing):
    score: float
    score_breakdown: ScoreBreakdown
    tier: Tier


class FunnelStats(CamelModel):
    scanned: int = 0
    matched: int = 0
    deduped: int = 0
    shortlist: int = 0


class ScanLogEntry(CamelModel):
    ts: int
    source: str
    message: str


class Job(CamelModel):
    id: str
    status: JobStatus
    brief: Brief
    log: List[ScanLogEntry] = Field(default_factory=list)
    funnel: FunnelStats = Field(default_factory=FunnelStats)
    results: List[ScoredListing] = Field(default_factory=list)
    error: Optional[str] = None
