from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.data_collection.config import Config, get_config, set_config
from backend.data_collection.weather import Weather


class ConfigPayload(BaseModel):
    start_date: str
    end_date: str
    lat: float
    lon: float


class WeatherQuery(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None
    tilt: int = 0
    azimuth: int = 180


app = FastAPI(title="HOME Optimization API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "fastapi"}


@app.post("/config")
def update_config(payload: ConfigPayload) -> dict:
    cfg = Config(
        start_date=payload.start_date,
        end_date=payload.end_date,
        lat=payload.lat,
        lon=payload.lon,
    )
    set_config(cfg)
    return {
        "message": "config updated",
        "start_date": cfg.start_date.isoformat(),
        "end_date": cfg.end_date.isoformat(),
        "lat": cfg.lat,
        "lon": cfg.lon,
    }


@app.get("/config")
def read_config() -> dict:
    cfg = get_config()
    if cfg is None:
        return {"config": None}

    return {
        "start_date": cfg.start_date.isoformat(),
        "end_date": cfg.end_date.isoformat(),
        "lat": cfg.lat,
        "lon": cfg.lon,
    }


@app.post("/weather")
def weather_snapshot(query: WeatherQuery) -> dict:
    cfg = get_config()
    if cfg is None and (query.lat is None or query.lon is None):
        raise HTTPException(
            status_code=400,
            detail="Set config first or provide lat/lon in request body.",
        )

    weather = Weather(
        lat=query.lat,
        lon=query.lon,
        start_date=getattr(cfg, "start_date", None),
        end_date=getattr(cfg, "end_date", None),
        tilt=query.tilt,
        azimuth=query.azimuth,
    )
    df = weather.fetch_weather_data()

    sample = df.head(24).reset_index().to_dict(orient="records")
    for row in sample:
        if isinstance(row.get("time"), datetime):
            row["time"] = row["time"].isoformat()

    return {
        "rows": len(df),
        "preview": sample,
    }
