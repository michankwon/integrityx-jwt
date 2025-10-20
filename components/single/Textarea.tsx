import React, { ChangeEventHandler } from "react";

interface TextareaProps {
  name: string;
  placeholder: string;
  value: string;
  onChange: ChangeEventHandler<HTMLTextAreaElement>;
  required?: boolean;
}

const Textarea: React.FC<TextareaProps> = ({
  name,
  placeholder,
  value,
  onChange,
  required = false,
}) => {
  return (
    <textarea
      name={name}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      required={required}
      className="w-full px-4 py-2 border focus:outline-none focus:ring-2 focus:ring-primary"
      rows={6}
    />
  );
};

export default Textarea;
