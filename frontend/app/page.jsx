"use client";
import Link from "next/link";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Activity, CheckCircle2, FlaskConical, Timer, Trophy, Plus } from "lucide-react";
import { api } from "@/lib/api";
import { usePoll } from "@/lib/hooks";
import { Card, ErrorBox, Kpi, Loading, fmtN, fmtT, scoreLabel, scoreOf, tip } from "@/components/ui";
import ExpTable from "@/components/ExpTable";

export default function Overview() {
  const { data, error, loading } = usePoll(api.experiments, 5000);
  if (loading) return <Loading />;
  if (error && !data) return <ErrorBox msg={error} />;
  const rows = [...data].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  const done = rows.filter((e) => e.status === "completed");
  const running = rows.filter((e) => ["running", "queued"].includes(e.status)).length;
  const avg = done.length ? done.reduce((s, e) => s + (e.execution_time || 0), 0) / done.length : null;
  const best = done.filter((e) => scoreOf(e) != null).sort((a, b) => scoreOf(b) - scoreOf(a))[0];
  const chrono = [...done].reverse().map((e, i) => ({ n: `#${i + 1}`, name: e.dataset_name, runtime: e.execution_time, score: scoreOf(e) }));

  return (
    <>
      <div className="head">
        <div><h1>Overview</h1><p className="mu">{new Date().toLocaleDateString([], { weekday: "short", day: "2-digit", month: "short", year: "numeric" })} · {rows.length} experiments</p></div>
        <Link href="/new" className="btn p"><Plus size={15} /> New experiment</Link>
      </div>
      <div className="grid g4">
        <Kpi icon={FlaskConical} label="Experiments" value={rows.length} sub={`${running} in progress`} />
        <Kpi icon={CheckCircle2} label="Completed" value={done.length} sub={rows.length ? `${Math.round((done.length / rows.length) * 100)}% success rate` : "No runs yet"} />
        <Kpi icon={Timer} label="Avg. pipeline time" value={fmtT(avg)} sub="Across completed runs" />
        <Kpi icon={Trophy} label={best ? `Best ${scoreLabel(best)}` : "Best score"} value={best ? fmtN(scoreOf(best)) : "—"} sub={best ? `${best.pipeline_result.evaluation.model_name} · ${best.dataset_name}` : "Complete a run to see it"} />
      </div>

      {rows.length === 0 ? (
        <Card className="mt"><div className="empty"><Activity size={28} /><h3>Run your first experiment</h3><p className="mu">Upload a CSV and AtlasML will clean, explore, train and report on it automatically.</p><Link href="/new" className="btn p">Upload a dataset</Link></div></Card>
      ) : (
        <>
          <div className="grid g2 mt">
            <Card title="Pipeline runtime" sub="Seconds per completed experiment">
              <div className="chart"><ResponsiveContainer>
                <AreaChart data={chrono}><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#5CE1D4" stopOpacity={0.4} /><stop offset="100%" stopColor="#5CE1D4" stopOpacity={0} /></linearGradient></defs>
                  <CartesianGrid stroke="#2b3035" vertical={false} /><XAxis dataKey="n" stroke="#808C9A" fontSize={11} tickLine={false} /><YAxis stroke="#808C9A" fontSize={11} tickLine={false} axisLine={false} width={36} />
                  <Tooltip {...tip} /><Area type="monotone" dataKey="runtime" stroke="#5CE1D4" strokeWidth={2} fill="url(#g)" /></AreaChart>
              </ResponsiveContainer></div>
            </Card>
            <Card title="Score by experiment" sub="R² or accuracy, higher is better">
              <div className="chart"><ResponsiveContainer>
                <BarChart data={chrono}><CartesianGrid stroke="#2b3035" vertical={false} /><XAxis dataKey="n" stroke="#808C9A" fontSize={11} tickLine={false} /><YAxis stroke="#808C9A" fontSize={11} tickLine={false} axisLine={false} width={30} domain={[0, 1]} />
                  <Tooltip {...tip} /><Bar dataKey="score" fill="#3B9087" radius={[4, 4, 0, 0]} /></BarChart>
              </ResponsiveContainer></div>
            </Card>
          </div>
          <Card title="Recent experiments" className="mt" right={<Link href="/experiments" className="btn">View all</Link>}><ExpTable rows={rows.slice(0, 6)} /></Card>
        </>
      )}
    </>
  );
}
