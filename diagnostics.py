
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/diagnostics", tags=["Diagnostics"])

class StreamData(BaseModel):
    rpm: int
    rail_actual: float
    rail_target: float
    boost: float
    maf: float
    coolant_temp: float

@router.post("/analyze")
async def analyze(data: StreamData):

    issues = []

    rail_diff = abs(data.rail_target - data.rail_actual)

    if rail_diff > 10:
        issues.append({
            "fault": "Fuel Pressure Deviation",
            "possible_causes": [
                "SCV Fault",
                "HP4 Pump Weak",
                "Injector Leak"
            ]
        })

    if data.boost < 100 and data.rpm > 2500:
        issues.append({
            "fault": "Possible Underboost",
            "possible_causes": [
                "Turbo VNT",
                "Boost Leak",
                "Vacuum Issue"
            ]
        })

    return {
        "status": "analyzed",
        "issues": issues
    }
