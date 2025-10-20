"use client";

import React, { createContext, useContext, useState, useCallback } from "react";

interface RefetchContextProps {
  triggerRefetch: () => void;
  shouldRefetch: boolean;
  resetRefetch: () => void;
}

const RefetchContext = createContext<RefetchContextProps | undefined>(
  undefined
);

export const RefetchProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [shouldRefetch, setShouldRefetch] = useState(false);

  const triggerRefetch = useCallback(() => {
    setShouldRefetch(true);
  }, []);

  const resetRefetch = useCallback(() => {
    setShouldRefetch(false);
  }, []);

  return (
    <RefetchContext.Provider
      value={{ triggerRefetch, shouldRefetch, resetRefetch }}
    >
      {children}
    </RefetchContext.Provider>
  );
};

export const useRefetch = (): RefetchContextProps => {
  const context = useContext(RefetchContext);
  if (!context) {
    throw new Error("useRefetch must be used within a RefetchProvider");
  }
  return context;
};
