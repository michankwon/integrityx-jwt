import React, { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  className?: string;
}

const Button: React.FC<ButtonProps> = ({ type = "button", children, className = "", disabled, ...props }) => {
  return (
    <button
      type={type}
      className={`px-4 py-3 hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-primary rounded shadow-lg
        ${disabled ? "cursor-not-allowed" : ""} 
        ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
