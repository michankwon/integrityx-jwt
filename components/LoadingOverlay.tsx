import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faDatabase } from "@fortawesome/free-solid-svg-icons";

const titles = ["Initializing Dashboard...", "Connecting to Server...", "Verifying Credentials...", "Loading User Data...", "Configuring Settings...", "Setting Up User...", "Getting Data...", "Almost Finished..."];

const LoadingOverlay: React.FC<{ isVisible: boolean }> = ({ isVisible }) => {
  const [titleIndex, setTitleIndex] = useState(0);

  useEffect(() => {
    if (!isVisible) return;

    const interval = setInterval(() => {
      setTitleIndex(Math.floor(Math.random() * titles.length));
    }, 4000);

    return () => clearInterval(interval);
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <motion.div className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex justify-center items-start z-50 p-8" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}>
      <motion.div className="bg-white p-8 rounded-lg shadow-lg text-center w-full max-w-lg" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} transition={{ duration: 0.3 }}>
        <div className="flex items-center justify-center mb-4">
          <FontAwesomeIcon icon={faDatabase} className="w-8 h-8 text-primary mr-3" />
          <h4 className="text-2xl text-gray-800 animate-pulse">{titles[titleIndex]}</h4>
          <svg className="animate-spin w-7 h-7 ml-1 text-primary mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 12h1.5M12 4v1.5M19.5 12H21M12 19.5V21M16.24 7.76l-1.06 1.06M7.76 16.24l1.06-1.06M16.24 16.24l-1.06-1.06M7.76 7.76l1.06 1.06" />
          </svg>
        </div>
        <div className="flex w-full justify-center">
          <div className="loader" />
        </div>
      </motion.div>
    </motion.div>
  );
};

export default LoadingOverlay;
