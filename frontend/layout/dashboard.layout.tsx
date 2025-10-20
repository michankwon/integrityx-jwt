"use client";

import "../app/globals.css";
import React, { ReactNode, useEffect } from "react";
import DefaultLayout from "./default.layout";
import { useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import Sidebar from "@/components/Sidebar";
import { useWalacorUser } from "@/hooks/user/useWalacorUser";
import LoadingOverlay from "@/components/LoadingOverlay";
import { useAddUser } from "@/hooks/user/useAddUser";

export default function DashboardLayout({ children }: { children?: ReactNode }) {
  const params = useParams();
  const { data, loading, isFetched } = useWalacorUser();
  const { addUser, loading: addUserLoading } = useAddUser();

  useEffect(() => {
    if (isFetched && !data) {
      addUser();
    }
  }, [isFetched, data, addUser]);

  return (
    <>
      <LoadingOverlay isVisible={addUserLoading} />
      <DefaultLayout>
        <div className="flex flex-col sm:flex-row max-w-9 bg-secondary z-20">
          <div className="fixed left-0 z-20">
            <Sidebar />
          </div>
          <div className="container-max bg-muted sm:py-12 min-h-screen w-full flex justify-center items-start relative">
            <AnimatePresence>
              <motion.div key={String(params?.path)} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.25 }}>
                {children}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
        <section className="w-full py-12 md:py-24 lg:py-32 bg-white">
          <div className="container grid items-center justify-center gap-4 px-4 text-center md:px-6">
            <div className="space-y-3">
              <h2 className="text-3xl font-semibold tracking-tighter md:text-4xl/tight">A demonstration of the Walacor Platform</h2>
              <p className="mx-auto max-w-[600px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Our platform is designed with auditability, transparency, and security in mind. We use the latest technologies to ensure that your data is safe and secure. Use this SDK to interface with some of the features of our platform.
              </p>
            </div>
          </div>
        </section>
      </DefaultLayout>
    </>
  );
}
