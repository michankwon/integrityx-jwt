"use client";

import DashboardLayout from "@/layout/dashboard.layout";
import SubDashboardLayout from "@/layout/subdashboard.layout";

const DashboardHome = () => {
  return (
    <DashboardLayout>
      <SubDashboardLayout>
        <div className="container mx-auto py-12">
          <h1 className="text-4xl font-semibold mb-4 text-center">Welcome to Walacor Dashboard</h1>
          <p className="text-gray-600 mb-6 text-center">Manage your data posts, profile, and settings all in one place.</p>

          <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
            <h2 className="text-2xl font-semibold mb-4">About Walacor</h2>
            <p className="text-gray-700 mb-4">
              Walacor is your ultimate data companion. Our platform provides powerful features and customizable schemas to enhance your data experience. Whether you are a beginner or experienced with data, Walacor offers the tools you need
              to create, manage, and grow your data. We demonstrate this with this blogging application.
            </p>
            <p className="text-gray-700 mb-4">With Walacor, you can:</p>
            <ul className="list-disc list-inside text-gray-700 mb-4">
              <li>Create and manage data effortlessly</li>
              <li>Customize the data schemas with ease</li>
              <li>Analyze your data with detailed granularities and audit histories</li>
              <li>Interact with your data through integrated features</li>
              <li>Unparalleled data security and privacy</li>
            </ul>
            <p className="text-gray-700">Explore the dashboard to get started and make the most of Walacors features!</p>
          </div>
        </div>
      </SubDashboardLayout>
    </DashboardLayout>
  );
};

export default DashboardHome;
