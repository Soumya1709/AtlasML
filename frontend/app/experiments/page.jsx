"use client";
import { useState } from "react";
import Link from "next/link";
import { Plus, Search } from "lucide-react";
import { api } from "@/lib/api";
import { usePoll } from "@/lib/hooks";
import { Card, ErrorBox, Loading } from "@/components/ui";
import ExpTable from "@/components/ExpTable";

const TABS = [["all", "All"], ["running", "Running"], ["completed", "Completed"], ["failed", "Failed"]];

export default function Experiments() {
  const { data, error, loading } = usePoll(api.experiments, 5000);
  const [tab, setTab] = useState("all");
  const [q, setQ] = useState("");
  if (loading) return <Loading />;
  if (error && !data) return <ErrorBox msg={error} />;
  const all = [...data].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  const inTab = (e, t) => t === "all" || (t === "running" ? ["running", "queued"].includes(e.status) : e.status === t);
  const rows = all.filter((e) => inTab(e, tab) && e.dataset_name.toLowerCase().includes(q.toLowerCase()));
  return (
    <>
      <div className="head"><div><h1>Experiments</h1><p className="mu">Every dataset you have run through the pipeline</p></div><Link href="/new" className="btn p"><Plus size={15} /> New experiment</Link></div>
      <Card>
        <div className="bar-row">
          <div className="tabs">{TABS.map(([k, l]) => <button key={k} className={tab === k ? "on" : ""} onClick={() => setTab(k)}>{l} <span className="count">{all.filter((e) => inTab(e, k)).length}</span></button>)}</div>
          <label className="search"><Search size={14} /><input placeholder="Search datasets" value={q} onChange={(e) => setQ(e.target.value)} /></label>
        </div>
        <ExpTable rows={rows} />
      </Card>
    </>
  );
}
