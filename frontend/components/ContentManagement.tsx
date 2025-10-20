import React, { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import Input from "@/components/single/Input";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import Button from "@/components/single/Button";
import Textarea from "@/components/single/Textarea";
import usePostSchema from "@/hooks/schema/usePostSchema";
import { useUpdateSchema } from "@/hooks/schema/useUpdateSchema";
import BaseUploadImage from "@/components/BaseUploadImage";
import { BlogData } from "@/schemas/blogSchema";
import { useAuth, useUser } from "@clerk/nextjs";
import { formatDate } from "@/lib/utils";
import { toast } from "react-hot-toast";
import { successToastStyle, errorToastStyle } from "@/styles/toastStyles";
import { useGetUser } from "@/hooks/user/useGetUser";
import { useReadSchemas } from "@/hooks/schema/useReadSchemas";
import { useRefetch } from "@/context/RefetchContext";

interface ContentManagementProps {
  initialBlog?: BlogData | null;
  setEditBlog?: React.Dispatch<React.SetStateAction<BlogData | null>>;
}

const ContentManagement: React.FC<ContentManagementProps> = ({ initialBlog = null, setEditBlog }) => {
  const router = useRouter();
  const today = new Date().toISOString().split("T")[0];
  const { userId } = useAuth();
  const { user: clerkUser } = useUser();
  const { getUser } = useGetUser();
  const { triggerRefetch } = useRefetch();
  const pathname = usePathname();

  const { data: blogs } = useReadSchemas(Number(process.env.NEXT_PUBLIC_WALACOR_BLOG_ETID));

  useEffect(() => {
    if (clerkUser) {
      getUser({ userId: clerkUser.id });
    }
  }, [clerkUser, getUser]);

  const initialBlogState: BlogData = {
    id: initialBlog?.id || String(new Date().getTime()),
    userId: userId || "",
    imageSrc: initialBlog?.imageSrc || "",
    imageAlt: initialBlog?.imageAlt || "",
    title: initialBlog?.title || "",
    description: initialBlog?.description || "",
    authorName: String(clerkUser?.firstName) + " " + String(clerkUser?.lastName) || String(clerkUser?.fullName) || "Anonymous",
    authorImage: String(clerkUser?.imageUrl) || "/placeholder-user.jpg",
    authorFallback: String(clerkUser?.firstName).slice(0, 1).toUpperCase() + " " + String(clerkUser?.lastName).slice(0, 1).toUpperCase() || "",
    date: initialBlog?.date || today,
    content: initialBlog?.content || "",
    IsDeleted: initialBlog?.IsDeleted || false,
    CreatedAt: initialBlog?.CreatedAt || Date.now(),
    UpdatedAt: initialBlog?.UpdatedAt || Date.now(),
    isPublished: initialBlog?.isPublished || false,
    publishedDate: initialBlog?.publishedDate || null,
    selectedVersion: initialBlog?.selectedVersion ?? true,
  };

  const [blog, setBlog] = useState<BlogData>(initialBlogState);

  const { postSchema, loading: postLoading } = usePostSchema(Number(process.env.NEXT_PUBLIC_WALACOR_BLOG_ETID));
  const { updateRecord, loading: updateLoading } = useUpdateSchema(Number(process.env.NEXT_PUBLIC_WALACOR_BLOG_ETID));

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setBlog((prevBlog) => ({ ...prevBlog, [name]: value }));
  };

  const handleEditorChange = (content: string) => {
    setBlog((prevBlog) => ({ ...prevBlog, content }));
  };

  const handleImageUpload = (url: string) => {
    setBlog((prevBlog) => ({ ...prevBlog, imageSrc: String(url) }));
  };

  const handleNavigation = () => {
    if (pathname === "/dashboard/create") {
      router.push("/dashboard/my-blogs");
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    try {
      const isFirstBlog = Array.isArray(blogs) && blogs.length === 0;

      const payload = {
        ...blog,
        selectedVersion: blog.UID ? false : isFirstBlog,
      };

      if (blog.UID) {
        const currentSelectedVersion = blogs ? blogs.find((blogItem) => blogItem.selectedVersion) : null;
        if (currentSelectedVersion && initialBlog?.id !== currentSelectedVersion.id) {
          await updateRecord({
            ...currentSelectedVersion,
            UID: currentSelectedVersion.UID,
            selectedVersion: false,
          });
        }
        await updateRecord(payload);
      } else {
        await postSchema(payload);
      }

      if (setEditBlog) setEditBlog(null);
      toast.success("Blog saved successfully!", successToastStyle);
      triggerRefetch();
      handleNavigation();
    } catch (error) {
      toast.error("Error saving blog", errorToastStyle);
      console.error("Error saving blog:", error);
    }
  };

  const handlePublish = async () => {
    const updatedBlog = {
      ...blog,
      isPublished: true,
      publishedDate: new Date().toISOString(),
      selectedVersion: true,
      ...(blog.UID ? { UID: blog.UID } : {}),
    };

    try {
      const currentLiveVersion = Array.isArray(blogs) ? blogs.find((blogItem) => blogItem.selectedVersion) : null;
      if (currentLiveVersion && initialBlog?.id !== currentLiveVersion.id) {
        await updateRecord({
          UID: currentLiveVersion.UID,
          selectedVersion: false,
        });
      }

      await (blog.UID ? updateRecord(updatedBlog) : postSchema(updatedBlog));

      if (setEditBlog) setEditBlog(null);
      toast.success("Blog published successfully!", successToastStyle);
      triggerRefetch();
      handleNavigation();
    } catch (error) {
      toast.error("Error publishing blog", errorToastStyle);
      console.error("Error publishing blog:", error);
    }
  };

  const handleCancelEdit = () => {
    if (setEditBlog) setEditBlog(null);
  };

  return (
    <div className="container mx-auto py-12">
      <h1 className={`${initialBlog ? "" : "mb-6"} text-3xl text-center font-semibold`}>{initialBlog ? "" : "Create Blog"}</h1>
      <p className="text-gray-600 mb-6 text-center">Here you can create and manage your blog content. Use the form below to create a new blog post or update an existing one.</p>

      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow-lg mb-6">
        <h2>Title of Blog</h2>
        <Input name="title" placeholder="Title" value={blog.title} onChange={handleChange} required />
        <h2>Brief Description of Blog</h2>
        <Textarea name="description" placeholder="Description" value={blog.description} onChange={handleChange} required />
        <BaseUploadImage onUpload={handleImageUpload} />

        <h2>Blog Content & Structure</h2>
        <p className="text-xs opacity-50 -my-2 -mt-4">(Limited to 500 characters for the description.)</p>
        <ReactQuill
          className="bg-white"
          value={blog.content}
          onChange={handleEditorChange}
          modules={{
            toolbar: [[{ header: "1" }, { header: "2" }, { font: [] }], [{ list: "ordered" }, { list: "bullet" }], ["bold", "italic", "underline"], ["link", "image"], [{ align: [] }], [{ color: [] }, { background: [] }], ["clean"]],
          }}
          formats={["header", "font", "size", "bold", "italic", "underline", "list", "bullet", "indent", "link", "image", "align", "color", "background"]}
        />

        <div className="flex flex-col gap-4">
          <Button type="submit" className={`bg-primary text-white w-full`} disabled={postLoading || updateLoading}>
            {postLoading || updateLoading ? "Saving..." : "Save Blog Post"}
          </Button>
          <Button type="button" className="w-full bg-secondary text-secondary-foreground border-2 border-black hover:bg-black hover:text-white transition-all" onClick={handlePublish} disabled={postLoading || updateLoading}>
            {postLoading || updateLoading ? "Publishing..." : "Save & Publish"}
          </Button>
          {initialBlog && (
            <Button type="button" className="w-full bg-none text-red-500 border-2 border-red-500 hover:bg-red-500 hover:text-white transition-all" onClick={handleCancelEdit}>
              Cancel Edit
            </Button>
          )}
        </div>

        <div className="flex justify-between gap-2 w-full">
          <span className="text-xs opacity-50">Author: {String(clerkUser?.firstName) + " " + String(clerkUser?.lastName) || "Anonymous"}</span>
          <span className="text-xs opacity-50">Date: {formatDate(today)}</span>
        </div>
      </form>
    </div>
  );
};

export default ContentManagement;
