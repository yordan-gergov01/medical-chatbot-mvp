# 🏥 Medical Center AI Chatbot — RAG + Agent MVP

An AI-powered appointment booking assistant for Bulgarian medical centers, built with OpenAI, FAISS, FastAPI and React.
 
> **⚠️ Demo Notice:** [medical-chatbot-mvp-fe.onrender.com](https://medical-chatbot-mvp-fe.onrender.com/) — This is a **client-facing demo**, not a production deployment. The backend runs on Render's free tier and may be slow to respond or unavailable. Intended for showcasing the product concept to potential clients.
 
 
## What It Does
 
Patients interact with a chat assistant embedded in a medical center website that:
 
1. **Understands symptoms** in Bulgarian and routes to the correct specialist
2. **Searches available doctors** by specialty or NHIF (НЗОК) acceptance
3. **Checks real-time availability** across a 30-day appointment calendar
4. **Books appointments** and issues a confirmation reference number
 
Emergency symptoms (stroke, heart attack, chest pain) are immediately redirected to **112**.
 
 
## Screenshots
 
<img width="1828" height="940" alt="medical-chatbot-mvp-1" src="https://github.com/user-attachments/assets/5577ce89-5443-4ac4-95f9-33e22c5a7335" />
<img width="1788" height="933" alt="medical-chatbot-mvp-2" src="https://github.com/user-attachments/assets/edf0f65e-c121-4f62-bf6f-7cabb5a439f2" />
<img width="1828" height="936" alt="medical-chatbot-mvp-3" src="https://github.com/user-attachments/assets/1880148c-b120-41ae-a15f-5d620c690ed6" />
<img width="1769" height="932" alt="medical-chatbot-mvp-4" src="https://github.com/user-attachments/assets/721e3ea9-70ef-4810-8853-6db5e84fe44e" />

 
## Architecture
 
```
User message (React frontend)
    │
    ▼
FastAPI Backend (/api/chat)
    │
    ▼
RAG Pipeline
    ├── Query Rewrite      gpt-4o-mini rewrites query for better recall
    ├── FAISS Search       cosine similarity over embedded documents
    └── LLM Rerank         gpt-4o-mini scores and reorders candidates
    │
    ▼
Agent Loop (gpt-4o-mini + function calling)
    ├── search_doctors      filter by specialty / NHIF
    ├── check_availability  real-time slot lookup
    └── book_appointment    confirms and issues booking reference
    │
    ▼
React Frontend (chat widget embedded in landing page)
```

 
## Tech Stack
 
| Layer | Technology |
|---|---|
| LLM + Agent | GPT-4o-mini (OpenAI) |
| Embeddings | text-embedding-3-small (OpenAI) |
| Vector DB | FAISS (local, CPU) |
| Agent framework | OpenAI function calling (native) |
| Backend | FastAPI + Uvicorn |
| Frontend | React 19 + TypeScript + Tailwind CSS v4 |
| UI Components | shadcn/ui (Radix UI) |
| Gradio UI | For internal testing only |
| Evaluation | LLM-as-judge + Hit@K retrieval metrics |
| Data | Synthetic Bulgarian medical dataset |
 
 
## Project Structure
 
```
medical-chatbot-mvp/
├── src/
│   ├── agent.py              # RAG + agent loop
│   ├── rag/
│   │   ├── indexer.py        # FAISS index builder
│   │   └── retriever.py      # Search, rewrite, rerank pipeline
│   └── tools/
│       └── tools.py          # search_doctors, check_availability, book_appointment
├── app/
│   └── gradio_app.py         # Gradio UI (internal testing)
├── data/
│   ├── raw/                  # doctors.json, specialties.json, appointments.json
│   └── processed/
│       ├── faiss_index/      # index.faiss, metadata.pkl, texts.pkl
│       └── knowledge_base/   # center_info.txt, faq.txt, services.txt
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/       # Navbar, Footer
│   │   │   └── ui/           # shadcn/ui components
│   │   ├── features/
│   │   │   ├── home/         # Hero, HomePage
│   │   │   ├── about/        # About section
│   │   │   ├── specialists/  # Specialists section
│   │   │   ├── specialties/  # Specialties section
│   │   │   ├── faq/          # FAQ section
│   │   │   ├── contact/      # Contact section
│   │   │   └── chat/         # ChatWidget (AI assistant)
│   │   ├── services/
│   │   │   └── api.ts        # API client
│   │   └── hooks/
│   ├── package.json
│   └── vite.config.ts
├── main.py                   # Setup script (generates appointments + builds FAISS index)
├── src/app.py                # FastAPI app
├── requirements.txt
└── render.yaml
```
 
 
## Dataset
 
All data is **synthetic** - no real patient data is used.
 
- 18 doctors across 12 specialties with realistic Bulgarian profiles
- 12 specialties with symptom-to-specialist mappings
- 30-day appointment calendar with ~65% availability
- Knowledge base covering center info, FAQ, and pricing

  
## License
 
MIT
