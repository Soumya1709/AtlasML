import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Chip, fmtD, fmtN, fmtT, scoreLabel, scoreOf, shortId } from "./ui";

export default function ExpTable({ rows }) {
  if (!rows.length) return <p className="mu empty">No experiments match.</p>;
  return (
    <div className="tw">
      <table>
        <thead><tr><th>Dataset</th><th>Status</th><th>Problem</th><th>Best model</th><th>Score</th><th>Runtime</th><th>Created</th><th /></tr></thead>
        <tbody>
          {rows.map((e) => {
            const r = e.pipeline_result || {};
            return (
              <tr key={e.experiment_id}>
                <td><Link href={`/experiments/${e.experiment_id}`}><div className="strong">{e.dataset_name}</div><div className="mu sm-t">{shortId(e.experiment_id)}</div></Link></td>
                <td><Chip status={e.status} /></td>
                <td>{r.problem_type || "—"}</td>
                <td>{r.evaluation?.model_name || "—"}</td>
                <td>{scoreOf(e) != null ? <span>{fmtN(scoreOf(e))} <span className="mu sm-t">{scoreLabel(e)}</span></span> : "—"}</td>
                <td>{fmtT(e.execution_time)}</td>
                <td>{fmtD(e.created_at)}</td>
                <td><Link href={`/experiments/${e.experiment_id}`} className="mu"><ArrowRight size={16} /></Link></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
