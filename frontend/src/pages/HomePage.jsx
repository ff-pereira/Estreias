import {Link} from "react-router-dom";
import { useState, useEffect, useRef } from "react";

import Body from '../components/Body';
import More from '../components/More';
import ErrorPage from "./ErrorPage.jsx";
import { useApi } from '../contexts/ApiProvider';

import { STATUS } from "../constants/status.jsx";
import { DEFAULTS } from "../constants/assets.jsx";


/**
 * @author ffpereira
 */
export default function HomePage() {
    const api = useApi();
    const [items, setItems] = useState([]);

    const [loading, setLoading] = useState(true);
    const [pagination, setPagination] = useState({ offset: 0, limit: 25, total: 0 });
    const [prevOffset, setPrevOffset] = useState(null);
    const [nextOffset, setNextOffset] = useState(null);
    const scrollRef = useRef(null);
    const [isAtTop, setIsAtTop] = useState(true);
    const [isLoadingPrev, setIsLoadingPrev] = useState(false);
    const [isLoadingNext, setIsLoadingNext] = useState(false);

    const url = "/grouped_releases";


    useEffect(() => {
        const scroller = scrollRef.current;
        if (!scroller) return;

        let lastIsAtTop = scroller.scrollTop === 0;
        let rafId = null;

        const updateIsAtTop = () => {
            const atTop = scroller.scrollTop === 0;
            if (atTop !== lastIsAtTop) {
                setIsAtTop(atTop);
                lastIsAtTop = atTop;
            }
            rafId = null;
        };

        const onScroll = () => {
            if (rafId === null) {
                rafId = requestAnimationFrame(updateIsAtTop);
            }
        };

        scroller.addEventListener('scroll', onScroll);

        updateIsAtTop();
        return () => {
            scroller.removeEventListener('scroll', onScroll);
            if (rafId !== null) cancelAnimationFrame(rafId);
        };
    }, []);


    useEffect(() => {
        (async () => {
            setLoading(true);
            try {
                const response = await api.get(url);
                if (response.ok) {
                    setItems(response.body.data);
                    setPagination(response.body.pagination);
                    setPrevOffset(response.body.pagination.offset - response.body.pagination.limit);
                    setNextOffset(response.body.pagination.offset + response.body.pagination.limit);
                } else {
                    setItems(null);
                }
            } catch{
                setItems(null);
            }
            setLoading(false);
        })();
    }, [api, url]);

    const loadPreviousPage = async () => {
        if (prevOffset === null || prevOffset < 0 || isLoadingPrev) return;

        setIsLoadingPrev(true);
        const prevUrl = `${url}?offset=${prevOffset}&limit=${pagination.limit}`;

        try {
            const response = await api.get(prevUrl);
            if (response.ok) {
                setItems(prev => [...response.body.data, ...prev]);
                setPagination(response.body.pagination);

                const scroller = scrollRef.current; // Maintain scroll position
                const prevScrollTop = scroller ? scroller.scrollTop : window.scrollY || document.documentElement.scrollTop;
                const prevScrollHeight = scroller ? scroller.scrollHeight : document.documentElement.scrollHeight;
                requestAnimationFrame(() => {
                    const newScrollHeight = scroller ? scroller.scrollHeight : document.documentElement.scrollHeight;
                    const delta = newScrollHeight - prevScrollHeight;
                    if (scroller) scroller.scrollTop = prevScrollTop + delta;
                    else window.scrollTo(0, prevScrollTop + delta);
                });
                setPrevOffset(prevOffset - pagination.limit);
            }
        } finally {
            setIsLoadingPrev(false);
        }
    };

    const loadNextPage = async () => {
        if (nextOffset === null || nextOffset >= pagination.total || isLoadingNext) return;

        setIsLoadingNext(true);
        const nextUrl = `${url}?offset=${nextOffset}&limit=${pagination.limit}`;

        try {
            const response = await api.get(nextUrl);
            if (response.ok) {
                setItems(prev => [...prev, ...response.body.data]);
                setPagination(response.body.pagination);
                setNextOffset(nextOffset + pagination.limit);
            }
        } finally {
            setIsLoadingNext(false);
        }
    };

    const CommaSeparatedLinks = ({ items, getLink, className }) => (
        <>
            {items.map((item, index) => (
                <span key={item.id || index}>
                    <Link className={className} to={getLink(item)}>{item.name || item}</Link>
                    {index < items.length - 1 && ", "}
                </span>
            ))}
        </>
    );

    useEffect(() => { document.title = "Estreias"; }, []);

    const getTitleClass = (length) => length > 50 ? "text-sm" : length > 40 ? "text-base" : "text-lg";


    return (
        <Body>
            {items === null ? (
                <ErrorPage code={STATUS.ERROR}/>
            ) : (
                <>
                    <div className="mt-4 w-full grid grid-cols-3 gap-3 h-14 text-sm md:text-base">
                        {isAtTop &&
                            <div className="text-xs md:text-base flex justify-start items-center">
                                {prevOffset !== null && prevOffset >= 0 &&
                                    <>
                                        <More pagination={pagination} direction="prev" loadPage={loadPreviousPage} message="Load Previous Releases" />
                                        <span className="ml-3 tracking-tight">Load previous releases</span>
                                    </>
                                }
                            </div>
                        }
                        <div className="col-start-2 text-primary tracking-tighter text-4xl flex justify-center items-center select-none">estreias</div>
                        <div className="mt-6 text-primary flex justify-end items-center">by ffpereira</div>
                    </div>

                    {loading ? (
                        <div ref={scrollRef} className="h-[82.5vh] bg-primary/30 overflow-auto w-full rounded-md flex justify-center items-center">
                            <div className="spinner"></div>
                        </div>
                    ) : (
                        <div ref={scrollRef} className="h-[82.5vh] bg-primary/30 overflow-auto w-full rounded-md scrollbar-minimal">
                            {items.map(films => (
                                <div key={films.date} className="px-3 pb-6 md:pb-10">
                                    <div className="my-2 flex justify-between text-dark-primary border-b-2 border-tealish/50">
                                        <span className="text-lg md:text-xl tracking-tighter">
                                            { films.days_until === 0 ? "Today" :
                                              films.days_until > 0 ? `in ${films.days_until} day${films.days_until > 1 ? 's' : ''}` :
                                              `${Math.abs(films.days_until)} day${Math.abs(films.days_until) > 1 ? 's' : ''} ago`
                                            }
                                        </span>
                                        <span className="text-lg md:text-2xl font-semibold ml-1 md:ml-6">{new Date(films.date).toLocaleDateString("pt-PT")}</span>
                                        <span className="text-lg md:text-xl tracking-tighter">{films.releases.length} releases</span>
                                    </div>
                                    <div className="grid grid-cols-3 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-2 md:gap-7 py-1 px-1">
                                        {films.releases.map(film => (
                                            <div key={film.film_id} className="md:grid md:grid-cols-5 items-center relative overflow-visible h-full">
                                                <Link className="col-span-2" to={`/film/${film.film_id}`}>
                                                    <img className="card2" alt={film.title} src={film.poster || DEFAULTS.image}
                                                         onError={(e) => {e.target.src = DEFAULTS.image}
                                                    }/>
                                                </Link>

                                                <div className="hidden md:flex md:col-span-3 flex-col justify-start items-center h-full tracking-tight">
                                                    <div className={`${getTitleClass(film.title.length)} pl-2 bg-tealish w-full font-semibold rounded-tr-md`}>
                                                        <Link to={`/film/${film.film_id}`} className="inline-block hover-text-colorless">{film.title}</Link>
                                                    </div>
                                                    <div className="pl-2 bg-tealish/85 text-sm w-full">
                                                        <CommaSeparatedLinks items={film.directors} getLink={d => `/person/${d.id}`} className="inline-block hover-text-colorless font-medium"/>
                                                    </div>
                                                    <div className="pl-2 bg-tealish/70 text-sm w-full">
                                                        <Link to={`/release_year/${film.release_year}`} className="inline-block hover-text-colorless">{film.release_year}</Link>
                                                        {film.runtime > 0 &&
                                                            <Link to={`/runtime/${film.runtime}`} className="inline-block hover-text-colorless">&nbsp;&nbsp;|&nbsp;&nbsp;{film.runtime} min</Link>
                                                        }
                                                        {film.content_rating &&
                                                            <Link to={`/content_rating/${encodeURIComponent(film.content_rating)}`} className="inline-block hover-text-colorless">&nbsp;&nbsp;|&nbsp;&nbsp;{film.content_rating}</Link>
                                                        }
                                                    </div>
                                                    <div className="pl-2 bg-tealish/55 text-sm w-full">
                                                        <CommaSeparatedLinks items={film.genres} getLink={g => `/genre/${g.id}`} className="inline-block hover-text-colorless"/>
                                                    </div>
                                                    {film.original_language &&
                                                        <div className="pl-2 bg-tealish/40 text-sm w-full">
                                                            <Link to={`/language/${film.original_language.id}`}
                                                                  className="inline-block hover-text-colorless">{film.original_language.english_name}</Link>
                                                        </div>
                                                    }
                                                    <div className="pl-2 bg-tealish/25 text-sm w-full ">
                                                        <Link to={`/distributor/${film.distributor}`}
                                                              className="inline-block hover-text-colorless">{film.distributor}</Link>
                                                    </div>

                                                    <div className="pl-2 bg-tealish/10 text-sm w-full flex flex-row justify-end gap-1 p-1">
                                                        {film.countries.map(country => (
                                                            <Link to={`/country/${country.id}`} key={`${film.id}-${country.id}`} className="">
                                                                <img src={country.flag} alt={country.name} className="w-6 rounded-xs transform hover:scale-110 transition ease-in-out duration-200"/>
                                                            </Link>
                                                        ))}
                                                    </div>
                                                </div>

                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                            {nextOffset !== null && nextOffset < pagination.total &&
                                <div className="-mt-4 mb-2 flex flex-col justify-center items-center">
                                    <span className="tracking-tight mb-2">Load Next Releases</span>
                                    <More pagination={pagination} direction="next" loadPage={loadNextPage} rotation={270} />
                                </div>
                            }
                        </div>
                    )}
                </>
            )}
        </Body>
    );
}
