from datetime import datetime
import json
import re
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.data_collection.config import Config, set_config
from backend.data_collection.prices import SpotMarktPrices, ConstPrice

from backend.assets.pv import PV
from backend.assets.battery import Battery
from backend.assets.gridconnection import GridConnection
from backend.assets.load import ConstantLoadProfile, StandardLoadProfile

from backend.optimization.optimizer import Optimizer


class CalculationPayload(BaseModel):
    objects: list[dict[str, Any]]




app = FastAPI(title="HOME Optimization API", version="1.0.0")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

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
    try:
        objects = payload.objects

        # Define Config and basic checks
        classtypes = [obj.get("class", False) for obj in objects]
        if not all(classtypes): raise ValueError("Unknown or undefined class")
        if not "config" in classtypes: raise ValueError("No Config found")
        if not any(["load" in classtype for classtype in classtypes]): raise ValueError("Include at least one load object")



        for object in objects:
            #Unpack sub-dictionaries
            object = unpack_subdicts(object)
            class_type = object.get("class", False)
            if class_type == "config":
                set_config(Config(**object))
                # Define Model
                #prices = SpotMarktPrices(DATA_DIR / "spotmarktpreise.csv")
                export_prices = ConstPrice(const_price=0.08)
                prices = ConstPrice(const_price=0.35)
            elif class_type == "pv":
                PV(**object)
            elif class_type == "battery":
                Battery(**object)
            elif class_type =="const_load":
                ConstantLoadProfile(**object)
            elif class_type == "std_load":
                StandardLoadProfile(**object)
            elif class_type == "grid_connection":
                GridConnection(import_prices=prices, export_prices=export_prices, **object)


        optimizer = Optimizer()
        results = optimizer.get_results()
        initial_capex = optimizer.capex.to_dict(orient="records")[0] if not optimizer.capex.empty else {}
        Optimizer.objects.clear()
        return {
            "objective_value": optimizer.objective_value,
            "results": json.loads(results.to_json(orient="split", date_format="iso")),
            "initial_capex": initial_capex,
        }

    except ValueError as e:
        Optimizer.objects.clear()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        Optimizer.objects.clear()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


    


def unpack_subdicts(data: dict, result_dict:dict = {}):
    for key, value in data.items():
        if isinstance(value, dict):
            unpack_subdicts(value, result_dict)
        else:
            clear_key = re.sub(r"\s*\[.*?\]", "", key) #clear units from gui
            result_dict[clear_key] = value
    return result_dict