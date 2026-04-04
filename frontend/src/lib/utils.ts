import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Derive initials from Bulgarian doctor name (е.g. "д-р Мария Иванова" → "МИ")
export function getInitials(name: string): string {
  return name
    .replace(/^(д-р|доц\.|проф\.)\s*/i, "")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}
