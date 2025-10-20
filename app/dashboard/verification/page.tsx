"use client";

import React from "react";
import DashboardLayout from "@/layout/dashboard.layout";
import SubDashboardLayout from "@/layout/subdashboard.layout";
import FileVerificationComponent from "@/components/FileVerificationComponent";

const VerificationPage: React.FC = () => {
  return (
    <DashboardLayout>
      <SubDashboardLayout>
        <FileVerificationComponent />
      </SubDashboardLayout>
    </DashboardLayout>
  );
};

export default VerificationPage;
