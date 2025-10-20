import { ProfileData } from "@/schemas/profileSchema";

export const checkUserConfiguration = async (userId: string, getUser: Function, setIsConfigured: Function, sessionConfigured: boolean) => {
  const userProfileData = await getUser({ userId });

  if (!userProfileData) {
    throw new Error("User profile data is not available");
  }

  const profile = userProfileData as ProfileData;

  if (sessionConfigured === true || profile?.isConfigured) {
    setIsConfigured(true);
    return { isConfigured: true, profile };
  }

  return { isConfigured: false, profile };
};
