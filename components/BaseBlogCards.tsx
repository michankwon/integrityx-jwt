import React from "react";
import BaseBlogCard from "@/components/BaseBlogCard";
import { blogData } from "@/data/blogData";

interface BaseBlogCardsProps {
  limit?: number;
}

const BaseBlogCards: React.FC<BaseBlogCardsProps> = ({ limit }) => {
  const blogsToShow = limit ? blogData.slice(0, limit) : blogData;

  return (
    <section className="w-full py-12 md:py-24 lg:py-32">
      <div className="container space-y-12 px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <div className="space-y-2">
            <div className="inline-block rounded-lg bg-muted px-3 py-1 text-sm mb-1">Latest Posts</div>
            <h2 className="text-3xl font-semibold tracking-tighter sm:text-5xl">Explore Our Blog</h2>
            <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">Discover a wealth of insights and inspiration from our talented writers.</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-7 justify-center items-start">
          {blogsToShow.map((blog) => (
            <BaseBlogCard
              id={blog.id}
              key={blog.id}
              imageSrc={blog.imageSrc.toString()}
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
              CreatedAt={0}
              UpdatedAt={0}
              isPublished={false}
              publishedDate={null}
              selectedVersion={false}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default BaseBlogCards;
