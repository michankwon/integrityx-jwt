"use client";

import { useRecoilValue } from "recoil";
import { tokenState } from "@/recoil/atoms";
import { useAuthentication } from "./useAuthentication";
import { useEffect } from "react";

const useAuthenticatedToken = () => {
  const { login } = useAuthentication();
  const token = useRecoilValue(tokenState);

  useEffect(() => {
    if (!token) {
      login();
    }
  }, [token, login]);

  return token;
};

export default useAuthenticatedToken;
