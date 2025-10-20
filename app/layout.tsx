import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "@/providers/Providers";
import { RefetchProvider } from "@/context/RefetchContext";
import { ClerkProvider } from "@clerk/nextjs";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Walacor App | Blog + CMS",
  description: "The data platform that handles hashing for you.",
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
          <RefetchProvider>
            <Providers>
              {children}
              <Toaster />
            </Providers>
          </RefetchProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
