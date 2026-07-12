import { NavLink } from "react-router-dom";
import {useEffect, useRef, useState} from "react";

import AboutPopup from "./AboutPopup.jsx";

import { LOGOS } from "../constants/assets.jsx";


/**
 * @author ffpereira
 */
export default function Header() {
  const [open, setOpen] = useState(false);
  const [menuHeight, setMenuHeight] = useState(0);

  const menuRef = useRef(null);
  const dropdownRef = useRef(null);
  const [isPopupOpen, setIsPopupOpen] = useState(false);

  const togglePopup = () => {
    setIsPopupOpen(!isPopupOpen);
  };

  useEffect(() => {
    if (menuRef.current) {
      if (open) {
        setMenuHeight(menuRef.current.scrollHeight);
      } else {
        setMenuHeight(0);
      }
    }
  }, [open]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        open &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target)
      ) {
        setOpen(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [open]);

  return (
    <>
      <div className="md:hidden sticky bg-primary top-0 h-[6px]"></div>
      <header className="sticky top-0 -mt-[6px] z-30 h-[65px]">
          <img src={LOGOS.waveMobile} alt="" aria-hidden="true" className="md:hidden fixed top-0 left-0 w-full opacity-90 pointer-events-none"/>
          <img src={LOGOS.wave} alt="" aria-hidden="true" className="hidden md:block fixed top-0 left-0 w-full opacity-90 pointer-events-none"/>

        <div className="relative w-full h-full grid grid-cols-3 items-center px-6">
          <div className="col-start-2 flex justify-center mt-2.5">
            <NavLink to="/">
              <img src={LOGOS.main} alt="Estreias" className="w-[63px] md:w-[55px] select-none hover:scale-105 transition"/>
            </NavLink>
          </div>

          <div className="flex justify-end mt-2.5 md:mt-6">
            <div
                ref={dropdownRef}
                onClick={() => setOpen(!open)}
                className="cursor-pointer select-none transform hover:scale-115 transition ease-in-out duration-200"
            >
              <div
                  className={`w-9 h-9 flex flex-col justify-center items-center transition duration-300 ${open ? 'open' : ''}`}>
                <span
                    className={`block w-6 h-0.5 bg-darker-primary transition-all duration-300 ${open ? 'rotate-45 translate-y-1.5' : ''}`}></span>
                <span
                    className={`block w-6 h-0.5 bg-darker-primary my-1 transition-all duration-300 ${open ? 'opacity-0' : ''}`}></span>
                <span
                    className={`block w-6 h-0.5 bg-darker-primary transition-all duration-300 ${open ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
              </div>
            </div>
          </div>

        </div>

        <div id="menu" ref={menuRef} style={{maxHeight: open ? `${menuHeight}px` : '0px',}}
             className={`${open ? "border-b-4 border-beige" : ""}
             overflow-hidden transition-all duration-300 ease-in-out text-base font-medium bg-primary-light text-primary w-full shadow-md`}>
          <div
              className="h-1/2 md:h-24 grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 py-2 md:py-1.5 px-4 justify-center items-end">
            <NavLink to="/"
                  className={({ isActive }) => `pt-4 pb-2 flex flex-col justify-center items-center border-b md:border-b-0 border-r border-primary/25 group
                  ${isActive ? "text-darker-primary bg-secondary/30 font-extrabold tracking-tight" : ""}`}>
              <svg
                  className="h-6 w-6 transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary"
                  fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round"
                      d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5"/>
              </svg>
              <span
                  className="transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary">Home</span>
            </NavLink>

            <NavLink to="/films"
                  className={({ isActive }) =>`pt-4 pb-2 flex flex-col justify-center items-center hover:bg-secondary/30 border-b md:border-b-0 md:border-r border-primary/25 group
                  ${isActive ? "text-darker-primary bg-secondary/30 font-extrabold tracking-tight" : ""}`}>
              <svg
                  className="h-6 w-6 transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0 1 18 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125v-1.5M4.875 8.25C5.496 8.25 6 8.754 6 9.375v1.5m0-5.25v5.25m0-5.25C6 5.004 6.504 4.5 7.125 4.5h9.75c.621 0 1.125.504 1.125 1.125m1.125 2.625h1.5m-1.5 0A1.125 1.125 0 0 1 18 7.125v-1.5m1.125 2.625c-.621 0-1.125.504-1.125 1.125v1.5m2.625-2.625c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125M18 5.625v5.25M7.125 12h9.75m-9.75 0A1.125 1.125 0 0 1 6 10.875M7.125 12C6.504 12 6 12.504 6 13.125m0-2.25C6 11.496 5.496 12 4.875 12M18 10.875c0 .621-.504 1.125-1.125 1.125M18 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m-12 5.25v-5.25m0 5.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125m-12 0v-1.5c0-.621-.504-1.125-1.125-1.125M18 18.375v-5.25m0 5.25v-1.5c0-.621.504-1.125 1.125-1.125M18 13.125v1.5c0 .621.504 1.125 1.125 1.125M18 13.125c0-.621.504-1.125 1.125-1.125M6 13.125v1.5c0 .621-.504 1.125-1.125 1.125M6 13.125C6 12.504 5.496 12 4.875 12m-1.5 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M19.125 12h1.5m0 0c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h1.5m14.25 0h1.5"/>
              </svg>
              <span className="transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary">Films</span>
            </NavLink>

            <NavLink to="/persons"
                     className={({ isActive }) =>`pt-4 pb-2 flex flex-col justify-center items-center hover:bg-secondary/30 border-b md:border-b-0 border-r border-primary/25 group
                     ${isActive ? "text-darker-primary bg-secondary/30 font-extrabold tracking-tight" : ""}`}>
              <svg className="h-6 w-6 transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" >
                <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z"/>
              </svg>
              <span className="transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary">Persons</span>
            </NavLink>

            <NavLink to="/stats"
                     className={({ isActive }) =>`pt-4 pb-2 flex flex-col justify-center items-center hover:bg-secondary/30 border-b md:border-b-0 md:border-r border-primary/25 group
                     ${isActive ? "text-darker-primary bg-secondary/30 font-extrabold tracking-tight" : ""}`}>
              <svg className="h-6 w-6 transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z"/>
              </svg>
              <span className="transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary">Stats</span>
            </NavLink>

            <NavLink to="/cinemas"
                     className={({ isActive }) =>`pt-4 pb-2 flex flex-col justify-center items-center hover:bg-secondary/30 border-r border-primary/25 group
                     ${isActive ? "text-darker-primary bg-secondary/30 font-extrabold tracking-tight" : ""}`}>
              <svg className="h-6 w-6 transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498 4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 0 0-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0Z"/>
              </svg>
              <span className="transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary">Cinemas</span>
            </NavLink>

            <div onClick={togglePopup}
                  className="pt-4 pb-2 flex flex-col justify-center items-center hover:bg-secondary/30 group cursor-pointer">
              <svg className="h-6 w-6 transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"/>
              </svg>
              <span className="transform group-hover:scale-115 transition ease-in-out duration-200 group-hover:text-dark-primary">About</span>
            </div>
          </div>
        </div>

      </header>
      <AboutPopup isOpen={isPopupOpen} onClose={togglePopup} />
    </>
  );
}
