import { AvailabilityResponse, ChatResponse, Doctor, Message, Specialty } from "@/types/api-responses";

  const BASE = import.meta.env.VITE_BASE_API_URL;
  
  async function request<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail ?? "Request failed");
    }
    return res.json() as Promise<T>;
  }
  
  export function fetchDoctors(params?: {
    specialty_id?: string;
    nhif_only?: boolean;
  }): Promise<Doctor[]> {
    const qs = new URLSearchParams();
    if (params?.specialty_id) qs.set("specialty_id", params.specialty_id);
    if (params?.nhif_only) qs.set("nhif_only", "true");
    const query = qs.toString() ? `?${qs}` : "";
    return request<Doctor[]>(`/doctors${query}`);
  }
  
  export function fetchSpecialties(): Promise<Specialty[]> {
    return request<Specialty[]>("/specialties");
  }
  
  export function fetchAvailability(
    doctorId: string,
    date?: string
  ): Promise<AvailabilityResponse> {
    const qs = date ? `?date=${date}` : "";
    return request<AvailabilityResponse>(`/availability/${doctorId}${qs}`);
  }
  
  export function sendChatMessage(
    message: string,
    history: Message[]
  ): Promise<ChatResponse> {
    return request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({ message, history }),
    });
  }