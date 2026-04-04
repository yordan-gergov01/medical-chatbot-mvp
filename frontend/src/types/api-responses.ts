export interface Doctor {
    id: string;
    name: string;
    specialty: string;
    specialty_id: string;
    years_experience: number;
    price: number;
    accepts_nhif: boolean;
    rating: number;
    reviews_count: number;
    bio: string;
    expertise: string[];
    languages: string[];
    academic_title: string | null;
    room: string;
  }
  
  export interface Specialty {
    id: string;
    name: string;
    description: string;
    symptoms: string[];
    avg_minutes: number;
  }
  
  export interface TimeSlot {
    date: string;
    time: string;
  }
  
  export interface AvailabilityResponse {
    doctor_id: string;
    doctor_name: string;
    specialty: string;
    room: string;
    slots: TimeSlot[];
  }
  
  export interface Message {
    role: "user" | "assistant";
    content: string;
  }
  
  export interface ChatResponse {
    reply: string;
    history: Message[];
  }