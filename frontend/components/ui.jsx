import { AlertTriangle, Loader2 } from "lucide-react";

export const fmtT = (s) => s == null ? "—" : s < 60 ? `${Number(s).toFixed(s < 1 ? 2 : 1)}s` : `${Math.floor(s / 60)}m ${Math.round(s % 60)}s`;
export const fmtN = (n, d = 3) => typeof n === "number" ? n.toFixed(d) : "—";
export const fmtD = (d) => d ? new Date(/Z|[+-]\d\d:?\d\d$/.test(d) ? d : d + "Z").toLocaleString([], { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "—";
export const shortId = (id) => (id || "").slice(0, 8);
export const clean = (f) => f.replace(/^(numerical|categorical)__/, "").replace(/_/g, " ");

export const scoreOf = (e) => { const ev = e?.pipeline_result?.evaluation; return ev ? (ev.r2 ?? ev.accuracy ?? ev.f1 ?? null) : null; };
export const scoreLabel = (e) => { const ev = e?.pipeline_result?.evaluation; return ev ? (ev.r2 != null ? "R²" : ev.accuracy != null ? "Accuracy" : "F1") : "Score"; };

const MAP = { completed: "ok", failed: "err", running: "info", queued: "mute", uploaded: "mute", pending: "mute" };
export function Chip({ status, children }) {
  return <span className={`chip ${MAP[status] || "mute"}`}>{children || status}</span>;
}

export function Kpi({ icon: Icon, label, value, sub, tag }) {
  return (
    <div className="card kpi">
      <div className="kpi-top"><span className="ico"><Icon size={16} /></span><span className="mu">{label}</span></div>
      <div className="kpi-v">{value}{tag && <span className="chip ok sm">{tag}</span>}</div>
      <div className="mu sm-t">{sub}</div>
    </div>
  );
}

export function Card({ title, sub, right, children, className = "" }) {
  return (
    <section className={`card ${className}`}>
      {(title || right) && (
        <div className="card-h">
          <div><h3>{title}</h3>{sub && <p className="mu sm-t">{sub}</p>}</div>{right}
        </div>
      )}
      {children}
    </section>
  );
}

export const ErrorBox = ({ msg }) => (
  <div className="alert err"><AlertTriangle size={16} /><span>{msg}</span></div>
);
export const Loading = () => <div className="loading"><Loader2 size={18} className="spin" /> Loading…</div>;
export const tip = { contentStyle: { background: "#202326", border: "1px solid #40464D", borderRadius: 10, fontSize: 12 }, cursor: { fill: "rgba(92,225,212,.06)" } };
