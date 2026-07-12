import { useState, useRef, useEffect } from "react";


/**
 * @author ffpereira
 */
export function useDropdown(initialOpen = false) {
  const [open, setOpen] = useState(initialOpen);
  const dropdownRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return { open, setOpen, dropdownRef };
}