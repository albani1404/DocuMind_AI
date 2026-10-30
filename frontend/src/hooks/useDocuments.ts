import { useCallback, useEffect, useState } from "react";
import { api } from "../services/api";
import type { Doc } from "../types";

/** Memuat daftar dokumen dan polling selama ada yang masih diproses. */
export function useDocuments() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [loading, setLoading] = useState(true);
  const refresh = useCallback(async () => {
    try { setDocs(await api.documents()); } finally { setLoading(false); }
  }, []);
  useEffect(() => { refresh(); }, [refresh]);
  const busy = docs.some((d) => d.status === "uploaded" || d.status === "processing");
  useEffect(() => {
    if (!busy) return;
    const t = setInterval(refresh, 3000);
    return () => clearInterval(t);
  }, [busy, refresh]);
  return { docs, loading, refresh };
}
