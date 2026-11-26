"use client";
import { Database, Server, Bot } from "lucide-react";
import { API, api } from "@/lib/api";
import { usePoll } from "@/lib/hooks";
import { Card, Chip, ErrorBox, Kpi, Loading } from "@/components/ui";

export default function Health() {
  const h = usePoll(api.health, 10000);
  const p = usePoll(api.pipeline, 0);
  if (h.loading) return <Loading />;
  return (
    <>
      <div className="head"><div><h1>System</h1><p className="mu">Backend at {API}</p></div></div>
      {h.error && !h.data ? <ErrorBox msg={h.error} /> : (
        <>
          <div className="grid g4" style={{ gridTemplateColumns: "repeat(3,1fr)" }}>
            <Kpi icon={Server} label="API" value={h.data.status} sub={`${h.data.service} v${h.data.version}`} />
            <Kpi icon={Database} label="Database" value={h.data.database} sub="PostgreSQL" />
            <Kpi icon={Bot} label="Agents" value={p.data?.total_agents ?? "—"} sub="Registered in the pipeline" />
          </div>
          <Card title="Pipeline agents" sub="Run in this order for every experiment" className="mt">
            <div className="agents">{(p.data?.registered_agents || []).map((a, i) => <div key={a} className="agent"><span className="mu">{i + 1}</span>{a.replace("Agent", "")}<Chip status="completed">Ready</Chip></div>)}</div>
          </Card>
        </>
      )}
    </>
  );
}
