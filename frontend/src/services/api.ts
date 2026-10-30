import type { Analytics, ChatMessage, Doc, Page, Source, User } from "../types";

const TOKEN_KEY = "documind_token";
export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t: string) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

async function req<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const t = tokenStore.get();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const res = await fetch(`/api${path}`, { ...init, headers });
  if (res.status === 401) { tokenStore.clear(); if (!path.startsWith("/auth")) location.href = "/login"; }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : `Permintaan gagal (${res.status})`);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}
const post = <T,>(p: string, b?: unknown) => req<T>(p, { method: "POST", body: b ? JSON.stringify(b) : undefined });

export const api = {
  login: (email: string, password: string) => post<{ access_token: string; user: User }>("/auth/login", { email, password }),
  register: (email: string, name: string, password: string) =>
    post<{ access_token: string; user: User }>("/auth/register", { email, name, password }),
  me: () => req<User>("/auth/me"),
  documents: () => req<Doc[]>("/documents"),
  document: (id: number) => req<Doc>(`/documents/${id}`),
  pages: (id: number) => req<Page[]>(`/documents/${id}/pages`),
  upload: (file: File) => { const f = new FormData(); f.append("file", file); return req<Doc>("/documents", { method: "POST", body: f }); },
  remove: (id: number) => req<void>(`/documents/${id}`, { method: "DELETE" }),
  reprocess: (id: number) => post<Doc>(`/documents/${id}/reprocess`),
  fileUrl: (id: number) => `/api/documents/${id}/file`,
  summarize: (id: number) => post<Doc>(`/ai/documents/${id}/summary`),
  extract: (id: number) => post<Doc>(`/ai/documents/${id}/extract`),
  compare: (a: number, b: number, focus?: string) =>
    post<{ similarity: number; analysis: string }>("/ai/compare", { document_a: a, document_b: b, focus: focus || null }),
  analytics: () => req<Analytics>("/ai/analytics"),
  search: (query: string, document_ids?: number[]) =>
    post<{ results: Source[] }>("/search", { query, document_ids: document_ids?.length ? document_ids : null }),
  chat: (question: string, conversation_id: number | null, document_ids?: number[]) =>
    post<{ conversation_id: number; answer: string; sources: Source[] }>("/chat", { question, conversation_id, document_ids }),
  messages: (cid: number) => req<ChatMessage[]>(`/chat/conversations/${cid}`),
  conversations: () => req<{ id: number; title: string; document_ids: number[] | null }[]>("/chat/conversations"),
};
