import React, { useState } from "react";
import { useVerifyFileMetadata } from "@/hooks/file/useVerifyFileMetadata";
import { useStoreFile } from "@/hooks/file/useStoreFile";
import { FileData } from "@/types/schema";
import Button from "@/components/single/Button";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { useDownloadFile } from "@/hooks/file/useDownloadFile";

const FileVerificationComponent = () => {
  const [file, setFile] = useState<File | null>(null);
  const [fileData, setFileData] = useState<FileData | null>(null);
  const [copiedText, setCopiedText] = useState<string | null>(null);
  const { downloadResult, downloadError, downloadLoading, downloadFile } = useDownloadFile();

  const handleDownloadFile = () => {
    if (fileData?.fileInfo?.file?.UID) {
      downloadFile(fileData.fileInfo.file.UID);
    }
  };

  const { result: verificationResult, error: verificationError, loading: verificationLoading, verifyMetadata } = useVerifyFileMetadata();
  const { result: storageResult, error: storageError, loading: storageLoading, storeFile } = useStoreFile(fileData);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const selectedFile = event.target.files[0];
      setFile(selectedFile);
    }
  };

  const handleVerifyMetadata = async () => {
    if (file) {
      await verifyMetadata(file);
    }
  };

  const handlePrepareFileData = () => {
    if (verificationResult && typeof verificationResult === "object" && verificationResult.data && verificationResult.data.fileInfo) {
      const { fileInfo } = verificationResult.data;

      const preparedFileData: FileData = {
        fileInfo: {
          file: {
            UID: fileInfo.file.UID || "",
            size: fileInfo.file.size || 0,
            Status: fileInfo.file.Status || "received",
            FH: fileInfo.file.FH || "",
          },
          fileSignature: fileInfo.fileSignature || "",
          fileHash: fileInfo.fileHash || "",
          totalEncryptedChunkFile: fileInfo.totalEncryptedChunkFile || 0,
        },
      };

      setFileData(preparedFileData);
    } else {
      console.warn("Verification result does not contain expected file information.");
    }
  };

  const handleStoreFile = async () => {
    if (fileData) {
      await storeFile();
    }
  };

  const handleCopy = (text: string) => {
    setCopiedText(text);
    setTimeout(() => setCopiedText(null), 2000);
  };

  return (
    <div className="container mx-auto py-12">
      <h1 className="text-4xl font-semibold mb-6 text-center">File Verification and Storage</h1>
      <p className="text-gray-600 mb-6 text-center">Follow the steps below to securely verify, prepare, and store your file.</p>

      <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
        <h2 className="text-2xl font-semibold mb-4">Step 1: Verify Metadata</h2>
        <p className="text-gray-700 mb-4">
          Verifying file metadata ensures that the file structure is correct and that the content is untampered. This process checks for file authenticity and provides a unique identifier for future reference.
        </p>

        <input type="file" onChange={handleFileChange} className="mb-4" />
        <Button onClick={handleVerifyMetadata} disabled={!file || verificationLoading} className="w-full mb-4 bg-primary text-white">
          {verificationLoading ? "Verifying..." : "Verify Metadata"}
        </Button>

        {verificationError && <p style={{ color: "red" }}>Verification Error: You may have already stored this file.</p>}

        {verificationResult && (
          <CopyToClipboard text={JSON.stringify(verificationResult, null, 2)} onCopy={() => handleCopy("verification")}>
            <div className="relative cursor-pointer bg-gray-100 p-4 rounded text-sm max-h-40 overflow-y-auto mt-4">
              <h3 className="text-lg font-semibold mb-2">Verification Result:</h3>
              <pre>{JSON.stringify(verificationResult, null, 2)}</pre>
              <button className="absolute top-2 right-2 px-2 py-1 hover:opacity-50 text-gray-500 rounded text-xs">{copiedText === "verification" ? "Copied" : "Copy"}</button>
            </div>
          </CopyToClipboard>
        )}
      </div>

      {verificationResult && (
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h2 className="text-2xl font-semibold mb-4">Step 2: Prepare File Data</h2>
          <p className="text-gray-700 mb-4">After verifying the metadata, this step prepares the file data into a structured format that can be stored securely.</p>
          <Button onClick={handlePrepareFileData} disabled={!verificationResult || verificationLoading} className="w-full mb-4 bg-primary text-white">
            Prepare File Data
          </Button>

          {fileData && (
            <CopyToClipboard text={JSON.stringify(fileData, null, 2)} onCopy={() => handleCopy("fileData")}>
              <div className="relative cursor-pointer bg-gray-100 p-4 rounded text-sm max-h-40 overflow-y-auto mt-4">
                <h3 className="text-lg font-semibold mb-2">Prepared File Data:</h3>
                <pre>{JSON.stringify(fileData, null, 2)}</pre>
                <button className="absolute top-2 right-2 px-2 py-1 hover:opacity-50 text-gray-500 rounded text-xs">{copiedText === "fileData" ? "Copied" : "Copy"}</button>
              </div>
            </CopyToClipboard>
          )}
        </div>
      )}

      {fileData && (
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h2 className="text-2xl font-semibold mb-4">Step 3: Store File</h2>
          <p className="text-gray-700 mb-4">In this final step, the prepared file data is securely stored. This step completes the process, ensuring that your file is accessible and organized within the system.</p>
          <Button onClick={handleStoreFile} disabled={!fileData || storageLoading} className="w-full mb-4 bg-primary text-white">
            {storageLoading ? "Storing..." : "Store File"}
          </Button>

          {storageResult && (
            <CopyToClipboard text={JSON.stringify(storageResult, null, 2)} onCopy={() => handleCopy("storage")}>
              <div className="relative cursor-pointer bg-gray-100 p-4 rounded text-sm max-h-40 overflow-y-auto mt-4">
                <h3 className="text-lg font-semibold mb-2">Storage Result:</h3>
                <pre>{JSON.stringify(storageResult, null, 2)}</pre>
                <button className="absolute top-2 right-2 px-2 py-1 hover:opacity-50 text-gray-500 rounded text-xs">{copiedText === "storage" ? "Copied" : "Copy"}</button>
              </div>
            </CopyToClipboard>
          )}
        </div>
      )}

      {fileData && (
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h2 className="text-2xl font-semibold mb-4">Step 4: Download File</h2>
          <p className="text-gray-700 mb-4">Click below to download the file to your device.</p>
          <Button onClick={handleDownloadFile} disabled={downloadLoading} className="w-full mb-4 bg-primary text-white">
            {downloadLoading ? "Downloading..." : "Download File"}
          </Button>
          {downloadError && <p style={{ color: "red" }}>Download Error: {(downloadError as Error)?.message}</p>}
        </div>
      )}
    </div>
  );
};

export default FileVerificationComponent;
