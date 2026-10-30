import { Link } from "react-router-dom";
import { api } from "../services/api";
import { useDocuments } from "../hooks/useDocuments";
import UploadZone from "../components/UploadZone";
import StatusBadge from "../components/StatusBadge";
import { formatBytes, formatDate } from "../utils/format";

export default function Documents() {
  const { docs, loading, refresh } = useDocuments();
  async function remove(id: number, name: string) {
    if (!confirm(`Hapus "${name}" beserta datanya?`)) return;
    await api.remove(id); refresh();
  }
  return (
    <>
      <h1>Dokumen</h1>
      <UploadZone onDone={refresh} />
      <div className="panel table-wrap">
        {loading ? <p className="muted">Memuat…</p> : docs.length === 0 ? <p className="muted">Belum ada dokumen.</p> : (
          <table>
            <thead><tr><th>Nama</th><th>Tipe</th><th>Halaman</th><th>Ukuran</th><th>Status</th><th>Diunggah</th><th /></tr></thead>
            <tbody>
              {docs.map((d) => (
                <tr key={d.id}>
                  <td><Link to={`/documents/${d.id}`}>{d.filename}</Link>{d.error && <small className="err">{d.error}</small>}</td>
                  <td>{d.file_type.toUpperCase()}{d.used_ocr && " · OCR"}</td>
                  <td>{d.page_count || "–"}</td><td>{formatBytes(d.size_bytes)}</td>
                  <td><StatusBadge status={d.status} /></td><td>{formatDate(d.created_at)}</td>
                  <td className="actions">
                    {d.status === "failed" && <button className="ghost" onClick={() => api.reprocess(d.id).then(refresh)}>Coba lagi</button>}
                    <button className="ghost danger" onClick={() => remove(d.id, d.filename)}>Hapus</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
