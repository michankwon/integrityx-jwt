"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { UserButton } from "@clerk/nextjs";

export default function BaseHeader() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  return (
    <header className={`px-4 lg:px-6 h-14 z-20 flex items-center top-0 sticky transition-all duration-300 ${scrolled ? "bg-white/30 backdrop-blur-md shadow-lg" : "bg-transparent"}`}>
      <div className="pointer-events-none flex items-center justify-center">
        <UserButton />
      </div>
      <nav className="ml-auto flex gap-4 sm:gap-6 items-center">
        <Link href="/" className="text-sm font-medium hover:underline underline-offset-4" prefetch={false}>
          Home
        </Link>
        <Link href="/read-the-blog" className="text-sm font-medium hover:underline underline-offset-4" prefetch={false}>
          Read
        </Link>
        <Link
          href="/dashboard"
          className="inline-flex h-9 items-center justify-center bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 rounded shadow-lg"
          prefetch={false}
        >
          Dashboard
        </Link>
      </nav>
    </header>
  );
}
