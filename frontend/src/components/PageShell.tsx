import { ReactNode } from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";
import { Premium3DBorders } from "./Premium3DBorders";

export const PageShell = ({ children }: { children: ReactNode }) => (
  <>
    <Premium3DBorders />
    <div className="theme-shell min-h-screen flex flex-col relative z-0" style={{ background: "transparent" }} data-testid="page-shell">
      <Navbar />
      <main className="theme-main-content flex-1 pt-[5rem] sm:pt-[5.5rem]">{children}</main>
      <Footer />
    </div>
  </>
);
