from datetime import datetime
import json
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.data_collection.config import Config, set_config
from backend.data_collection.prices import SpotMarktPrices, ConstPrice

from backend.assets.pv import PV
from backend.assets.battery import Battery
from backend.assets.load import ConstantLoadProfile

from backend.optimization.optimizer import Optimizer


class CalculationPayload(BaseModel):
    objects: list[dict[str, Any]]




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


@app.post("/calculate")
def calculate(payload: CalculationPayload) -> dict:
    objects = payload.objects

    # Define Config
    set_config(
        Config(
            start_date="30.09.2025 22.15",
            end_date="30.06.2026 22.00",
            lat=51.1657,
            lon=10.4515,
        )
    )

    # Define Model
    prices = SpotMarktPrices("data\\spotmarktpreise.csv")
    export_prices = ConstPrice(const_price=0.08)

    PV(rated_power=1000, tilt=30, azimuth=180, temperature_coefficient=-0.005)
    ConstantLoadProfile(constant_load=300)

    Battery(expandable=True, lifetime=25, wacc=0, spec_capex=0.18, capacity=1000, max_charge_rate=1000, max_discharge_rate=1000)

    optimizer = Optimizer(import_prices=prices, export_prices=export_prices)
    results = optimizer.get_results()
    return {
        "objective_value": optimizer.objective_value,
        "results": json.loads(results.to_json(orient="split", date_format="iso")),
    }


    


