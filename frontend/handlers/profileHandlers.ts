import { ProfileData } from "@/schemas/profileSchema";

export const filterProfilesByUserId = (
  profiles: ProfileData[],
  userId?: string
): ProfileData | null => {
  return (
    profiles.find((profile: ProfileData) => profile.userId === userId) || null
  );
};
