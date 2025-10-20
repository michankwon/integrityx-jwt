import { SchemaType } from "@/types/schema";

export const blogSchema: SchemaType = {
  ETId: Number(process.env.NEXT_PUBLIC_WALACOR_BLOG_ETID),
  TableName: "blogs",
  Family: "blog-family",
  DoSummary: true,
  Fields: [
    {
      FieldName: "id",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "userId",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "imageSrc",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "imageAlt",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "title",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "description",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "authorName",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "authorImage",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "authorFallback",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "date",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    {
      FieldName: "content",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    { FieldName: "IsDeleted", DataType: "BOOLEAN", Default: false },
    { FieldName: "isPublished", DataType: "BOOLEAN", Default: false },
    {
      FieldName: "publishedDate",
      DataType: "TEXT",
      MaxLength: 2048,
      Required: false,
    },
    { FieldName: "selectedVersion", DataType: "BOOLEAN", Default: false },
  ],
  Indexes: [
    {
      Fields: ["id"],
      IndexValue: "id",
      ForceUpdate: false,
      Delete: false,
    },
    {
      Fields: ["selectedVersion"],
      IndexValue: "selectedVersion",
      ForceUpdate: true,
      Delete: false,
    },
  ],
};

export interface BlogData {
  UID?: string;
  id: string;
  userId: string;
  imageSrc: string;
  imageAlt: string;
  title: string;
  description: string;
  authorName: string;
  authorImage: string;
  authorFallback: string;
  date: string;
  content: string;
  IsDeleted: boolean;
  isPublished: boolean;
  publishedDate: string | null;
  CreatedAt: number;
  UpdatedAt: number;
  selectedVersion: boolean;
}
