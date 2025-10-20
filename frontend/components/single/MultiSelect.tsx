import React, { ChangeEventHandler, useState, useEffect, useRef } from "react";

interface MultiSelectProps {
  name?: string;
  values: string[];
  onChange: (values: string[]) => void;
  options: { label: string; value: string }[];
  className?: string;
  placeholder?: string;
}

const MultiSelect: React.FC<MultiSelectProps> = ({
  name,
  values,
  onChange,
  options,
  className,
  placeholder = "Select options",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const handleToggle = () => {
    setIsOpen((prev) => !prev);
  };

  const handleOptionClick = (value: string) => {
    if (values.includes(value)) {
      onChange(values.filter((v) => v !== value));
    } else {
      onChange([...values, value]);
    }
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (
      wrapperRef.current &&
      !wrapperRef.current.contains(event.target as Node)
    ) {
      setIsOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className={`bg-white relative ${className}`} ref={wrapperRef}>
      <div
        className="flex justify-between items-center px-2 cursor-pointer"
        onClick={handleToggle}
      >
        <span>{values.length > 0 ? values.join(", ") : placeholder}</span>
        <span
          className={`transform scale-50 transition-transform duration-200 ${
            isOpen ? "rotate-180" : "rotate-0"
          }`}
        >
          ▼
        </span>
      </div>
      {isOpen && (
        <div className="absolute left-0 right-0 top-full mt-1 bg-white border shadow-lg z-10">
          {options.map((option) => (
            <label
              key={option.value}
              className="block px-4 py-2 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={values.includes(option.value)}
                onChange={() => handleOptionClick(option.value)}
                className="mr-2"
              />
              {option.label}
            </label>
          ))}
        </div>
      )}
    </div>
  );
};

export default MultiSelect;
