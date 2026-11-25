"use client";
import { useRef, useState } from "react";
import Link from "next/link";
import { CloudUpload, FileSpreadsheet, X, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";
import { Card, ErrorBox, fmtN } from "@/components/ui";

export default function NewExperiment() {
  const input = useRef(null);
  const [file, setFile] = useState(null);
  const [drag, setDrag] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState(null);
  const [res, setRes] = useState(null);

  const pick = (f) => { setErr(null); setRes(null); if (f && !f.name.toLowerCase().endsWith(".csv")) { setErr("Only .csv files are supported."); return; } setFile(f || null); };
  const submit = async () => {
    setBusy(true); setErr(null);
    try { setRes(await api.upload(file)); } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };
  const s = res?.summary;

  return (
    <>
      <div className="head"><div><h1>New experiment</h1><p className="mu">Upload a CSV. AtlasML detects the target, cleans, trains and reports.</p></div></div>
      <div className="grid g2r">
        <div className="stack">
          <Card title="Upload dataset" sub="CSV files only. The pipeline starts as soon as the upload finishes.">
            <div className={`drop ${drag ? "on" : ""}`} onDragOver={(e) => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)}
              onDrop={(e) => { e.preventDefault(); setDrag(false); pick(e.dataTransfer.files[0]); }}>
              <span className="drop-ico"><CloudUpload size={22} /></span>
              <b>Drag and drop your CSV here</b><span className="mu sm-t">or</span>
              <button className="btn" onClick={() => input.current.click()}>Browse files</button>
              <input ref={input} type="file" accept=".csv" hidden onChange={(e) => pick(e.target.files[0])} />
            </div>
            {file && (
              <div className="file">
                <FileSpreadsheet size={18} /><div className="grow"><div className="strong">{file.name}</div><div className="mu sm-t">{(file.size / 1048576).toFixed(2)} MB</div></div>
                {busy ? <div className="prog w"><i className="indet" /></div> : !res && <button className="x" onClick={() => setFile(null)}><X size={16} /></button>}
              </div>
            )}
            {err && <div style={{ marginTop: 12 }}><ErrorBox msg={err} /></div>}
            {!res && <button className="btn p wide" disabled={!file || busy} onClick={submit}>{busy ? "Uploading and profiling…" : "Start experiment"}</button>}
          </Card>

          {s && (
            <Card title="Dataset profile" sub="What AtlasML found before the pipeline started"
              right={res.experiment_id ? <Link href={`/experiments/${res.experiment_id}`} className="btn p">Open experiment <ArrowRight size={15} /></Link> : null}>
              {!res.experiment_id && <ErrorBox msg="The upload response has no experiment_id. Add experiment_id to UploadResponse in the backend, then upload again. Meanwhile find the run under Experiments." />}
              <div className="facts">
                <div><span className="mu">Rows</span><b>{s.rows.toLocaleString()}</b></div><div><span className="mu">Columns</span><b>{s.columns}</b></div>
                <div><span className="mu">Target</span><b>{s.target_column || "—"}</b></div><div><span className="mu">Problem</span><b>{s.problem_type}</b></div>
              </div>
              <ul className="notes">{s.dataset_problems.map((p) => <li key={p}>{p}</li>)}</ul>
              <div className="tw"><table><thead><tr>{s.column_names.map((c) => <th key={c}>{c}</th>)}</tr></thead>
                <tbody>{s.preview.map((r, i) => <tr key={i}>{s.column_names.map((c) => <td key={c}>{String(r[c])}</td>)}</tr>)}</tbody></table></div>
            </Card>
          )}
        </div>

        <Card title="Run summary" right={<span className="chip mute">{res ? "Queued" : "Draft"}</span>}>
          <dl className="dl">
            <dt>File</dt><dd>{file?.name || "Not selected"}</dd>
            <dt>Rows × columns</dt><dd>{s ? `${s.rows} × ${s.columns}` : "After upload"}</dd>
            <dt>Missing values</dt><dd>{s ? `${fmtN(s.dataset_quality.missing_percentage, 1)}%` : "After upload"}</dd>
            <dt>Duplicate rows</dt><dd>{s ? s.dataset_quality.duplicate_rows : "After upload"}</dd>
          </dl>
          <p className="mu sm-t" style={{ marginTop: 16 }}>The pipeline runs 11 agents: dataset, cleaning, EDA, features, model selection, training, tuning, evaluation, explainability, deployment and report.</p>
        </Card>
      </div>
    </>
  );
}
