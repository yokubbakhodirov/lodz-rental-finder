import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .jobs import create_scan_job, get_job

app = FastAPI(title="Łódź Rental Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lodz-rental-finder.vercel.app",
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    brief: str = ""


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/scan")
async def start_scan(payload: ScanRequest):
    raw_text = payload.brief.strip()
    if not raw_text:
        return JSONResponse(status_code=400, content={"error": "brief is required"})
    job = create_scan_job(raw_text)
    return {"jobId": job.id}


@app.get("/api/scan/{job_id}")
def get_scan(job_id: str):
    job = get_job(job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": "job not found"})
    return job.model_dump(by_alias=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
