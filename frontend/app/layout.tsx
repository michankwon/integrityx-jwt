import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ClerkProvider } from "@clerk/nextjs";
import { LayoutContent } from "@/components/LayoutContent";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Walacor Financial Integrity Platform",
  description: "Secure document verification, attestations, and compliance management",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>
          <LayoutContent>{children}</LayoutContent>
        </body>
      </html>
    </ClerkProvider>
  );
}
