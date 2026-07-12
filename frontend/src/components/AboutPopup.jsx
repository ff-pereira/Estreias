import { useEffect } from "react";

import { LOGOS } from "../constants/assets.jsx";


/**
 * @author ffpereira
 */
export default function AboutPopup({ isOpen, onClose }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {

      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="font-normal fixed inset-0 flex items-center justify-center bg-primary/75 z-50 text-primary" onClick={onClose}>
      <div
          className="p-6 md:p-8 bg-secondary rounded-3xl shadow-lg border-4 border-primary flex flex-col justify-center items-center relative"
          onClick={(e) => e.stopPropagation()}>
        <img src={LOGOS.main} alt="estreias Logo" className="mt-0.5 w-[35px]"/>
        <div className="text-primary tracking-tighter text-4xl text-center select-none">estreias</div>
        <div className="text-base md:text-lg">Author: <strong>ffpereira</strong></div>
        <div className="text-base md:text-lg mb-4">Contact: <strong>estreias@ffpereira.com</strong></div>
        <div
            className="scrollbar-minimal rounded-md w-[75vw] md:w-[50vw] h-[55vh] md:h-[50vh] overflow-y-auto font-normal p-1 md:p-4 text-justify space-y-2 md:space-y-8 text-sm md:text-base">
          <p>
            Estreias is an <strong>open-source, independent project</strong> that tracks and presents film releases in Portuguese cinemas,
            including upcoming and past titles, cinema screenings across the country, and aggregated insights on the individuals most frequently involved in widely released productions.
            Data is collected automatically and updated daily.
          </p>
          <p>
            Data is collected from publicly accessible sources and third-party services, 
            including The Movie Database (TMDb), and is regularly updated to reflect the latest available information.
          </p>
          <p className="font-bold">
            This project is <span className="underline">not</span> affiliated with, endorsed, or sponsored by TMDb, any cinema operators, distributors, or related entities. 
            All film, cast, crew, and related content remains the intellectual property of their respective owners.
            No personally identifiable information is collected, stored, or shared. The project follows <strong>best practices for data privacy and responsible data usage.</strong>
          </p>
          <p>
            This project is strictly non-commercial and is intended solely for research and educational purposes.
            The author disclaims any liability for errors, omissions, or inaccuracies in the data presented.
          </p>
        </div>

        <svg xmlns="http://www.w3.org/2000/svg"
             className="absolute top-2 right-2 cursor-pointer hover:scale-110 ease-in-out duration-200"
             viewBox="0 0 640 640"
             fill="#252121" width="32" height="32"
             onClick={onClose}>
          <path
              d="M183.1 137.4C170.6 124.9 150.3 124.9 137.8 137.4C125.3 149.9 125.3 170.2 137.8 182.7L275.2 320L137.9 457.4C125.4 469.9 125.4 490.2 137.9 502.7C150.4 515.2 170.7 515.2 183.2 502.7L320.5 365.3L457.9 502.6C470.4 515.1 490.7 515.1 503.2 502.6C515.7 490.1 515.7 469.8 503.2 457.3L365.8 320L503.1 182.6C515.6 170.1 515.6 149.8 503.1 137.3C490.6 124.8 470.3 124.8 457.8 137.3L320.5 274.7L183.1 137.4z"/>
        </svg>

      </div>
    </div>
  );
}
