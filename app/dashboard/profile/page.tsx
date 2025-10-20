"use client";

import React, { useState, useEffect } from "react";
import DashboardLayout from "@/layout/dashboard.layout";
import Button from "@/components/single/Button";
import Input from "@/components/single/Input";
import Dropdown from "@/components/single/Dropdown";
import { useClerk } from "@clerk/nextjs";
import Link from "next/link";
import { toast } from "react-hot-toast";
import { successToastStyle, errorToastStyle, loadingToastStyle } from "@/styles/toastStyles";
import { ProfileData } from "@/schemas/profileSchema";
import { useUpdateSchema } from "@/hooks/schema/useUpdateSchema";
import { useReadSchemas } from "@/hooks/schema/useReadSchemas";
import { RoleData } from "@/schemas/roleSchema";
import SubDashboardLayout from "@/layout/subdashboard.layout";
import { useWalacorUser } from "@/hooks/user/useWalacorUser";

const Profile = () => {
  const { data: userData, error, loading: userLoading, isFetched, refetch } = useWalacorUser();
  const { signOut } = useClerk();
  const { updateRecord, loading: updatingUser, error: updateError } = useUpdateSchema(Number(process.env.NEXT_PUBLIC_WALACOR_PROFILE_ETID));
  const { data: availableRoles, readSchemas } = useReadSchemas(Number(process.env.NEXT_PUBLIC_WALACOR_ROLE_ETID));

  const [firstName, setFirstName] = useState("Fetching...");
  const [lastName, setLastName] = useState("Fetching...");
  const [selectedRole, setSelectedRole] = useState<string>("");
  const [isUpdated, setIsUpdated] = useState(false);

  useEffect(() => {
    if (isFetched && userData) {
      setFirstName(userData.firstName || "");
      setLastName(userData.lastName || "");
      setSelectedRole(userData.userRole || "");
    }
    readSchemas();
  }, [isFetched, userData, error, readSchemas]);

  const handleRoleChange = (selectedRole: string) => {
    setSelectedRole(selectedRole);
    setIsUpdated(true);
  };

  const handleUpdate = async () => {
    if (!userData) return;
    toast.loading("Updating profile...", loadingToastStyle);
    try {
      const updatedUserData: Partial<ProfileData> = {
        UID: userData.UID,
        firstName,
        lastName,
        userRole: selectedRole,
      };

      await updateRecord(updatedUserData);

      toast.dismiss();
      toast.success("Profile updated successfully!", successToastStyle);
      setIsUpdated(false);

      await refetch();
    } catch (error) {
      toast.dismiss();
      toast.error("Failed to update profile", errorToastStyle);
      console.error("Failed to update profile", error);
    }
  };

  const handleSignOut = async () => {
    sessionStorage.clear();
    await signOut();
    window.location.href = "/";
  };

  return (
    <DashboardLayout>
      <SubDashboardLayout>
        <div className="w-full mx-auto p-8">
          <h1 className="text-3xl font-semibold mb-6 text-center">Profile</h1>
          <p className="text-gray-600 mb-6 text-center">Walacor allows us to create profile data structures for our users. This is a simple example of how you can edit and update your profile data.</p>
          <div className="space-y-4 bg-white p-6 rounded-lg shadow-lg mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">First Name</label>
              <Input
                type="text"
                value={firstName}
                onChange={(e) => {
                  setFirstName(e.target.value);
                  setIsUpdated(true);
                }}
                className={`mt-1 block w-full p-2 border border-gray-300 ${userLoading ? "animate-pulse bg-gray-200" : ""}`}
                disabled={userLoading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Last Name</label>
              <Input
                type="text"
                value={lastName}
                onChange={(e) => {
                  setLastName(e.target.value);
                  setIsUpdated(true);
                }}
                className={`mt-1 block w-full p-2 border border-gray-300 ${userLoading ? "animate-pulse bg-gray-200" : ""}`}
                disabled={userLoading}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Role</label>
              <Dropdown
                value={selectedRole}
                onChange={handleRoleChange}
                placeholder={"Select Role"}
                options={(availableRoles as unknown as RoleData[])?.map((role: RoleData) => role.roleName + " (" + role.scope + ")") || ["Loading..."]}
                className="mt-1 block w-full p-2 border text-black border-gray-300"
              />
              <Link href="/dashboard/role" className="mt-4 text-xs text-gray-500 cursor-pointer hover:underline">
                Want to add role?
              </Link>
            </div>
            <div className="mt-6">
              <Button className={`bg-primary text-white w-full`} onClick={handleUpdate} disabled={!isUpdated || updatingUser || userLoading}>
                {updatingUser ? "Updating..." : "Update Profile"}
              </Button>
              {updateError && <p className="text-red-500 mt-2">Error updating profile: {updateError.message}</p>}
            </div>
            <div className="mt-6">
              <Button className="bg-red-500 text-white w-full" onClick={handleSignOut}>
                Sign out
              </Button>
            </div>
          </div>
        </div>
      </SubDashboardLayout>
    </DashboardLayout>
  );
};

export default Profile;
