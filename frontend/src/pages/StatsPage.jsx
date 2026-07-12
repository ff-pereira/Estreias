import {Link, useParams} from "react-router-dom";
import {useEffect, useRef, useState} from "react";

import WorldMap from "../map/Map.jsx";
import ErrorPage from "./ErrorPage.jsx";
import Body from "../components/Body.jsx";
import PieChart from "../components/PieChart.jsx";
import {useApi} from "../contexts/ApiProvider.jsx";
import TopPersons from "../components/TopPersons.jsx";
import ColumnChart from "../components/ColumnChart.jsx";

import { STATUS } from "../constants/status.jsx";
import { MONTH_NAMES } from "../constants/options.jsx";
import { FLAGS, DEFAULTS } from "../constants/assets.jsx";


/**
 * @author ffpereira
 */
export default function StatsPage({ type }) {
    const api = useApi();
    const { detail_id } = useParams();
    const scrollContainerRef = useRef(null);

    const [stats, setStats] = useState();
    const [detail, setDetail] = useState();

    function getTypeTitle(type) {
        const customTitles = {
            pt_release_year: "Portuguese Release Year",
            release_year: "Year",
            content_rating: "Content Rating",
            stats: "Total Stats",
            month: "Portuguese Release Month"
        };

        if (customTitles[type]) return customTitles[type];

        return type
            .split("_")
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");
    }

    const yearIcon = (<svg className="absolute right-4 w-6 h-6 md:w-8 md:h-8 text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5"/>
        </svg>)
    const iconMap = {
        stats:(
            <svg className="absolute right-4 w-6 h-6 md:w-8 md:h-8 text-dark-primary" fill="#5a6256" viewBox="0 0 24 24" strokeWidth="0.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z"/>
            </svg>
        ),
        language: (
            <svg className="absolute right-4 w-6 h-6 md:w-8 md:h-8 text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m10.5 21 5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 0 1 6-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 0 1-3.827-5.802"/>
            </svg>
        ),
        distributor: (
            <svg className="absolute right-4 w-6 h-6 md:w-8 md:h-8 text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 20.25h12m-7.5-3v3m3-3v3m-10.125-3h17.25c.621 0 1.125-.504 1.125-1.125V4.875c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125Z"/>
            </svg>
        ),
        genre: (
             <svg className="absolute right-4 w-6 h-6 md:w-8 md:h-8 text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.53 16.122a3 3 0 0 0-5.78 1.128 2.25 2.25 0 0 1-2.4 2.245 4.5 4.5 0 0 0 8.4-2.245c0-.399-.078-.78-.22-1.128Zm0 0a15.998 15.998 0 0 0 3.388-1.62m-5.043-.025a15.994 15.994 0 0 1 1.622-3.395m3.42 3.42a15.995 15.995 0 0 0 4.764-4.648l3.876-5.814a1.151 1.151 0 0 0-1.597-1.597L14.146 6.32a15.996 15.996 0 0 0-4.649 4.763m3.42 3.42a6.776 6.776 0 0 0-3.42-3.42"/>
            </svg>
        ),
        content_rating: (
            <svg className="absolute right-4 w-6 h-6 md:w-8 md:h-8 text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Zm6-10.125a1.875 1.875 0 1 1-3.75 0 1.875 1.875 0 0 1 3.75 0Zm1.294 6.336a6.721 6.721 0 0 1-3.17.789 6.721 6.721 0 0 1-3.168-.789 3.376 3.376 0 0 1 6.338 0Z"/>
            </svg>
        ),
        release_year: yearIcon,
        pt_release_year: yearIcon,
        month: yearIcon,
        runtime: (
            <svg className="absolute right-4 w-6 h-6 md:w-8 md:h-8 text-dark-primary" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
            </svg>

        )
    };

    useEffect(() => {
        if (scrollContainerRef.current) scrollContainerRef.current.scrollTo({top: 0, behavior: "smooth",});
    }, [type, detail_id]);

    useEffect(() => {
        if (type === "stats") {
            document.title = "Estreias - Total Stats";
            return
        }

        if (type === "month") {
            setDetail({ name: MONTH_NAMES[Number(detail_id) - 1] });
            document.title = `Estreias - Month: ${MONTH_NAMES[Number(detail_id) - 1]}`;
            return;
        } else if (type === "content_rating" || type === "runtime" || type === "release_year" || type === "pt_release_year" || type === "distributor") {
            setDetail({name: detail_id});
            document.title = `Estreias - ${getTypeTitle(type)}: ${detail_id}`
            return;
        }

        (async () => {
            try{
                const response = await api.get(`/${type}/${detail_id}`);
                if (response.ok) {
                    setDetail(response.body);
                    if(type === "genre" || type === "language" || type === "country") document.title = `Estreias - ${getTypeTitle(type)}: ${response.body.name}`;
                    else document.title = `Estreias - ${type.charAt(0).toUpperCase() + type.slice(1)}: ${detail_id}`;
                } else{
                    setDetail(null);
                }
            } catch {
                setDetail(null);
            }

        })();
    }, [api, type, detail_id]);

    useEffect(() => {
        let formattedId = detail_id
        if(type === "content_rating") formattedId = detail_id.replaceAll("/", "-");

        let url = `/stats`;
        if(type !== "stats") url = `/stats?${type}=${formattedId}`;

        (async () => {
            try {
                const response = await api.get(url);
                if (response.ok) {
                    setStats(response.body);
                } else{
                    setStats(null);
                }
            } catch {
                setStats(null);
            }
        })();
    }, [api, type, detail_id]);

    return (
        <Body>
            {stats === undefined ? (
                <div className="mt-[5vh] h-[86.25vh] md:h-[85vh] bg-primary/30 w-full rounded-md flex justify-center items-center">
                    <div className="spinner"></div>
                </div>
            ) : (
                <>
                    {stats === null ? (
                        <ErrorPage code={STATUS.ERROR}/>
                    ) :
                        <div className="mt-[5vh] h-[86.25vh] md:h-[85vh] bg-primary/30 w-full rounded-md flex flex-col border-b border-primary/30">

                            <div className="relative col-span-full flex justify-center items-center py-1 bg-tealish/50 border-b-3 border-tealish text-center rounded-t-md">
                                <div className="hidden md:inline text-dark-primary absolute left-4 tracking-tighter text-4xl">estreias</div>
                                { type === "stats" ? <div className="text-xl md:text-3xl text-dark-primary font-bold">Total Stats</div> : detail &&(
                                    <div className="text-xl md:text-3xl text-dark-primary font-bold">{getTypeTitle(type)}: {detail.name}</div>
                                )}

                                {(detail || type === "stats") && (
                                    type === "country"
                                        ? <img className="absolute right-4 h-6 md:h-8 w-auto rounded-sm" src={detail.flag} alt="flag"/>
                                        : (iconMap[type] || iconMap.stats)
                                )}

                            </div>

                            <div ref={scrollContainerRef} className="flex-1 overflow-auto scrollbar-minimal">
                                <div className="grid grid-cols-12 gap-2 px-2 pt-2 text-darker-primary">

                                    <div className="col-span-full grid grid-cols-4 gap-2 p-2">
                                        <div className="col-span-full md:col-span-1 flex flex-col justify-center items-center
                                        border-b md:border-b-0 border-primary/25 pb-4 md:pb-0">
                                            <div className="text-8xl md:text-9xl">{stats.total.released}</div>
                                            <div className="">Films Released in PT cinemas since 2012</div>
                                        </div>

                                        <div className="pt-2 md:pt-0 col-span-full md:col-span-3 grid grid-cols-6 gap-2">

                                            <div className="col-span-full grid grid-cols-2 md:grid-cols-4 gap-2 justify-center items-center">
                                                <div className="flex flex-col justify-center items-center relative border-r md:border-r-0 border-primary/25">
                                                    <div className="text-4xl">{stats.total.genres}</div>
                                                    <div className="text-sm md:text-base">Genres</div>
                                                    <svg className="absolute top-0 left-0 md:left-auto md:right-[28%] opacity-50 h-8 w-8"
                                                         fill="none" viewBox="0 0 24 24"
                                                         strokeWidth="1.5" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round"
                                                              d="M9.53 16.122a3 3 0 0 0-5.78 1.128 2.25 2.25 0 0 1-2.4 2.245 4.5 4.5 0 0 0 8.4-2.245c0-.399-.078-.78-.22-1.128Zm0 0a15.998 15.998 0 0 0 3.388-1.62m-5.043-.025a15.994 15.994 0 0 1 1.622-3.395m3.42 3.42a15.995 15.995 0 0 0 4.764-4.648l3.876-5.814a1.151 1.151 0 0 0-1.597-1.597L14.146 6.32a15.996 15.996 0 0 0-4.649 4.763m3.42 3.42a6.776 6.776 0 0 0-3.42-3.42"/>
                                                    </svg>
                                                </div>

                                                <div className="flex flex-col justify-center items-center relative">
                                                    <div className="text-4xl">{stats.total.languages}</div>
                                                    <div className="text-sm md:text-base">Languages</div>
                                                    <svg className="absolute top-0 right-0 md:right-[28%] opacity-50 h-8 w-8"
                                                         fill="none" viewBox="0 0 24 24"
                                                         strokeWidth="1.5" stroke="currentColor">
                                                    <path strokeLinecap="round" strokeLinejoin="round" d="m10.5 21 5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 0 1 6-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 0 1-3.827-5.802"/>
                                                    </svg>
                                                </div>

                                                <div className="flex flex-col justify-center items-center relative border-r md:border-r-0 border-primary/25">
                                                    <div className="text-4xl">{stats.total.countries}</div>
                                                    <div className="text-sm md:text-base">Countries</div>
                                                    <svg className="absolute top-0 left-0 md:left-auto md:right-[28%] opacity-50 h-8 w-8" fill="none" viewBox="0 0 24 24"
                                                         strokeWidth="1.5" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round"
                                                              d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
                                                        <path strokeLinecap="round" strokeLinejoin="round"
                                                              d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z"/>
                                                    </svg>
                                                </div>

                                                <div className="flex flex-col justify-center items-center relative">
                                                    <div className="text-4xl">{stats.total.distributors}</div>
                                                    <div className="text-sm md:text-base">Distributors</div>
                                                    <svg className="absolute top-0 right-0 md:right-[28%] opacity-50 h-8 w-8" fill="none" viewBox="0 0 24 24"
                                                         strokeWidth="1.5" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round"
                                                              d="M6 20.25h12m-7.5-3v3m3-3v3m-10.125-3h17.25c.621 0 1.125-.504 1.125-1.125V4.875c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125Z"/>
                                                    </svg>
                                                </div>
                                            </div>

                                            <div className="col-span-full grid grid-cols-2 md:grid-cols-5 gap-2 justify-center items-center">
                                                <div className="col-span-full md:col-span-1 flex flex-col justify-center items-center relative">
                                                    <div className="text-4xl">{stats.total.actors}</div>
                                                    <div className="text-sm md:text-base">Actors</div>
                                                    <svg className="hidden md:block absolute top-0 right-1/8 opacity-50 h-8 w-8" fill="none" viewBox="0 0 24 24"
                                                         strokeWidth="1.5" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round"
                                                              d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z"/>
                                                    </svg>
                                                </div>

                                                <div className="flex flex-col justify-center items-center relative  border-r md:border-r-0 border-primary/25">
                                                    <div className="text-4xl">{stats.total.directors}</div>
                                                    <div className="text-sm md:text-base">Directors</div>
                                                    <svg className="absolute top-0 left-0 md:left-auto md:right-1/6 opacity-50 h-8 w-8" fill="none" viewBox="0 0 24 24"
                                                         strokeWidth="1.5" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round"
                                                              d="M10.34 15.84c-.688-.06-1.386-.09-2.09-.09H7.5a4.5 4.5 0 1 1 0-9h.75c.704 0 1.402-.03 2.09-.09m0 9.18c.253.962.584 1.892.985 2.783.247.55.06 1.21-.463 1.511l-.657.38c-.551.318-1.26.117-1.527-.461a20.845 20.845 0 0 1-1.44-4.282m3.102.069a18.03 18.03 0 0 1-.59-4.59c0-1.586.205-3.124.59-4.59m0 9.18a23.848 23.848 0 0 1 8.835 2.535M10.34 6.66a23.847 23.847 0 0 0 8.835-2.535m0 0A23.74 23.74 0 0 0 18.795 3m.38 1.125a23.91 23.91 0 0 1 1.014 5.395m-1.014 8.855c-.118.38-.245.754-.38 1.125m.38-1.125a23.91 23.91 0 0 0 1.014-5.395m0-3.46c.495.413.811 1.035.811 1.73 0 .695-.316 1.317-.811 1.73m0-3.46a24.347 24.347 0 0 1 0 3.46"/>
                                                    </svg>
                                                </div>

                                                <div className="flex flex-col justify-center items-center relative">
                                                    <div className="text-4xl">{stats.total.writers}</div>
                                                    <div className="text-sm md:text-base">Writers</div>
                                                    <svg className="absolute top-0 right-0 md:right-1/6 opacity-50 h-8 w-8" fill="none"
                                                         viewBox="0 0 24 24"
                                                         strokeWidth="1.5" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round"
                                                              d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25"/>
                                                    </svg>
                                                </div>

                                                <div className="flex flex-col justify-center items-center relative  border-r md:border-r-0 border-primary/25">
                                                    <div className="text-4xl">{stats.total.composers}</div>
                                                    <div className="text-sm md:text-base">Composers</div>
                                                    <svg className="absolute top-0 left-0 md:left-auto md:right-1/6 opacity-50 h-8 w-8" fill="none"
                                                         viewBox="0 0 24 24"
                                                         strokeWidth="1.5" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round"
                                                              d="m9 9 10.5-3m0 6.553v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32.377a1.803 1.803 0 1 1-.99-3.467l2.31-.66a2.25 2.25 0 0 0 1.632-2.163Zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32.377a1.803 1.803 0 0 1-.99-3.467l2.31-.66A2.25 2.25 0 0 0 9 15.553Z"/>
                                                    </svg>
                                                </div>

                                                <div className="flex flex-col justify-center items-center relative">
                                                    <div className="text-4xl">{stats.total.cinematographers}</div>
                                                    <div className="text-sm md:text-base">Cinematographers</div>
                                                    <svg className="absolute top-0 right-0 md:right-1/6 opacity-50 h-8 w-8" fill="none"
                                                         viewBox="0 0 24 24"
                                                         strokeWidth="1.5" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round"
                                                              d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z"/>
                                                        <path strokeLinecap="round" strokeLinejoin="round"
                                                              d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z"/>
                                                    </svg>
                                                </div>

                                            </div>

                                        </div>
                                    </div>

                                    <div className="col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50 grid grid-cols-6 gap-2 p-2">
                                        <div className="hidden md:block col-span-5">
                                            <ColumnChart type="pt_release_year" additionalStyles="rounded-t-md"
                                                title="Films by year released in PT" height={250}
                                                categories={stats.grouped.releases_by_year.map(item => item.year)}
                                                countData={stats.grouped.releases_by_year.map(item => item.count)}
                                                avgRuntimeData={stats.grouped.releases_by_year.map(item => Number(item.avg_runtime))}
                                            />
                                            <ColumnChart type="month" additionalStyles="rounded-b-md"
                                                title="Films by month released" height={250}
                                                categories={stats.grouped.releases_by_month.map(item => item.month)}
                                                countData={stats.grouped.releases_by_month.map(item => item.count)}
                                                avgRuntimeData={stats.grouped.releases_by_month.map(item => Number(item.avg_runtime))}
                                            />
                                        </div>

                                        <div className="col-span-full md:col-span-1 grid grid-cols-2 md:grid-cols-1 gap-2 justify-center items-center">
                                            <div className="flex flex-col justify-center items-center col-span-2 md:col-span-1">
                                                <div className="text-4xl">{stats.total.upcoming}</div>
                                                <div className="text-sm md:text-base">Upcoming Releases</div>
                                            </div>
                                            <div className="flex flex-col justify-center items-center pb-2 md:pb-0">
                                                <div className="text-4xl">{stats.total.only_portugal}</div>
                                                <div className="text-sm md:text-base">PT Only Films</div>
                                                <img className="mt-2 w-10 md:w-12 rounded-sm shadow-md" src={FLAGS.pt} alt="Portuguese Flag"/>
                                            </div>
                                            <div className="flex flex-col justify-center items-center pb-2 md:pb-0">
                                                <div className="text-4xl">{stats.total.with_portugal}</div>
                                                <div className="text-sm md:text-base">PT Collaboration Films</div>
                                                <div className="flex gap-2">
                                                    <img className="mt-2 w-10 md:w-12 rounded-sm shadow-md" src={FLAGS.pt} alt="Portuguese Flag"/>
                                                    <img className="mt-2 w-10 md:w-12 rounded-sm shadow-md" src={FLAGS.eu} alt="European Union Flag"/>
                                                </div>

                                            </div>
                                        </div>

                                    </div>

                                    <div className="col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50 grid grid-cols-6 gap-2 p-2">
                                        <div className="hidden md:block col-span-5">
                                            <WorldMap films_by_country={stats.grouped.films_by_country}/>
                                        </div>

                                        <div className="col-span-full md:col-span-1 grid grid-rows-11 md:grid-rows-12 justify-center items-center  pb-2 md:pb-0">
                                            <div className="font-semibold md:text-xl text-center border-b-2 border-tealish/25 mb-2 md:mb-0">Top 10 Countries</div>
                                            {stats.grouped.films_by_country.filter(country => country.count > 0).slice(0, 10).map(country => (
                                                <div key={`${country.country_id}-top10country`} className="flex gap-1">
                                                    <Link className="text-center hover-text"
                                                          to={`/country/${country.country_id}`}>
                                                          {country.flag_url && <img src={country.flag_url} alt="flag" className="h-5 w-auto inline-block rounded-sm mr-2" />}
                                                          {country.country_name}
                                                    </Link>
                                                    <div className="font-semibold">&nbsp;&nbsp;{country.count}</div>
                                                </div>
                                            ))}
                                        </div>

                                    </div>

                                    <div className="col-span-full grid grid-cols-4 md:grid-cols-12 gap-1 md:gap-2 bg-secondary/50 rounded-md border-2 border-tealish/50 p-2">
                                        <div className="col-span-full font-semibold md:text-xl text-center border-b-2 border-tealish/25">Most Popular Films</div>
                                        {stats.top.popular.map(film => (
                                            <div key={film.id} className="relative col-span-1 flex-shrink-0 flex flex-col items-center overflow-visible group">
                                                <Link to={`/film/${film.id}`}>
                                                    <img className="card" alt={film.title} src={film.poster || DEFAULTS.image} onError={(e) => e.target.src = DEFAULTS.image}/>
                                                </Link>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="hidden md:block col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50 p-2">
                                        <div className="col-span-full font-semibold text-xl text-center border-b-2 border-tealish/25">Films by Year</div>

                                        <div className="mt-2">
                                            <ColumnChart type="release_year" additionalStyles="rounded-md"
                                                title="Films by Year" height={500}
                                                categories={stats.grouped.films_by_year.map(item => item.year)}
                                                countData={stats.grouped.films_by_year.map(item => item.count)}
                                                avgRuntimeData={stats.grouped.films_by_year.map(item => Number(item.avg_runtime))}
                                            />
                                        </div>

                                    </div>


                                    <div className="hidden md:block col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50 grid grid-cols-6 gap-2 p-2">
                                        <div className="col-span-full font-semibold text-xl text-center border-b-2 border-tealish/25">Films by Genre</div>

                                        <div className="col-span-full grid grid-cols-2 gap-2 justify-center items-center">
                                            <div className="flex flex-col justify-center items-center">
                                                <div className="text-4xl">{stats.total.animation_films}
                                                    <span className="text-xl ml-2">({stats.total.percentage_animation_films}%)</span>
                                                </div>
                                                <div className="">Animated</div>
                                            </div>
                                            <div className="flex flex-col justify-center items-center">
                                                <div className="text-4xl">{stats.total.documentary_films}
                                                    <span
                                                        className="text-xl ml-2">({stats.total.percentage_documentary_films}%)</span>
                                                </div>
                                                <div className="">Documentaries</div>
                                            </div>
                                        </div>
                                        <div className="col-span-full">
                                            <ColumnChart type="genre" additionalStyles="rounded-md"
                                                title="Films by Genre" height={275}
                                                idMap={Object.fromEntries(stats.grouped.films_by_genre.map(item => [item.genre_name, item.genre_id]))}
                                                categories={stats.grouped.films_by_genre.map(item => item.genre_name)}
                                                countData={stats.grouped.films_by_genre.map(item => item.count)}
                                                avgRuntimeData={stats.grouped.films_by_genre.map(item => Number(item.avg_runtime))}
                                            />
                                        </div>

                                    </div>

                                    <div className="col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50 grid grid-cols-2 md:grid-cols-4 gap-2 p-2">
                                        <div className="col-span-full md:col-span-1">
                                            <TopPersons title="Male Directors" data={stats.top_crew_by_gender.director["2"]}/>
                                        </div>

                                        <div className="col-span-full md:col-span-1">
                                            <TopPersons title="Female Directors" data={stats.top_crew_by_gender.director["1"]}/>
                                        </div>

                                        <div className="col-span-2 grid grid-cols-3 gap-2 justify-center items-center text-center">
                                            <div className="col-span-full grid grid-cols-2">
                                                <div className="flex flex-col justify-center items-center">
                                                    <div className="text-sm md:text-base">Total Directing Credits</div>
                                                    <div className="text-3xl md:text-4xl font-semibold">{stats.total.director_credits}</div>
                                                </div>
                                                <div className="flex flex-col justify-center items-center">
                                                    <div className="hidden md:inline">Average Credits per Director</div>
                                                    <div className="md:hidden text-sm">Avg Credits per Director</div>
                                                    <div className="text-3xl md:text-4xl font-semibold">{stats.total.avg_credits_per_director}</div>
                                                </div>
                                            </div>

                                            <div className="col-span-3 grid grid-cols-2 md:grid-cols-3 gap-2">
                                                <div className="col-span-full md:col-span-1 flex flex-col justify-center items-center">
                                                    <div className="text-sm md:text-base">Female Directed Films</div>
                                                    <div
                                                        className="text-3xl md:text-4xl font-semibold">{stats.total.female_directed} </div>
                                                    <div className="text-lg md:text-2xl">({stats.total.percentage_female_directed}%)
                                                    </div>
                                                </div>

                                                <div className="flex flex-col justify-center items-center">
                                                    <div className="text-sm md:text-base">Directors with just one credit</div>
                                                    <div
                                                        className="text-3xl md:text-4xl font-semibold">{stats.total.directors_with_one_film}</div>
                                                    <div
                                                        className="text-lg md:text-2xl">({stats.total.percentage_directors_with_one_film}%)
                                                    </div>
                                                </div>

                                                <div className="flex flex-col justify-center items-center">
                                                    <div className="text-sm md:text-base">Directors with multiple credits</div>
                                                    <div
                                                        className="text-3xl md:text-4xl font-semibold">{stats.total.directors_with_multiple_films} </div>
                                                    <div
                                                        className="text-lg md:text-2xl">({stats.total.percentage_directors_with_multiple_films}%)
                                                    </div>
                                                </div>


                                            </div>


                                        </div>
                                    </div>

                                    <div className="col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50 grid grid-cols-2 md:grid-cols-4 gap-2 p-2 text-center">
                                        <div className="col-span-full md:col-span-1 order-1 md:order-2">
                                            <TopPersons title="Actors" data={stats.top_actors_by_gender["2"]}/>
                                        </div>

                                        <div className="col-span-full md:col-span-1 order-2 md:order-2">
                                            <TopPersons title="Actresses" data={stats.top_actors_by_gender["1"]}/>
                                        </div>


                                        <div className="col-span-2 grid grid-cols-2 gap-2 justify-center items-center order-3 md:order-1">
                                            <div className="flex flex-col justify-center items-center">
                                                <div className="text-sm md:text-base">Total Acting Performances</div>
                                                <div
                                                    className="text-3xl md:text-4xl font-semibold">{stats.total.actor_performances}</div>
                                            </div>
                                            <div className="flex flex-col justify-center items-center">
                                                <div className="text-sm md:text-base">Average Performances per Actor
                                                </div>
                                                <div
                                                    className="text-3xl md:text-4xl font-semibold">{stats.total.avg_performances_per_actor}</div>
                                            </div>

                                            <div className="flex flex-col justify-center items-center">
                                                <div className="text-sm md:text-base">Actors with just one credit</div>
                                                <div
                                                    className="text-3xl md:text-4xl font-semibold">{stats.total.actors_with_one_film}</div>
                                                <div
                                                    className="text-lg md:text-2xl">({stats.total.percentage_actors_with_one_film}%)
                                                </div>
                                            </div>

                                            <div className="flex flex-col justify-center items-center">
                                                <div className="text-sm md:text-base">Actors with multiple credits</div>
                                                <div
                                                    className="text-3xl md:text-4xl font-semibold">{stats.total.actors_with_multiple_films} </div>
                                                <div
                                                    className="text-lg md:text-2xl">({stats.total.percentage_actors_with_multiple_films}%)
                                                </div>
                                            </div>

                                            <div className="flex flex-col justify-center items-center">
                                                <div className="text-sm md:text-base">Voice Acting Performances</div>
                                                <div
                                                    className="text-3xl md:text-4xl font-semibold">{stats.total.voice_performances} </div>
                                                <div
                                                    className="text-lg md:text-2xl">({stats.total.percentage_voice_performances}%)
                                                </div>
                                            </div>

                                            <div className="flex flex-col justify-center items-center">
                                                <div className="text-sm md:text-base">Uncredited Performances</div>
                                                <div
                                                    className="text-3xl md:text-4xl font-semibold">{stats.total.uncredited_performances} </div>
                                                <div
                                                    className="text-lg md:text-2xl">({stats.total.percentage_uncredited_performances}%)
                                                </div>
                                            </div>

                                        </div>

                                    </div>

                                    <div className="hidden md:grid md:grid-cols-2 col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50">
                                        <div className="col-span-full">
                                            <ColumnChart type="language" additionalStyles="rounded-t-md"
                                                         title="Films by Top 10 Lanuages" height={275}
                                                         idMap={Object.fromEntries(stats.grouped.films_by_language.map(item => [item.language, item.language_id]))}
                                                categories={stats.grouped.films_by_language.map(item => item.language)}
                                                countData={stats.grouped.films_by_language.map(item => item.count)}
                                                avgRuntimeData={stats.grouped.films_by_language.map(item => Number(item.avg_runtime))}
                                            />
                                        </div>


                                        <PieChart
                                            title="Films by Content Rating" height={275}
                                            labels={stats.grouped.films_by_content_rating.map(item => item.content_rating)}
                                            countData={stats.grouped.films_by_content_rating.map(item => item.count)}
                                            avgRuntimeData={stats.grouped.films_by_content_rating.map(item => Number(item.avg_runtime))}
                                        />

                                        <ColumnChart type="distributor"
                                            title="Films by Top 5 Distributors" height={320}
                                            categories={stats.grouped.films_by_distributor.map(item => item.distributor)}
                                            countData={stats.grouped.films_by_distributor.map(item => item.count)}
                                            avgRuntimeData={stats.grouped.films_by_distributor.map(item => Number(item.avg_runtime))}
                                        />

                                        <div className="col-span-full">
                                            <ColumnChart type="runtime" additionalStyles="rounded-b-md"
                                                title="Films by Runtime" height={275}
                                                categories={stats.grouped.films_by_runtime.map(item => item.runtime_range)}
                                                countData={stats.grouped.films_by_runtime.map(item => item.count)}
                                                avgRuntimeData={stats.grouped.films_by_runtime.map(item => Number(item.avg_runtime))}
                                            />
                                        </div>

                                    </div>

                                    <div
                                        className="col-span-full bg-secondary/50 rounded-md border-2 border-tealish/50 grid grid-cols-2 md:grid-cols-6 gap-2 p-2 mb-2">
                                        <div
                                            className="hidden md:inline col-span-full font-semibold text-xl text-center border-b-2 border-tealish/25">Top
                                            Crew
                                        </div>

                                        <TopPersons title="Male Writers" size={3}
                                                    data={stats.top_crew_by_gender.writer["2"]}/>
                                        <TopPersons title="Female Writers" size={3}
                                                    data={stats.top_crew_by_gender.writer["1"]}/>
                                        <TopPersons title="Male Composers" size={3}
                                                    data={stats.top_crew_by_gender.composer["2"]}/>
                                        <TopPersons title="Female Composers" size={3}
                                                    data={stats.top_crew_by_gender.composer["1"]}/>
                                        <TopPersons title="Male Cinematographers" size={3} noPadding={true}
                                                    data={stats.top_crew_by_gender.cinematographer["2"]}/>
                                        <TopPersons title="Female Cinematographers" size={3} noPadding={true}
                                                    data={stats.top_crew_by_gender.cinematographer["1"]}/>

                                    </div>

                                    {/*
                                    <div
                                        className="col-span-full         flex sm:flex-col flex-row justify-center items-center border-2 border-accent rounded-xl w-full">
                                        <WorldMap films_by_country={stats.grouped.films_by_country}/>
                                    </div>
                                    */}
                                </div>
                            </div>
                        </div>
                    }
                </>
            )}
        </Body>
    );
}