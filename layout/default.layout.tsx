import BaseAlert from "@/components/BaseAlert";
import BaseFooter from "@/components/BaseFooter";
import BaseHeader from "@/components/BaseHeader";
import BottomPopup from "@/components/BottomPopup";
import HelpDropdown from "@/components/HelpDropdown";
import React, { ReactNode } from "react";

export default function DefaultLayout({ children }: { children?: ReactNode }) {
  return (
    <div className="flex flex-col min-h-dvh relative">
      <BaseAlert />
      <BaseHeader />
      <HelpDropdown />
      <main className="flex-1 z-10">{children}</main>
      <BottomPopup />
    </div>
  );
}
