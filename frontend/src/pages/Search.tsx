import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { useDocuments } from "../hooks/useDocuments";
import ChatPanel from "../components/ChatPanel";
import type { Source } from "../types";

export default function Search() {
  const { docs } = useDocuments();
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState<number[]>([]);
  const [results, setResults] = useState<Source[] | null>(null);
  const [error, setError] = useState("");
  const [mode, setMode] = useState<"search" | "chat">("search");
  const indexed = docs.filter((d) => d.status === "indexed");
  const toggle = (id: number) => setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));

  async function go() {
    if (q.trim().length < 2) return;
    setError("");
    try { setResults((await api.search(q, selected)).results); } catch (e) { setError((e as Error).message); }
  }
  return (
    <>
      <h1>Pencarian multi-dokumen</h1>
      <div className="panel">
        <h2>Cakupan</h2>
        <div className="chips">
          {indexed.map((d) => <button key={d.id} className={selected.includes(d.id) ? "chip on" : "chip"} onClick={() => toggle(d.id)}>{d.filename}</button>)}
          {!indexed.length && <p className="muted">Belum ada dokumen terindeks.</p>}
        </div>
        <p className="muted">{selected.length ? `${selected.length} dokumen dipilih` : "Semua dokumen dicari"}</p>
        <div className="tabs">
          <button className={mode === "search" ? "on" : ""} onClick={() => setMode("search")}>Cari kutipan</button>
          <button className={mode === "chat" ? "on" : ""} onClick={() => setMode("chat")}>Tanya semua dokumen</button>
        </div>
        {mode === "search" ? (
          <>
            <div className="composer">
              <input value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && go()} placeholder="Cari berdasarkan makna, bukan hanya kata kunci…" />
              <button className="primary" onClick={go}>Cari</button>
            </div>
            {error && <p className="err">{error}</p>}
            {results && (results.length === 0 ? <p className="muted">Tidak ada hasil.</p> : (
              <ul className="results">
                {results.map((r, i) => (
                  <li key={i}><Link to={`/documents/${r.document_id}`}>{r.filename}</Link><small> hal. {r.page} · skor {r.score}</small><p>{r.snippet}…</p></li>
                ))}
              </ul>
            ))}
          </>
        ) : <ChatPanel documentIds={selected.length ? selected : undefined} placeholder="Tanyakan lintas dokumen…" />}
      </div>
    </>
  );
}
