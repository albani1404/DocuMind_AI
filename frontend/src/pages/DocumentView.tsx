import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../services/api";
import ChatPanel from "../components/ChatPanel";
import StatusBadge from "../components/StatusBadge";
import type { Doc, Page } from "../types";

type Tab = "chat" | "summary" | "extract";

export default function DocumentView() {
  const id = Number(useParams().id);
  const [doc, setDoc] = useState<Doc | null>(null);
  const [pages, setPages] = useState<Page[]>([]);
  const [tab, setTab] = useState<Tab>("chat");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [active, setActive] = useState<number | null>(null);
  const refs = useRef<Record<number, HTMLElement | null>>({});

  useEffect(() => {
    let stop = false;
    const load = async () => {
      const d = await api.document(id); if (stop) return;
      setDoc(d);
      if (d.status === "indexed") setPages(await api.pages(id));
      else if (d.status !== "failed") setTimeout(load, 3000);
    };
    load().catch((e) => setError(e.message));
    return () => { stop = true; };
  }, [id]);

  function openPage(_: number, p: number) {
    setActive(p); refs.current[p]?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  async function run(kind: "summarize" | "extract") {
    setBusy(true); setError("");
    try { setDoc(await api[kind](id)); } catch (e) { setError((e as Error).message); }
    setBusy(false);
  }
  if (!doc) return <p className="muted">{error || "Memuat…"}</p>;

  return (
    <>
      <header className="doc-head">
        <h1>{doc.filename}</h1><StatusBadge status={doc.status} />
        <a className="ghost" href={api.fileUrl(id)}>Unduh asli</a>
      </header>
      {doc.status !== "indexed" ? (
        <div className="panel"><p>{doc.status === "failed" ? `Pemrosesan gagal: ${doc.error}` : "Dokumen sedang dibaca dan diindeks. Halaman ini akan diperbarui otomatis."}</p></div>
      ) : (
        <div className="split">
          <section className="panel viewer">
            <h2>Isi dokumen ({pages.length} halaman{doc.used_ocr ? ", OCR" : ""})</h2>
            {pages.map((p) => (
              <article key={p.page_number} ref={(el) => (refs.current[p.page_number] = el)} className={active === p.page_number ? "page hit" : "page"}>
                <h3>Halaman {p.page_number}{p.ocr_confidence != null && <small> · akurasi OCR {(p.ocr_confidence * 100).toFixed(0)}%</small>}</h3>
                <p>{p.text || <em>(kosong)</em>}</p>
              </article>
            ))}
          </section>
          <section className="panel side-panel">
            <div className="tabs" role="tablist">
              {([["chat", "Tanya dokumen"], ["summary", "Ringkasan"], ["extract", "Ekstraksi"]] as [Tab, string][]).map(([t, l]) => (
                <button key={t} role="tab" aria-selected={tab === t} className={tab === t ? "on" : ""} onClick={() => setTab(t)}>{l}</button>
              ))}
            </div>
            {error && <p className="err">{error}</p>}
            {tab === "chat" && <ChatPanel documentIds={[id]} onOpenPage={openPage} />}
            {tab === "summary" && (
              <div className="pane">
                {doc.summary ? <p className="prewrap">{doc.summary}</p> : <p className="muted">Belum ada ringkasan.</p>}
                <button className="primary" disabled={busy} onClick={() => run("summarize")}>{busy ? "Meringkas…" : doc.summary ? "Buat ulang ringkasan" : "Buat ringkasan"}</button>
              </div>
            )}
            {tab === "extract" && (
              <div className="pane">
                {doc.extracted ? <dl className="kv">{Object.entries(doc.extracted).map(([k, v]) => (
                  <div key={k}><dt>{k.replace(/_/g, " ")}</dt><dd>{typeof v === "string" ? v : <pre>{JSON.stringify(v, null, 2)}</pre>}</dd></div>
                ))}</dl> : <p className="muted">Belum ada hasil ekstraksi.</p>}
                <button className="primary" disabled={busy} onClick={() => run("extract")}>{busy ? "Mengekstrak…" : doc.extracted ? "Ekstrak ulang" : "Ekstrak informasi"}</button>
              </div>
            )}
          </section>
        </div>
      )}
    </>
  );
}
