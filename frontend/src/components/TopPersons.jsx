import {Link} from "react-router-dom";
import defaultImage from "../assets/default_w300.jpg";


/**
 * @author ffpereira
 */
export default function TopPersons({title, data, size=5, noPadding = false}){
    return (
        <div className="flex flex-col justify-center items-center">
            <div className={`md:px-2 grid ${size <= 3 ? "grid-cols-3" : "grid-cols-2"} gap-1 md:gap-2 ${noPadding ? "" : "pb-2 md:pb-0"}`}>
                <div className={`${size <= 3 ? "text-xs md:text-base" : ""} col-span-full border-b-2 border-primary/25 font-semibold text-center`}>Top {size} {title}</div>
                <div className={`relative ${size <= 3 ? "col-span-2" : "col-span-1"} flex-shrink-0 flex flex-col items-center`}>
                    {data.slice(0, 1).map(person => (
                        <div className="relative flex-shrink-0 flex flex-col items-center text-center overflow-visible group">
                            <Link to={`/person/${person.id}`} key={`${person.id}-portrait`}>
                                <img src={person.portrait || defaultImage}
                                     onError={(e) => e.target.src = defaultImage} alt={person.name}
                                     className="rounded-md h-auto relative cursor-pointer hover:shadow-2xl shadow-md transform hover:scale-102 transition ease-in-out duration-200"
                                />
                            </Link>
                            <div className="absolute bottom-0 text-xs md:text-sm font-semibold bg-secondary/75 py-0.5 md:py-1.5 px-1 md:px-2 rounded-md text-black text-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                                {person.name}
                            </div>
                            <div className="absolute top-1 right-1 z-10 w-7 h-7 md:w-8 md:h-8 text-sm md:text-base flex items-center justify-center text-center bg-accent/85 text-secondary border border-secondary/50 font-bold rounded-full p-1 md:p-2 shadow-sm select-none">
                                {person.films_count}
                            </div>
                        </div>
                    ))}
                </div>
                <div className={`col-span-1 grid ${size <= 3 ? "grid-rows-2" : "grid-cols-2"} gap-1 md:gap-2`}>
                    {data.slice(1, size).map(person => (
                        <div className="relative flex-shrink-0 flex flex-col items-center text-center overflow-visible group">
                            <Link to={`/person/${person.id}`} key={`${person.id}-portrait`}>
                                <img src={person.portrait || defaultImage}
                                     onError={(e) => e.target.src = defaultImage} alt={person.name}
                                     className="rounded-md h-auto relative cursor-pointer hover:shadow-2xl shadow-md transform hover:scale-105 transition ease-in-out duration-200"
                                />
                            </Link>
                            <div className="absolute bottom-0 text-xs md:text-sm font-semibold bg-secondary/75 py-0.5 md:py-1.5 px-1 md:px-2 rounded-md text-black text-center opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                                {person.name}
                            </div>
                            <div className="absolute top-1 right-1 z-10 w-7 h-7 md:w-8 md:h-8 text-sm md:text-base flex items-center justify-center text-center bg-accent/85 text-secondary border border-secondary/50 font-bold rounded-full p-1 md:p-2 shadow-sm">
                                {person.films_count}
                            </div>
                        </div>

                    ))}
                </div>
            </div>
        </div>
    );
}
