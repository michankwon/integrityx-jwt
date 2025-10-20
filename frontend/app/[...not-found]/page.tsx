"use client";

import Link from "next/link";

const Custom404 = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100">
      <h1 className="text-5xl font-semibold mb-4">404 - Page Not Found</h1>
      <p className="text-lg mb-8">
        Sorry, the page you are looking for does not exist.
      </p>
      <Link
        href="/"
        className="bg-primary text-primary-foreground px-4 py-2 rounded-lg"
      >
        Go to Home
      </Link>
      <div className="mt-4 text-sm text-gray-600">
        <p>Attempted path not valid.</p>
      </div>
    </div>
  );
};

export default Custom404;
