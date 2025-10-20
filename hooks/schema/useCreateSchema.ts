import { useState } from "react";
import axios from "axios";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";

export function useCreateSchema() {
  const token = useAuthenticatedToken();
  const [loading, setLoading] = useState(false);

  const createSchema = async (etid: number, schemaData: any) => {
    const schema = {
      ETId: 50,
      SV: 1,
      Schema: schemaData,
    };

    setLoading(true);
    try {
      const response = await axios.post(`${String(process.env.NEXT_PUBLIC_EC2_WALACOR)}/api/schemas/`, schema, {
        headers: {
          Authorization: `${token}`,
          ETId: etid,
          SV: 1,
        },
      });

      return response.data;
    } catch (error) {
      console.error("Error creating schema:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return { createSchema, loading };
}
