import { BlogData } from "@/schemas/blogSchema";

export const filterBlogs = (blogs: BlogData[], userId: string, onlyPublished: boolean) => {
  return blogs.filter((blog: BlogData) => {
    return !blog.IsDeleted && blog.userId === userId && (!onlyPublished || blog.isPublished);
  });
};

export const getLatestBlogs = (filteredBlogs: BlogData[]) => {
  return filteredBlogs.reduce((acc: BlogData[], current: BlogData) => {
    const existing = acc.find((item) => item.id === current.id);
    if (!existing || new Date(current.CreatedAt) > new Date(existing.CreatedAt)) {
      acc = acc.filter((item) => item.id !== current.id);
      acc.push(current);
    }
    return acc;
  }, [] as BlogData[]);
};

export const getLiveBlogs = (filteredBlogs: BlogData[]) => {
  return filteredBlogs.filter((blog: BlogData) => blog.selectedVersion);
};

export const mergeLiveAndLatestBlogs = (latestBlogs: BlogData[], liveBlogs: BlogData[]) => {
  return latestBlogs.map((latestBlog: BlogData) => {
    const liveBlog = liveBlogs.find((blog: BlogData) => blog.id === latestBlog.id);
    return liveBlog ? { ...latestBlog, ...liveBlog } : latestBlog;
  });
};
