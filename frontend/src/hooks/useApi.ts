import { useState, useEffect } from "react";

import { fetchDoctors, fetchSpecialties } from "@/services/api";
import { Doctor, Specialty } from "@/types/api-responses";


function useFetch<T>(fetcher: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetcher()
      .then((d) => { if (!cancelled) { setData(d); setLoading(false); } })
      .catch((e) => { if (!cancelled) { setError(e.message); setLoading(false); } });
    return () => { cancelled = true; };
  }, []);

  return { data, loading, error };
}

export function useDoctors(params?: { specialty_id?: string; nhif_only?: boolean }) {
  return useFetch<Doctor[]>(() => fetchDoctors(params));
}

export function useSpecialties() {
  return useFetch<Specialty[]>(fetchSpecialties);
}