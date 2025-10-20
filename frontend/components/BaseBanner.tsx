import React from "react";
import Link from "next/link";
import { blogData } from "../data/blogData";
import { formatDate } from "@/lib/utils";

export default function BaseBanner() {
  const featuredBlog = blogData[0];

  return (
    <section className="w-full pt-12 md:pt-24 lg:pt-32 p-8">
      <div className="px-4 md:px-6 space-y-10 xl:space-y-16">
        <div className="grid max-w-[1300px] mx-auto gap-4 px-4 sm:px-6 md:px-10 md:grid-cols-2 md:gap-16">
          <div>
            <h1 className="lg:leading-tighter text-3xl font-semibold tracking-tighter sm:text-4xl md:text-5xl xl:text-[3.4rem] 2xl:text-[3.75rem]">
              The Ultimate Blog Starter Kit
            </h1>
            <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
              Beautifully designed components that you can copy and paste into
              your blog.
            </p>
            <div className="space-x-4 mt-6">
              <Link
                href="/read-the-blog"
                className="inline-flex h-9 items-center justify-center bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
                prefetch={false}
              >
                Read the Blog
              </Link>
            </div>
          </div>
          <div className="flex flex-col items-start space-y-4 w-full">
            <div className="inline-block rounded-lg bg-muted px-3 py-1 text-sm mt-8 md:mt-0">
              Featured Posts
            </div>
            <div className="flex flex-col items-center justify-center">
              <Link
                href={`/blog/${featuredBlog.id}`}
                className="group grid gap-2 overflow-hidden hover:shadow transition-shadow border"
                prefetch={false}
              >
                <img src={featuredBlog.imageSrc} alt={""} />
                <div className="p-4 space-y-2">
                  <h3 className="text-xl font-semibold group-hover:underline">
                    {featuredBlog.title}
                  </h3>
                  <h3 className="text-sm">{formatDate(featuredBlog.date)}</h3>
                  <p className="text-muted-foreground line-clamp-2">
                    {featuredBlog.description}
                  </p>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <span>{featuredBlog.authorName}</span>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
