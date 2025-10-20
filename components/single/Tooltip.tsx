import { faInfoCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export const Tooltip = ({ text }: { text: string }) => (
  <div className="relative group">
    <FontAwesomeIcon icon={faInfoCircle} className="ml-1 text-gray-500 cursor-pointer" />
    <div className="absolute left-0 bottom-full mb-1 hidden w-48 p-2 text-xs text-white bg-black rounded group-hover:block">{text}</div>
  </div>
);
