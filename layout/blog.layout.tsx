import React, { ReactNode } from "react";
import DefaultLayout from "./default.layout";

export default function BlogLayout({ children }: { children?: ReactNode }) {
  return (
    <DefaultLayout>
      <div className="container mx-auto py-12 min-h-screen">{children}</div>
    </DefaultLayout>
  );
}
