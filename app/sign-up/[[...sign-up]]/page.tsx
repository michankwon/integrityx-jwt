import CenterLayout from "@/layout/center.layout";
import { SignUp } from "@clerk/nextjs";

export default function Page() {
  return (
    <CenterLayout>
      <SignUp />
    </CenterLayout>
  );
}
