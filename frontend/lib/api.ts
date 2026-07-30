// Server components (SSR) run inside the docker network and should hit the
// backend service directly; the browser (client components) needs the
// externally reachable URL instead.
const SERVER_API_URL = process.env.INTERNAL_API_URL ?? "http://localhost:8000";
export const PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function apiBaseUrl(): string {
  return typeof window === "undefined" ? SERVER_API_URL : PUBLIC_API_URL;
}

export type JobLevel = "intern" | "junior" | "mid" | "senior" | "staff" | "unknown";
export type DegreeRequirement = "none" | "bachelor" | "master" | "phd";

export interface Company {
  id: number;
  name: string;
  slug: string;
  careers_url: string | null;
}

export interface Job {
  id: number;
  title: string;
  location: string | null;
  department: string | null;
  level: JobLevel;
  min_years_experience: number | null;
  degree_requirement: DegreeRequirement;
  url: string;
  posted_at: string | null;
  first_seen_at: string;
  company: Company;
}

export interface JobListResponse {
  total: number;
  page: number;
  page_size: number;
  items: Job[];
}

export interface JobFilters {
  title?: string;
  level?: JobLevel;
  location?: string;
  min_years?: number;
  degree?: DegreeRequirement;
  posted_after?: string;
  page?: number;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API error ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export function getJobs(filters: JobFilters): Promise<JobListResponse> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") params.set(key, String(value));
  }
  return apiFetch<JobListResponse>(`/api/jobs?${params.toString()}`);
}

export function getJob(id: number): Promise<Job> {
  return apiFetch<Job>(`/api/jobs/${id}`);
}

export function register(email: string, password: string) {
  return apiFetch(`/api/auth/register`, { method: "POST", body: JSON.stringify({ email, password }) });
}

export function login(email: string, password: string) {
  return apiFetch<{ access_token: string; token_type: string }>(`/api/auth/login`, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}
