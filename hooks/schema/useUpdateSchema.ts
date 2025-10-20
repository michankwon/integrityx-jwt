import { useState } from "react";
import axios from "axios";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";
import { useRefetch } from "@/context/RefetchContext";
import { MainData } from "@/types/schema";

export function useUpdateSchema(etid: number) {
  const token = useAuthenticatedToken();

  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  const { triggerRefetch } = useRefetch();

  const updateRecord = async (data: MainData | Partial<MainData>) => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const response = await axios.post(
        `${String(process.env.NEXT_PUBLIC_EC2_WALACOR)}/api/envelopes/submit`,
        { Data: [data] },
        {
          headers: {
            Authorization: `${token}`,
            ETId: etid,
            "Content-Type": "application/json",
          },
        }
      );

      setResponse(response.data);
      triggerRefetch();

      return response.data;
    } catch (error) {
      console.error("Error updating record:", error);
      setError(error as Error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return { updateRecord, loading, response, error };
}
