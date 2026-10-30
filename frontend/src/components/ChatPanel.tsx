import { useEffect, useRef, useState } from 'react';
import { api } from '../services/api';
import type { ChatMessage, Source } from '../types';

interface Props {
  documentIds?: number[];
  onOpenPage?: (docId: number, page: number) => void;
  placeholder?: string;
}

function Answer({ text, sources, onOpenPage }: { text: string; sources?: Source[] | null; onOpenPage?: Props['onOpenPage'] }) {
  // ubah [S1] menjadi tombol sitasi yang menuju halaman sumber
  const parts = text.split(/(\[S\d+\])/g);
  return (
    <p className="answer">
      {parts.map((p, i) => {
        const m = p.match(/^\[S(\d+)\]$/);
        const src = m ? sources?.[Number(m[1]) - 1] : undefined;
        return src ? (
          <button key={i} className="cite" title={src.snippet} onClick={() => onOpenPage?.(src.document_id, src.page)}>
            hal. {src.page}
          </button>
        ) : (
          <span key={i}>{p}</span>
        );
      })}
    </p>
  );
}

export default function ChatPanel({ documentIds, onOpenPage, placeholder }: Props) {
  const [msgs, setMsgs] = useState<ChatMessage[]>([]);
  const [q, setQ] = useState('');
  const [cid, setCid] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const log = useRef<HTMLDivElement>(null);

  // gulir hanya area chat, bukan seluruh halaman
  useEffect(() => {
    const el = log.current;
    if (el && msgs.length) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
  }, [msgs, busy]);

  async function ask() {
    const question = q.trim();
    if (!question || busy) return;
    setQ('');
    setError('');
    setBusy(true);
    setMsgs((m) => [...m, { role: 'user', content: question }]);
    try {
      const r = await api.chat(question, cid, documentIds);
      setCid(r.conversation_id);
      setMsgs((m) => [...m, { role: 'assistant', content: r.answer, sources: r.sources }]);
    } catch (e) {
      setError((e as Error).message);
    }
    setBusy(false);
  }

  return (
    <section className="chat">
      <div className="log" ref={log}>
        {!msgs.length && <p className="muted">Ajukan pertanyaan tentang isi dokumen. Jawaban disertai halaman sumbernya.</p>}
        {msgs.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            {m.role === 'user' ? (
              <p>{m.content}</p>
            ) : (
              <>
                <Answer text={m.content} sources={m.sources} onOpenPage={onOpenPage} />
                {!!m.sources?.length && (
                  <div className="sources">
                    {m.sources.map((s, j) => (
                      <button key={j} className="chip" onClick={() => onOpenPage?.(s.document_id, s.page)}>
                        [S{j + 1}] {s.filename} · hal. {s.page}
                      </button>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        ))}
        {busy && (
          <div className="msg assistant">
            <p className="muted">Mencari dan menyusun jawaban…</p>
          </div>
        )}
        {error && <p className="err">{error}</p>}
      </div>
      <div className="composer">
        <input value={q} placeholder={placeholder ?? 'Tanyakan sesuatu tentang dokumen…'} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && ask()} />
        <button className="primary" onClick={ask} disabled={busy || !q.trim()}>
          Kirim
        </button>
      </div>
    </section>
  );
}
