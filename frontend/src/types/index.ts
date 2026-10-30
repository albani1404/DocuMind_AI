export interface User { id: number; email: string; name: string }
export type DocStatus = "uploaded" | "processing" | "indexed" | "failed";
export interface Doc {
  id: number; filename: string; file_type: string; size_bytes: number; page_count: number;
  chunk_count: number; status: DocStatus; error?: string | null; used_ocr: boolean;
  summary?: string | null; extracted?: Record<string, unknown> | null; created_at: string;
}
export interface Page { page_number: number; text: string; ocr_confidence?: number | null }
export interface Source { document_id: number; filename: string; page: number; score: number; snippet: string }
export interface ChatMessage { role: "user" | "assistant"; content: string; sources?: Source[] | null }
export interface Analytics {
  documents: number; pages: number; chunks: number; bytes: number; ocr_documents: number;
  conversations: number; by_status: Record<string, number>;
}
