import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.tools.tools import _doctors, _specialties, _appointments
from src.agent import MedicalAgent

app = FastAPI(title="Zdrave Plus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading agent...")
agent = MedicalAgent()
print("Agent ready.")


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str
    history: list[dict]


@app.get("/api/doctors")
def get_doctors(specialty_id: Optional[str] = None, nhif_only: bool = False):
    """Returns all doctors, optionally filtered by specialty and/or NHIF."""
    results = list(_doctors.values())

    if specialty_id:
        results = [d for d in results if d.get("specialty_id") == specialty_id]
    if nhif_only:
        results = [d for d in results if d.get("accepts_nhif")]

    return [
        {
            "id": d["id"],
            "name": d["name"],
            "specialty": d["specialty"],
            "specialty_id": d["specialty_id"],
            "years_experience": d["years_experience"],
            "price": d["price_consultation"],
            "accepts_nhif": d.get("accepts_nhif", False),
            "rating": d["rating"],
            "reviews_count": d.get("reviews_count", 0),
            "bio": d.get("bio", ""),
            "expertise": d.get("expertise", []),
            "languages": d.get("languages", []),
            "academic_title": d.get("academic_title"),
            "room": d.get("room", ""),
        }
        for d in results
    ]


@app.get("/api/specialties")
def get_specialties():
    """Returns all medical specialties with symptom lists."""
    return [
        {
            "id": s["id"],
            "name": s["specialty"],
            "description": s["description"],
            "symptoms": s["symptoms"],
            "avg_minutes": s["avg_consultation_minutes"],
        }
        for s in _specialties.values()
    ]


@app.get("/api/availability/{doctor_id}")
def get_availability(doctor_id: str, date: Optional[str] = None):
    """Returns available slots for a doctor. Optional date filter: YYYY-MM-DD."""
    from datetime import datetime

    if doctor_id not in _appointments:
        raise HTTPException(status_code=404, detail="Doctor not found")

    appt = _appointments[doctor_id]
    today = datetime.today().strftime("%Y-%m-%d")
    slots = [s for s in appt["slots"] if s["available"] and s["date"] >= today]

    if date:
        slots = [s for s in slots if s["date"] == date]

    return {
        "doctor_id": doctor_id,
        "doctor_name": appt["doctor_name"],
        "specialty": appt["specialty"],
        "room": appt["room"],
        "slots": [{"date": s["date"], "time": s["time"]} for s in slots[:20]],
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Main chat endpoint - runs the full RAG + agent pipeline."""
    try:
        reply, updated_history = agent.chat(req.message, req.history)
        return ChatResponse(reply=reply, history=updated_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health():
    return {"status": "ok"}