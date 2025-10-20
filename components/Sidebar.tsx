import { useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { FaHome, FaPlus, FaBlog, FaUser, FaDatabase, FaFish, FaJava, FaCheck, FaBars, FaTimes } from "react-icons/fa";
import { motion, AnimatePresence } from "framer-motion";

const sidebarItems = [
  { name: "Home", href: "/dashboard", icon: <FaHome />, description: "Dashboard overview" },
  { name: "Schemas", href: "/dashboard/schemas", icon: <FaDatabase />, description: "View Schemas" },
  { name: "Create", href: "/dashboard/create", icon: <FaPlus />, description: "Create new content" },
  { name: "My Blogs", href: "/dashboard/my-blogs", icon: <FaBlog />, description: "View your blogs" },
  { name: "Profile", href: "/dashboard/profile", icon: <FaUser />, description: "Edit your profile" },
  { name: "Roles", href: "/dashboard/role", icon: <FaJava />, description: "Edit your roles" },
  { name: "Hooks", href: "/dashboard/hooks", icon: <FaFish />, description: "View Hooks" },
  { name: "Verification", href: "/dashboard/verification", icon: <FaCheck />, description: "Review Verification" },
];

const Sidebar = () => {
  const router = useRouter();
  const pathname = usePathname();
  const [loadingItem, setLoadingItem] = useState<string | null>(null);
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const [isSidebarVisible, setIsSidebarVisible] = useState(false);

  const handleClick = (href: string) => {
    if (pathname === href) return;
    setLoadingItem(href);
    setIsSidebarVisible(false); // Trigger sidebar hide animation

    // Delay navigation to allow sidebar to slide out
    setTimeout(() => {
      router.push(href);
      setLoadingItem(null);
    }, 300); // Adjust duration to match animation timing
  };

  return (
    <div>
      <div className="p-4">
        <button
          onClick={() => setIsSidebarVisible(!isSidebarVisible)}
          className="p-2 flex items-center justify-center w-10 h-10 rounded-full shadow-lg transition-all duration-300 active:scale-90"
          style={{
            backgroundColor: "#0f172a",
            color: "#ffffff",
          }}
        >
          {isSidebarVisible ? <FaTimes /> : <FaBars />}
        </button>
      </div>

      <AnimatePresence>
        {isSidebarVisible && (
          <motion.div key="sidebar" initial={{ x: -300, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -300, opacity: 0 }} transition={{ type: "spring", stiffness: 150, damping: 20 }} className="w-full sm:flex flex-col">
            {sidebarItems.map((item, index) => {
              const isActive = pathname === item.href;
              const isLoading = loadingItem === item.href;
              const isHovered = hoveredItem === item.href;

              return (
                <div
                  key={index}
                  onClick={() => handleClick(item.href)}
                  className={`flex items-center justify-start p-4 cursor-pointer transition-all`}
                  style={{
                    transition: "background-color 0.3s ease, color 0.3s ease",
                  }}
                  onMouseEnter={() => setHoveredItem(item.href)}
                  onMouseLeave={() => setHoveredItem(null)}
                >
                  <div className={`w-10 h-10 flex justify-center items-center rounded-full ${isActive ? "bg-[#0f172a] text-white" : ""}`}>
                    {isLoading ? (
                      <motion.div className={`animate-spin ${isHovered || isActive ? "" : "text-primary"}`} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
                        <svg className="w-6 h-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 12h1.5M12 4v1.5M19.5 12H21M12 19.5V21M16.24 7.76l-1.06 1.06M7.76 16.24l1.06-1.06M16.24 16.24l-1.06-1.06M7.76 7.76l1.06 1.06" />
                        </svg>
                      </motion.div>
                    ) : (
                      item.icon
                    )}
                  </div>
                  <div className={`flex flex-col ml-4 transition-all ${isHovered ? "opacity-100 bg-muted backdrop-blur-xl shadow-xl z-20 p-2 rounded-lg" : "opacity-0"}`}>
                    <span className="font-semibold">{item.name}</span>
                    <span className="text-sm text-gray-500">{item.description}</span>
                  </div>
                </div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Sidebar;
