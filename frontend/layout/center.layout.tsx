import React, { ReactNode } from "react";

export default function CenterLayout({ children }: { children?: ReactNode }) {
  return (
    <div className="flex flex-col min-h-screen justify-center items-center w-full">
      {children}
    </div>
  );
}
