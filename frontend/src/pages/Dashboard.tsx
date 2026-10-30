import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { useDocuments } from "../hooks/useDocuments";
import UploadZone from "../components/UploadZone";
import StatusBadge from "../components/StatusBadge";
import type { Analytics } from "../types";
import { formatBytes, formatDate } from "../utils/format";

export default function Dashboard() {
  const { docs, refresh } = useDocuments();
  const [stats, setStats] = useState<Analytics | null>(null);
  useEffect(() => { api.analytics().then(setStats).catch(() => {}); }, [docs]);

  const cards: [string, string | number][] = stats ? [
    ["Dokumen", stats.documents], ["Halaman diproses", stats.pages], ["Chunk di vector store", stats.chunks],
    ["Dokumen hasil OCR", stats.ocr_documents], ["Percakapan", stats.conversations], ["Ukuran total", formatBytes(stats.bytes)],
  ] : [];
  const total = stats?.documents || 1;

  return (
    <>
      <h1>Dashboard</h1>
      <div className="stats">{cards.map(([k, v]) => <div key={k} className="panel stat"><span>{k}</span><strong>{v}</strong></div>)}</div>
      {stats && (
        <div className="panel">
          <h2>Status pemrosesan</h2>
          <div className="bar">
            {Object.entries(stats.by_status).map(([s, n]) => <i key={s} className={s} style={{ width: `${(n / total) * 100}%` }} title={`${s}: ${n}`} />)}
          </div>
          <p className="muted">{Object.entries(stats.by_status).map(([s, n]) => `${n} ${s}`).join(" · ") || "Belum ada dokumen"}</p>
        </div>
      )}
      <UploadZone onDone={refresh} />
      <div className="panel">
        <h2>Dokumen terbaru</h2>
        {docs.length === 0 ? <p className="muted">Unggah dokumen pertama Anda untuk mulai bertanya.</p> : (
          <ul className="rows">
            {docs.slice(0, 5).map((d) => (
              <li key={d.id}><Link to={`/documents/${d.id}`}>{d.filename}</Link><StatusBadge status={d.status} />
                <small>{d.page_count} hal. · {formatBytes(d.size_bytes)} · {formatDate(d.created_at)}</small></li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}
