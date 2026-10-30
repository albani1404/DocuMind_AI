import { useRef, useState } from "react";
import { api } from "../services/api";

const ACCEPT = ".pdf,.docx,.jpg,.jpeg,.png";

export default function UploadZone({ onDone }: { onDone: () => void }) {
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function send(files: FileList | null) {
    if (!files?.length) return;
    setBusy(true); setError("");
    for (const f of Array.from(files)) {
      try { await api.upload(f); } catch (e) { setError(`${f.name}: ${(e as Error).message}`); }
    }
    setBusy(false); onDone();
  }

  return (
    <div className={`drop ${over ? "over" : ""}`} role="button" tabIndex={0}
      onClick={() => input.current?.click()} onKeyDown={(e) => e.key === "Enter" && input.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setOver(true); }} onDragLeave={() => setOver(false)}
      onDrop={(e) => { e.preventDefault(); setOver(false); send(e.dataTransfer.files); }}>
      <input ref={input} type="file" accept={ACCEPT} multiple hidden onChange={(e) => send(e.target.files)} />
      <strong>{busy ? "Mengunggah…" : "Letakkan dokumen di sini atau klik untuk memilih"}</strong>
      <small>PDF, DOCX, JPG, PNG — maksimal 25 MB per file</small>
      {error && <p className="err">{error}</p>}
    </div>
  );
}
