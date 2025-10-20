"use client";

import Link from "next/link";
import DefaultLayout from "@/layout/default.layout";
import BaseBlogCard from "@/components/BaseBlogCard";
import { BlogData } from "@/schemas/blogSchema";
import { useEffect, useState } from "react";
import { useReadSchemas } from "@/hooks/schema/useReadSchemas";
import { toast } from "react-hot-toast";

export default function ReadTheBlog() {
  const [blogs, setBlogs] = useState<BlogData[]>([]);
  const { data, error, readSchemas } = useReadSchemas(Number(process.env.NEXT_PUBLIC_WALACOR_BLOG_ETID));

  useEffect(() => {
    readSchemas();
  }, [readSchemas]);

  useEffect(() => {
    if (Array.isArray(data)) {
      const filteredBlogs = data.filter((blog): blog is BlogData => (blog as BlogData).isPublished && !(blog as BlogData).IsDeleted).sort((a: BlogData, b: BlogData) => new Date(b.CreatedAt).getTime() - new Date(a.CreatedAt).getTime());
      setBlogs(filteredBlogs);
    }
  }, [data]);

  useEffect(() => {
    if (error) {
      toast.error("Failed to load blogs");
    }
  }, [error]);

  return (
    <DefaultLayout>
      <div className="flex min-h-screen flex-col bg-background text-foreground">
        <main className="flex-1">
          <section className="bg-muted">
            <div className="container flex flex-col gap-8 px-4 py-12 items-center md:gap-16 md:px-6 md:py-16 lg:py-24">
              <div className="flex flex-col gap-4">
                <div className="space-y-2">
                  <div className="inline-block rounded-lg bg-white px-3 py-1 text-sm">Featured</div>
                  <h1 className="text-3xl font-semibold tracking-tighter sm:text-4xl md:text-5xl">Introducing the Ultimate Blog Starter Kit</h1>
                </div>
                <p className="text-muted-foreground">Discover the powerful features and customizable components that will take your blog to the next level.</p>
                <Link
                  href={`blog/${blogs[0]?.id}`}
                  className="inline-flex h-9 items-center justify-center bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
                  prefetch={false}
                >
                  Read More
                </Link>
              </div>
            </div>
          </section>

          <section className="py-12 md:py-16 lg:py-24">
            <div className="container grid grid-cols-1 gap-8 px-4 md:grid-cols-2 md:gap-7 md:px-6 lg:grid-cols-3 lg:gap-7">
              {blogs.map((blog) => (
                <BaseBlogCard
                  key={blog.id}
                  id={blog.id}
                  imageSrc={blog.imageSrc}
                  imageAlt={blog.imageAlt}
                  title={blog.title}
                  description={blog.description}
                  authorName={blog.authorName}
                  authorImage={blog.authorImage}
                  authorFallback={blog.authorFallback}
                  date={blog.date}
                  userId={""}
                  content={""}
                  IsDeleted={false}
                  CreatedAt={blog.CreatedAt}
                  UpdatedAt={blog.UpdatedAt}
                  isPublished={blog.isPublished}
                  publishedDate={blog.publishedDate}
                  selectedVersion={false}
                />
              ))}
            </div>
          </section>
        </main>
      </div>
    </DefaultLayout>
  );
}
