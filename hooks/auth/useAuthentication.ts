import axios from "axios";
import { useRecoilState } from "recoil";
import { tokenState } from "@/recoil/atoms";

export function useAuthentication() {
  const [token, setToken] = useRecoilState(tokenState);

  async function login() {
    try {
      const res = await axios.post(
        `${String(process.env.NEXT_PUBLIC_EC2_WALACOR)}/api/auth/login`,
        {
          userName: String(process.env.NEXT_PUBLIC_WALACOR_USERNAME),
          password: String(process.env.NEXT_PUBLIC_WALACOR_PASSWORD),
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      setToken(res.data.api_token);
    } catch (error) {
      console.error("Error logging in:", error);
    }
  }

  return { token, login };
}
