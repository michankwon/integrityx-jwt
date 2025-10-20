"use client";

import React from "react";
import ContentManagement from "@/components/ContentManagement";
import DashboardLayout from "@/layout/dashboard.layout";
import SubDashboardLayout from "@/layout/subdashboard.layout";

const CreateBlog: React.FC = () => {
  return (
    <DashboardLayout>
      <SubDashboardLayout>
        <ContentManagement />
      </SubDashboardLayout>
    </DashboardLayout>
  );
};

export default CreateBlog;
