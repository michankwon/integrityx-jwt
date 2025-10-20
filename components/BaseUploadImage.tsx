/* eslint-disable @next/next/no-img-element */
"use client";

import React, { useState, ChangeEvent, useRef } from "react";
import axios from "axios";
import BaseLoader from "./BaseLoader";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeftRotate, faCheck, faX, faInfoCircle } from "@fortawesome/free-solid-svg-icons";
import { useVerifyFileMetadata } from "@/hooks/file/useVerifyFileMetadata";
import { Tooltip } from "./single/Tooltip";

interface BaseUploadImageProps {
  onUpload: (url: string) => void;
}

const BaseUploadImage: React.FC<BaseUploadImageProps> = ({ onUpload }) => {
  const [useVerification, setUseVerification] = useState<boolean>(false);
  const [message, setMessage] = useState<string>("");
  const [isError, setIsError] = useState<boolean>(false);
  const [errorSolution, setErrorSolution] = useState<string>("");
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isTimedOut, setIsTimedOut] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);

  const { result: verificationResult, error: verificationError, fileExists, loading: verificationLoading, verifyMetadata } = useVerifyFileMetadata();

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] ?? null;
    setFile(selectedFile);

    setUploadedImageUrl("");
    setMessage("");
    setIsError(false);
    setErrorSolution("");
    setIsLoading(true);
    setIsTimedOut(false);

    if (selectedFile) {
      const timeoutId = setTimeout(() => {
        setIsTimedOut(true);
        setIsLoading(false);
        setMessage("Upload timed out. Please try again.");
      }, 10000);

      if (useVerification) {
        await verifyMetadata(selectedFile);

        if (fileExists) {
          clearTimeout(timeoutId);
          setMessage("This image has already been used. Please upload an original image.");
          setErrorSolution("Consider using a different or modified image to ensure uniqueness.");
          setIsError(true);
          setIsLoading(false);
          return;
        }

        if (verificationError) {
          clearTimeout(timeoutId);
          setMessage(verificationError);
          setIsError(true);
          setIsLoading(false);
          return;
        }
      }

      const reader = new FileReader();
      reader.onloadend = async () => {
        const image = reader.result as string;
        const imageName = `image-${Date.now()}`;
        try {
          const response = await axios.post("/api/uploadImage", {
            imageName,
            image,
          });

          clearTimeout(timeoutId);
          setMessage("Image uploaded successfully!");
          setIsError(false);
          setErrorSolution("");
          setUploadedImageUrl(response.data.imageUrl);
          onUpload(response.data.imageUrl);
        } catch (error: any) {
          clearTimeout(timeoutId);
          let errorMessage = "Failed to upload image.";
          let solutionMessage = "";

          if (error.response && error.response.status) {
            const status = error.response.status;
            if (status === 413) {
              errorMessage = "The image is too large to upload.";
              solutionMessage = `
                The image is too large. Try resizing it using:
                <ul>
                  <li>
                    TinyJPG: <a href="https://tinyjpg.com/" target="_blank" rel="noopener noreferrer" style="color:blue;">https://tinyjpg.com/</a>
                  </li>
                  <li>
                    Image Resizer: <a href="https://imageresizer.com/" target="_blank" rel="noopener noreferrer" style="color:blue;">https://imageresizer.com/</a>
                  </li>
                </ul>`;
            } else if (status === 400) {
              errorMessage = error.response.data.error || errorMessage;
              if (errorMessage.includes("Unsupported file type")) {
                solutionMessage = "Please upload a JPEG, PNG, or GIF image.";
              } else if (errorMessage.includes("not a valid image")) {
                solutionMessage = "The uploaded file is not a valid image. Please check the file and try again.";
              }
            } else {
              solutionMessage = "Please try again or contact support if the problem persists.";
            }
          }
          setMessage(errorMessage);
          setIsError(true);
          setErrorSolution(solutionMessage);
          console.error("Error uploading image:", error);
        } finally {
          setIsLoading(false);
        }
      };
      reader.readAsDataURL(selectedFile);
    } else {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (file) {
      handleFileChange({
        target: { files: [file] },
      } as unknown as ChangeEvent<HTMLInputElement>);
    }
  };

  return (
    <div>
      <h2>Upload Image to Blog</h2>

      <div className="flex items-center mb-4">
        <label className="mr-2 text-sm font-semibold flex items-center">
          Use Verification System
          <span className="text-gray-500">
            <Tooltip
              text="
              Enable this to check if the file has already been uploaded. Useful for maintaining data integrity in the Walacor platform.
              This feature checks the metadata of the file to see if it has been uploaded before. If the file has been uploaded, you will be notified to upload a new image. Note: This feature may take longer to upload images as it performs additional checks."
            />
          </span>
        </label>
        <input type="checkbox" checked={useVerification} onChange={(e) => setUseVerification(e.target.checked)} className="toggle-checkbox" />
      </div>

      <input id="file-upload" type="file" accept="image/*" onChange={handleFileChange} ref={fileInputRef} />

      {isLoading && (
        <div className="flex gap-1 items-center">
          <span>Loading...</span>
          <BaseLoader />
        </div>
      )}

      {message && !isLoading && (
        <div style={{ color: isError ? "red" : "green" }}>
          <p>
            {isError ? <FontAwesomeIcon className="scale-75" icon={faX} /> : <FontAwesomeIcon icon={faCheck} />} {message}
          </p>
          {isError && <div dangerouslySetInnerHTML={{ __html: errorSolution }} style={{ color: "black" }} />}
          {isTimedOut && (
            <div>
              <button
                onClick={handleRetry}
                style={{
                  backgroundColor: "gray",
                  color: "white",
                  border: "none",
                  padding: "5px 10px",
                  cursor: "pointer",
                  marginTop: "10px",
                  display: "flex",
                  alignItems: "center",
                  borderRadius: "5px",
                }}
              >
                <FontAwesomeIcon icon={faArrowLeftRotate} />
                <span className="ml-1">Try Again</span>
              </button>
            </div>
          )}
        </div>
      )}
      {uploadedImageUrl && !isLoading && (
        <div>
          <img src={uploadedImageUrl} alt="Uploaded Image" style={{ maxWidth: "100%", height: "auto" }} />
        </div>
      )}
    </div>
  );
};

export default BaseUploadImage;
