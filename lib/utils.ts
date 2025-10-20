import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const options = { year: "numeric", month: "long", day: "numeric" } as const;
  return date.toLocaleDateString("en-US", options);
};

export function formatTimestampToDateTime(timestamp: number): string {
  const date = new Date(timestamp);

  const dateOptions: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  const formattedDate = date.toLocaleDateString("en-US", dateOptions);

  const timeOptions: Intl.DateTimeFormatOptions = {
    hour: "numeric",
    minute: "numeric",
    hour12: true,
  };
  const formattedTime = date.toLocaleTimeString("en-US", timeOptions);

  return `${formattedDate}, ${formattedTime}`;
}
