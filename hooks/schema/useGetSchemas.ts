import axios from "axios";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";

export function useGetSchemas() {
  const token = useAuthenticatedToken();

  const getSchemas = async (etid: number) => {
    try {
      const response = await axios.get(`${String(process.env.NEXT_PUBLIC_EC2_WALACOR)}/api/schemas/${etid}`, {
        headers: {
          Authorization: `${token}`,
          ETId: etid,
        },
      });

      return response.data;
    } catch (error) {
      console.error("Error fetching schemas:", error);
      throw error;
    }
  };

  return { getSchemas };
}
