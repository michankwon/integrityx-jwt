import CenterLayout from "@/layout/center.layout";
import { SignIn } from "@clerk/nextjs";

export default function Page() {
  return (
    <CenterLayout>
      <SignIn />
    </CenterLayout>
  );
}
