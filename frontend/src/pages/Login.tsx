import { useState, type FormEvent } from "react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const { signIn } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [f, setF] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault(); setBusy(true); setError("");
    try {
      const r = mode === "login" ? await api.login(f.email, f.password) : await api.register(f.email, f.name, f.password);
      signIn(r.access_token, r.user);
    } catch (err) { setError((err as Error).message); }
    setBusy(false);
  }

  return (
    <div className="auth">
      <form onSubmit={submit} className="panel auth-card">
        <div className="brand"><span className="mark" />DocuMind AI</div>
        <h1>{mode === "login" ? "Masuk ke ruang kerja" : "Buat akun"}</h1>
        {mode === "register" && <label>Nama<input required minLength={2} value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} /></label>}
        <label>Email<input required type="email" value={f.email} onChange={(e) => setF({ ...f, email: e.target.value })} /></label>
        <label>Kata sandi<input required type="password" minLength={8} value={f.password} onChange={(e) => setF({ ...f, password: e.target.value })} /></label>
        {error && <p className="err">{error}</p>}
        <button className="primary" disabled={busy}>{mode === "login" ? "Masuk" : "Daftar"}</button>
        <button type="button" className="ghost" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "Belum punya akun? Daftar" : "Sudah punya akun? Masuk"}
        </button>
      </form>
    </div>
  );
}
