import { useState, useCallback } from "react";
import axios from "axios";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";
import { ProfileData } from "@/schemas/profileSchema";

export const useGetUser = () => {
  const [data, setData] = useState<ProfileData | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);
  const token = useAuthenticatedToken();

  const getUser = useCallback(
    async (filter: { userId?: string }) => {
      setLoading(true);

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

        if (res.data && res.data.success && Array.isArray(res.data.data)) {
          const filteredUser = res.data.data.find((user: ProfileData) => user.userId === filter.userId);

          setData(filteredUser || null);
        } else {
          setError(new Error("Unexpected response structure or no data returned"));
        }
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  return { data, error, loading, getUser };
};
