"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Button from "@/components/single/Button";
import { usePathname } from "next/navigation";
import { useRecoilState } from "recoil";
import { bottomPopupVisibleState } from "@/recoil/atoms";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faQuestionCircle } from "@fortawesome/free-solid-svg-icons";

const BottomPopup: React.FC = () => {
  const pathname = usePathname();
  const [isVisible, setIsVisible] = useState(false);
  const [showPopup, setShowPopup] = useRecoilState(bottomPopupVisibleState);

  const infoTabs = {
    "/": {
      title: "Welcome to Walacor",
      description: "Walacor is a platform that allows you to manage your data effectively. This blog kit is a demonstration of the platform's capabilities.",
      actionLabel: "Get Started",
      actionUrl: "/dashboard",
    },
    "/dashboard": {
      title: "Have you created a schema yet?",
      description: "Schemas are essential to get started managing your data. Create a schema to define the structure of your data and start managing your data effectively.",
      actionLabel: "Create Schemas",
      actionUrl: "/dashboard/schemas",
    },
    "/dashboard/schemas": {
      title: "Select a schema to view data",
      description:
        "You need to create a schema to manage your data effectively. Schemas define the structure of your data and allow you to validate data against the schema. Select a schema then scroll down and click on the create schema button.",
      actionLabel: "",
      actionUrl: "/dashboard/schemas",
    },
    "/dashboard/hooks": {
      title: "Explore the Hooks",
      description: "Hooks are a powerful feature in Walacor that allows you to interact with the platform and extend its capabilities. Hooks are used to interact with the data platform.",
      actionLabel: "",
      actionUrl: "/dashboard/hooks",
    },
    "/dashboard/create": {
      title: "Create a new blog",
      description: "Assuming the Blog Schema has been created successfully, you can now create and edit blogs that will be validated against the schema to ensure data integrity.",
      actionLabel: "",
      actionUrl: "/dashboard/create",
    },
    "/dashboard/my-blogs": {
      title: "Have you created a blog yet?",
      description: "Manage your blog content using this system. Create, update, and delete blog posts while utilizing Walacor's features for content validation and audit trails.",
      actionLabel: "Create Blog",
      actionUrl: "/dashboard/create",
    },
    "/dashboard/profile": {
      title: "Update your profile",
      description: "The profile management system allows you to update your personal information, such as your name and role, and manage your data in Walacor. Try changing your role to see what features are available to you.",
      actionLabel: "",
      actionUrl: "/dashboard/profile",
    },
    "/dashboard/role": {
      title: "Create user roles",
      description: "Create user roles within the Walacor platform. Define scopes such as AdminAccess, ReadWrite, or ReadOnly to control access to different areas of the system.",
      actionLabel: "",
      actionUrl: "/dashboard/roles",
    },
    "/read-the-blog": {
      title: "Read the blog",
      description: "This section shows off the blog posts that have been created and published using the Walacor platform. You can view the content in your dashboard.",
      actionLabel: "",
      actionUrl: "/read-the-blog",
    },
    "/dashboard/verification": {
      title: "Verify File Uniqueness",
      description: "Use the file verification feature to ensure that the files you upload are unique. This helps maintain data integrity by avoiding duplicate entries.",
      actionLabel: "Learn More",
      actionUrl: "/dashboard/verify-help",
    },
  };

  const currentInfo = infoTabs[pathname as keyof typeof infoTabs];

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (currentInfo && showPopup) {
        setIsVisible(true);
      }
    }, 2000);

    return () => clearTimeout(timeoutId);
  }, [currentInfo, showPopup]);

  const handleAction = () => {
    if (currentInfo?.actionUrl) {
      window.location.href = currentInfo.actionUrl;
    }
  };

  const onDismiss = () => {
    setIsVisible(false);
    setShowPopup(false);
  };

  return (
    <>
      <AnimatePresence>
        {isVisible && currentInfo && (
          <>
            <motion.div onClick={onDismiss} className="fixed inset-0 bg-black bg-opacity-50 z-40" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }} />

            <motion.div
              className="fixed inset-x-0 bottom-0 bg-blue-100 p-6 shadow-lg flex justify-between items-center z-50"
              initial={{ opacity: 0, y: 100 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 100 }}
              transition={{ duration: 0.5 }}
            >
              <div>
                <h3 className="text-lg font-semibold text-blue-900">{currentInfo.title}</h3>
                <p className="text-blue-800">{currentInfo.description}</p>
              </div>
              <div className="space-x-4 flex w-full justify-end">
                {currentInfo.actionLabel && (
                  <Button onClick={handleAction} className="bg-blue-500 text-white px-4 py-2 rounded">
                    {currentInfo.actionLabel}
                  </Button>
                )}
                <Button onClick={onDismiss} className="bg-transparent text-blue-500 px-4 py-2 border border-blue-500 rounded">
                  Dismiss
                </Button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {!showPopup && (
        <Button
          onClick={() => {
            setIsVisible(true);
            setShowPopup(true);
          }}
          className="fixed bottom-4 right-4 z-20 bg-blue-100 text-blue-900 rounded-full p-3 shadow-lg"
        >
          <FontAwesomeIcon icon={faQuestionCircle} />
        </Button>
      )}
    </>
  );
};

export default BottomPopup;
