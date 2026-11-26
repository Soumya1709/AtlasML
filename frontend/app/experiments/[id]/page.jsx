"use client";
import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CheckCircle2, Circle, Download, Gauge, Loader2, RotateCcw, Timer, Trophy, XCircle, Cpu, ChevronLeft } from "lucide-react";
import { api, downloadUrl } from "@/lib/api";
import { usePoll } from "@/lib/hooks";
import { Card, Chip, ErrorBox, Kpi, Loading, clean, fmtD, fmtN, fmtT, shortId, tip } from "@/components/ui";

const ORDER = ["DatasetAgent", "CleaningAgent", "EDAAgent", "FeatureAgent", "ModelSelectionAgent", "TrainingAgent", "HyperparameterTuningAgent", "EvaluationAgent", "SHAPAgent", "DeploymentAgent", "ReportAgent"];
const TABS = [["overview", "Overview"], ["models", "Models"], ["explain", "Explainability"], ["data", "Data"], ["artifacts", "Artifacts"]];
const axis = { stroke: "#808C9A", fontSize: 11, tickLine: false };

export default function Detail() {
  const { id } = useParams();
  const [tab, setTab] = useState("overview");
  const [retrying, setRetrying] = useState(null);
  const [note, setNote] = useState(null);
  const { data, error, loading, reload } = usePoll(async () => {
    const [s, a, x] = await Promise.all([api.status(id), api.agents(id), api.experiment(id)]);
    return { s, a, x };
  }, (d) => (d && ["completed", "failed"].includes(d.s.status) ? 8000 : 2000), id);

  if (loading) return <Loading />;
  if (error && !data) return <ErrorBox msg={error} />;
  const { s, a, x } = data;
  const r = s.pipeline_result || {};
  const ev = r.evaluation;
  const byName = {};
  for (const e of a) if (!byName[e.agent_name] || e.attempt_number >= byName[e.agent_name].attempt_number) byName[e.agent_name] = e;
  const doneCount = ORDER.filter((n) => byName[n]?.status === "completed").length;
  const active = ["running", "queued"].includes(s.status);
  const metrics = ev ? Object.entries(ev).filter(([k, v]) => typeof v === "number" && k !== "test_rows").slice(0, 3) : [];

  const retry = async (exec) => {
    setRetrying(exec.execution_id); setNote(null);
    try { await api.retry(id, exec.execution_id); setNote(`Retry started for ${exec.agent_name}.`); setTimeout(reload, 1200); }
    catch (e) { setNote(e.message); } finally { setRetrying(null); }
  };

  return (
    <>
      <Link href="/experiments" className="back"><ChevronLeft size={14} /> Experiments</Link>
      <div className="head">
        <div><h1>{x.dataset_name} <Chip status={s.status} /></h1><p className="mu">Experiment {shortId(id)} · started {fmtD(x.created_at)}{r.problem_type ? ` · ${r.problem_type}` : ""}</p></div>
        <div className="head-r"><div className="mu sm-t">{active ? `Running ${s.current_agent?.replace("Agent", "") || ""}` : `${doneCount}/${ORDER.length} agents done`}</div><div className="prog w"><i style={{ width: `${(doneCount / ORDER.length) * 100}%` }} /></div></div>
      </div>
      {s.error_message && <div style={{ marginBottom: 16 }}><ErrorBox msg={`${s.current_agent}: ${s.error_message}`} /></div>}
      {note && <div className="alert info" style={{ marginBottom: 16 }}>{note}</div>}

      <div className="grid g4">
        <Kpi icon={Trophy} label="Best model" value={<span className="kpi-sm">{ev?.model_name || "—"}</span>} sub={r.hyperparameter_tuning ? `${r.hyperparameter_tuning.cv_folds}-fold CV tuned` : "Waiting for results"} />
        {metrics.length ? metrics.map(([k, v], i) => <Kpi key={k} icon={i === 0 ? Gauge : Cpu} label={k.toUpperCase()} value={fmtN(v)} sub={i === 0 ? `${ev.test_rows} test rows` : "Lower is better"} />) : [0, 1, 2].map((i) => <Kpi key={i} icon={Gauge} label="Metric" value="—" sub="Available after evaluation" />)}
      </div>

      <Card title="Agent pipeline" sub="Each agent retries up to 3 times automatically" className="mt">
        <div className="steps">
          {ORDER.map((n, i) => {
            const e = byName[n];
            const st = !e ? "pending" : e.status === "completed" ? "completed" : e.status === "failed" ? "failed" : "running";
            const Ico = st === "completed" ? CheckCircle2 : st === "failed" ? XCircle : st === "running" ? Loader2 : Circle;
            return (
              <div key={n} className={`step ${st}`}>
                <Ico size={18} className={st === "running" ? "spin" : ""} />
                <div className="grow"><div className="strong">{i + 1}. {n.replace("Agent", "")}</div>
                  <div className="mu sm-t">{e ? `${fmtT(e.execution_time)}${e.attempt_number > 1 ? ` · attempt ${e.attempt_number}` : ""}` : "Waiting"}</div>
                  {st === "failed" && <div className="err-t">{e.error_message}</div>}</div>
                {st === "failed" && <button className="btn sm" disabled={retrying === e.execution_id} onClick={() => retry(e)}><RotateCcw size={13} /> Retry</button>}
              </div>
            );
          })}
        </div>
      </Card>

      <div className="tabs big">{TABS.map(([k, l]) => <button key={k} className={tab === k ? "on" : ""} onClick={() => setTab(k)}>{l}</button>)}</div>
      {tab === "overview" && <Overview r={r} a={a} s={s} />}
      {tab === "models" && <Models r={r} />}
      {tab === "explain" && <Explain r={r} />}
      {tab === "data" && <Data r={r} />}
      {tab === "artifacts" && <Artifacts id={id} />}
    </>
  );
}

const Wait = () => <Card><p className="mu empty">Results appear here once the pipeline reaches this stage.</p></Card>;

function Overview({ r, a }) {
  const times = ORDER.map((n) => ({ name: n.replace("Agent", ""), t: a.filter((e) => e.agent_name === n).slice(-1)[0]?.execution_time || 0 }));
  const d = r.eda || {};
  return (
    <div className="grid g2">
      <Card title="Time per agent" sub="Seconds, latest attempt"><div className="chart tall"><ResponsiveContainer>
        <BarChart data={times} layout="vertical" margin={{ left: 40 }}><CartesianGrid stroke="#2b3035" horizontal={false} /><XAxis type="number" {...axis} /><YAxis type="category" dataKey="name" {...axis} width={150} /><Tooltip {...tip} /><Bar dataKey="t" fill="#5CE1D4" radius={[0, 4, 4, 0]} /></BarChart>
      </ResponsiveContainer></div></Card>
      <Card title="Run details">
        <dl className="dl">
          <dt>Target column</dt><dd>{r.target_column || "—"}</dd><dt>Rows × columns</dt><dd>{r.rows ? `${r.rows} × ${r.columns}` : "—"}</dd>
          <dt>Training / test rows</dt><dd>{r.training ? `${r.training.training_rows} / ${r.training.testing_rows}` : "—"}</dd>
          <dt>Selected features</dt><dd>{r.deployment?.selected_features?.length ?? "—"}</dd><dt>Candidates</dt><dd>{r.model_selection?.candidate_models?.join(", ") || "—"}</dd>
          <dt>Total runtime</dt><dd>{fmtT(r.pipeline_execution_time)}</dd>
          <dt>Observations</dt><dd>{(d.observations || r.dataset_problems || ["—"]).join(" ")}</dd>
        </dl>
      </Card>
    </div>
  );
}

function Models({ r }) {
  const t = r.hyperparameter_tuning;
  if (!t) return <Wait />;
  const rows = Object.entries(t.models).map(([name, m]) => ({ name, mse: m.cv_score != null ? -m.cv_score : null, params: m.best_params }));
  return (
    <div className="grid g2">
      <Card title="Cross-validated error" sub={`${t.scoring} · ${t.cv_folds} folds · lower is better`}><div className="chart tall"><ResponsiveContainer>
        <BarChart data={rows}><CartesianGrid stroke="#2b3035" vertical={false} /><XAxis dataKey="name" {...axis} tickFormatter={(v) => v.replace("Regressor", "").replace("Classifier", "")} /><YAxis {...axis} axisLine={false} width={34} /><Tooltip {...tip} />
          <Bar dataKey="mse" radius={[4, 4, 0, 0]}>{rows.map((m) => <Cell key={m.name} fill={m.name === t.selected_model ? "#5CE1D4" : "#3B9087"} />)}</Bar></BarChart>
      </ResponsiveContainer></div></Card>
      <Card title="Tuning results" sub={`Selected: ${t.selected_model}`}>
        <div className="tw"><table><thead><tr><th>Model</th><th>CV error</th><th>Best parameters</th></tr></thead><tbody>
          {rows.map((m) => <tr key={m.name}><td className="strong">{m.name}{m.name === t.selected_model && <span className="chip ok sm"> selected</span>}</td><td>{fmtN(m.mse, 2)}</td>
            <td className="mu sm-t">{Object.keys(m.params).length ? Object.entries(m.params).map(([k, v]) => `${k.replace("model__", "")}=${v}`).join(", ") : "defaults"}</td></tr>)}
        </tbody></table></div>
      </Card>
    </div>
  );
}

function Explain({ r }) {
  const x = r.explainability;
  if (!x) return <Wait />;
  const rows = x.feature_importance.slice(0, 12).map((f) => ({ name: clean(f.feature), v: f.importance }));
  return (
    <Card title="Feature importance" sub={`Top 12 · ${x.method.replace(/_/g, " ")}`}>
      <div className="chart xtall"><ResponsiveContainer>
        <BarChart data={rows} layout="vertical" margin={{ left: 60 }}><CartesianGrid stroke="#2b3035" horizontal={false} /><XAxis type="number" {...axis} /><YAxis type="category" dataKey="name" {...axis} width={230} /><Tooltip {...tip} formatter={(v) => fmtN(v, 2)} /><Bar dataKey="v" fill="#5CE1D4" radius={[0, 4, 4, 0]} /></BarChart>
      </ResponsiveContainer></div>
      {x.note && <p className="mu sm-t" style={{ marginTop: 12 }}>{x.note}</p>}
    </Card>
  );
}

function Data({ r }) {
  const e = r.eda;
  if (!e) return <Wait />;
  const cols = Object.keys(e.correlations || {});
  return (
    <div className="stack">
      <div className="grid g2">
        <Card title="Numerical summary"><div className="tw"><table><thead><tr><th>Column</th><th>Mean</th><th>Median</th><th>Std</th><th>Min</th><th>Max</th><th>Outliers</th></tr></thead><tbody>
          {Object.entries(e.numerical_summary).map(([c, v]) => <tr key={c}><td className="strong">{c}</td><td>{fmtN(v.mean, 1)}</td><td>{fmtN(v.median, 1)}</td><td>{fmtN(v.std, 1)}</td><td>{v.min}</td><td>{v.max}</td><td>{v.outlier_count_iqr}</td></tr>)}</tbody></table></div></Card>
        <Card title="Data quality"><dl className="dl">
          <dt>Cleaning</dt><dd>{r.cleaning ? `${r.cleaning.original_rows} → ${r.cleaning.final_rows} rows` : "—"}</dd><dt>Duplicates removed</dt><dd>{r.cleaning?.duplicates_removed ?? "—"}</dd>
          <dt>Missing values</dt><dd>{r.dataset_quality ? `${r.dataset_quality.total_missing_values} (${fmtN(r.dataset_quality.missing_percentage, 1)}%)` : "—"}</dd><dt>Memory</dt><dd>{r.dataset_quality?.memory_usage_mb} MB</dd></dl></Card>
      </div>
      {cols.length > 0 && <Card title="Correlations" sub="Pearson, numerical columns"><div className="heat" style={{ gridTemplateColumns: `140px repeat(${cols.length},1fr)` }}>
        <span />{cols.map((c) => <span key={c} className="mu sm-t c">{c}</span>)}
        {cols.map((row) => [<span key={row} className="mu sm-t">{row}</span>, ...cols.map((c) => { const v = e.correlations[row][c]; return <span key={row + c} className="cell" style={{ background: `rgba(92,225,212,${Math.abs(v) * 0.85})`, color: Math.abs(v) > 0.5 ? "#091615" : "#F6F7F9" }}>{fmtN(v, 2)}</span>; })])}
      </div></Card>}
      <div className="grid g3">{Object.entries(e.categorical_summary).map(([c, v]) => { const tot = Object.values(v.top_values).reduce((s, n) => s + n, 0); return (
        <Card key={c} title={c} sub={`${v.unique_values} values`}>{Object.entries(v.top_values).map(([k, n]) => <div key={k} className="hb"><span>{k}</span><div className="prog"><i style={{ width: `${(n / tot) * 100}%` }} /></div><span className="mu">{n}</span></div>)}</Card>); })}</div>
    </div>
  );
}

function Artifacts({ id }) {
  const { data, error, loading } = usePoll(() => api.artifacts(id), 0, id);
  if (loading) return <Loading />;
  if (error) return <ErrorBox msg={error} />;
  if (!data.length) return <Wait />;
  return (
    <Card title="Artifacts" sub="Files produced by this run"><div className="tw"><table><thead><tr><th>Name</th><th>Type</th><th>Created</th><th /></tr></thead><tbody>
      {data.map((f) => <tr key={f.artifact_id}><td className="strong">{f.artifact_name}</td><td><span className="chip mute">{f.artifact_type}</span></td><td>{fmtD(f.created_at)}</td>
        <td style={{ textAlign: "right" }}><a className="btn sm" href={downloadUrl(id, f.artifact_id)}><Download size={13} /> Download</a></td></tr>)}</tbody></table></div></Card>
  );
}
