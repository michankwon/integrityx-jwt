import { useState, useCallback } from "react";
import axios from "axios";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";
import { FileVerificationResponse } from "@/types/schema";

export const useVerifyFileMetadata = () => {
  const [result, setResult] = useState<FileVerificationResponse | string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fileExists, setFileExists] = useState(false);
  const [loading, setLoading] = useState(false);
  const token = useAuthenticatedToken();

  const verifyMetadata = useCallback(
    async (file: File) => {
      if (!token || !file) return;

      const formData = new FormData();
      formData.append("file", file);

      setLoading(true);
      setFileExists(false);
      try {
        const res = await axios.post(`${process.env.NEXT_PUBLIC_EC2_WALACOR}/api/v2/files/verify`, formData, {
          headers: {
            Authorization: `${token}`,
            "Content-Type": "multipart/form-data",
          },
        });

        if (res.data) {
          setResult(res.data);
          setError(null);
        } else {
          setError("Unexpected response structure");
        }
      } catch (err) {
        if (axios.isAxiosError(err) && err.response?.status === 422) {
          setFileExists(true);
          setError("This file has already been used. Please upload a unique file.");
        } else {
          setError("An error occurred during verification. It is likely you have already verified this file, please try again with a new file.");
        }
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  return { result, error, fileExists, loading, verifyMetadata };
};
