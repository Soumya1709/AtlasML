import { Inter, Saira } from "next/font/google";
import "./globals.css";
import Nav from "@/components/Nav";

const saira = Saira({ subsets: ["latin"], weight: ["500", "600", "700", "800", "900"], style: ["normal", "italic"], variable: "--font-saira" });
const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata = { title: "AtlasML", description: "Autonomous machine learning research scientist" };

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${saira.variable} ${inter.variable}`}>
      <body><Nav /><main className="page">{children}</main></body>
    </html>
  );
}
