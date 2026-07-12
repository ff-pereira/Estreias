import {Link} from "react-router-dom";

import { STATUS } from "../constants/status.jsx";


/**
 * @author ffpereira
 */
export default function ErrorPage({code}) {

    const handleReload = () => {
        window.location.reload();
    };

    return (
        <>
            <div className="mt-4 w-full grid grid-cols-3 gap-3 h-14 text-sm md:text-base">
                <div className="col-start-2 text-primary tracking-tighter text-4xl flex justify-center items-center select-none">estreias
                </div>
                <div className="mt-6 text-primary flex justify-end items-center">by ffpereira</div>
            </div>
            <div className="h-[82.5vh] bg-primary/30 overflow-auto w-full rounded-md flex flex-col justify-center items-center text-dark-primary">
                <div className="text-9xl font-bold">{code}</div>

                {code === STATUS.ERROR ? (
                    <>
                        <div className="text-3xl font-semibold tracking-tight text-center">Service Unavailable</div>
                        <div className="mt-4 mb-12 text-lg">The service is temporarily unavailable. Please try again later.</div>
                        <button
                            className="bg-accent text-white select-none hover-text-colorless cursor-pointer rounded-md p-2 text-center flex items-center justify-center gap-2"
                            onClick={handleReload}>
                            Try Again
                        </button>
                    </>
                ) : (
                    <>
                        <div className="text-3xl font-semibold tracking-tight text-center">Page Not Found</div>
                        <div className="mt-4 mb-12 text-lg">The page you are looking for does not exist.</div>
                        <Link to="/"
                              className="bg-accent text-white select-none hover-text-colorless cursor-pointer rounded-md p-2 text-center flex items-center justify-center gap-2">
                            Home
                        </Link>
                    </>
                )}

            </div>
        </>
    );
}