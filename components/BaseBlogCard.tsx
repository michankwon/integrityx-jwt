import Link from "next/link";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { formatDate } from "@/lib/utils";
import { BlogData } from "@/schemas/blogSchema";

const BaseBlogCard: React.FC<BlogData> = ({ id, imageSrc, imageAlt, title, description, authorName, authorImage, authorFallback, date }) => {
  return (
    <Link href={`/blog/${id}`} className="bg-muted group grid gap-2 rounded-lg overflow-hidden shadow-sm hover:shadow transition-shadow max-w-[400px]" prefetch={false}>
      <img src={imageSrc} width={400} height={225} alt={imageAlt} className="aspect-video object-cover" />
      <div className="p-4 space-y-2">
        <h3 className="text-xl font-semibold group-hover:underline">{title}</h3>
        <h3 className="text-sm">{formatDate(date)}</h3>
        <p className="text-muted-foreground line-clamp-2">{description}</p>
        <div className="flex items-center text-sm text-muted-foreground">
          <Avatar className="w-6 h-6 mr-2">
            <AvatarImage src={authorImage} />
            <AvatarFallback>{authorFallback}</AvatarFallback>
          </Avatar>
          <span>{authorName}</span>
        </div>
      </div>
    </Link>
  );
};

export default BaseBlogCard;
