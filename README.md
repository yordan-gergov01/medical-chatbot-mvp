# 🏥 Medical Center AI Chatbot — RAG + Agent MVP

An AI-powered appointment booking assistant for Bulgarian medical centers, built with OpenAI, FAISS, and Gradio.

> **Live Demo:** [medical-chatbot-assistant.onrender.com](https://medical-chatbot-mvp.onrender.com/) (only for personal DEMOs)


## What It Does

Patients interact with a chat assistant that:

1. **Understands symptoms** in Bulgarian and routes to the correct specialist
2. **Searches available doctors** by specialty or NHIF (НЗОК) acceptance
3. **Checks real-time availability** across a 30-day appointment calendar
4. **Books appointments** and issues a confirmation reference number

Emergency symptoms (stroke, heart attack) are immediately redirected to 112.


## Architecture

```
User message
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
Gradio UI
```


## Tech Stack

| Layer | Technology |
|---|---|
| LLM + Agent | GPT-4o-mini (OpenAI) |
| Embeddings | text-embedding-3-small (OpenAI) |
| Vector DB | FAISS (local, CPU) |
| Agent framework | OpenAI function calling (native) |
| UI | Gradio |
| Evaluation | LLM-as-judge + Hit@K retrieval metrics |
| Data | Synthetic Bulgarian medical dataset |


## Dataset

All data is **synthetic** - no real patient data is used.

- 18 doctors across 12 specialties with realistic Bulgarian profiles
- 12 specialties with symptom-to-specialist mappings
- 30-day appointment calendar with ~65% availability
- Knowledge base covering center info, FAQ, and pricing


## License

MIT
