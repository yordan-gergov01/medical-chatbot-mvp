import json
import random
import string
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR  = BASE_DIR / "data" / "raw"

# Load data once at import time

def _load(filename: str) -> dict | list:
    with open(RAW_DIR / filename, encoding="utf-8") as f:
        return json.load(f)

_doctors = {d["id"]: d for d in _load("doctors.json")}
_specialties = {s["id"]: s for s in _load("specialties.json")}
_appointments = _load("appointments.json")   # dict keyed by doctor_id


def search_doctors(specialty_id: str | None = None, nhif_only: bool = False) -> dict:
    """
    Returns doctors filtered by specialty and/or NHIF acceptance.
    Used by the agent to answer "which doctors treat X" questions.
    """
    results = list(_doctors.values())

    if specialty_id:
        results = [d for d in results if d.get("specialty_id") == specialty_id]

    if nhif_only:
        results = [d for d in results if d.get("accepts_nhif")]

    if not results:
        return {"found": False, "message": "No doctors found for the given criteria."}

    doctors_out = []
    for d in results:
        doctors_out.append({
            "id": d["id"],
            "name": d["name"],
            "specialty": d["specialty"],
            "years_experience": d["years_experience"],
            "price_consultation": d["price_consultation"],
            "accepts_nhif": d.get("accepts_nhif", False),
            "rating": d["rating"],
            "languages": d.get("languages", []),
        })

    return {"found": True, "count": len(doctors_out), "doctors": doctors_out}


def check_availability(doctor_id: str, date: str | None = None) -> dict:
    """
    Returns available appointment slots for a doctor.
    date format: YYYY-MM-DD (optional — returns all upcoming if omitted).
    """
    if doctor_id not in _appointments:
        return {"available": False, "message": f"No schedule found for doctor {doctor_id}."}

    appt_data = _appointments[doctor_id]
    slots = appt_data["slots"]

    today = datetime.today().strftime("%Y-%m-%d")
    slots = [s for s in slots if s["available"] and s["date"] >= today]

    if date:
        slots = [s for s in slots if s["date"] == date]

    if not slots:
        msg = f"No available slots for {doctor_id}"
        msg += f" on {date}." if date else " in the upcoming period."
        return {"available": False, "message": msg}

    # Return max 10 slots to keep context manageable
    slots_out = [{"date": s["date"], "time": s["time"]} for s in slots[:10]]

    return {
        "available": True,
        "doctor_id": doctor_id,
        "doctor_name": appt_data["doctor_name"],
        "specialty": appt_data["specialty"],
        "room": appt_data["room"],
        "slots": slots_out,
    }


def book_appointment(
    doctor_id: str,
    date: str,
    time: str,
    patient_name: str,
    patient_phone: str,
) -> dict:
    """
    Books an appointment slot. Marks it as unavailable in the in-memory data.
    Returns a confirmation with a booking reference number.
    """
    if doctor_id not in _appointments:
        return {"success": False, "message": f"Doctor {doctor_id} not found."}

    appt_data = _appointments[doctor_id]
    slot = next(
        (s for s in appt_data["slots"] if s["date"] == date and s["time"] == time),
        None,
    )

    if not slot:
        return {"success": False, "message": f"Slot {date} {time} not found for {doctor_id}."}

    if not slot["available"]:
        return {"success": False, "message": f"Slot {date} at {time} is already booked."}

    # Mark as booked (in-memory only for MVP)
    slot["available"] = False
    slot["patient_name"] = patient_name
    slot["patient_phone"] = patient_phone

    # Generate a short reference code
    ref = "MC-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    doctor = _doctors.get(doctor_id, {})

    return {
        "success": True,
        "reference": ref,
        "doctor_name": doctor.get("name", appt_data["doctor_name"]),
        "specialty": doctor.get("specialty", appt_data["specialty"]),
        "room": appt_data["room"],
        "date": date,
        "time": time,
        "patient_name": patient_name,
        "message": (
            f"Часът е успешно записан! Референтен номер: {ref}. "
            f"Моля, носете лична карта при посещението."
        ),
    }


# OpenAI function schemas
# These are passed directly to the OpenAI API as tools.

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_doctors",
            "description": (
                "Search for doctors by specialty and/or NHIF acceptance. "
                "Use this when the patient asks which doctors are available for a specialty."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "specialty_id": {
                        "type": "string",
                        "description": (
                            "Specialty ID to filter by. "
                            "Valid values: cardiology, neurology, orthopedics, dermatology, "
                            "gastroenterology, endocrinology, pulmonology, ent, gynecology, "
                            "ophthalmology, urology, psychiatry"
                        ),
                    },
                    "nhif_only": {
                        "type": "boolean",
                        "description": "If true, return only doctors who accept NHIF (НЗОК).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": (
                "Check available appointment slots for a specific doctor. "
                "Use this after the patient has chosen a doctor. "
                "Optionally filter by date."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {
                        "type": "string",
                        "description": "Doctor ID from search_doctors results (e.g. dr_001).",
                    },
                    "date": {
                        "type": "string",
                        "description": "Optional date filter in YYYY-MM-DD format.",
                    },
                },
                "required": ["doctor_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": (
                "Book a specific appointment slot for a patient. "
                "Only call this after the patient has confirmed the doctor, date, time, "
                "and provided their name and phone number."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id":     {"type": "string", "description": "Doctor ID."},
                    "date":          {"type": "string", "description": "Date in YYYY-MM-DD format."},
                    "time":          {"type": "string", "description": "Time in HH:MM format."},
                    "patient_name":  {"type": "string", "description": "Full name of the patient."},
                    "patient_phone": {"type": "string", "description": "Phone number of the patient."},
                },
                "required": ["doctor_id", "date", "time", "patient_name", "patient_phone"],
            },
        },
    },
]

# Dispatcher — maps function name → callable
TOOL_DISPATCH = {
    "search_doctors": search_doctors,
    "check_availability": check_availability,
    "book_appointment": book_appointment,
}
