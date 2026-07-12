import {useEffect, useState} from "react";
import {Link, useParams} from "react-router-dom";

import ErrorPage from "./ErrorPage.jsx";
import Body from "../components/Body.jsx";
import {useApi} from "../contexts/ApiProvider.jsx";
import CinemaListMap from "../components/CinemaListMap.jsx";

import { STATUS } from "../constants/status.jsx";
import { LOGOS, DEFAULTS } from "../constants/assets.jsx";


/**
 * @author ffpereira
 */
export default function FilmPage() {
    const api = useApi();
    const { film_id } = useParams();

    const [film, setFilm] = useState();
    const [status, setStatus] = useState(STATUS.LOADING);

    useEffect(() => {
        (async () => {
            try {
                const response = await api.get(`/film/${film_id}`);
                if (response.ok) {
                    setFilm(response.body);
                    setStatus(STATUS.OK);
                } else if (response.status === 404) {
                    setStatus(STATUS.NOT_FOUND);
                }
                else{
                    setStatus(STATUS.ERROR);
                }
            } catch {
                setStatus(STATUS.ERROR);
            }
        })();
    }, [api, film_id]);

    useEffect(() => {
        if (film === undefined) return;
        document.title = film === null ? "Film - Not found" : `Film - ${film.title}`;
        return () => { document.title = "Estreias"; };
    }, [film]);

    const directors = film?.crew?.filter(p => p.role === "director") || [];
    const runtimeDisplay = film?.runtime > 0 ? film.runtime : "N/A";
    const releaseStatus = film?.upcoming ? "Upcoming" : film?.in_cinemas ? "In Cinemas" : "Released";
    const handleImageError = (fallback) => (e) => {e.target.src = fallback;};

    return (
        <Body>
            { status === STATUS.LOADING ? (
                <div className="mt-[5vh] h-[86.25vh] md:h-[85vh] bg-primary/30 w-full rounded-md flex justify-center items-center">
                    <div className="spinner"></div>
                </div>
            ) : status === STATUS.NOT_FOUND ? ( <ErrorPage code={STATUS.NOT_FOUND} />
            ) : status === STATUS.ERROR ? ( <ErrorPage code={STATUS.ERROR} />
            ) : (
                <>
                    {film === null ?
                        <div>Film Not Found</div>
                        :
                        <div className="mt-[5vh] h-[86.25vh] md:h-[85vh] bg-primary/30 overflow-auto w-full rounded-md scrollbar-minimal">
                            <div className="grid grid-cols-12 gap-x-2 px-2 md:px-4 pt-2">
                                <div
                                    className="col-span-full md:col-span-8 text-balance text-3xl md:text-4xl font-semibold text-darker-primary">{film.title}</div>

                                <div className="hidden col-span-4 md:grid grid-cols-3 gap-1">
                                    <div className="-mt-2 -mb-4 mr-2 flex justify-center items-center text-dark-primary">Year</div>
                                    <div className="-mt-2 -mb-4 mr-2 flex justify-center items-center text-darker-primary">Runtime</div>
                                    <div className="-mt-2 -mb-4 mr-2 flex justify-center items-center text-dark-primary">Status</div>
                                </div>

                                <div
                                    className="col-span-full md:col-span-8 md:text-xl text-darker-primary">{film.tagline}</div>

                                <div className="hidden col-span-4 md:grid grid-cols-3 gap-1">
                                    <Link to={`/release_year/${film.release_year}`}
                                          className="text-3xl -mt-2 mr-2 mb-2 flex justify-center transform hover-text tracking-tighter text-darker-primary font-semibold">
                                        {film.release_year}
                                    </Link>
                                    <Link to={`/runtime/${film.runtime}`}
                                          className="text-3xl -mt-2 mr-2 mb-2 flex justify-center transform hover-text tracking-tighter text-darker-primary font-semibold">
                                        {runtimeDisplay}
                                    </Link>
                                    <div className="text-2xl -mt-2 mr-2 mb-2 flex justify-center tracking-tight text-darker-primary font-semibold">
                                        {releaseStatus}
                                    </div>
                                </div>

                                <div className="md:hidden col-span-full mt-2 grid grid-cols-3 gap-2">
                                    <img className="col-span-2 w-full rounded-md shadow-md" alt={film.title}
                                         src={film.poster || DEFAULTS.image}
                                         onError={handleImageError(DEFAULTS.image)}/>
                                    <div className="flex flex-col justify-center items-center">
                                        <div className="text-darker-primary">Year</div>
                                        <Link to={`/release_year/${film.release_year}`}
                                              className="text-3xl text-center pb-4 tracking-tighter text-darker-primary font-semibold">
                                            {film.release_year}
                                        </Link>
                                        <div className="pt-4 border-t border-primary/25 w-full text-center text-darker-primary">Runtime</div>
                                        <Link to={`/runtime/${film.runtime}`}
                                              className="text-3xl text-center pb-4 tracking-tighter text-darker-primary font-semibold">
                                            {runtimeDisplay}
                                        </Link>
                                        <div className="pt-4 border-t border-primary/25 w-full text-center text-darker-primary">Status</div>
                                        <div className="text-xl text-center tracking-tight text-darker-primary font-semibold">
                                            {releaseStatus}
                                        </div>
                                    </div>
                                </div>

                                <div className="col-span-full md:col-span-8 flex flex-col gap-2 h-full">
                                    <div className="order-2 md:order-1 relative rounded-md overflow-hidden">
                                        <img src={film.backdrop || DEFAULTS.backdrop}
                                             onError={handleImageError(DEFAULTS.backdrop)}
                                             alt={film.title}
                                             className="hidden md:block  absolute inset-0 w-full h-full object-cover z-0"/>

                                        <div className="hidden md:block  absolute inset-0 bg-black/20 z-0"/>

                                        <div className="hidden md:block  relative z-10 p-4 w-78">
                                            <div className="group [perspective:1000px]">
                                                <div
                                                    className="border-2 border-tealish/50 rounded-md shadow-xl transition-all duration-500 [transform-style:preserve-3d] group-hover:[transform:rotateY(180deg)]">
                                                    <img className="w-full rounded-md shadow-md" alt={film.title}
                                                         src={film.poster || DEFAULTS.image}
                                                         onError={handleImageError(DEFAULTS.image)}/>
                                                    <div
                                                        className="absolute inset-0 [backface-visibility:hidden] [transform:rotateY(180deg)]">
                                                        <img className="w-full rounded-md shadow-md" alt={film.title}
                                                             src={film.poster || DEFAULTS.image}
                                                             onError={handleImageError(DEFAULTS.image)}/>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {directors.length > 0 && (
                                            <div className="md:absolute md:bottom-4 md:right-4 md:z-20 md:w-1/3">
                                                <div
                                                    className="grid grid-cols-2 bg-secondary/50 md:bg-secondary/75 rounded-md border-2 border-tealish/50 z-10 md:m-2 justify-center items-center">

                                                    {/* Director name */}
                                                    <div className="p-4">
                                                        <div
                                                            className="text-xl md:text-2xl text-center font-semibold border-b md:border-b-2 border-tealish/25">
                                                            Director
                                                        </div>

                                                        <div
                                                            className="md:text-lg mt-2 flex flex-col justify-center items-center">
                                                            {directors.map(person => (
                                                                <Link className="text-center hover-text"
                                                                      key={`${person.person_id}-text`}
                                                                      to={`/person/${person.person_id}`}>
                                                                    {person.person_name}
                                                                </Link>
                                                            ))}
                                                        </div>
                                                    </div>

                                                    {/* Director portrait */}
                                                    <div
                                                        className="flex overflow-x-auto scrollbar-minimal px-4 gap-2 text-lg py-2 justify-center items-center">
                                                        {directors.map(person => (
                                                            <Link to={`/person/${person.person_id}`}
                                                                  key={`${person.person_id}-portrait`}
                                                                  className="group flex-shrink-0 flex flex-col items-center relative overflow-visible">
                                                                <img src={person.portrait || DEFAULTS.image}
                                                                     onError={handleImageError(DEFAULTS.image)}
                                                                     alt={person.person_name}
                                                                     className="rounded-md w-20 h-auto relative cursor-pointer hover:shadow-2xl shadow-md transform hover:scale-105 transition ease-in-out duration-200"
                                                                />
                                                                <div
                                                                    className="absolute bottom-0 z-10 px-2 py-1 text-xs text-center text-white bg-gray-800/90 rounded-lg shadow-sm opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                                                                    {person.person_name}
                                                                </div>
                                                            </Link>
                                                        ))}
                                                    </div>

                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    <div className="order-1 md:order-2 col-span-2 md:text-lg my-2 md:my-1 h-38 md:h-21 overflow-auto md:[&::-webkit-scrollbar]:hidden">{film.description}</div>

                                    <div className="order-3 col-span-2 flex overflow-x-auto scrollbar-minimal py-2 mr-2">
                                        {film.cast && film.cast.length > 0 && film.cast.map(person => (
                                            <Link key={`${person.person_id}-cast`} to={`/person/${person.person_id}`}
                                                  className="group flex-shrink-0 flex flex-col items-center relative">
                                                <img
                                                    className="rounded-md w-20 h-auto relative cursor-pointer hover:shadow-2xl shadow-md transform hover:scale-105 transition ease-in-out duration-200 mx-2"
                                                    alt={person.person_name} src={person.portrait || DEFAULTS.image}
                                                    onError={handleImageError(DEFAULTS.image)}/>
                                                <div
                                                    className="absolute z-10 px-3 py-2 text-xs text-white text-center bg-gray-800/90 rounded-lg shadow-sm opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">{person.character}</div>
                                                <div
                                                    className="absolute bottom-0 z-10 px-2 py-1 text-xs text-center text-white bg-gray-800/90 rounded-lg shadow-sm tooltip">{person.person_name}</div>
                                            </Link>
                                        ))}
                                    </div>

                                </div>

                                <div className="mt-2 md:mt-0 col-span-full md:col-span-4 relative grid grid-cols-2 gap-2 h-full">

                                    <div
                                        className="col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50 grid grid-cols-2 p-2">

                                        <div className="flex flex-col justify-center items-center">
                                            <div className="text-sm md:text-base">Distributor</div>
                                            {film.distributor ? (
                                                <div className="flex flex-wrap justify-center items-center">
                                                    <Link to={`/distributor/${encodeURIComponent(film.distributor)}`}>
                                                        <div
                                                            className="-mt-1 text-center text-lg md:text-xl hover-text font-semibold">{film.distributor}</div>
                                                    </Link>
                                                </div>
                                            ) : (
                                                <div className="-mt-1 text-xl font-semibold">N/A</div>
                                            )}
                                        </div>

                                        <div
                                            className="flex flex-col justify-center items-center border-l border-tealish/25">
                                            <div className="text-sm md:text-base">Content Rating</div>
                                            <div className="flex flex-wrap justify-center items-center">
                                                {film.content_rating ? (
                                                    <Link
                                                        to={`/content_rating/${encodeURIComponent(film.content_rating)}`}>
                                                        <div
                                                            className="-mt-1 text-lg md:text-xl hover-text font-semibold">{film.content_rating}</div>
                                                    </Link>
                                                ) : (
                                                    <div className="-mt-1 text-xl font-semibold">N/A</div>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex flex-col justify-center items-center">
                                            <div className="text-sm md:text-base text-center">Worldwide Release Date
                                            </div>
                                            <div className="-mt-1 text-xl font-semibold">
                                                {film.release_date ?
                                                    new Date(film.release_date).toLocaleDateString("pt-PT") : "N/A"
                                                }
                                            </div>
                                        </div>

                                        <div
                                            className="flex flex-col justify-center items-center border-l border-tealish/25">
                                        <div className="text-sm md:text-base text-center">Portuguese Release Date
                                            </div>
                                            <div className="-mt-1 text-xl font-semibold">
                                                {film.pt_release_date ?
                                                    new Date(film.pt_release_date).toLocaleDateString("pt-PT") : "N/A"
                                                }
                                            </div>
                                        </div>

                                    </div>

                                    <div className="col-span-full grid grid-cols-2 gap-2">
                                        <div
                                            className="bg-secondary/50 rounded-md border-2 border-tealish/50 flex flex-col gap-2 p-2">
                                            <div>
                                                <div className="text-sm md:text-base font-semibold text-center">Origin
                                                    Country
                                                </div>
                                                <div
                                                    className="mx-2 px-4 pt-4 pb-2 col-span-2 text-lg flex flex-wrap justify-center items-center border-b border-tealish/25">
                                                    {film.countries?.map((country) => (
                                                        <Link key={`${country.id}-origin-country`}
                                                              to={`/country/${encodeURIComponent(country.id)}`}
                                                              className="mb-2 mr-2">
                                                            <img
                                                                className="w-[34px] h-[22px] md:w-[48px] md:h-[32px] rounded-sm hover:shadow-sm transform hover:scale-105 transition ease-in-out duration-200 shadow-md"
                                                                src={country.flag} alt={country.id}/>
                                                        </Link>
                                                    ))}
                                                </div>
                                            </div>

                                            <div>
                                                <div className="text-sm md:text-base font-semibold text-center">Original
                                                    Language
                                                </div>
                                                <div
                                                    className="mx-2 pb-4 col-span-2 text-base flex flex-wrap justify-center items-center border-b border-tealish/25">
                                                    <Link
                                                        to={`/language/${encodeURIComponent(film.original_language_obj.id)}`}
                                                        className="hover-text">
                                                        {film.original_language_obj.name}
                                                    </Link>
                                                </div>
                                            </div>

                                            <div>
                                                <div className="text-sm md:text-base font-semibold text-center">Spoken
                                                    Languages
                                                </div>
                                                <div
                                                    className="pb-2 mx-2 text-base flex flex-wrap gap-x-2 justify-center items-center h-16 overflow-auto [&::-webkit-scrollbar]:hidden border-b border-tealish/25">
                                                    {film.spoken_languages?.map((language) => (
                                                        <Link key={`${language.english_name}-spk-language`}
                                                              to={`/language/${encodeURIComponent(language.id)}`}
                                                              className="hover-text">
                                                            {language.name}
                                                        </Link>
                                                    ))}
                                                </div>
                                            </div>

                                            <div>
                                                <div
                                                    className="text-sm md:text-base font-semibold text-center px-2">Genres
                                                </div>
                                                <div
                                                    className="text-base flex flex-col justify-center items-center h-26 overflow-auto [&::-webkit-scrollbar]:hidden pt-2 mx-2 ">
                                                    {film.genres?.map((genre) => (
                                                        <Link key={genre.id}
                                                              to={`/genre/${encodeURIComponent(genre.id)}`}
                                                              className="hover-text">
                                                            {genre.name}
                                                        </Link>
                                                    ))}
                                                </div>
                                            </div>

                                        </div>

                                        <div
                                            className="bg-secondary/50 rounded-md border-2 border-tealish/50 h-full grid grid-rows-3 gap-2 p-2">
                                            {film.crew && film.crew.length > 0 && (
                                                <>

                                                    {/* Writers */}
                                                    <div
                                                        className="flex flex-col overflow-hidden justify-start items-center border-b border-tealish/25">
                                                        <div
                                                            className="text-sm md:text-base font-semibold mb-1 shrink-0">Writers
                                                        </div>
                                                        <div
                                                            className="w-full text-center flex-1 max-h-24 overflow-auto [&::-webkit-scrollbar]:hidden">
                                                            {film.crew
                                                                .filter(p => p.role === "writer")
                                                                .map(person => (
                                                                    <div key={`${person.person_id}-writer`}
                                                                         className="">
                                                                        <Link to={`/person/${person.person_id}`}>
                                                                            <div
                                                                                className="hover-text">{person.person_name}</div>
                                                                        </Link>
                                                                    </div>
                                                                ))}
                                                        </div>
                                                    </div>

                                                    {/* Composers */}
                                                    <div
                                                        className="flex flex-col overflow-hidden justify-start items-center border-b border-tealish/25">
                                                        <div
                                                            className="text-sm md:text-base font-semibold mb-1 shrink-0">Composers
                                                        </div>
                                                        <div
                                                            className="w-full text-center flex-1 max-h-24 overflow-auto [&::-webkit-scrollbar]:hidden">
                                                            {film.crew
                                                                .filter(p => p.role === "composer")
                                                                .map(person => (
                                                                    <div key={`${person.person_id}-composer`}
                                                                         className="mb-2">
                                                                        <Link to={`/person/${person.person_id}`}>
                                                                            <div
                                                                                className="hover-text">{person.person_name}</div>
                                                                        </Link>
                                                                    </div>
                                                                ))}
                                                        </div>
                                                    </div>

                                                    {/* Cinematographers */}
                                                    <div
                                                        className="flex flex-col overflow-hidden justify-start items-center">
                                                        <div
                                                            className="text-sm md:text-base font-semibold mb-1 shrink-0">Cinematography
                                                        </div>
                                                        <div
                                                            className="w-full text-center flex-1 max-h-24 overflow-auto [&::-webkit-scrollbar]:hidden">
                                                            {film.crew
                                                                .filter(p => p.role === "cinematographer")
                                                                .map(person => (
                                                                    <div key={`${person.person_id}-cinematographer`}
                                                                         className="mb-2">
                                                                        <Link to={`/person/${person.person_id}`}>
                                                                            <div
                                                                                className="hover-text">{person.person_name}</div>
                                                                        </Link>
                                                                    </div>
                                                                ))}
                                                        </div>
                                                    </div>


                                                </>
                                            )}
                                        </div>
                                    </div>

                                    {film.budget > 0 && film.revenue > 0 && (
                                        <div
                                            className="col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50 grid grid-cols-2 gap-2 p-2">
                                            <div className="col-span-full font-semibold flex justify-center">Box
                                                Office
                                            </div>

                                            <div className="-mt-2 md:-mt-6 flex flex-col justify-center items-center">
                                                <div className="text-sm md:text-base">Budget</div>
                                                <div
                                                    className="-mt-1 text-lg md:text-xl font-semibold">{Number((film.budget / 1_000_000).toFixed(2))}M
                                                    $
                                                </div>
                                            </div>

                                            <div className="-mt-2 md:-mt-6 flex flex-col justify-center items-center">
                                                <div className="text-sm md:text-base">Revenue</div>
                                                <div
                                                    className="-mt-1 text-lg md:text-xl font-semibold">{Number((film.revenue / 1_000_000).toFixed(2))}M
                                                    $
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    <div
                                        className="col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50 grid grid-cols-2 gap-2 mb-2 md:mb-0">
                                        <div
                                            className="col-span-full grid grid-cols-3 flex-grow justify-center items-center p-2">
                                            <div className="flex justify-center items-center">
                                                <a href={`https://imdb.com/title/${film.imdb_id}`}
                                                   target="_blank" rel="noopener noreferrer">
                                                    <img src={LOGOS.imdb} alt="IMDb"
                                                         className="w-12 transform hover:scale-110 transition ease-in-out duration-200"/>
                                                </a>
                                            </div>
                                            <div
                                                className="flex justify-center items-center border-l border-tealish/25">
                                                <a href={`https://www.themoviedb.org/movie/${film.tmdb_id}`}
                                                   target="_blank" rel="noopener noreferrer">
                                                    <img src={LOGOS.tmdb} alt="TMDB"
                                                         className="w-12 transform hover:scale-110 transition ease-in-out duration-200"/>
                                                </a>
                                            </div>
                                            <div
                                                className="flex justify-center items-center border-l border-tealish/25">
                                                <a href={`https://letterboxd.com/tmdb/${film.tmdb_id}`}
                                                   target="_blank" rel="noopener noreferrer">
                                                    <img src={LOGOS.letterboxd} alt="letterboxd"
                                                         className="w-12 transform hover:scale-110 transition ease-in-out duration-200"/>
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="col-span-full pb-2">
                                    {film && film.in_cinemas &&
                                        <CinemaListMap fullHeight={"h-[65vh] md:h-[72vh]"} mapHeight={"h-[72vh]"}
                                                       film_id={film_id}/>}
                                </div>
                            </div>
                        </div>
                    }
                </>
            )}
        </Body>
    );
}