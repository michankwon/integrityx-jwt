import React, { useState } from "react";
import Image from "next/image";
import { BlogData } from "@/schemas/blogSchema";

const BaseBlog: React.FC<BlogData> = ({
  title,
  description,
  imageSrc,
  imageAlt,
  content,
  authorName,
  date,
}) => {
  const [isImageLoaded, setIsImageLoaded] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const options = { year: "numeric", month: "long", day: "numeric" } as const;
    return date.toLocaleDateString("en-US", options);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-4xl font-semibold mb-4 text-center">{title}</h1>
      <p className="text-gray-600 mb-6 text-center">{description}</p>

      {!isImageLoaded && (
        <div className="w-full h-96 bg-muted animate-pulse rounded-md my-8" />
      )}

      <Image
        className={`my-8 transition-opacity duration-500 ${
          isImageLoaded ? "opacity-100" : "opacity-0"
        }`}
        src={imageSrc}
        alt={imageAlt}
        width={800}
        height={500}
        onLoadingComplete={() => setIsImageLoaded(true)}
      />
      {content && (
        <div
          className="prose prose-lg dark:prose-invert flex flex-col gap-1 mx-auto"
          dangerouslySetInnerHTML={{ __html: content }}
        />
      )}
      <div className="mt-8 text-sm text-gray-600 text-center">
        <p>By {authorName}</p>
        <p>{formatDate(date)}</p>
      </div>
    </div>
  );
};

export default BaseBlog;
