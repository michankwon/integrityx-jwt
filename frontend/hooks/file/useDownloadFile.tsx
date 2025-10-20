import { useState, useCallback } from "react";
import axios from "axios";
import useAuthenticatedToken from "../auth/useAuthenticatedToken";

export const useDownloadFile = () => {
  const [downloadResult, setDownloadResult] = useState(null);
  const [downloadError, setDownloadError] = useState<any>(null);
  const [downloadLoading, setDownloadLoading] = useState(false);

  const token = useAuthenticatedToken();

  const downloadFile = useCallback(
    async (UID: string) => {
      setDownloadLoading(true);
      try {
        const response = await axios.post(`${process.env.NEXT_PUBLIC_EC2_WALACOR}/api/v2/files/download`, JSON.stringify({ UID }), {
          headers: {
            Authorization: `${token}`,
            "Content-Type": "application/json",
          },
          responseType: "blob",
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `file_${UID}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();

        setDownloadResult(response.data);
        setDownloadError(null);
      } catch (error) {
        setDownloadError(error);
      } finally {
        setDownloadLoading(false);
      }
    },
    [token]
  );

  return { downloadResult, downloadError, downloadLoading, downloadFile };
};
