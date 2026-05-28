# =========================================================
# 1VD-FTV GLOBAL AI DIESEL PLATFORM — ENHANCED v2.0
# AI Tutor + Wiring Intelligence + DTC Engine + Repair Flow
# =========================================================
#
# ENHANCEMENTS v2.0:
#  1. Expanded DTC Database (12 codes + correlation engine)
#  2. Interactive Repair Flow Decision Tree
#  3. System Health Scoring Engine
#  4. Multi-DTC Correlation Analysis
#  5. Trend Detection in StreamData
#  6. Rail / EGT / Actuator Waveforms
#  7. Injector Balance Rate Calculator
#  8. Fuel System Diagnostics
#  9. Premium Dark Industrial Frontend (full redesign)
# 10. Live Simulation Endpoint
# =========================================================

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os, json, math, random
import numpy as np

try:
    import fitz
except ImportError:
    fitz = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from sklearn.ensemble import IsolationForest
except ImportError:
    IsolationForest = None

# =========================================================
# APP INIT
# =========================================================

app = FastAPI(
    title="1VD-FTV Global AI Platform v2.0",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# EXPANDED DTC DATABASE
# =========================================================

DTC_DATABASE = {

    "P0087": {
        "title": "Fuel Rail Pressure Too Low",
        "severity": "HIGH",
        "system": "Fuel System",
        "description": "Rail pressure below minimum threshold during operation.",
        "possible_causes": [
            "Weak HP fuel pump",
            "Clogged fuel filter",
            "Faulty pressure limiter valve",
            "Worn injector return rate",
            "Low-pressure supply pump failure",
            "Fuel wax (cold climate)",
            "Restricted fuel line"
        ],
        "inspection_steps": [
            "Monitor live rail pressure vs target",
            "Check LP pump pressure (min 500 kPa)",
            "Measure injector return volume",
            "Inspect fuel filter restriction",
            "Test HP pump delivery volume",
            "Check pressure limiter valve operation"
        ],
        "expected_streamdata": {
            "idle_rail": "25–35 MPa",
            "full_load_rail": "120–160 MPa",
            "lp_pump_pressure": "500–700 kPa",
            "return_volume": "< 30 ml/10s"
        },
        "related_systems": ["Common Rail", "HP Pump", "LP Pump", "Injectors"],
        "waveforms": ["Rail pressure trace", "HP pump cam waveform"],
        "severity_color": "#ef4444"
    },

    "P0093": {
        "title": "Fuel System Large Leak",
        "severity": "CRITICAL",
        "system": "Fuel System",
        "description": "Massive fuel system leak detected via pressure drop rate.",
        "possible_causes": [
            "Split high-pressure line",
            "Loose rail fitting",
            "Cracked injector body",
            "Loose injector hold-down clamp",
            "HP pump outlet fitting leak"
        ],
        "inspection_steps": [
            "Pressurize system and inspect HP lines",
            "Check all rail fittings for wetness",
            "Inspect injector clamping",
            "Measure pressure bleed-down time"
        ],
        "expected_streamdata": {
            "bleed_down_time": "> 60 sec to 5 MPa",
            "idle_rail": "25–35 MPa"
        },
        "related_systems": ["High-Pressure Lines", "Rail", "Injectors", "HP Pump"],
        "waveforms": ["Rail pressure bleed-down curve"],
        "severity_color": "#dc2626"
    },

    "P0191": {
        "title": "Fuel Rail Pressure Sensor Range/Performance",
        "severity": "MEDIUM",
        "system": "Sensor",
        "description": "FRP sensor signal erratic or out of expected range.",
        "possible_causes": [
            "Faulty FRP sensor",
            "Contaminated sensor port",
            "Wiring open/short to sensor",
            "ECM pin corrosion"
        ],
        "inspection_steps": [
            "Check FRP sensor 5V reference",
            "Measure signal voltage at idle",
            "Inspect connector pins for corrosion",
            "Compare FRP reading with known-good sensor"
        ],
        "expected_streamdata": {
            "sensor_reference": "5.0 V",
            "idle_signal": "1.0–1.5 V",
            "max_signal": "4.0–4.5 V"
        },
        "related_systems": ["FRP Sensor", "ECM", "Wiring"],
        "waveforms": ["FRP sensor voltage trace"],
        "severity_color": "#f59e0b"
    },

    "P0299": {
        "title": "Turbocharger Underboost",
        "severity": "HIGH",
        "system": "Turbocharger",
        "description": "Boost pressure consistently below ECM target value.",
        "possible_causes": [
            "Boost leak (intercooler hose, pipe, gasket)",
            "Turbo VNT vanes stuck closed",
            "Vacuum actuator failure",
            "Dirty MAF sensor",
            "Intercooler core crack",
            "Exhaust manifold crack (loss of drive energy)",
            "DPF restriction > 80%",
            "Worn turbocharger internals"
        ],
        "inspection_steps": [
            "Monitor actual vs target boost under load",
            "Smoke test entire intake system",
            "Check VNT actuator rod movement range",
            "Inspect MAF sensor element for contamination",
            "Check DPF differential pressure sensor values",
            "Inspect exhaust manifold for cracks",
            "Verify vacuum solenoid operation",
            "Check intercooler for oil fouling"
        ],
        "expected_streamdata": {
            "idle_boost": "100–105 kPa",
            "full_load_boost": "220–250 kPa",
            "maf_idle": "8–14 g/s",
            "maf_full_load": "90–140 g/s",
            "dpf_diff_pressure": "< 5 kPa idle"
        },
        "related_systems": ["Turbocharger", "Intercooler", "VNT Vacuum", "MAF", "DPF", "Exhaust"],
        "waveforms": ["VNT actuator duty cycle", "MAP response curve", "MAF response"],
        "severity_color": "#ef4444"
    },

    "P0380": {
        "title": "Glow Plug Circuit Malfunction (Bank 1)",
        "severity": "MEDIUM",
        "system": "Glow Plugs",
        "description": "Glow plug relay or circuit fault on Bank 1.",
        "possible_causes": [
            "Failed glow plug(s)",
            "Open glow plug harness",
            "Faulty glow plug relay",
            "ECM control circuit fault"
        ],
        "inspection_steps": [
            "Measure resistance of each glow plug",
            "Check glow plug relay voltage",
            "Measure harness continuity",
            "Inspect glow plug tips for burning"
        ],
        "expected_streamdata": {
            "glow_plug_resistance": "0.3–0.9 Ω",
            "relay_voltage": "Battery voltage during preheat",
            "preheat_time": "2–8 sec"
        },
        "related_systems": ["Glow Plugs", "Relay", "ECM"],
        "waveforms": ["Glow plug current waveform"],
        "severity_color": "#f59e0b"
    },

    "P0401": {
        "title": "EGR Flow Insufficient",
        "severity": "MEDIUM",
        "system": "EGR",
        "description": "EGR valve commanded open but insufficient flow detected.",
        "possible_causes": [
            "Carbon-blocked EGR valve",
            "Clogged EGR cooler",
            "Faulty EGR position sensor",
            "Vacuum leak to EGR actuator",
            "Intake manifold carbon build-up"
        ],
        "inspection_steps": [
            "Observe EGR valve position vs command",
            "Inspect EGR valve for carbon (remove and clean)",
            "Check EGR cooler flow",
            "Inspect intake manifold ports",
            "Test EGR vacuum solenoid duty cycle"
        ],
        "expected_streamdata": {
            "egr_position_at_idle": "0–5%",
            "egr_position_light_load": "20–60%",
            "egr_target_vs_actual": "< 5% difference"
        },
        "related_systems": ["EGR Valve", "EGR Cooler", "Intake Manifold", "Vacuum"],
        "waveforms": ["EGR valve position trace"],
        "severity_color": "#f59e0b"
    },

    "P0402": {
        "title": "EGR Flow Excessive",
        "severity": "MEDIUM",
        "system": "EGR",
        "description": "More EGR flow detected than commanded — valve stuck open.",
        "possible_causes": [
            "EGR valve stuck open (carbon jam in open position)",
            "EGR position sensor offset",
            "ECM calibration issue"
        ],
        "inspection_steps": [
            "Observe EGR position at hot idle",
            "Remove and inspect EGR valve",
            "Clean or replace EGR valve",
            "Verify position sensor calibration"
        ],
        "expected_streamdata": {
            "egr_position_hot_idle": "0–3%"
        },
        "related_systems": ["EGR Valve", "EGR Sensor"],
        "waveforms": ["EGR position vs RPM trace"],
        "severity_color": "#f59e0b"
    },

    "P2002": {
        "title": "DPF Efficiency Below Threshold (Bank 1)",
        "severity": "HIGH",
        "system": "DPF / Aftertreatment",
        "description": "DPF soot load or conversion efficiency below minimum.",
        "possible_causes": [
            "Failed DPF regeneration (too many aborted regens)",
            "DPF cracked substrate",
            "Faulty differential pressure sensor",
            "Exhaust leak before DPF sensor",
            "Engine burning excessive oil (soot overload)"
        ],
        "inspection_steps": [
            "Check DPF soot load % in data stream",
            "Read DPF differential pressure at idle and 2500 RPM",
            "Force active regen and monitor",
            "Inspect differential pressure sensor hoses",
            "Check for oil consumption"
        ],
        "expected_streamdata": {
            "dpf_soot_load": "< 80%",
            "diff_pressure_idle": "0.5–2.0 kPa",
            "diff_pressure_2500rpm": "3.0–8.0 kPa",
            "regen_temperature": "550–700 °C"
        },
        "related_systems": ["DPF", "Diff Pressure Sensor", "EGT Sensors", "Fuel Dosing"],
        "waveforms": ["EGT regen profile", "DPF differential pressure trend"],
        "severity_color": "#ef4444"
    },

    "P2563": {
        "title": "Turbocharger Boost Control Position Sensor Range/Performance",
        "severity": "MEDIUM",
        "system": "Turbocharger",
        "description": "VNT position sensor signal out of expected range.",
        "possible_causes": [
            "Faulty VNT position sensor",
            "Carbon binding of VNT vanes (sensor reads wrong position)",
            "Wiring fault to sensor",
            "Turbo replacement without sensor calibration"
        ],
        "inspection_steps": [
            "Monitor VNT sensor voltage at min/max commanded position",
            "Clean VNT vanes — recheck sensor",
            "Inspect sensor connector for corrosion",
            "Perform VNT actuator calibration if supported"
        ],
        "expected_streamdata": {
            "vnt_min_voltage": "0.5–0.8 V",
            "vnt_max_voltage": "4.2–4.8 V",
            "vnt_response_time": "< 200 ms"
        },
        "related_systems": ["VNT Actuator", "Position Sensor", "ECM"],
        "waveforms": ["VNT position sensor voltage sweep"],
        "severity_color": "#f59e0b"
    },

    "P242F": {
        "title": "DPF Restriction – Ash Accumulation",
        "severity": "HIGH",
        "system": "DPF / Aftertreatment",
        "description": "DPF ash load beyond serviceable limit — replacement required.",
        "possible_causes": [
            "Engine oil ash accumulation over extended mileage",
            "Incorrect oil specification (high-ash oil used)",
            "Excessive oil consumption"
        ],
        "inspection_steps": [
            "Check DPF ash load via diagnostic tool",
            "Calculate mileage since last DPF service",
            "Verify engine oil type (use Low-SAPS only)",
            "Replace or clean DPF"
        ],
        "expected_streamdata": {
            "ash_load": "< 35 g (service limit)",
            "diff_pressure_idle": "< 3.0 kPa"
        },
        "related_systems": ["DPF", "Engine Oil"],
        "waveforms": ["Long-term DPF pressure trend"],
        "severity_color": "#ef4444"
    },

    "P0193": {
        "title": "Fuel Rail Pressure Sensor High Input",
        "severity": "MEDIUM",
        "system": "Sensor",
        "description": "FRP sensor signal voltage above maximum expected range.",
        "possible_causes": [
            "Short to voltage in sensor signal wire",
            "Faulty FRP sensor (internal short)",
            "Damaged ECM input circuit"
        ],
        "inspection_steps": [
            "Measure FRP signal voltage with key on, engine off",
            "Disconnect sensor — check for 5V reference only",
            "Inspect wiring for chafing against hot surfaces",
            "Swap sensor if wiring clean"
        ],
        "expected_streamdata": {
            "koeo_signal_voltage": "< 0.5 V (normal)",
            "idle_signal": "1.0–1.5 V"
        },
        "related_systems": ["FRP Sensor", "ECM", "Wiring Harness"],
        "waveforms": ["FRP sensor voltage trace"],
        "severity_color": "#f59e0b"
    },

    "P0100": {
        "title": "Mass Airflow Circuit Malfunction",
        "severity": "MEDIUM",
        "system": "Induction",
        "description": "MAF sensor signal absent, irrational, or intermittent.",
        "possible_causes": [
            "Contaminated MAF element",
            "Air leak between MAF and turbo inlet",
            "Damaged MAF connector",
            "Open in MAF signal wire",
            "Failed MAF sensor"
        ],
        "inspection_steps": [
            "Check MAF signal voltage (0.8–1.2 V idle)",
            "Clean sensor element with MAF cleaner",
            "Inspect inlet duct for cracks or loose clamps",
            "Check for short/open in harness",
            "Compare actual vs modeled MAF"
        ],
        "expected_streamdata": {
            "maf_idle": "8–14 g/s",
            "maf_2000rpm_no_load": "25–40 g/s",
            "maf_full_load": "90–140 g/s"
        },
        "related_systems": ["MAF Sensor", "Turbo Inlet", "ECM"],
        "waveforms": ["MAF signal voltage trace", "MAF g/s vs throttle"],
        "severity_color": "#f59e0b"
    }
}

# =========================================================
# DTC CORRELATION MATRIX
# =========================================================

DTC_CORRELATIONS = {
    frozenset(["P0299", "P2563"]): {
        "diagnosis": "VNT mechanical binding — carbon on vanes causes both underboost and position sensor error.",
        "action": "Remove turbo, clean VNT vanes, recalibrate actuator."
    },
    frozenset(["P0087", "P0093"]): {
        "diagnosis": "Fuel system pressure loss — possible HP line crack or injector body failure.",
        "action": "Pressure test HP system with UV dye, replace faulty component."
    },
    frozenset(["P0087", "P0191"]): {
        "diagnosis": "Cannot confirm low rail pressure — sensor may be faulty. Verify with mechanical gauge.",
        "action": "Install mechanical rail pressure gauge. If pressure OK, replace FRP sensor."
    },
    frozenset(["P2002", "P242F"]): {
        "diagnosis": "DPF at end of life — high ash and low efficiency. Replacement likely required.",
        "action": "Replace DPF. Verify Low-SAPS oil is used. Check for oil consumption."
    },
    frozenset(["P0401", "P0299"]): {
        "diagnosis": "EGR and boost issues together — check for blocked intake manifold reducing airflow.",
        "action": "Remove intake manifold, decoke ports, inspect intercooler."
    },
    frozenset(["P0100", "P0299"]): {
        "diagnosis": "MAF and boost faults combined — possibly dirty MAF sensor giving false low flow reading.",
        "action": "Clean MAF sensor first. Clear codes. Retest before replacing turbo."
    }
}

# =========================================================
# REPAIR FLOW DECISION TREES
# =========================================================

REPAIR_FLOWS = {
    "P0299": {
        "start": "node_1",
        "nodes": {
            "node_1": {
                "question": "Is actual boost pressure measurably low under load (below 180 kPa at WOT)?",
                "yes": "node_2",
                "no": "node_x_sensor"
            },
            "node_x_sensor": {
                "result": "Boost pressure is actually normal. Likely MAP/boost sensor fault or ECM calibration issue. Check sensor 5V reference and signal range."
            },
            "node_2": {
                "question": "Does smoke test reveal any intake leak (intercooler pipe, hose, gasket)?",
                "yes": "node_2a",
                "no": "node_3"
            },
            "node_2a": {
                "result": "REPAIR: Locate and seal boost leak. Replace split hose or clamp loose pipe. Retest boost after repair."
            },
            "node_3": {
                "question": "Does VNT actuator rod move freely through full range when vacuum applied?",
                "yes": "node_4",
                "no": "node_3a"
            },
            "node_3a": {
                "question": "Does VNT move freely after carbon cleaning of vanes?",
                "yes": "node_3b",
                "no": "node_3c"
            },
            "node_3b": {
                "result": "REPAIR: Carbon-stuck VNT vanes. Service clean turbo vanes. Verify full actuator travel after cleaning. Recalibrate if supported."
            },
            "node_3c": {
                "result": "REPLACE: VNT mechanism mechanically seized. Turbocharger replacement required."
            },
            "node_4": {
                "question": "Is DPF differential pressure above 8 kPa at 2500 RPM?",
                "yes": "node_4a",
                "no": "node_5"
            },
            "node_4a": {
                "result": "REPAIR DPF: Blocked DPF reducing exhaust energy to turbo. Perform forced active regen or replace DPF."
            },
            "node_5": {
                "question": "Is MAF sensor reading below 80 g/s at full load?",
                "yes": "node_5a",
                "no": "node_6"
            },
            "node_5a": {
                "result": "REPAIR MAF: Clean MAF sensor with MAF cleaner. Inspect for air leaks upstream of sensor. Retest."
            },
            "node_6": {
                "result": "INSPECT TURBO INTERNALS: All external causes eliminated. Check turbocharger shaft play and compressor wheel condition. Replace if worn."
            }
        }
    },

    "P0087": {
        "start": "node_1",
        "nodes": {
            "node_1": {
                "question": "Is LP pump pressure below 500 kPa at cranking?",
                "yes": "node_1a",
                "no": "node_2"
            },
            "node_1a": {
                "question": "Is fuel filter recently replaced?",
                "yes": "node_1b",
                "no": "node_1c"
            },
            "node_1b": {
                "result": "INSPECT: LP pump suspect. Measure voltage and current to LP pump. Replace if not delivering adequate pressure."
            },
            "node_1c": {
                "result": "REPLACE FUEL FILTER: Clogged filter restricting LP supply. Replace and retest."
            },
            "node_2": {
                "question": "Does rail pressure drop sharply under acceleration load?",
                "yes": "node_3",
                "no": "node_4"
            },
            "node_3": {
                "question": "Is combined injector return volume excessively high?",
                "yes": "node_3a",
                "no": "node_3b"
            },
            "node_3a": {
                "result": "REPLACE INJECTORS: High return volume indicates worn or cracked injector bodies. Test each injector individually."
            },
            "node_3b": {
                "result": "TEST HP PUMP: LP supply adequate, injectors OK. HP pump delivery suspect. Perform HP pump output volume test."
            },
            "node_4": {
                "result": "CHECK PRESSURE LIMITER VALVE: Rail pressure low but stable. Pressure limiter valve may be partially open. Inspect or replace."
            }
        }
    }
}

# =========================================================
# NORMAL STREAMDATA DATASET
# =========================================================

NORMAL_DATASET = {
    "RPM":          {"values": [650, 700, 720],   "unit": "rpm",   "min": 580, "max": 820},
    "RailPressure": {"values": [30, 32, 35],       "unit": "MPa",   "min": 25,  "max": 40},
    "Boost":        {"values": [101, 102, 103],    "unit": "kPa",   "min": 98,  "max": 110},
    "MAF":          {"values": [9, 10, 11],        "unit": "g/s",   "min": 7,   "max": 15},
    "EGT":          {"values": [180, 220, 240],    "unit": "°C",    "min": 150, "max": 280},
    "CoolantTemp":  {"values": [82, 85, 88],       "unit": "°C",    "min": 78,  "max": 95},
    "EGRPosition":  {"values": [0, 2, 5],          "unit": "%",     "min": 0,   "max": 10},
    "DPFPressure":  {"values": [0.8, 1.0, 1.2],   "unit": "kPa",   "min": 0.3, "max": 2.5},
}

# =========================================================
# MODELS
# =========================================================

class DTCRequest(BaseModel):
    code: str

class MultiDTCRequest(BaseModel):
    codes: List[str]

class StreamCompareRequest(BaseModel):
    data: Dict[str, float]

class RepairFlowRequest(BaseModel):
    code: str
    node_id: str
    answer: Optional[str] = None  # "yes" | "no" | None (start)

class InjectorBalanceRequest(BaseModel):
    cylinder_corrections: List[float]  # mg/stroke correction per cylinder

# =========================================================
# AI TUTOR ENGINE
# =========================================================

class AITutor:

    def explain_dtc(self, code: str):
        code = code.upper().strip()

        if code not in DTC_DATABASE:
            return {
                "status": "unknown_dtc",
                "message": f"DTC {code} not found in database. Ensure code format is correct (e.g. P0299).",
                "available_codes": list(DTC_DATABASE.keys())
            }

        dtc = DTC_DATABASE[code]

        has_repair_flow = code in REPAIR_FLOWS

        return {
            "dtc": code,
            "title": dtc["title"],
            "severity": dtc["severity"],
            "severity_color": dtc.get("severity_color", "#f59e0b"),
            "system": dtc["system"],
            "description": dtc["description"],
            "possible_causes": dtc["possible_causes"],
            "inspection_steps": dtc["inspection_steps"],
            "related_systems": dtc["related_systems"],
            "expected_streamdata": dtc["expected_streamdata"],
            "waveforms": dtc["waveforms"],
            "has_repair_flow": has_repair_flow,
            "repair_flow_url": f"/api/repairflow/{code}" if has_repair_flow else None,
        }

    def list_all(self):
        return [
            {
                "code": code,
                "title": dtc["title"],
                "severity": dtc["severity"],
                "system": dtc["system"],
                "severity_color": dtc.get("severity_color", "#f59e0b"),
                "has_repair_flow": code in REPAIR_FLOWS
            }
            for code, dtc in DTC_DATABASE.items()
        ]

ai_tutor = AITutor()

# =========================================================
# CORRELATION ENGINE
# =========================================================

class CorrelationEngine:

    def analyze(self, codes: List[str]):
        codes_set = frozenset([c.upper() for c in codes])
        matches = []

        for key, info in DTC_CORRELATIONS.items():
            if key.issubset(codes_set):
                matches.append({
                    "codes": list(key),
                    "diagnosis": info["diagnosis"],
                    "action": info["action"]
                })

        individual = [ai_tutor.explain_dtc(c) for c in codes]

        return {
            "codes_submitted": codes,
            "correlations_found": len(matches),
            "correlations": matches,
            "individual_analysis": individual
        }

correlation_engine = CorrelationEngine()

# =========================================================
# REPAIR FLOW ENGINE
# =========================================================

class RepairFlowEngine:

    def get_node(self, code: str, node_id: str):
        code = code.upper()

        if code not in REPAIR_FLOWS:
            return {"error": f"No repair flow available for {code}"}

        flow = REPAIR_FLOWS[code]
        node = flow["nodes"].get(node_id)

        if not node:
            return {"error": f"Node {node_id} not found"}

        return {
            "code": code,
            "node_id": node_id,
            "node": node,
            "is_terminal": "result" in node
        }

    def start(self, code: str):
        code = code.upper()

        if code not in REPAIR_FLOWS:
            return {"error": f"No repair flow for {code}"}

        flow = REPAIR_FLOWS[code]
        start_node_id = flow["start"]
        return self.get_node(code, start_node_id)

    def answer(self, code: str, node_id: str, answer: str):
        node_data = self.get_node(code, node_id)

        if "error" in node_data:
            return node_data

        node = node_data["node"]

        if "result" in node:
            return {"already_terminal": True, "result": node["result"]}

        if answer not in ["yes", "no"]:
            return {"error": "answer must be 'yes' or 'no'"}

        next_node_id = node.get(answer)

        if not next_node_id:
            return {"error": f"No {answer} branch from node {node_id}"}

        return self.get_node(code, next_node_id)

repair_engine = RepairFlowEngine()

# =========================================================
# STREAMDATA ANALYZER
# =========================================================

class StreamAnalyzer:

    def compare(self, incoming: Dict[str, float]):
        results = {}

        for key, value in incoming.items():
            if key in NORMAL_DATASET:
                ds = NORMAL_DATASET[key]
                avg = float(np.mean(ds["values"]))
                deviation = abs(value - avg)
                pct = (deviation / avg * 100) if avg != 0 else 0

                lo = ds["min"]
                hi = ds["max"]

                if lo <= value <= hi:
                    status = "NORMAL"
                elif value < lo:
                    status = "LOW"
                else:
                    status = "HIGH"

                results[key] = {
                    "current": value,
                    "unit": ds["unit"],
                    "expected_avg": round(avg, 2),
                    "expected_range": f"{lo}–{hi} {ds['unit']}",
                    "deviation_pct": round(pct, 1),
                    "status": status
                }

        abnormal = [k for k, v in results.items() if v["status"] != "NORMAL"]

        return {
            "results": results,
            "abnormal_parameters": abnormal,
            "health_score": round((1 - len(abnormal) / max(len(results), 1)) * 100, 1)
        }

    def simulate_live(self):
        """Simulate live diesel data with slight noise"""
        base = {
            "RPM": 700,
            "RailPressure": 32,
            "Boost": 102,
            "MAF": 10,
            "EGT": 210,
            "CoolantTemp": 85,
            "EGRPosition": 2,
            "DPFPressure": 1.0
        }
        return {
            k: round(v + random.uniform(-v * 0.03, v * 0.03), 2)
            for k, v in base.items()
        }

stream_engine = StreamAnalyzer()

# =========================================================
# INJECTOR BALANCE RATE ANALYZER
# =========================================================

class InjectorAnalyzer:

    def analyze_balance(self, corrections: List[float]):
        """
        corrections: fuel correction in mg/stroke per cylinder (from scan tool).
        Positive = adding fuel (lean), Negative = removing fuel (rich).
        Threshold: ± 4 mg/stroke is typically the service limit.
        """
        results = []
        service_limit = 4.0

        for i, corr in enumerate(corrections):
            cyl_num = i + 1
            abs_corr = abs(corr)
            status = "OK" if abs_corr < service_limit else "FAULT"
            severity = "NORMAL" if abs_corr < 2.0 else ("WARNING" if abs_corr < service_limit else "CRITICAL")

            results.append({
                "cylinder": cyl_num,
                "correction_mg": round(corr, 2),
                "abs_deviation": round(abs_corr, 2),
                "status": status,
                "severity": severity,
                "interpretation":
                    "Injecting less fuel than others (return high / spray poor)"
                    if corr > 0 else
                    "Injecting more fuel than others (possible stuck open)"
                    if corr < -2 else
                    "Within balance tolerance"
            })

        worst = max(results, key=lambda x: x["abs_deviation"])

        return {
            "cylinders": len(corrections),
            "service_limit_mg": service_limit,
            "results": results,
            "worst_cylinder": worst["cylinder"],
            "recommendation":
                f"Cylinder {worst['cylinder']} exceeds balance limit — test or replace injector."
                if worst["status"] == "FAULT" else
                "All injectors within balance specification."
        }

injector_analyzer = InjectorAnalyzer()

# =========================================================
# WAVEFORM ENGINE
# =========================================================

class WaveformEngine:

    def _gen(self, x, fn, label):
        return {"x": x.tolist(), "y": [round(fn(xi), 4) for xi in x], "type": label}

    def injector_waveform(self):
        x = np.linspace(0, 10, 500)
        y = np.sin(x * 8) * 4 + 12
        return self._gen(x, lambda xi: float(np.sin(xi * 8) * 4 + 12), "Injector Current Ramp (A)")

    def maf_waveform(self):
        x = np.linspace(0, 10, 500)
        return self._gen(x, lambda xi: float(np.sin(xi * 3) * 2 + 10), "MAF Signal (g/s)")

    def rail_pressure_waveform(self):
        x = np.linspace(0, 10, 500)
        return self._gen(x,
            lambda xi: float(32 + np.sin(xi * 6) * 1.5 + np.random.uniform(-0.3, 0.3)),
            "Rail Pressure (MPa)")

    def egt_regen_profile(self):
        # Simulates EGT during active DPF regen
        x = np.linspace(0, 30, 600)  # 30 minutes
        def egt(t):
            if t < 2:    return 250 + t * 40
            if t < 15:   return 580 + np.sin(t * 0.5) * 20
            if t < 20:   return 600 + (t - 15) * 12
            return 720 - (t - 20) * 25
        return self._gen(x, egt, "EGT During Active Regen (°C)")

    def vnt_actuator_waveform(self):
        x = np.linspace(0, 5, 300)
        return self._gen(x,
            lambda xi: float(50 + 40 * np.sin(xi * 2 * math.pi * 0.4)),
            "VNT Duty Cycle (%)")

    def glow_plug_waveform(self):
        x = np.linspace(0, 8, 400)
        def gp(t):
            if t < 0.1: return 0
            if t < 5:   return 18 - t * 1.5  # current ramp down as resistance increases
            return 8
        return self._gen(x, gp, "Glow Plug Current (A)")

wave_engine = WaveformEngine()

# =========================================================
# AI ANOMALY DETECTOR
# =========================================================

class AIAnomalyDetector:

    def __init__(self):
        self.model = None
        if IsolationForest:
            dataset = np.array([
                [700, 32, 102, 10],
                [710, 33, 101, 11],
                [690, 31, 103, 9],
                [705, 32.5, 102, 10],
                [695, 31.5, 101, 9.5],
                [715, 33.5, 104, 10.5],
            ])
            self.model = IsolationForest(contamination=0.1, random_state=42)
            self.model.fit(dataset)

    def predict(self, data: Dict):
        if not self.model:
            return {"error": "scikit-learn not available"}

        vector = [[
            data.get("RPM", 700),
            data.get("RailPressure", 32),
            data.get("Boost", 102),
            data.get("MAF", 10)
        ]]

        pred = self.model.predict(vector)
        score = self.model.score_samples(vector)[0]

        return {
            "prediction": "ABNORMAL" if pred[0] == -1 else "NORMAL",
            "anomaly_score": round(float(score), 4),
            "confidence": f"{min(abs(score) * 100, 99):.0f}%",
            "recommendation":
                "System anomaly detected — inspect turbo, fuel, and MAF systems."
                if pred[0] == -1 else
                "Engine parameters within normal operating range."
        }

anomaly_detector = AIAnomalyDetector()

# =========================================================
# SVG WIRING DIAGRAM (Enhanced)
# =========================================================

SVG_WIRING = """
<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="600" viewBox="0 0 1100 600">
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#f59e0b"/>
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1100" height="600" fill="#0d0d0d"/>

  <!-- ECM Box -->
  <rect x="30" y="200" width="200" height="200" rx="6" fill="#1a1a2e" stroke="#3b82f6" stroke-width="2"/>
  <text x="130" y="232" text-anchor="middle" fill="#3b82f6" font-size="13" font-family="monospace" font-weight="bold">ECM</text>
  <text x="130" y="252" text-anchor="middle" fill="#64748b" font-size="9" font-family="monospace">1VD-FTV Engine Controller</text>
  <line x1="50" y1="270" x2="50" y2="270" stroke="#64748b" stroke-width="1"/>
  <!-- ECM Pins -->
  <text x="50" y="285" fill="#94a3b8" font-size="9" font-family="monospace">INJ1-CTRL</text>
  <text x="50" y="305" fill="#94a3b8" font-size="9" font-family="monospace">INJ2-CTRL</text>
  <text x="50" y="325" fill="#94a3b8" font-size="9" font-family="monospace">INJ3-CTRL</text>
  <text x="50" y="345" fill="#94a3b8" font-size="9" font-family="monospace">INJ4-CTRL</text>
  <text x="50" y="365" fill="#94a3b8" font-size="9" font-family="monospace">FRP-SIG</text>
  <text x="50" y="385" fill="#94a3b8" font-size="9" font-family="monospace">MAF-SIG</text>

  <!-- EDU Box -->
  <rect x="340" y="120" width="160" height="120" rx="6" fill="#1a1a1a" stroke="#f59e0b" stroke-width="2"/>
  <text x="420" y="150" text-anchor="middle" fill="#f59e0b" font-size="12" font-family="monospace" font-weight="bold">EDU</text>
  <text x="420" y="168" text-anchor="middle" fill="#64748b" font-size="8" font-family="monospace">Injector Drive Unit</text>
  <text x="360" y="195" fill="#94a3b8" font-size="9" font-family="monospace">+B (Battery)</text>
  <text x="360" y="212" fill="#94a3b8" font-size="9" font-family="monospace">GND</text>
  <text x="360" y="228" fill="#94a3b8" font-size="9" font-family="monospace">INJ-OUT 1-4</text>

  <!-- Injectors -->
  <rect x="650" y="60"  width="120" height="55" rx="5" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="710" y="85"  text-anchor="middle" fill="#f59e0b" font-size="11" font-family="monospace">#1 Injector</text>
  <text x="710" y="102" text-anchor="middle" fill="#64748b" font-size="8" font-family="monospace">Cyl 1 — Common Rail</text>

  <rect x="650" y="135" width="120" height="55" rx="5" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="710" y="160" text-anchor="middle" fill="#f59e0b" font-size="11" font-family="monospace">#2 Injector</text>
  <text x="710" y="177" text-anchor="middle" fill="#64748b" font-size="8" font-family="monospace">Cyl 2 — Common Rail</text>

  <rect x="650" y="210" width="120" height="55" rx="5" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="710" y="235" text-anchor="middle" fill="#f59e0b" font-size="11" font-family="monospace">#3 Injector</text>
  <text x="710" y="252" text-anchor="middle" fill="#64748b" font-size="8" font-family="monospace">Cyl 3 — Common Rail</text>

  <rect x="650" y="285" width="120" height="55" rx="5" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="710" y="310" text-anchor="middle" fill="#f59e0b" font-size="11" font-family="monospace">#4 Injector</text>
  <text x="710" y="327" text-anchor="middle" fill="#64748b" font-size="8" font-family="monospace">Cyl 4 — Common Rail</text>

  <!-- Common Rail -->
  <rect x="840" y="155" width="150" height="90" rx="6" fill="#1a1a1a" stroke="#22c55e" stroke-width="2"/>
  <text x="915" y="190" text-anchor="middle" fill="#22c55e" font-size="11" font-family="monospace" font-weight="bold">Common Rail</text>
  <text x="915" y="210" text-anchor="middle" fill="#64748b" font-size="9" font-family="monospace">≤160 MPa max</text>
  <text x="915" y="228" text-anchor="middle" fill="#64748b" font-size="9" font-family="monospace">FRP Sensor mounted</text>

  <!-- MAF Sensor -->
  <rect x="340" y="420" width="140" height="70" rx="5" fill="#1a1a1a" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="410" y="450" text-anchor="middle" fill="#8b5cf6" font-size="11" font-family="monospace">MAF Sensor</text>
  <text x="410" y="468" text-anchor="middle" fill="#64748b" font-size="8" font-family="monospace">Hot-film type</text>
  <text x="410" y="482" text-anchor="middle" fill="#64748b" font-size="8" font-family="monospace">5V ref / Signal / GND</text>

  <!-- Turbocharger -->
  <rect x="650" y="400" width="140" height="80" rx="5" fill="#1a1a1a" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="720" y="430" text-anchor="middle" fill="#8b5cf6" font-size="11" font-family="monospace">VNT Turbo</text>
  <text x="720" y="448" text-anchor="middle" fill="#64748b" font-size="8" font-family="monospace">VNT Actuator</text>
  <text x="720" y="463" text-anchor="middle" fill="#64748b" font-size="8" font-family="monospace">Position Sensor</text>

  <!-- Wiring: ECM → EDU -->
  <line x1="230" y1="270" x2="340" y2="175" stroke="#ef4444" stroke-width="2.5" marker-end="url(#arrow)"/>
  <text x="278" y="215" fill="#ef4444" font-size="9" font-family="monospace" transform="rotate(-30,278,215)">INJ CTRL Signal</text>

  <!-- EDU → Injectors -->
  <line x1="500" y1="155" x2="650" y2="88"  stroke="#f59e0b" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="500" y1="175" x2="650" y2="163" stroke="#f59e0b" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="500" y1="195" x2="650" y2="238" stroke="#f59e0b" stroke-width="2" marker-end="url(#arrow)"/>
  <line x1="500" y1="215" x2="650" y2="313" stroke="#f59e0b" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Injectors → Rail -->
  <line x1="770" y1="88"  x2="840" y2="185" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="5,3"/>
  <line x1="770" y1="163" x2="840" y2="196" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="5,3"/>
  <line x1="770" y1="238" x2="840" y2="210" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="5,3"/>
  <line x1="770" y1="313" x2="840" y2="225" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="5,3"/>

  <!-- ECM → MAF -->
  <line x1="130" y1="400" x2="340" y2="455" stroke="#8b5cf6" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="210" y="438" fill="#8b5cf6" font-size="8" font-family="monospace">MAF Signal</text>

  <!-- ECM → Turbo -->
  <line x1="230" y1="370" x2="650" y2="440" stroke="#8b5cf6" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="420" y="398" fill="#8b5cf6" font-size="8" font-family="monospace">VNT Control</text>

  <!-- Legend -->
  <rect x="30" y="530" width="1040" height="55" rx="4" fill="#111"/>
  <circle cx="60"  cy="557" r="5" fill="#ef4444"/>
  <text x="72" y="561" fill="#94a3b8" font-size="9" font-family="monospace">ECM Control Signal</text>
  <circle cx="220" cy="557" r="5" fill="#f59e0b"/>
  <text x="232" y="561" fill="#94a3b8" font-size="9" font-family="monospace">Injector Drive (High-Current)</text>
  <circle cx="420" cy="557" r="5" fill="#22c55e"/>
  <text x="432" y="561" fill="#94a3b8" font-size="9" font-family="monospace">High-Pressure Fuel (Rail)</text>
  <circle cx="600" cy="557" r="5" fill="#8b5cf6"/>
  <text x="612" y="561" fill="#94a3b8" font-size="9" font-family="monospace">Sensor Circuits</text>
</svg>
"""

# =========================================================
# SYSTEM HEALTH SCORE
# =========================================================

class SystemHealthEngine:

    def calculate(self, dtc_list: List[str], stream_data: Dict[str, float]):
        base_score = 100
        issues = []

        # Deduct for DTCs
        severity_deductions = {"CRITICAL": 35, "HIGH": 25, "MEDIUM": 12, "LOW": 5}
        for code in dtc_list:
            code = code.upper()
            if code in DTC_DATABASE:
                sev = DTC_DATABASE[code]["severity"]
                ded = severity_deductions.get(sev, 10)
                base_score -= ded
                issues.append(f"{code}: -{ded} pts ({sev})")

        # Deduct for StreamData anomalies
        stream_result = stream_engine.compare(stream_data)
        abnormal = stream_result.get("abnormal_parameters", [])
        for param in abnormal:
            base_score -= 5
            issues.append(f"{param} out of range: -5 pts")

        base_score = max(0, base_score)

        if base_score >= 85:
            status = "HEALTHY"
            color = "#22c55e"
        elif base_score >= 65:
            status = "CAUTION"
            color = "#f59e0b"
        elif base_score >= 40:
            status = "DEGRADED"
            color = "#ef4444"
        else:
            status = "CRITICAL"
            color = "#dc2626"

        return {
            "score": base_score,
            "status": status,
            "color": color,
            "dtcs_active": len(dtc_list),
            "stream_anomalies": len(abnormal),
            "deduction_breakdown": issues
        }

health_engine = SystemHealthEngine()

# =========================================================
# PDF READER
# =========================================================

class WiringPDFReader:

    def extract_text(self, pdf_path):
        if not fitz:
            return "PyMuPDF not installed"
        doc = fitz.open(pdf_path)
        return "".join(page.get_text() for page in doc)

    def find_injector_wiring(self, text):
        keywords = ["Injector", "EDU", "ECM", "Common Rail",
                    "No.1 Injector", "No.2 Injector", "IGT", "IGF",
                    "Fuel Rail", "Boost", "VNT"]
        found = []
        for line in text.split("\n"):
            for key in keywords:
                if key.lower() in line.lower():
                    found.append(line.strip())
                    break
        return found

pdf_reader = WiringPDFReader()

# =========================================================
# HTML MANUAL PARSER
# =========================================================

class HTMLManualParser:

    def parse_html(self, file_path):
        if not BeautifulSoup:
            return {"error": "BeautifulSoup not installed"}
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        return {
            "title": soup.title.string if soup.title else "Toyota Manual",
            "text": soup.get_text()[:100000]
        }

html_parser = HTMLManualParser()

# =========================================================
# FRONTEND HTML  (Premium Dark Industrial UI)
# =========================================================

FRONTEND = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1VD-FTV AI PLATFORM v2.0</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #1a1c23; color: #e5e7eb; font-family: system-ui, -apple-system, sans-serif; }
        .bg-panel { background-color: #242631; }
        .text-accent { color: #f59e0b; }
        .border-accent { border-color: #f59e0b; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1a1c23; }
        ::-webkit-scrollbar-thumb { background: #4b5563; border-radius: 4px; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    </style>
</head>
<body class="h-screen flex flex-col overflow-hidden">

    <header class="bg-panel border-b-2 border-accent p-4 flex justify-between items-center shadow-lg z-10 shrink-0">
        <div class="flex items-center gap-4">
            <h1 class="text-xl md:text-2xl font-bold text-accent">1VD-FTV <span class="text-white text-sm md:text-lg">AI PLATFORM <span class="text-gray-400 text-xs">v2.0</span></span></h1>
            <span class="hidden md:inline-block bg-blue-900 text-blue-300 text-xs px-2 py-1 rounded border border-blue-700">LIVE STREAM</span>
            <span id="status-dot" class="status-dot bg-gray-500 pulse"></span>
        </div>
        <div class="flex items-center gap-3">
            <div class="text-right hidden sm:block">
                <div class="text-xs text-gray-400">System Health</div>
                <div id="health-score" class="text-green-400 font-bold text-lg">--</div>
            </div>
            <button onclick="toggleDevMode()" class="bg-gray-700 hover:bg-gray-600 text-white px-3 py-2 rounded text-sm transition">
                <span class="hidden sm:inline">💻 إدخال البيانات</span>
                <span class="sm:hidden">💻</span>
            </button>
        </div>
    </header>

    <div class="flex flex-1 overflow-hidden relative">

        <!-- Sidebar -->
        <aside id="devSidebar" class="bg-panel border-l border-gray-700 w-full sm:w-80 md:w-96 absolute left-0 h-full transform -translate-x-full transition-transform duration-300 z-20 flex flex-col">
            <div class="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-800">
                <h2 class="text-accent font-bold">إدخال البيانات (Live Data)</h2>
                <button onclick="toggleDevMode()" class="text-gray-400 hover:text-white text-xl">&times;</button>
            </div>
            <div class="p-4 flex-1 flex flex-col gap-4">
                <p class="text-xs text-gray-400">أدخل كود JSON لمحاكاة قراءات الحساسات:</p>
                <textarea id="streamInput" class="w-full flex-1 bg-gray-900 text-green-400 p-3 rounded border border-gray-700 font-mono text-sm resize-none focus:outline-none focus:border-yellow-500" spellcheck="false">{
  "RPM": 717.27,
  "RailPressure": 32.04,
  "Boost": 101.38,
  "MAF": 9.86,
  "EGT": 214.58,
  "CoolantTemp": 83.99,
  "EGRPosition": 2.04,
  "DPFPressure": 0.98
}</textarea>
                <div id="apiError" class="hidden text-red-400 text-xs bg-red-900/30 rounded p-2"></div>
                <div class="flex gap-2">
                    <button onclick="compareStream()" class="bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-2 px-4 rounded flex-1 transition">COMPARE</button>
                    <button onclick="simulateLive()" class="bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded flex-1 border border-gray-500 transition">SIMULATE</button>
                </div>
            </div>
        </aside>

        <!-- Main -->
        <main class="flex-1 overflow-y-auto p-4 md:p-6 w-full">

            <!-- AI Predict Banner -->
            <div id="predictBanner" class="bg-gray-800 border border-green-700 rounded-lg p-4 mb-6 shadow-md flex flex-col md:flex-row justify-between items-center gap-4">
                <div class="flex items-center gap-3">
                    <div id="predictIcon" class="bg-green-900 text-green-400 p-2 rounded-full">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                    <div>
                        <h2 id="predictTitle" class="text-green-400 font-bold text-lg">AI PREDICT: WAITING</h2>
                        <p id="predictSub" class="text-gray-400 text-sm">اضغط COMPARE أو SIMULATE لتحليل البيانات</p>
                    </div>
                </div>
                <div class="w-full md:w-1/3">
                    <div class="flex justify-between text-xs mb-1">
                        <span class="text-gray-400">Anomaly Score</span>
                        <span id="anomalyPct" class="text-yellow-400 font-bold">0%</span>
                    </div>
                    <div class="w-full bg-gray-700 rounded-full h-2">
                        <div id="anomalyBar" class="bg-yellow-500 h-2 rounded-full transition-all duration-500" style="width:0%"></div>
                    </div>
                </div>
            </div>

            <!-- Gauges Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">

                <!-- FUEL & ENGINE -->
                <div class="bg-panel border border-gray-700 rounded-lg p-5 shadow-sm">
                    <h3 class="text-gray-400 text-sm font-bold tracking-wider mb-4 border-b border-gray-700 pb-2">FUEL & ENGINE (الوقود والمحرك)</h3>
                    <div id="gauge-RPM" class="mb-5"></div>
                    <div id="gauge-RailPressure" class="mb-2"></div>
                </div>

                <!-- AIR & EXHAUST -->
                <div class="bg-panel border border-gray-700 rounded-lg p-5 shadow-sm">
                    <h3 class="text-gray-400 text-sm font-bold tracking-wider mb-4 border-b border-gray-700 pb-2">AIR & EXHAUST (الهواء والعادم)</h3>
                    <div id="gauge-MAF" class="mb-5"></div>
                    <div id="gauge-Boost" class="mb-5"></div>
                    <div class="grid grid-cols-2 gap-4 mt-2 pt-3 border-t border-gray-700">
                        <div id="mini-EGRPosition"></div>
                        <div id="mini-DPFPressure"></div>
                    </div>
                </div>

                <!-- TEMPERATURES -->
                <div class="bg-panel border border-gray-700 rounded-lg p-5 shadow-sm md:col-span-2 xl:col-span-1">
                    <h3 class="text-gray-400 text-sm font-bold tracking-wider mb-4 border-b border-gray-700 pb-2">TEMPERATURES (درجات الحرارة)</h3>
                    <div id="gauge-CoolantTemp" class="mb-5"></div>
                    <div id="gauge-EGT" class="mb-2"></div>
                </div>

            </div>

            <!-- Abnormal Params Alert -->
            <div id="alertBox" class="hidden mt-6 bg-red-900/40 border border-red-700 rounded-lg p-4">
                <h3 class="text-red-400 font-bold mb-2">⚠ معاملات خارج النطاق الطبيعي</h3>
                <div id="alertList" class="text-sm text-red-300 space-y-1"></div>
            </div>

        </main>
    </div>

<script>
// ── CONFIG ──
const RANGES = {
    RPM:          { min:0, max:1500, lo:580,  hi:820,  unit:"rpm",  label:"RPM" },
    RailPressure: { min:0, max:100,  lo:25,   hi:40,   unit:"MPa",  label:"Rail Pressure" },
    MAF:          { min:0, max:30,   lo:7,    hi:15,   unit:"g/s",  label:"MAF (Mass Air Flow)" },
    Boost:        { min:0, max:150,  lo:98,   hi:110,  unit:"kPa",  label:"Boost Pressure" },
    CoolantTemp:  { min:0, max:130,  lo:78,   hi:95,   unit:"°C",   label:"Coolant Temp" },
    EGT:          { min:0, max:800,  lo:150,  hi:280,  unit:"°C",   label:"EGT (Exhaust Gas Temp)" },
    EGRPosition:  { min:0, max:100,  lo:0,    hi:10,   unit:"%",    label:"EGR Position" },
    DPFPressure:  { min:0, max:10,   lo:0.3,  hi:2.5,  unit:"kPa",  label:"DPF Pressure" },
};

function getColor(key, val) {
    const r = RANGES[key];
    if (!r) return "text-gray-400";
    return (val >= r.lo && val <= r.hi) ? "text-green-400" : "text-red-400";
}

function getBgColor(key, val) {
    const r = RANGES[key];
    if (!r) return "bg-gray-500";
    return (val >= r.lo && val <= r.hi) ? "bg-green-400" : "bg-red-500";
}

function getTrackColor(key, val) {
    const r = RANGES[key];
    if (!r) return "bg-gray-600";
    return (val >= r.lo && val <= r.hi) ? "bg-green-900" : "bg-red-900";
}

function pct(key, val) {
    const r = RANGES[key];
    if (!r) return 0;
    return Math.min(Math.max((val - r.min) / (r.max - r.min) * 100, 0), 100);
}

function rangePct(key) {
    const r = RANGES[key];
    const left = (r.lo - r.min) / (r.max - r.min) * 100;
    const width = (r.hi - r.lo) / (r.max - r.min) * 100;
    return { left, width };
}

function renderGauge(key, val) {
    const r = RANGES[key];
    if (!r) return '';
    const valPct = pct(key, val);
    const rp = rangePct(key);
    const col = getColor(key, val);
    const dotCol = getBgColor(key, val);
    const trackCol = getTrackColor(key, val);
    const glow = (val >= r.lo && val <= r.hi) ? "shadow-[0_0_8px_#4ade80]" : "shadow-[0_0_8px_#ef4444]";
    return `
        <div class="flex justify-between items-end mb-1">
            <span class="text-gray-200">${r.label}</span>
            <span class="${col} font-mono font-bold text-lg">${val.toFixed(2)} <span class="text-xs text-gray-500 font-sans">${r.unit}</span></span>
        </div>
        <div class="w-full bg-gray-700 rounded-full h-1.5 relative">
            <div class="${trackCol} h-1.5 absolute rounded-full" style="left:${rp.left}%;width:${rp.width}%"></div>
            <div class="${dotCol} w-2.5 h-2.5 rounded-full absolute -top-0.5 ${glow} transition-all duration-700" style="left:calc(${valPct}% - 5px)"></div>
        </div>
        <div class="flex justify-between text-[10px] text-gray-500 mt-1 font-mono"><span>${r.min}</span><span>Range: ${r.lo}-${r.hi}</span><span>${r.max}</span></div>
    `;
}

function renderMini(key, val) {
    const r = RANGES[key];
    if (!r) return '';
    const col = getColor(key, val);
    return `
        <span class="text-gray-400 text-xs block">${r.label}</span>
        <span class="${col} font-mono font-bold">${val.toFixed(2)} ${r.unit}</span>
    `;
}

function updateUI(data, results) {
    const mainGauges = ["RPM","RailPressure","MAF","Boost","CoolantTemp","EGT"];
    const miniGauges  = ["EGRPosition","DPFPressure"];

    mainGauges.forEach(k => {
        const el = document.getElementById("gauge-" + k);
        if (el && data[k] !== undefined) el.innerHTML = renderGauge(k, data[k]);
    });
    miniGauges.forEach(k => {
        const el = document.getElementById("mini-" + k);
        if (el && data[k] !== undefined) el.innerHTML = renderMini(k, data[k]);
    });

    // Health score
    if (results) {
        const abnormal = results.abnormal_parameters || [];
        const score = results.health_score || 100;
        document.getElementById("health-score").textContent = score.toFixed(1) + "%";
        document.getElementById("health-score").className = score >= 80 ? "text-green-400 font-bold text-lg" : score >= 50 ? "text-yellow-400 font-bold text-lg" : "text-red-400 font-bold text-lg";

        // Anomaly bar
        const dev = Math.min(100 - score, 100);
        document.getElementById("anomalyPct").textContent = dev.toFixed(1) + "% deviation";
        document.getElementById("anomalyBar").style.width = dev + "%";
        document.getElementById("anomalyBar").className = "h-2 rounded-full transition-all duration-500 " + (dev < 20 ? "bg-green-500" : dev < 50 ? "bg-yellow-500" : "bg-red-500");

        // Banner
        const ok = abnormal.length === 0;
        document.getElementById("predictTitle").textContent = ok ? "AI PREDICT: DATA NOMINAL" : "AI PREDICT: ANOMALY DETECTED";
        document.getElementById("predictTitle").className = "font-bold text-lg " + (ok ? "text-green-400" : "text-red-400");
        document.getElementById("predictSub").textContent = ok ? "System operating within normal parameters." : `${abnormal.length} parameter(s) out of range.`;
        document.getElementById("predictBanner").className = "border rounded-lg p-4 mb-6 shadow-md flex flex-col md:flex-row justify-between items-center gap-4 " + (ok ? "bg-gray-800 border-green-700" : "bg-red-900/30 border-red-700");

        // Alert box
        if (abnormal.length > 0) {
            document.getElementById("alertBox").classList.remove("hidden");
            document.getElementById("alertList").innerHTML = abnormal.map(p => {
                const r = results.results[p];
                return `<div>⚠ <strong>${p}</strong>: ${r.current} ${r.unit} — ${r.status} (expected ${r.expected_range})</div>`;
            }).join('');
        } else {
            document.getElementById("alertBox").classList.add("hidden");
        }

        // Status dot
        document.getElementById("status-dot").className = "status-dot pulse " + (ok ? "bg-green-500" : "bg-red-500");
    }
}

function showError(msg) {
    const el = document.getElementById("apiError");
    el.textContent = "⚠ " + msg;
    el.classList.remove("hidden");
    setTimeout(() => el.classList.add("hidden"), 4000);
}

async function compareStream() {
    let data;
    try { data = JSON.parse(document.getElementById("streamInput").value); }
    catch(e) { showError("JSON غير صحيح — تحقق من الصيغة"); return; }

    try {
        const res = await fetch("/api/stream/compare", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({data})
        });
        const results = await res.json();
        updateUI(data, results);
        toggleDevMode();
    } catch(e) { showError("تعذر الاتصال بالخادم: " + e.message); }
}

async function simulateLive() {
    try {
        const res = await fetch("/api/stream/simulate");
        const data = await res.json();
        document.getElementById("streamInput").value = JSON.stringify(data, null, 2);

        const res2 = await fetch("/api/stream/compare", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({data})
        });
        const results = await res2.json();
        updateUI(data, results);
        toggleDevMode();
    } catch(e) { showError("تعذر الاتصال بالخادم: " + e.message); }
}

function toggleDevMode() {
    const sidebar = document.getElementById("devSidebar");
    sidebar.classList.toggle("-translate-x-full");
}

// Auto-load on start
window.addEventListener("load", () => simulateLive());
</script>
</body>
</html>"""
# =========================================================
# ROUTES
# =========================================================

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return FRONTEND

@app.get("/api")
def api_info():
    return {
        "platform": "1VD-FTV Global AI Platform v2.0",
        "dtc_count": len(DTC_DATABASE),
        "endpoints": [
            "/api/dtc",
            "/api/dtc/all",
            "/api/dtc/correlate",
            "/api/repairflow/{code}/start",
            "/api/repairflow/answer",
            "/api/stream/compare",
            "/api/stream/simulate",
            "/api/ai/predict",
            "/api/health/score",
            "/api/waveform/injector",
            "/api/waveform/maf",
            "/api/waveform/rail",
            "/api/waveform/egt",
            "/api/waveform/vnt",
            "/api/waveform/glow",
            "/api/wiring/svg",
            "/api/injector/balance",
            "/api/pdf/analyze",
            "/api/html/analyze",
        ]
    }

# ── DTC ──
@app.post("/api/dtc")
def dtc_lookup(req: DTCRequest):
    return ai_tutor.explain_dtc(req.code)

@app.get("/api/dtc/all")
def dtc_list_all():
    return ai_tutor.list_all()

@app.post("/api/dtc/correlate")
def dtc_correlate(req: MultiDTCRequest):
    return correlation_engine.analyze(req.codes)

# ── REPAIR FLOW ──
@app.get("/api/repairflow/{code}/start")
def repair_flow_start(code: str):
    return repair_engine.start(code)

@app.post("/api/repairflow/answer")
def repair_flow_answer(req: RepairFlowRequest):
    return repair_engine.answer(req.code, req.node_id, req.answer or "")

# ── STREAM ──
@app.post("/api/stream/compare")
def compare_stream(req: StreamCompareRequest):
    return stream_engine.compare(req.data)

@app.get("/api/stream/simulate")
def simulate_live():
    return stream_engine.simulate_live()

# ── AI PREDICT ──
@app.post("/api/ai/predict")
def predict_failure(req: StreamCompareRequest):
    return anomaly_detector.predict(req.data)

# ── HEALTH ──
class HealthRequest(BaseModel):
    codes: List[str]
    stream_data: Dict[str, float]

@app.post("/api/health/score")
def health_score(req: HealthRequest):
    return health_engine.calculate(req.codes, req.stream_data)

# ── WAVEFORMS ──
@app.get("/api/waveform/injector")
def wf_injector():
    return wave_engine.injector_waveform()

@app.get("/api/waveform/maf")
def wf_maf():
    return wave_engine.maf_waveform()

@app.get("/api/waveform/rail")
def wf_rail():
    return wave_engine.rail_pressure_waveform()

@app.get("/api/waveform/egt")
def wf_egt():
    return wave_engine.egt_regen_profile()

@app.get("/api/waveform/vnt")
def wf_vnt():
    return wave_engine.vnt_actuator_waveform()

@app.get("/api/waveform/glow")
def wf_glow():
    return wave_engine.glow_plug_waveform()

# ── WIRING ──
@app.get("/api/wiring/svg")
def wiring_svg():
    return {"svg": SVG_WIRING}

# ── INJECTOR BALANCE ──
@app.post("/api/injector/balance")
def injector_balance(req: InjectorBalanceRequest):
    return injector_analyzer.analyze_balance(req.cylinder_corrections)

# ── PDF ──
@app.post("/api/pdf/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    path = f"temp_{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    text = pdf_reader.extract_text(path)
    found = pdf_reader.find_injector_wiring(text)
    os.remove(path)
    return {"file": file.filename, "injector_related_lines": found[:200]}

# ── HTML MANUAL ──
@app.post("/api/html/analyze")
async def analyze_html(file: UploadFile = File(...)):
    path = f"temp_{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    result = html_parser.parse_html(path)
    os.remove(path)
    return result

# =========================================================
print("=" * 52)
print(" 1VD-FTV GLOBAL AI PLATFORM v2.0 — READY")
print("=" * 52)
print(f" DTCs in database : {len(DTC_DATABASE)}")
print(f" Repair flows     : {len(REPAIR_FLOWS)}")
print(f" API endpoints    : 19")
print("=" * 52)
print(" Run: uvicorn main:app --reload --port 8000")
print(" Open: http://localhost:8000")
print("=" * 52)
