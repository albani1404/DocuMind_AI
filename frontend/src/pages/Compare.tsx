import { useState } from "react";
import { api } from "../services/api";
import { useDocuments } from "../hooks/useDocuments";

export default function Compare() {
  const { docs } = useDocuments();
  const indexed = docs.filter((d) => d.status === "indexed");
  const [a, setA] = useState(0), [b, setB] = useState(0), [focus, setFocus] = useState("");
  const [res, setRes] = useState<{ similarity: number; analysis: string } | null>(null);
  const [busy, setBusy] = useState(false), [error, setError] = useState("");

  async function run() {
    setBusy(true); setError(""); setRes(null);
    try { setRes(await api.compare(a, b, focus)); } catch (e) { setError((e as Error).message); }
    setBusy(false);
  }
  const select = (v: number, set: (n: number) => void, label: string) => (
    <label>{label}
      <select value={v} onChange={(e) => set(Number(e.target.value))}>
        <option value={0}>Pilih dokumen…</option>
        {indexed.map((d) => <option key={d.id} value={d.id}>{d.filename}</option>)}
      </select>
    </label>
  );
  return (
    <>
      <h1>Bandingkan dokumen</h1>
      <div className="panel form-grid">
        {select(a, setA, "Dokumen A")}{select(b, setB, "Dokumen B")}
        <label className="wide">Fokus perbandingan (opsional)
          <input value={focus} onChange={(e) => setFocus(e.target.value)} placeholder="mis. klausul pembayaran, risiko keamanan" />
        </label>
        <button className="primary" disabled={!a || !b || busy} onClick={run}>{busy ? "Membandingkan…" : "Bandingkan"}</button>
      </div>
      {error && <p className="err">{error}</p>}
      {res && <div className="panel"><p className="muted">Kemiripan teks: {(res.similarity * 100).toFixed(1)}%</p><p className="prewrap">{res.analysis}</p></div>}
    </>
  );
}
