import { useState, useCallback, useRef } from "react";
import { useUser } from "@clerk/nextjs";
import { useWalacorUser } from "@/hooks/user/useWalacorUser";
import usePostSchema from "../schema/usePostSchema";
import { useCreateSchema } from "@/hooks/schema/useCreateSchema";
import axios from "axios";
import { profileSchema, ProfileData } from "@/schemas/profileSchema";
import { blogSchema } from "@/schemas/blogSchema";
import { roleSchema } from "@/schemas/roleSchema";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";

export const useAddUser = () => {
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);
  const isAdding = useRef(false);
  const { user: clerkUser } = useUser();
  const { data: userData, isFetched } = useWalacorUser();
  const { postSchema, response: postResponse, error: postError } = usePostSchema(Number(process.env.NEXT_PUBLIC_WALACOR_PROFILE_ETID));
  const { createSchema } = useCreateSchema();
  const token = useAuthenticatedToken();

  const cooldownPeriod = 5000;
  const maxRetries = 3;

  const confirmUserInDB = async (userId: string): Promise<boolean> => {
    try {
      const res = await axios.post(
        `${String(process.env.NEXT_PUBLIC_EC2_WALACOR)}/api/query/get`,
        {},
        {
          headers: {
            ETId: Number(process.env.NEXT_PUBLIC_WALACOR_PROFILE_ETID),
            Authorization: `${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      return res.data?.data.some((user: ProfileData) => user.userId === userId) || false;
    } catch {
      return false;
    }
  };

  const createAllSchemas = async () => {
    try {
      await createSchema(Number(process.env.NEXT_PUBLIC_WALACOR_BLOG_ETID), blogSchema);
      await createSchema(Number(process.env.NEXT_PUBLIC_WALACOR_PROFILE_ETID), profileSchema);
      await createSchema(Number(process.env.NEXT_PUBLIC_WALACOR_ROLE_ETID), roleSchema);
    } catch (err) {
      setError(new Error("Failed to create required schemas"));
      throw err;
    }
  };

  const addUser = useCallback(async () => {
    if (!clerkUser || isAdding.current) return;

    isAdding.current = true;
    setLoading(true);

    await createAllSchemas();

    try {
      const userExistsInDB = await confirmUserInDB(clerkUser.id);
      if (userExistsInDB) {
        setLoading(false);
        return;
      }

      const payload: ProfileData = {
        userId: clerkUser.id,
        firstName: clerkUser.firstName || "First",
        lastName: clerkUser.lastName || "Last",
        userRole: "Viewer",
      };

      let attempt = 0;
      let userAdded = false;

      while (attempt < maxRetries && !userAdded) {
        if (attempt > 0) {
          await new Promise((resolve) => setTimeout(resolve, cooldownPeriod));
        }

        await postSchema(payload);

        if (postError) {
          setError(postError);
          break;
        }

        userAdded = await confirmUserInDB(clerkUser.id);

        if (!userAdded) attempt++;
      }

      if (!userAdded) {
        setError(new Error("Failed to add user after maximum retries"));
      }
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
      isAdding.current = false;

      if (!userData) {
        window.location.reload();
      }
    }
  }, [clerkUser, postSchema, postError, createSchema]);

  return { response: postResponse, error, loading, addUser };
};
