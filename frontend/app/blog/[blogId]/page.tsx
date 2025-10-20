"use client";

import { useParams } from "next/navigation";
import BaseMoreStories from "@/components/BaseMoreStories";
import BaseBlog from "@/components/BaseBlog";
import BlogLayout from "@/layout/blog.layout";
import Link from "next/link";
import useReadOneSchema from "@/hooks/schema/useReadOneSchema";
import { useEffect, useState } from "react";
import { blogData } from "@/data/blogData";
import { BlogData } from "@/schemas/blogSchema";

const BlogPost = () => {
  const params = useParams();
  const blogId = String(params?.blogId);

  const [blog, setBlog] = useState<BlogData | null | any>(() => {
    const defaultBlog = blogData.find((b) => b.id === blogId);
    return defaultBlog || null;
  });

  const { response, error, loading, readOneSchema } = useReadOneSchema(blogId, Number(process.env.NEXT_PUBLIC_WALACOR_BLOG_ETID));

  useEffect(() => {
    if (!response && !loading && !error) {
      readOneSchema();
    }
  }, [readOneSchema, response, loading, error]);

  useEffect(() => {
    if (response) {
      setBlog(response);
    }
  }, [response]);

  if (!blog) {
    return (
      <BlogLayout>
        <div className="w-full text-center flex flex-col justify-center items-center">
          <h1 className="text-2xl font-semibold mb-4">Blog Not Found</h1>
          <p className="text-gray-600 mb-6">Sorry, the blog post you are looking for does not exist or has been removed.</p>
          <Link
            href="/"
            className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
            prefetch={false}
          >
            Go to Homepage
          </Link>
          <Link
            href="/read-the-blog"
            className="inline-flex h-9 items-center justify-center rounded-md bg-muted px-4 py-2 text-sm font-medium text-muted-foreground shadow transition-colors hover:bg-muted/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 mt-4"
            prefetch={false}
          >
            View All Blogs
          </Link>
        </div>
      </BlogLayout>
    );
  }

  return (
    <BlogLayout>
      <BaseBlog
        title={blog.title}
        description={blog.description}
        imageSrc={blog.imageSrc.toString()}
        imageAlt={blog.imageAlt}
        content={blog.content}
        authorName={blog.authorName}
        date={blog.date}
        id={""}
        userId={""}
        authorImage={""}
        authorFallback={""}
        IsDeleted={false}
        CreatedAt={0}
        UpdatedAt={0}
        isPublished={false}
        publishedDate={null}
        selectedVersion={false}
      />
      <BaseMoreStories currentBlogId={blogId} />
    </BlogLayout>
  );
};

export default BlogPost;
