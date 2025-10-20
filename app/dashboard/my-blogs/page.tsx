"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import DashboardLayout from "@/layout/dashboard.layout";
import Button from "@/components/single/Button";
import { BlogData } from "@/schemas/blogSchema";
import { useUpdateSchema } from "@/hooks/schema/useUpdateSchema";
import ContentManagement from "@/components/ContentManagement";
import { formatTimestampToDateTime } from "@/lib/utils";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowUpRightFromSquare, faCheckCircle, faChevronDown, faChevronUp, faRedo, faTrash, faUndo } from "@fortawesome/free-solid-svg-icons";
import { toast } from "react-hot-toast";
import { successToastStyle, errorToastStyle } from "@/styles/toastStyles";
import { useGetUser } from "@/hooks/user/useGetUser";
import { useUser } from "@clerk/nextjs";
import { diffWords } from "diff";
import { Tooltip } from "@/components/single/Tooltip";
import { useReadSchemas } from "@/hooks/schema/useReadSchemas";
import BaseLoader from "@/components/BaseLoader";
import SubDashboardLayout from "@/layout/subdashboard.layout";

const MyBlogs: React.FC = () => {
  const [blogs, setBlogs] = useState<BlogData[]>([]);
  const [editBlog, setEditBlog] = useState<BlogData | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showPublishModal, setShowPublishModal] = useState<BlogData | null>(null);
  const [revisionToDelete, setRevisionToDelete] = useState<BlogData | null>(null);
  const [blogToDelete, setBlogToDelete] = useState<BlogData | null>(null);
  const [openRevisions, setOpenRevisions] = useState<{ [key: string]: boolean }>({});
  const [includePreviousRevision, setIncludePreviousRevision] = useState<{ [key: string]: boolean }>({});
  const [showDeletedRevisions, setShowDeletedRevisions] = useState(false);
  const [showMore, setShowMore] = useState<{ [key: string]: boolean }>({});
  const [showMoreDescription, setShowMoreDescription] = useState<{ [key: string]: boolean }>({});
  const [showMoreTitle, setShowMoreTitle] = useState<{ [key: string]: boolean }>({});
  const [isTimeoutActive, setIsTimeoutActive] = useState<boolean>(false);

  const { data: mainData, loading, readSchemas } = useReadSchemas(Number(process.env.NEXT_PUBLIC_WALACOR_BLOG_ETID));
  const { updateRecord } = useUpdateSchema(Number(process.env.NEXT_PUBLIC_WALACOR_BLOG_ETID));

  const { user: clerkUser } = useUser();
  const { getUser } = useGetUser();

  useEffect(() => {
    if (clerkUser) {
      getUser({ userId: clerkUser.fullName || clerkUser.id });
    }
  }, [clerkUser, getUser]);

  useEffect(() => {
    readSchemas();
  }, [readSchemas]);

  useEffect(() => {
    if (!loading && blogs.length === 0) {
      const timeout = setTimeout(() => {
        setIsTimeoutActive(true);
      }, 5000);

      return () => clearTimeout(timeout);
    }
  }, [blogs, loading]);

  useEffect(() => {
    if (isTimeoutActive) {
      const createBlog = confirm("No blogs found, do you want to create a blog?");
      if (createBlog) {
        window.location.href = "/dashboard/create";
      }
    }
  }, [isTimeoutActive]);

  const filterAndSortBlogs = (blogs: BlogData[]): BlogData[] => {
    const nonDeletedBlogs = blogs.filter((blog) => !blog.IsDeleted);

    const latestBlogs = Object.values(
      nonDeletedBlogs.reduce((acc: { [id: string]: BlogData }, blog: BlogData) => {
        if (!acc[blog.id] || new Date(blog.CreatedAt) > new Date(acc[blog.id].CreatedAt)) {
          acc[blog.id] = blog;
        }
        return acc;
      }, {})
    );

    return latestBlogs.sort((a, b) => new Date(b.CreatedAt).getTime() - new Date(a.CreatedAt).getTime());
  };

  useEffect(() => {
    if (mainData) {
      const filteredAndSortedBlogs = filterAndSortBlogs(mainData as BlogData[]);
      setBlogs(filteredAndSortedBlogs);
    }
  }, [mainData]);

  const groupedRevisions = (mainData as BlogData[])?.reduce((acc: { [key: string]: BlogData[] }, revision: BlogData) => {
    const blogId = revision.id.toString();
    if (!acc[blogId]) {
      acc[blogId] = [];
    }
    acc[blogId].push(revision);
    return acc;
  }, {});

  const toggleRevisions = (blogId: string) => {
    setOpenRevisions((prevOpen) => ({
      ...prevOpen,
      [blogId]: !prevOpen[blogId],
    }));
  };

  const toggleIncludePrevious = (blogId: string) => {
    setIncludePreviousRevision((prevInclude) => ({
      ...prevInclude,
      [blogId]: !prevInclude[blogId],
    }));
  };

  const toggleShowMore = (blogId: string) => {
    setShowMore((prevShowMore) => ({
      ...prevShowMore,
      [blogId]: !prevShowMore[blogId],
    }));
  };

  const toggleShowMoreDescription = (blogId: string) => {
    setShowMoreDescription((prevShowMore) => ({
      ...prevShowMore,
      [blogId]: !prevShowMore[blogId],
    }));
  };

  const toggleShowMoreTitle = (blogId: string) => {
    setShowMoreTitle((prevShowMore) => ({
      ...prevShowMore,
      [blogId]: !prevShowMore[blogId],
    }));
  };

  const truncateContent = (content: string, length: number) => {
    if (content.length <= length) return content;
    return `${content.substring(0, length)}...`;
  };

  const canPerformActions = () => true;

  const confirmDelete = async () => {
    if (blogToDelete) {
      try {
        const blogCopy = { UID: blogToDelete.UID, IsDeleted: true };
        await updateRecord(blogCopy);

        const relatedRevisions = groupedRevisions?.[blogToDelete.id] || [];
        if (relatedRevisions.length > 0) {
          for (const revision of relatedRevisions) {
            await updateRecord({ UID: revision.UID, IsDeleted: true });
          }
        }

        setShowModal(false);
        setBlogToDelete(null);
        toast.success("Blog and its revisions deleted successfully!", successToastStyle);
      } catch (error) {
        toast.error("Failed to delete blog and revisions.", errorToastStyle);
      }
    }
  };

  const confirmDeleteRevision = async () => {
    if (revisionToDelete) {
      try {
        await updateRecord({ UID: revisionToDelete.UID, IsDeleted: true });
        setRevisionToDelete(null);
        toast.success("Revision deleted successfully!", successToastStyle);
      } catch (error) {
        toast.error("Failed to delete revision.", errorToastStyle);
      }
    }
  };

  const handleDelete = (blog: BlogData) => {
    setBlogToDelete(blog);
    setShowModal(true);
  };

  const handleDeleteRevision = (revision: BlogData) => {
    setRevisionToDelete(revision);
  };

  const handleEdit = (blog: BlogData) => {
    setEditBlog(blog);
    toast.success("You can now edit the blog.", successToastStyle);
  };

  const handleTogglePublish = async (blog: BlogData) => {
    if (!canPerformActions()) {
      toast.error("You do not have permission to publish/unpublish this blog.", errorToastStyle);
      return;
    }

    const updatedBlog = {
      UID: blog.UID,
      isPublished: !blog.isPublished,
      publishedDate: blog.isPublished ? null : new Date().toISOString(),
    };
    try {
      await updateRecord(updatedBlog);
      toast.success(blog.isPublished ? "Blog unpublished successfully!" : "Blog published successfully!", successToastStyle);
    } catch (error) {
      toast.error("Failed to change publish status.", errorToastStyle);
    }
  };

  const restoreBlogOrRevision = async (blogOrRevision: BlogData) => {
    try {
      await updateRecord({ UID: blogOrRevision.UID, IsDeleted: false });
      toast.success("Item restored successfully!", successToastStyle);
    } catch (error) {
      toast.error("Failed to restore item.", errorToastStyle);
    }
  };

  const createHighlightedDiff = (oldText: string, newText: string, showDiff: boolean) => {
    if (!showDiff) return newText;

    const diff = diffWords(oldText, newText);
    const result: JSX.Element[] = [];

    diff.forEach((part, index) => {
      if (part.added) {
        result.push(
          <span key={`added-${index}`} className="bg-green-200">
            {part.value}
          </span>
        );
      } else if (part.removed) {
        result.push(
          <span key={`removed-${index}`} className="bg-red-200">
            {part.value}
          </span>
        );
      } else {
        result.push(<span key={`normal-${index}`}>{part.value}</span>);
      }
    });

    return result;
  };

  const promoteToLive = async (blogId: string, revision: BlogData) => {
    try {
      const currentLiveVersion = blogs.find((blog) => blog.selectedVersion);
      if (currentLiveVersion) {
        await updateRecord({
          UID: currentLiveVersion.UID,
          selectedVersion: false,
          isPublished: false,
        });
      }

      await updateRecord({
        UID: revision.UID,
        id: blogId,
        selectedVersion: true,
        isPublished: true,
      });

      toast.success("Revision promoted to live version!", successToastStyle);
    } catch (error) {
      toast.error("Failed to promote revision.", errorToastStyle);
    }
  };

  const promoteWithoutPublishing = async (blogId: string, revision: BlogData) => {
    try {
      const currentLiveVersion = blogs.find((blog) => blog.selectedVersion && blog.id !== revision.id);
      if (currentLiveVersion) {
        await updateRecord({
          UID: currentLiveVersion.UID,
          selectedVersion: false,
          isPublished: false,
        });
      }

      await updateRecord({
        UID: revision.UID,
        id: blogId,
        selectedVersion: true,
        isPublished: false,
      });

      readSchemas();
      toast.success("Revision selected as live version (not published)!", successToastStyle);
    } catch (error) {
      toast.error("Failed to select revision as live version.", errorToastStyle);
    }
  };

  return (
    <>
      <DashboardLayout>
        <SubDashboardLayout>
          <div className="container mx-auto py-12">
            <h1 className="text-3xl font-semibold text-center mb-6">My Blogs</h1>
            <p className="text-gray-600 mb-6 text-center">
              This is an example of data fetched from the Walacor platform. This page is a simple blog management system that allows you to view, edit, delete, publish, and restore blogs and their revisions.
            </p>

            {blogs.length <= 0 ? (
              <div className="space-y-6 flex gap-2 items-center animate-pulse text-center w-full justify-center">
                <span className="text-sm text-gray-600 flex items-center gap-2">
                  Fetching... <BaseLoader />
                </span>
              </div>
            ) : editBlog ? (
              <ContentManagement initialBlog={editBlog} setEditBlog={setEditBlog} />
            ) : (
              <div className="space-y-6">
                {blogs.map((blog) => (
                  <div key={blog.id} className="bg-white p-4 border rounded shadow-lg">
                    <h2 className="text-xl font-semibold mb-2">
                      {blog.title.length > 30 ? (
                        <>
                          {showMoreTitle[blog.id] ? blog.title : truncateContent(blog.title, 30)}
                          <button className="text-blue-500 hover:underline text-sm ml-2" onClick={() => toggleShowMoreTitle(blog.id)}>
                            {showMoreTitle[blog.id] ? "See Less" : "See More"}
                          </button>
                        </>
                      ) : (
                        blog.title
                      )}
                    </h2>
                    <Link target="_blank" href={`/blog/${blog.id}`} className="hover:underline transition-all mr-2 flex items-center gap-1 opacity-50 hover:opacity-100 mb-2">
                      <span>Read Blog</span>
                      <FontAwesomeIcon icon={faArrowUpRightFromSquare} />
                    </Link>
                    <p className="text-gray-600 mb-4">
                      {blog.description.length > 100 ? (
                        <>
                          {showMore[blog.id] ? blog.description : truncateContent(blog.description, 100)}
                          <button className="text-blue-500 hover:underline text-sm mb-4" onClick={() => toggleShowMore(blog.id)}>
                            {showMore[blog.id] ? "See Less" : "See More"}
                          </button>
                        </>
                      ) : (
                        blog.description
                      )}
                    </p>
                    <div className="flex justify-between items-center">
                      <div />
                      {canPerformActions() && (
                        <div className="flex space-x-2 items-center">
                          {blog.IsDeleted ? (
                            <Button className="bg-yellow-500 text-white" onClick={() => restoreBlogOrRevision(blog)}>
                              Restore
                              <FontAwesomeIcon className="ml-2" icon={faUndo} />
                            </Button>
                          ) : (
                            <>
                              <Button className="bg-red-500 text-white" onClick={() => handleDelete(blog)}>
                                Delete
                              </Button>
                              <Button className="bg-primary text-primary-foreground" onClick={() => handleEdit(blog)}>
                                Edit
                              </Button>
                              <Button className={blog.isPublished ? "bg-gray-500 text-white" : "bg-green-500 text-white"} onClick={() => handleTogglePublish(blog)}>
                                {blog.isPublished ? "Unpublish" : "Publish"}
                              </Button>
                            </>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="flex justify-between items-center">
                      <button className="hover:underline transition-all mr-2 flex items-center gap-1 opacity-50 hover:opacity-100 mb-2 text-xs" onClick={() => toggleRevisions(blog.id)}>
                        {openRevisions[blog.id] ? "Hide Revisions" : "See Revisions"}
                        <FontAwesomeIcon icon={openRevisions[blog.id] ? faChevronUp : faChevronDown} />
                      </button>
                      <span className="opacity-50 text-xs mt-4">Created: {formatTimestampToDateTime(blog.CreatedAt)}</span>
                    </div>
                    {openRevisions[blog.id] && (
                      <div className="mt-4 p-4">
                        <div className="flex items-center mb-4">
                          <label className="mr-2 text-sm font-semibold flex items-center">
                            Show Changes
                            <Tooltip text="This feature is to show the changes between the current revision and the previous revision. This is useful for easily identifying what has changed between revisions." />
                          </label>
                          <input type="checkbox" checked={includePreviousRevision[blog.id] || false} onChange={() => toggleIncludePrevious(blog.id)} className="toggle-checkbox" />
                        </div>
                        <div className="flex items-center mb-4">
                          <label className="mr-2 text-sm font-semibold flex items-center">
                            Show Data in Walacor
                            <Tooltip text="This feature is to show off Walacor's robust data platform in that we store ALL history and maintain an indefinite audit log -- particularly useful for compliance and regulatory purposes." />
                          </label>
                          <input type="checkbox" checked={showDeletedRevisions} onChange={(e) => setShowDeletedRevisions(e.target.checked)} className="toggle-checkbox" />
                        </div>
                        <h3 className="font-semibold mb-2">Revision History:</h3>
                        <div className="space-y-4">
                          {groupedRevisions[blog.id] &&
                            groupedRevisions[blog.id]
                              .reverse()
                              .filter((revision: BlogData) => showDeletedRevisions || !revision.IsDeleted)
                              .map((revision: BlogData, index: number) => {
                                const previousRevision = groupedRevisions[blog.id][index + 1];
                                const isLive = revision.selectedVersion;

                                return (
                                  <div key={index} className={`border p-4 rounded shadow-lg ${isLive ? "border-green-500 bg-green-50" : "border-gray-300"} ${revision.IsDeleted ? "bg-gray-100" : ""}`}>
                                    <div className="flex justify-between items-center mb-2">
                                      <div className="text-sm text-gray-600">
                                        <strong>Revision ID:</strong> {revision.id}
                                      </div>
                                      {isLive && <div className="text-xs text-green-600 font-semibold">Current Version</div>}
                                    </div>
                                    <div className="text-sm text-gray-600 mb-2">
                                      <strong>Author:</strong> {revision.authorName}
                                    </div>
                                    <div className="text-sm text-gray-600 mb-2">
                                      <strong>Created At:</strong> {formatTimestampToDateTime(revision.CreatedAt)}
                                    </div>
                                    {includePreviousRevision[blog.id] && previousRevision ? (
                                      <>
                                        <div className="mb-2">
                                          <strong>Title:</strong> {createHighlightedDiff(previousRevision.title, revision.title, includePreviousRevision[blog.id])}
                                        </div>
                                        <div className="mb-2">
                                          <strong>Description:</strong> {createHighlightedDiff(previousRevision.description, revision.description, includePreviousRevision[blog.id])}
                                        </div>
                                        <div className="mb-2">
                                          <strong>Content:</strong> {createHighlightedDiff(previousRevision.content, revision.content, includePreviousRevision[blog.id])}
                                        </div>
                                      </>
                                    ) : (
                                      <div className="mt-4">
                                        <h4 className="font-semibold mb-1">Revision Content:</h4>
                                        <div className="p-2 bg-gray-50 border rounded">
                                          <div className="mb-2">
                                            <strong>Title:</strong>{" "}
                                            {revision.title.length > 30 ? (
                                              <>
                                                {showMoreTitle[revision.id] ? revision.title : truncateContent(revision.title, 30)}
                                                <button className="text-blue-500 hover:underline text-sm ml-2" onClick={() => toggleShowMoreTitle(revision.id)}>
                                                  {showMoreTitle[revision.id] ? "See Less" : "See More"}
                                                </button>
                                              </>
                                            ) : (
                                              revision.title
                                            )}
                                          </div>
                                          <div className="mb-2">
                                            <strong>Description:</strong>{" "}
                                            {revision.description.length > 50 ? (
                                              <>
                                                {showMoreDescription[revision.id] ? revision.description : truncateContent(revision.description, 50)}
                                                <button className="text-blue-500 hover:underline text-sm ml-2" onClick={() => toggleShowMoreDescription(revision.id)}>
                                                  {showMoreDescription[revision.id] ? "See Less" : "See More"}
                                                </button>
                                              </>
                                            ) : (
                                              revision.description
                                            )}
                                          </div>
                                          <div className="mb-2">
                                            <strong>Content:</strong>{" "}
                                            {revision.content.length > 50 ? (
                                              <>
                                                {showMore[revision.id] ? revision.content : truncateContent(revision.content, 50)}
                                                <button className="text-blue-500 hover:underline text-sm ml-2" onClick={() => toggleShowMore(revision.id)}>
                                                  {showMore[revision.id] ? "See Less" : "See More"}
                                                </button>
                                              </>
                                            ) : (
                                              revision.content
                                            )}
                                          </div>
                                        </div>
                                      </div>
                                    )}
                                    <div className="mt-4 flex items-center space-x-2">
                                      {isLive ? (
                                        <>
                                          <Button className="bg-green-500 text-white cursor-not-allowed" onClick={() => toast.success("This is the current version.", successToastStyle)}>
                                            Current Version
                                            <FontAwesomeIcon className="ml-2" icon={faCheckCircle} />
                                          </Button>
                                          <Button
                                            className="bg-red-500 text-white"
                                            onClick={async () => {
                                              try {
                                                await updateRecord({
                                                  UID: revision.UID,
                                                  selectedVersion: false,
                                                  isPublished: false,
                                                });
                                                toast.success("Version unselected successfully!", successToastStyle);
                                                readSchemas();
                                              } catch (error) {
                                                toast.error("Failed to unselect version.", errorToastStyle);
                                              }
                                            }}
                                          >
                                            Unselect Version
                                          </Button>
                                        </>
                                      ) : (
                                        !revision.IsDeleted && (
                                          <Button className="bg-primary text-primary-foreground hover:bg-primary-hover hover:text-primary-hover" onClick={() => setShowPublishModal(revision)}>
                                            Select Version
                                            <FontAwesomeIcon className="ml-2" icon={faRedo} />
                                          </Button>
                                        )
                                      )}
                                      {revision.IsDeleted ? (
                                        <Button className="bg-yellow-500 text-white" onClick={() => restoreBlogOrRevision(revision)}>
                                          Restore
                                          <FontAwesomeIcon className="ml-2" icon={faUndo} />
                                        </Button>
                                      ) : (
                                        !isLive && (
                                          <Button className="bg-red-500 text-white hover:bg-red-600" onClick={() => handleDeleteRevision(revision)}>
                                            Delete
                                            <FontAwesomeIcon className="ml-2" icon={faTrash} />
                                          </Button>
                                        )
                                      )}
                                    </div>
                                  </div>
                                );
                              })}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </SubDashboardLayout>
      </DashboardLayout>
      {showModal && (
        <div onClick={() => setShowModal(false)} className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Are you sure?</h2>
            <p className="mb-6">Do you really want to delete this blog?</p>
            <div className="flex justify-end space-x-2">
              <Button className="bg-gray-500 text-white" onClick={() => setShowModal(false)}>
                Cancel
              </Button>
              <Button className="bg-red-500 text-white" onClick={confirmDelete}>
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}

      {revisionToDelete && (
        <div onClick={() => setRevisionToDelete(null)} className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Are you sure?</h2>
            <p className="mb-6">Do you really want to delete this revision?</p>
            <div className="flex justify-end space-x-2">
              <Button className="bg-gray-500 text-white" onClick={() => setRevisionToDelete(null)}>
                Cancel
              </Button>
              <Button className="bg-red-500 text-white" onClick={confirmDeleteRevision}>
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}

      {showPublishModal && (
        <div onClick={() => setShowPublishModal(null)} className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Confirm Version Selection</h2>
            <p className="mb-6">Do you want to select this revision as the live version?</p>
            <div className="flex justify-end space-x-2">
              <Button className="bg-gray-500 text-white" onClick={() => setShowPublishModal(null)}>
                Cancel
              </Button>
              <Button
                className="bg-green-500 text-white"
                onClick={() => {
                  if (showPublishModal) {
                    promoteToLive(showPublishModal.id, showPublishModal);
                    setShowPublishModal(null);
                  }
                }}
              >
                Select Version & Publish
              </Button>
              <Button
                className="bg-primary text-white"
                onClick={() => {
                  if (showPublishModal) {
                    promoteWithoutPublishing(showPublishModal.id, showPublishModal);
                    setShowPublishModal(null);
                  }
                }}
              >
                Select Version & Do Not Publish
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default MyBlogs;
