import {useEffect, useState} from "react";
import {Link, useParams} from "react-router-dom";

import ErrorPage from "./ErrorPage.jsx";
import Body from "../components/Body.jsx";
import {useApi} from "../contexts/ApiProvider.jsx";
import RadarChart from "../components/RadarChart.jsx";

import { STATUS } from "../constants/status.jsx";
import { LOGOS, DEFAULTS } from "../constants/assets.jsx";


/**
 * @author ffpereira
 */
export default function PersonPage() {
    const api = useApi();
    const { person_id } = useParams();

    const [person, setPerson] = useState();
    const [personStats, setPersonStats] = useState();
    const [status, setStatus] = useState("loading");

    useEffect(() => {
        (async () => {
            try{
                const response = await api.get(`/person/${person_id}`);
                if (response.ok) {
                    setPerson(response.body);
                    setStatus(STATUS.OK);
                } else if(response.status === 404){
                    setStatus(STATUS.NOT_FOUND);
                } else{
                    setStatus(STATUS.ERROR);
                }
            } catch {
                setStatus(STATUS.ERROR);
            }
        })();
    }, [api, person_id]);

    useEffect(() => {
        (async () => {
            try {
                const response = await api.get(`/person/roles/${person_id}`);
                if (response.ok) {
                    setPersonStats(response.body);
                } else {
                    setPersonStats(null);
                }
            } catch {
                setPersonStats(null);
            }
        })();
    }, [api, person_id]);

    useEffect(() => {
        if (person === undefined) return;
        document.title = person === null ? "Person - Not found" : `${person.name}`;
        return () => { document.title = "Estreias"; };
    }, [person]);

    const getSections = () => {
        if (!person) return [];

        const sections = [];
        const knownFor = person.known_for_department?.toLowerCase();

        const priorityMap = {
            acting: "cast",
            directing: "director",
            camera: "camera",
            sound: "sound",
            writing: "writer"
        };

        const allSections = [];
        if (person.cast_roles.length > 0) {
            allSections.push({
                type: "cast",
                title: "Films as actor",
                items: person.cast_roles
            });
        }

        Object.entries(person.crew_roles).forEach(([role, films]) => {
            allSections.push({
                type: "crew",
                title: `Films as ${role}`,
                items: films
            });
        });

        if (allSections.length === 0) return [];

        // Determine the first section
        let firstSectionIndex = -1;
        if (priorityMap[knownFor]) {
            firstSectionIndex = allSections.findIndex(s =>
                (priorityMap[knownFor] === "cast" && s.type === "cast") ||
                s.title.toLowerCase().includes(priorityMap[knownFor])
            );
        }

        // If no match, pick the one with the highest count
        if (firstSectionIndex === -1) {
            firstSectionIndex = allSections.reduce(
                (maxIdx, s, idx, arr) => s.items.length > arr[maxIdx].items.length ? idx : maxIdx,
                0
            );
        }

        sections.push(allSections[firstSectionIndex]);
        allSections
            .filter((_, idx) => idx !== firstSectionIndex)
            .sort((a, b) => b.items.length - a.items.length)
            .forEach(s => sections.push(s));

        return sections;
    };

    const iconMap = {
        acting:(
            <svg className="hidden md:block absolute top-4 right-[17.5%] opacity-50 h-9 w-9" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z"/>
            </svg>
        ),
        directing:(
            <svg className="hidden md:block absolute top-4 right-[17.5%] opacity-50 h-9 w-9" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round"
                      d="M10.34 15.84c-.688-.06-1.386-.09-2.09-.09H7.5a4.5 4.5 0 1 1 0-9h.75c.704 0 1.402-.03 2.09-.09m0 9.18c.253.962.584 1.892.985 2.783.247.55.06 1.21-.463 1.511l-.657.38c-.551.318-1.26.117-1.527-.461a20.845 20.845 0 0 1-1.44-4.282m3.102.069a18.03 18.03 0 0 1-.59-4.59c0-1.586.205-3.124.59-4.59m0 9.18a23.848 23.848 0 0 1 8.835 2.535M10.34 6.66a23.847 23.847 0 0 0 8.835-2.535m0 0A23.74 23.74 0 0 0 18.795 3m.38 1.125a23.91 23.91 0 0 1 1.014 5.395m-1.014 8.855c-.118.38-.245.754-.38 1.125m.38-1.125a23.91 23.91 0 0 0 1.014-5.395m0-3.46c.495.413.811 1.035.811 1.73 0 .695-.316 1.317-.811 1.73m0-3.46a24.347 24.347 0 0 1 0 3.46"/>
            </svg>
        ),
        writing: (
            <svg className="hidden md:block absolute top-4 right-[17.5%] opacity-50 h-9 w-9" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25"/>
            </svg>
        ),
        sound: (
            <svg className="hidden md:block absolute top-4 right-[17.5%] opacity-50 h-9 w-9" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m9 9 10.5-3m0 6.553v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32.377a1.803 1.803 0 1 1-.99-3.467l2.31-.66a2.25 2.25 0 0 0 1.632-2.163Zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32.377a1.803 1.803 0 0 1-.99-3.467l2.31-.66A2.25 2.25 0 0 0 9 15.553Z"/>
            </svg>
        ),
        camera: (
             <svg className="hidden md:block absolute top-4 right-[17.5%] opacity-50 h-9 w-9" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z"/>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z"/>
            </svg>
        )
    };
    const formatDate = (dateStr) => dateStr ? new Date(dateStr).toLocaleDateString("pt-PT") : "-";

    return (
        <Body>
            { status === STATUS.LOADING ? (
                <div className="mt-[5vh] h-[86.25vh] md:h-[85vh] bg-primary/30 overflow-auto w-full rounded-md flex justify-center items-center">
                    <div className="spinner"></div>
                </div>
            ) : status === STATUS.NOT_FOUND ? (<ErrorPage code={STATUS.NOT_FOUND} />
            ) : status === STATUS.ERROR ? (<ErrorPage code={STATUS.ERROR} />
            ) : (
                <>
                    {person === null ?
                        <div>Person Not Found</div>
                        :
                        <div className="mt-[5vh] h-[86.25vh] md:h-[85vh] bg-primary/30 overflow-auto w-full rounded-md scrollbar-minimal">

                            <div className="grid grid-cols-12 gap-x-2 px-2 pt-2 relative">
                                {iconMap[person.known_for_department?.toLowerCase()]}
                                <div className="relative col-span-full md:col-span-2 grid grid-cols-4 gap-1">
                                    <img className="col-span-4 w-full shadow-md rounded-md" alt={person.name}
                                         src={person.portrait || DEFAULTS.image}
                                         onError={(e) => e.target.src = DEFAULTS.image}/>
                                </div>

                                <div className="relative col-span-full md:col-span-8 gap-1 pl-2">
                                    <div className="row-span-1 flex flex-col mt-2">
                                        <div className="text-balance text-3xl md:text-4xl font-semibold text-darker-primary">{person.name}</div>
                                        {person.name !== person.original_name &&
                                            <div className="font-semibold md:text-xl text-darker-primary">{person.original_name}</div>
                                        }
                                        <div className="mt-2 md:mt-0 text-darker-primary">{person.pob}</div>
                                        { person.known_for_department &&
                                            <div className="my-2">Known for {person.known_for_department}</div>
                                        }
                                    </div>

                                    {person.biography &&
                                        <div className="my-4 md:mt-0 h-42 md:h-74 text-base overflow-auto scrollbar-minimal">{person.biography}</div>
                                    }
                                </div>

                                <div className="mt-2 md:mt-0 relative col-span-full md:col-span-2 grid grid-rows-3 gap-1">
                                    {person.birthday &&
                                        <div className="p-2 row-span-1 grid grid-cols-4 gap-1 text-center bg-secondary/50 rounded-md border-2 border-tealish/50">
                                            <div className="col-span-full text-base border-b border-tealish/25">{person.age}</div>

                                            <div className={`mt-2 text-base font-semibold ${person.deathday ? "col-span-2" : "col-span-full"}`}>Birthday
                                            </div>

                                            {person.deathday && (
                                                <div className="mt-2 text-base font-semibold col-span-2">Deathday</div>
                                            )}

                                            <div className={`-mt-4 text-lg md:text-xl flex justify-center items-center ${person.deathday ? "col-span-2" : "col-span-full"}`}>
                                                {formatDate (person.birthday)}
                                            </div>

                                            {person.deathday && (
                                                <div className="-mt-4 text-lg md:text-xl flex justify-center items-center col-span-2">
                                                    {formatDate (person.deathday)}
                                                </div>
                                            )}
                                        </div>
                                    }

                                    <div className="bg-secondary/50 row-span-2 grid grid-cols-1 justify-center items-center rounded-md border-2 border-tealish/50">
                                        {personStats &&
                                            <RadarChart title="Person Stats" data={personStats} />
                                        }
                                    </div>

                                    <div className="row-span-1 flex justify-center items-center bg-secondary/50 rounded-md border-2 border-tealish/50">
                                        <div className="col-span-full grid grid-cols-2 flex-grow justify-center items-center p-2">
                                            <div className="flex justify-center items-center">
                                                <a href={`https://imdb.com/name/${person.imdb_id}`}
                                                   target="_blank" rel="noopener noreferrer">
                                                    <img src={LOGOS.imdb} alt="IMDb" className="w-12 transform hover:scale-110 transition ease-in-out duration-200"/>
                                                </a>
                                            </div>
                                            <div
                                                className="flex justify-center items-center border-l border-tealish/25">
                                                <a href={`https://www.themoviedb.org/person/${person.id}`} target="_blank" rel="noopener noreferrer">
                                                    <img src={LOGOS.tmdb} alt="TMDB" className="w-12 transform hover:scale-110 transition ease-in-out duration-200"/>
                                                </a>
                                            </div>
                                        </div>
                                    </div>

                                </div>

                                <div className="col-span-full">
                                     {getSections().map((section, idx) => (
                                        <div key={section.title} className="mt-2">
                                            <div className="text-xl font-semibold border-b border-accent">{section.title}</div>
                                            <div className="flex overflow-auto scrollbar-minimal space-x-2 py-2 px-1">
                                                {section.items.map(film => (
                                                    <div key={`${film.film_id}-${section.title}`}
                                                         className="relative flex-shrink-0 flex flex-col items-center text-center overflow-visible group">
                                                        <Link to={`/film/${film.film_id}`}>
                                                            <img className="card w-28 md:w-36"
                                                                 src={film.poster || DEFAULTS.image}
                                                                 alt={film.name}
                                                                 onError={(e) => e.target.src = DEFAULTS.image}/>
                                                        </Link>
                                                        <div className="text-base mt-1 font-semibold">{formatDate(film.pt_release_date)}</div>
                                                        {film.upcoming &&
                                                            <div
                                                                className="text-xs bg-accent/75 text-white absolute top-1 right-1 items-center justify-center p-1 md:p-2 rounded-full">Upcoming</div>
                                                        }
                                                        {film.in_cinemas &&
                                                            <div className="text-xs bg-darker-primary/75 text-white absolute top-1 right-1 items-center justify-center p-1 md:p-2 rounded-full">Now Showing</div>
                                                        }
                                                        {film.character &&
                                                            <div className="hidden group-hover:block absolute bottom-8 text-xs md:text-sm font-semibold bg-secondary/75 py-0.5 md:py-1.5 px-1 md:px-2 rounded-md">{film.character}</div>
                                                        }
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                     ))}
                                </div>



                            </div>


                        </div>
                    }
                </>
            )}
        </Body>
    );
}