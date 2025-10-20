import { useState, useCallback } from "react";
import axios from "axios";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";
import { FileData } from "@/types/schema";

export const useStoreFile = (fileData: FileData | null) => {
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const token = useAuthenticatedToken();

  const storeFile = useCallback(async () => {
    if (!token || !fileData) return;

    setLoading(true);

    try {
      const res = await axios.post(`${process.env.NEXT_PUBLIC_EC2_WALACOR}/api/v2/files/store`, fileData, {
        headers: {
          Authorization: `${token}`,
          "Content-Type": "application/json",
        },
      });

      if (res.data) {
        setResult(res.data);
        setError(null);
      } else {
        setError(new Error("Unexpected response structure"));
      }
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [token, fileData]);

  return { result, error, loading, storeFile };
};
