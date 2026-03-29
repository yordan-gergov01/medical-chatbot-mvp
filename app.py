"""
app.py - Hugging Face Spaces entry point.

On startup:
  1. Generates appointments.json (future dates)
  2. Builds rag_documents.json
  3. Builds FAISS index via OpenAI embeddings
  4. Launches the Gradio app
"""
import json
import sys
import pickle
import random
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"
KB_DIR = PROC_DIR / "knowledge_base"
IDX_DIR = PROC_DIR / "faiss_index"

PROC_DIR.mkdir(parents=True, exist_ok=True)
IDX_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))

print("Step 1: Generating appointments...")

with open(RAW_DIR / "doctors.json", encoding="utf-8") as f:
    doctors = json.load(f)

WORK_DAYS = {
    "dr_001":[0,2,4], "dr_002":[1,3], "dr_003":[0,1,3,4], "dr_004":[1,2,4],
    "dr_005":[0,2,3], "dr_006":[1,3,4], "dr_007":[0,1,2,3,4], "dr_008":[0,2,4],
    "dr_009":[0,1,2,3,4], "dr_010":[1,3,4], "dr_011":[0,1,2,3,4], "dr_012":[0,2,4],
    "dr_013":[0,2,3], "dr_014":[0,1,2,3,4], "dr_015":[0,1,3,4],
    "dr_016":[0,2,3,4], "dr_017":[1,2,4], "dr_018":[1,2,3,4],
}
AFTERNOON_ONLY = ["dr_018", "dr_003"]
MORNING = ["08:30","09:00","09:30","10:00","10:30","11:00","11:30","12:00"]
AFTERNOON = ["13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00"]

random.seed(42)
start = datetime.today() + timedelta(days=1)
appts = {}

for doc in doctors:
    did = doc["id"]
    slots = []
    for offset in range(30):
        day = start + timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        if day.weekday() not in WORK_DAYS.get(did, [0,1,2,3,4]):
            continue
        times = AFTERNOON if did in AFTERNOON_ONLY else MORNING + AFTERNOON
        for t in times:
            slots.append({
                "date": day.strftime("%Y-%m-%d"),
                "time": t,
                "available": random.random() > 0.35,
            })
    appts[did] = {
        "doctor_id": did,
        "doctor_name": doc["name"],
        "specialty": doc["specialty"],
        "room": doc["room"],
        "slots": slots,
    }

with open(RAW_DIR / "appointments.json", "w", encoding="utf-8") as f:
    json.dump(appts, f, ensure_ascii=False)

total = sum(len(v["slots"]) for v in appts.values())
available = sum(sum(1 for s in v["slots"] if s["available"]) for v in appts.values())
print(f"{total} slots generated ({available} available)")

print("Step 2: Building RAG documents...")

with open(RAW_DIR / "specialties.json", encoding="utf-8") as f:
    specialties = json.load(f)

def doctor_to_doc(doc):
    nhif = "Приема по НЗОК с направление" if doc.get("accepts_nhif") else "Само платени прегледи"
    acad = f"{doc['academic_title']} " if doc.get("academic_title") else ""
    text = (
        f"Лекар: {acad}{doc['name']}\n"
        f"Специалност: {doc['specialty']}\n"
        f"Опит: {doc['years_experience']} години\n"
        f"{doc.get('bio', '')}\n\n"
        f"Специализира в: {', '.join(doc.get('expertise', []))}\n"
        f"Езици: {', '.join(doc.get('languages', []))}\n"
        f"Цена: {doc['price_consultation']} лева\n"
        f"{nhif}\n"
        f"Оценка: {doc['rating']}/5.0\n"
        f"Кабинет: {doc.get('room', '')}"
    )
    return {
        "id": f"doctor_{doc['id']}",
        "text": text,
        "metadata": {
            "type": "doctor",
            "doctor_id": doc["id"],
            "specialty_id": doc["specialty_id"],
            "specialty": doc["specialty"],
            "accepts_nhif": doc.get("accepts_nhif", False),
            "price": doc["price_consultation"],
            "rating": doc["rating"],
        },
    }

def specialty_to_doc(spec):
    text = (
        f"Специалност: {spec['specialty']}\n"
        f"{spec['description']}\n\n"
        f"Симптоми: {', '.join(spec['symptoms'])}\n\n"
        f"Спешни симптоми: {', '.join(spec.get('urgent_symptoms', []))}\n"
        f"Процедури: {', '.join(spec.get('common_procedures', []))}"
    )
    return {
        "id": f"specialty_{spec['id']}",
        "text": text,
        "metadata": {
            "type": "specialty",
            "specialty_id": spec["id"],
            "specialty": spec["specialty"],
        },
    }

kb_docs = []
for kb_file in sorted(KB_DIR.glob("*.txt")):
    for i, para in enumerate(kb_file.read_text(encoding="utf-8").split("\n\n")):
        if len(para.strip()) >= 50:
            kb_docs.append({
                "id": f"kb_{kb_file.stem}_{i:03d}",
                "text": para.strip(),
                "metadata": {"type": "knowledge_base", "source": kb_file.stem},
            })

all_docs = (
    [doctor_to_doc(d) for d in doctors] +
    [specialty_to_doc(s) for s in specialties] +
    kb_docs
)

with open(PROC_DIR / "rag_documents.json", "w", encoding="utf-8") as f:
    json.dump(all_docs, f, ensure_ascii=False, indent=2)

print(f"{len(all_docs)} documents ready")

print("Step 3: Building FAISS index...")

import faiss
from openai import OpenAI

client = OpenAI()
texts = [d["text"] for d in all_docs]
meta = [{"id": d["id"], **d["metadata"]} for d in all_docs]
embs = []
BATCH = 50

for i in range(0, len(texts), BATCH):
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts[i : i + BATCH],
    )
    embs.extend([r.embedding for r in resp.data])
    print(f"Embedded {min(i + BATCH, len(texts))}/{len(texts)}")

embs_np = np.array(embs, dtype=np.float32)
faiss.normalize_L2(embs_np)

index = faiss.IndexFlatIP(1536)
index.add(embs_np)

faiss.write_index(index, str(IDX_DIR / "index.faiss"))

with open(IDX_DIR / "metadata.pkl", "wb") as f:
    pickle.dump(meta, f)

texts_map = {d["id"]: d["text"] for d in all_docs}
with open(IDX_DIR / "texts.pkl", "wb") as f:
    pickle.dump(texts_map, f)

print(f"  FAISS index: {index.ntotal} vectors")
print("Setup complete — launching app...\n")

from app.gradio_app import build_ui

demo = build_ui()
demo.launch(server_name="0.0.0.0", server_port=7860)