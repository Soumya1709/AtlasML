"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Plus } from "lucide-react";

const LINKS = [["/", "Overview"], ["/experiments", "Experiments"], ["/new", "New experiment"], ["/health", "System"]];

export default function Nav() {
  const p = usePathname();
  const on = (h) => (h === "/" ? p === "/" : p.startsWith(h));
  return (
    <header className="top">
      <Link href="/" className="logo"><span className="dots">{Array.from({ length: 9 }).map((_, i) => <i key={i} />)}</span><b>Atlas<em>ML</em></b></Link>
      <nav className="pill">{LINKS.map(([h, l]) => <Link key={h} href={h} className={on(h) ? "on" : ""}>{l}</Link>)}</nav>
      <div className="top-r"><Link href="/new" className="btn p"><Plus size={15} /> New</Link><span className="avatar">AT</span></div>
    </header>
  );
}
