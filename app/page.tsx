"use client";

import BaseBanner from "@/components/BaseBanner";
import BaseBlogCards from "@/components/BaseBlogCards";
import BaseFooter from "@/components/BaseFooter";
import DefaultLayout from "@/layout/default.layout";

export default function Home() {
  return (
    <DefaultLayout>
      <BaseBanner />
      <BaseBlogCards limit={3} />
      <BaseFooter />
    </DefaultLayout>
  );
}
