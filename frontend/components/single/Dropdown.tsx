import React, { useState, useEffect, useRef } from "react";

interface DropdownProps {
  name?: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
  className?: string;
  placeholder?: string;
}

const Dropdown: React.FC<DropdownProps> = ({ name, value, onChange, options, className, placeholder = "Select an option" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const handleToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsOpen((prev) => !prev);
  };

  const handleOptionClick = (e: React.MouseEvent, optionValue: string) => {
    e.stopPropagation();
    onChange(optionValue);
    setIsOpen(false);
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
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
      <div className="flex justify-between items-center px-2 cursor-pointer" onClick={handleToggle}>
        <span>{value ? value : placeholder}</span>
        <span className={`transform scale-50 transition-transform duration-200 ${isOpen ? "rotate-180" : "rotate-0"}`}>▼</span>
      </div>
      {isOpen && (
        <div className="absolute left-0 right-0 top-full mt-1 bg-white border shadow-lg z-10 max-h-48 overflow-y-auto">
          {options.map((option) => (
            <div key={option} className={`block px-4 py-2 cursor-pointer hover:bg-gray-100 ${option === value ? "bg-gray-200" : ""}`} onClick={(e) => handleOptionClick(e, option)}>
              {option}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dropdown;
