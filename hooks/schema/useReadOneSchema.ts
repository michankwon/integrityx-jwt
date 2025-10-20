import { useState, useCallback, useEffect } from "react";
import axios from "axios";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";
import { BlogData } from "@/schemas/blogSchema";
import { useRefetch } from "@/context/RefetchContext";

const useReadOneSchema = (id: string, etid: number) => {
  const [response, setResponse] = useState<BlogData | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const token = useAuthenticatedToken();
  const { shouldRefetch, resetRefetch } = useRefetch();

  const readOneSchema = useCallback(async () => {
    if (!token) return;

    setLoading(true);
    try {
      const res = await axios.post(
        `${String(
          process.env.NEXT_PUBLIC_EC2_WALACOR
        )}/api/query/get?fromSummary=true`,
        { id },
        {
          headers: {
            ETId: etid,
            Authorization: `${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      const data = res.data?.data || [];
      const latestRecord = data.reduce(
        (latest: BlogData | null, current: BlogData) => {
          if (!latest || current.UpdatedAt > latest.UpdatedAt) {
            return current;
          }
          return latest;
        },
        null
      );

      setError(null);
      setResponse(latestRecord);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [token, id, etid]);

  useEffect(() => {
    if (token) {
      readOneSchema();
    }
  }, [readOneSchema, token]);

  useEffect(() => {
    if (shouldRefetch) {
      readOneSchema().then(resetRefetch);
    }
  }, [shouldRefetch, readOneSchema, resetRefetch]);

  return { response, error, loading, readOneSchema };
};

export default useReadOneSchema;
