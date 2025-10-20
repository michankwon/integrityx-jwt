"use client";

import React, { useState } from "react";
import Input from "@/components/single/Input";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import Button from "@/components/single/Button";
import Textarea from "@/components/single/Textarea";
import DashboardLayout from "@/layout/dashboard.layout";

const ContentManagement = () => {
  const [blog, setBlog] = useState({
    id: "",
    userId: "",
    href: "",
    imageSrc: "",
    imageAlt: "",
    title: "",
    description: "",
    authorName: "",
    authorImage: "/placeholder-user.jpg",
    authorFallback: "",
    date: "",
    content: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setBlog((prevBlog) => ({ ...prevBlog, [name]: value }));
  };

  const handleEditorChange = (content: string) => {
    setBlog((prevBlog) => ({ ...prevBlog, content }));
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  };

  return (
    <DashboardLayout>
      <div className="container mx-auto py-12">
        <h1 className="text-3xl font-semibold mb-6">Content Management</h1>
        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            name="id"
            placeholder="ID"
            value={blog.id}
            onChange={handleChange}
            required
          />
          <Input
            name="userId"
            placeholder="User ID"
            value={blog.userId}
            onChange={handleChange}
            required
          />
          <Input
            name="href"
            placeholder="URL Slug"
            value={blog.href}
            onChange={handleChange}
            required
          />
          <Input
            name="imageSrc"
            placeholder="Image Source URL"
            value={blog.imageSrc}
            onChange={handleChange}
            required
          />
          <Input
            name="imageAlt"
            placeholder="Image Alt Text"
            value={blog.imageAlt}
            onChange={handleChange}
            required
          />
          <Input
            name="title"
            placeholder="Title"
            value={blog.title}
            onChange={handleChange}
            required
          />
          <Textarea
            name="description"
            placeholder="Description"
            value={blog.description}
            onChange={handleChange}
            required
          />
          <Input
            name="authorName"
            placeholder="Author Name"
            value={blog.authorName}
            onChange={handleChange}
            required
          />
          <Input
            name="authorFallback"
            placeholder="Author Fallback Initials"
            value={blog.authorFallback}
            onChange={handleChange}
            required
          />
          <Input
            name="date"
            type="date"
            placeholder="Publication Date"
            value={blog.date}
            onChange={handleChange}
            required
          />
          <ReactQuill
            value={blog.content}
            onChange={handleEditorChange}
            modules={{
              toolbar: [
                [{ header: "1" }, { header: "2" }, { font: [] }],
                [{ list: "ordered" }, { list: "bullet" }],
                ["bold", "italic", "underline"],
                ["link", "image"],
                [{ align: [] }],
                [{ color: [] }, { background: [] }],
                ["clean"],
              ],
            }}
            formats={[
              "header",
              "font",
              "size",
              "bold",
              "italic",
              "underline",
              "list",
              "bullet",
              "indent",
              "link",
              "image",
              "align",
              "color",
              "background",
            ]}
          />
          <Button
            type="submit"
            className="w-full bg-primary text-primary-foreground"
          >
            Save Blog Post
          </Button>
        </form>
      </div>
    </DashboardLayout>
  );
};

export default ContentManagement;
