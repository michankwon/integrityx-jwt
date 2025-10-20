"use client";

import { faInfoCircle, faChevronDown, faChevronUp, faUser, faCode, faDatabase, faTimes } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState, ReactNode } from "react";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

const HelpDropdown: React.FC = () => {
  const pathname = usePathname();
  const [isHelpVisible, setIsHelpVisible] = useState(false);

  const infoTabs: { [key: string]: { title: string; description: string; additionalInfo?: ReactNode } } = {
    "/dashboard": {
      title: "Blog Content Management System",
      description: "This dashboard demonstrates Walacor's capabilities through a blog management system. It covers basic CRUD operations and advanced features like audit trails, data replication, and schema validation.",
    },
    "/dashboard/schemas": {
      title: "Schema Validation",
      description:
        "Please ensure that you create schemas for Blog, Profile, and Role by clicking the respective tabs. These schemas are essential for the Walacor platform to validate the data sent to the database and maintain data integrity.",
    },
    "/read-the-blog": {
      title: "Explore the Blog Platform",
      description: "This section showcases published and shows off the visibility of the blog posts. You can read the blogs and see how the data is managed and displayed.",
      additionalInfo: <p className="text-blue-800">Go to Dashboard and select My Blogs to toggle which blogs are published and visible.</p>,
    },
    "/dashboard/blog": {
      title: "Blog Management",
      description: "Manage your blog content using this system. Create, update, and delete blog posts while utilizing Walacor's features for content validation and audit trails.",
    },
    "/dashboard/role": {
      title: "Role Management",
      description: "Manage user roles within the Walacor platform. Define scopes such as AdminAccess, ReadWrite, or ReadOnly to control access to different areas of the system.",
    },
    "/dashboard/create": {
      title: "Schema Creation",
      description: "After the Blog Schema has been created successfully, you can now create and edit blogs that will be validated against the schema to ensure data integrity.",
    },
    "/dashboard/my-blogs": {
      title: "Data Management",
      description:
        "This blog management system showcases Walacor's robust capabilities, including creating, editing, and publishing blogs. It also demonstrates advanced features such as version control, audit trails, and schema validation, ensuring data accuracy and compliance.",
    },
    "/dashboard/profile": {
      title: "Profile Management",
      description:
        "The profile management system allows you to update your personal information, such as your name and role, and manage your data in Walacor. This feature demonstrates CRUD operations and schema validation processes to ensure data integrity.",
    },
    "/dashboard/hooks": {
      title: "API Interaction",
      description: "",
      additionalInfo: (
        <div className="flex flex-col items-center space-x-4 justify-center">
          <div className="flex w-full flex-row justify-between">
            <p className="text-blue-800 text-center flex flex-col items-center justify-center">
              The Walacor Platform is structured as follows:
              <div className="flex items-center gap-1 flex-row">
                <FontAwesomeIcon icon={faUser} className="text-blue-800 mr-1" /> <strong>Client</strong> →
                <FontAwesomeIcon icon={faCode} className="text-blue-800 mx-1" /> <strong>Hooks</strong> →
                <FontAwesomeIcon icon={faDatabase} className="text-blue-800 mx-1" /> <strong>Walacor</strong>
              </div>
            </p>
            <div />
          </div>
        </div>
      ),
    },
    "/dashboard/verification": {
      title: "File Verification",
      description: "Use this feature to verify file metadata against existing records in the Walacor system. This helps ensure the file's uniqueness and prevents duplicate uploads.",
      additionalInfo: (
        <div className="text-blue-800 mt-2">
          <p>If a file is already in the system, you’ll receive a message indicating the duplicate. Try uploading a different or modified file to continue.</p>
          <p className="mt-2">
            <FontAwesomeIcon icon={faInfoCircle} className="mr-1" /> Tip: Only upload unique files to maintain data integrity and avoid redundancy.
          </p>
        </div>
      ),
    },
  };

  const currentPathInfo = infoTabs[pathname as string];

  return (
    currentPathInfo && (
      <div className="relative w-full">
        <div className="bg-blue-100 h-16 p-4 shadow-md flex items-center space-x-4 cursor-pointer" onClick={() => setIsHelpVisible(!isHelpVisible)}>
          <div className="flex items-center justify-center">
            <FontAwesomeIcon icon={faInfoCircle} className="text-blue-800 text-xl" />
          </div>
          <h3 className="text-lg whitespace-nowrap font-semibold text-blue-900">{currentPathInfo.title}</h3>
          <div className="w-full flex justify-end">
            {isHelpVisible ? (
              <button className="text-blue-800 text-xl focus:outline-none" onClick={() => setIsHelpVisible(false)}>
                <FontAwesomeIcon icon={faTimes} className="w-8 text-sm" />
              </button>
            ) : (
              <FontAwesomeIcon icon={faChevronDown} className="text-blue-800 text-sm w-8" />
            )}
          </div>
        </div>

        <AnimatePresence>
          {isHelpVisible && (
            <motion.div className="absolute bg-blue-100 p-4 shadow-lg rounded-b-lg z-50 w-full left-0" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.1 }}>
              <p className="text-blue-800">{currentPathInfo.description}</p>
              {currentPathInfo.additionalInfo}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    )
  );
};

export default HelpDropdown;
