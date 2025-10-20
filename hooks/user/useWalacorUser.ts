import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { useRecoilState } from "recoil";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";
import { useUser } from "@clerk/nextjs";
import { userState, userFetched } from "@/recoil/atoms";
import { ProfileData } from "@/schemas/profileSchema";

export const useWalacorUser = () => {
  const { user: clerkUser } = useUser();
  const [data, setData] = useRecoilState<ProfileData | null>(userState);
  const [isFetched, setIsFetched] = useRecoilState(userFetched);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);
  const token = useAuthenticatedToken();

  const fetchUser = useCallback(async () => {
    if (!clerkUser) return;

    setLoading(true);
    setError(null);

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
        const userEntries = res.data.data.filter((user: ProfileData) => user.userId === clerkUser.id).sort((a: ProfileData, b: ProfileData) => Number(b.CreatedAt) - Number(a.CreatedAt));

        setData(userEntries[0] || null);
      } else {
        setError(new Error("Unexpected response structure or no data returned"));
      }
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
      setIsFetched(true);
    }
  }, [clerkUser, token]);

  useEffect(() => {
    if (clerkUser && token && !isFetched) {
      fetchUser();
    }
  }, [clerkUser, token, isFetched, fetchUser]);

  return { data, error, loading, isFetched, refetch: fetchUser };
};
