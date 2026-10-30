import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const nav = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/documents", label: "Dokumen" },
  { to: "/search", label: "Pencarian" },
  { to: "/compare", label: "Bandingkan" },
];

export default function DashboardLayout() {
  const { user, signOut } = useAuth();
  return (
    <div className="shell">
      <aside className="side">
        <div className="brand"><span className="mark" />DocuMind AI</div>
        <nav>
          {nav.map((n) => (
            <NavLink key={n.to} to={n.to} end={n.end} className={({ isActive }) => (isActive ? "nav on" : "nav")}>{n.label}</NavLink>
          ))}
        </nav>
        <div className="who">
          <div><strong>{user?.name}</strong><small>{user?.email}</small></div>
          <button className="ghost" onClick={signOut}>Keluar</button>
        </div>
      </aside>
      <main className="main"><Outlet /></main>
    </div>
  );
}
