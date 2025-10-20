import { useState, useCallback, useEffect } from "react";
import axios from "axios";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";
import { BlogData } from "@/schemas/blogSchema";
import { useRefetch } from "@/context/RefetchContext";

const useReadSchemas = (etid: number) => {
  const [response, setResponse] = useState<BlogData[] | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const token = useAuthenticatedToken();
  const { shouldRefetch, resetRefetch } = useRefetch();

  const fetchSchemas = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.post(
        `${String(process.env.NEXT_PUBLIC_EC2_WALACOR)}/api/query/get?fromSummary=true`,
        {},
        {
          headers: {
            ETId: etid,
            Authorization: `${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      setResponse(res.data?.data);
      setError(null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [token, etid]);

  useEffect(() => {
    fetchSchemas();
  }, [fetchSchemas]);

  useEffect(() => {
    if (shouldRefetch) {
      fetchSchemas().then(resetRefetch);
    }
  }, [shouldRefetch, fetchSchemas, resetRefetch]);

  return { response, error, loading, fetchSchemas };
};

export default useReadSchemas;
