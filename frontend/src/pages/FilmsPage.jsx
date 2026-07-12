import {Link} from "react-router-dom";
import {useEffect, useState} from "react";

import ErrorPage from "./ErrorPage.jsx";
import Body from "../components/Body.jsx";
import More from "../components/More.jsx";
import {useApi} from "../contexts/ApiProvider.jsx";
import {useDebounce} from "../hooks/UseDebounce.jsx";
import InputField from "../components/InputField.jsx";
import SortDropdown from "../components/SortDropdown.jsx";
import FiltersDropdown from "../components/FiltersDropdown.jsx";
import CheckboxDropdown from "../components/CheckboxDropdown.jsx";

import { STATUS } from "../constants/status.jsx";
import { DEFAULTS } from "../constants/assets.jsx";
import { FILMS_SORT_OPTIONS } from "../constants/options.jsx";


function buildParams({ sort, sortDir, title, inCinemas, upcoming, genres, countries, distributors, contentRatings, offset }) {
    const params = new URLSearchParams();
    if (sort) params.append("sort", sort);
    if (sortDir) params.append("sort_dir", sortDir);
    if (title) params.append("title", title);
    if (inCinemas) params.append("in_cinemas", "true");
    if (upcoming) params.append("upcoming", "true");
    if (genres?.length) params.append("genres", genres.join(","));
    if (countries?.length) params.append("countries", countries.join(","));
    if (distributors?.length) params.append("distributors", distributors.join(","));
    if (contentRatings?.length) params.append("content_ratings", contentRatings.join(","));
    if (offset !== undefined) params.append("offset", offset);
    return params.toString();
}


/**
 * @author ffpereira
 */
export default function FilmsPage() {
    const api = useApi();
    const [films, setFilms] = useState([]);
    const [loading, setLoading] = useState(true);
    const [pagination, setPagination] = useState({ offset: 0, limit: 60, total: 0 });
    const [nextOffset, setNextOffset] = useState(null);
    const [isLoadingNext, setIsLoadingNext] = useState(false);

    // Filters
    const [sortBy, setSortBy] = useState("pt_release_date");
    const [sortDir, setSortDir] = useState("asc");

    const [titleSearch, setTitleSearch] = useState('');
    const debouncedTitleSearch = useDebounce(titleSearch, 250);
    const [inCinemasFilter, setInCinemasFilter] = useState(false);
    const [upcomingFilter, setUpcomingFilter] = useState(false);
    const [selectedGenres, setSelectedGenres] = useState([]);
    const [selectedCountries, setSelectedCountries] = useState([]);
    const [selectedDistributors, setSelectedDistributors] = useState([]);
    const [selectedContentRatings, setSelectedContentRatings] = useState([]);

    const [genresList, setGenresList] = useState([]);
    const [countriesList, setCountriesList] = useState([]);
    const [distributorsList, setDistributorsList] = useState([]);
    const [contentRatingList, setContentRatingList] = useState([]);

    const url = "/films";
    const alwaysVisible = ["runtime", "budget", "revenue"].includes(sortBy);

    const clearAllFilters = () => {
        setTitleSearch('');
        setInCinemasFilter(false);
        setUpcomingFilter(false);
        setSelectedGenres([]);
        setSelectedCountries([]);
        setSelectedDistributors([]);
        setSelectedContentRatings([]);
    };

    const fetchList = async (endpoint, setter) => {
        const query = buildParams({
            sort: sortBy, sortDir: sortDir,
            title: debouncedTitleSearch,
            inCinemas: inCinemasFilter,
            upcoming: upcomingFilter,
            genres: selectedGenres,
            countries: selectedCountries,
            distributors: selectedDistributors,
            contentRatings: selectedContentRatings,
        });
        const response = await api.get(`${endpoint}?${query}`);
        setter(response.ok ? response.body : []);
    };

    // Fetch filters whenever dependencies change
    useEffect(() => {
        fetchList("/genres", setGenresList);
        fetchList("/countries", setCountriesList);
        fetchList("/distributors", setDistributorsList);
        fetchList("/content_ratings", setContentRatingList);
    }, [api, debouncedTitleSearch, inCinemasFilter, upcomingFilter, selectedGenres, selectedCountries, selectedDistributors, selectedContentRatings]);

    useEffect(() => {
        (async () => {
            setLoading(true);
            setPagination({ offset: 0, limit: 60, total: 0 });

            const params = buildParams({
                sort: sortBy, sortDir: sortDir,
                title: debouncedTitleSearch,
                inCinemas: inCinemasFilter,
                upcoming: upcomingFilter,
                genres: selectedGenres,
                countries: selectedCountries,
                distributors: selectedDistributors,
                contentRatings: selectedContentRatings,
                });

            const response = await api.get(`${url}?${params}`);
            if (response.ok) {
                setFilms(response.body.data);
                setPagination(response.body.pagination);
                setNextOffset(response.body.pagination.offset + response.body.pagination.limit);
            } else{
                setFilms(null);
            }

            setLoading(false);
        })();
    }, [api, debouncedTitleSearch, inCinemasFilter, upcomingFilter, selectedGenres, selectedCountries, selectedDistributors, selectedContentRatings, sortBy, sortDir]);

    const loadNextPage = async () => {
        if (nextOffset === null || nextOffset >= pagination.total || isLoadingNext) return;

        setIsLoadingNext(true);

        const params = buildParams({
            sort: sortBy, sortDir: sortDir,
            title: debouncedTitleSearch,
            inCinemas: inCinemasFilter,
            upcoming: upcomingFilter,
            genres: selectedGenres,
            countries: selectedCountries,
            distributors: selectedDistributors,
            contentRatings: selectedContentRatings,
            offset: nextOffset,
        });

        try {
            const response = await api.get(`${url}?${params}`);
            if (response.ok) {
                setFilms(prev => [...prev, ...response.body.data]);
                setPagination(response.body.pagination);
                setNextOffset(nextOffset + pagination.limit);
            }
        } finally {
            setIsLoadingNext(false);
        }
    };

    useEffect(() => {document.title = "Estreias - Films";}, []);

    return (
        <Body>
            {films === null ? (
                <ErrorPage code={STATUS.ERROR}/>
            ) : (
                <>
                    <div className="mt-6 grid grid-cols-7 md:grid-cols-8 gap-x-2 relative mb-2 md:mb-0">
                        <div className="col-span-3 flex items-center gap-2">
                            <div className="hidden md:flex items-center gap-2 bg-primary/30 p-2 rounded-md text-dark-primary">
                                <svg fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-6 h-6">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0 1 18 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125v-1.5M4.875 8.25C5.496 8.25 6 8.754 6 9.375v1.5m0-5.25v5.25m0-5.25C6 5.004 6.504 4.5 7.125 4.5h9.75c.621 0 1.125.504 1.125 1.125m1.125 2.625h1.5m-1.5 0A1.125 1.125 0 0 1 18 7.125v-1.5m1.125 2.625c-.621 0-1.125.504-1.125 1.125v1.5m2.625-2.625c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125M18 5.625v5.25M7.125 12h9.75m-9.75 0A1.125 1.125 0 0 1 6 10.875M7.125 12C6.504 12 6 12.504 6 13.125m0-2.25C6 11.496 5.496 12 4.875 12M18 10.875c0 .621-.504 1.125-1.125 1.125M18 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m-12 5.25v-5.25m0 5.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125m-12 0v-1.5c0-.621-.504-1.125-1.125-1.125M18 18.375v-5.25m0 5.25v-1.5c0-.621.504-1.125 1.125-1.125M18 13.125v1.5c0 .621.504 1.125 1.125 1.125M18 13.125c0-.621.504-1.125 1.125-1.125M6 13.125v1.5c0 .621-.504 1.125-1.125 1.125M6 13.125C6 12.504 5.496 12 4.875 12m-1.5 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M19.125 12h1.5m0 0c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h1.5m14.25 0h1.5"/>
                                </svg>
                            </div>

                            <div className="flex-1">
                                <InputField name="titleSearch" placeholder="Search by title" type="text"
                                            value={titleSearch}
                                            onChange={e => setTitleSearch(e.target.value)}></InputField>
                            </div>

                        </div>

                        <label className="col-span-2 md:col-span-1 flex flex-col justify-center items-center cursor-pointer hover-text-colorless">
                            <span className="text-xs md:text-base font-semibold text-dark-primary select-none">In Cinemas</span>
                            <input
                                type="checkbox"
                                checked={inCinemasFilter}
                                onChange={e => {
                                    const isChecked = e.target.checked;
                                    setInCinemasFilter(isChecked);
                                    if (isChecked) setUpcomingFilter(false);
                                }}
                                className="accent-primary"
                            />

                        </label>

                        <label className="col-span-2 md:col-span-1 flex flex-col justify-center items-center cursor-pointer hover-text-colorless">
                            <span className="text-xs md:text-base font-semibold text-dark-primary select-none">Upcoming</span>
                            <input
                                type="checkbox"
                                checked={upcomingFilter}
                                onChange={e => {
                                    const isChecked = e.target.checked;
                                    setUpcomingFilter(isChecked);
                                      if (isChecked) setInCinemasFilter(false);
                                    }}
                                className="accent-primary"
                            />
                        </label>

                        <div className="flex col-span-full md:col-span-2 items-center">
                            <div className="block mr-2">
                                <FiltersDropdown clearFilters={clearAllFilters}>
                                    <CheckboxDropdown label="Filter by genres" hideMargins={true}
                                        options={genresList}
                                        selected={selectedGenres}
                                        setSelected={setSelectedGenres}
                                    />
                                    <CheckboxDropdown label="Filter by countries" hideMargins={true}
                                        options={countriesList}
                                        selected={selectedCountries}
                                        setSelected={setSelectedCountries}
                                    />
                                    <CheckboxDropdown label="Filter by distributors" hideMargins={true}
                                        options={distributorsList}
                                        selected={selectedDistributors}
                                        setSelected={setSelectedDistributors}
                                    />
                                    <CheckboxDropdown label="Filter by content rating" hideMargins={true}
                                        options={contentRatingList}
                                        selected={selectedContentRatings}
                                        setSelected={setSelectedContentRatings}
                                    />
                                </FiltersDropdown>
                            </div>

                            <div className="flex-1">
                                <SortDropdown
                                    label="Sort by"
                                    options={FILMS_SORT_OPTIONS}
                                    selected={sortBy}
                                    setSelected={setSortBy}
                                />
                            </div>

                            <div className="block ml-2">
                                <button type="button"
                                        onClick={() => setSortDir(prev => (prev === "asc" ? "desc" : "asc"))}
                                        className="p-2 rounded-full cursor-pointer bg-primary/30 hover:bg-primary/40 flex items-center
                                                 text-dark-primary hover:scale-110 transition ease-in-out duration-200"
                                >
                                    <span className={`transition-transform duration-200 ${sortDir === "desc" ? "rotate-180" : ""}`}>
                                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                                          <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5"/>
                                        </svg>
                                    </span>
                                </button>
                            </div>
                        </div>

                        <div className="hidden md:flex flex-col items-center justify-center">
                            <div>Total Films</div>
                            <div className="-mt-1 text-2xl font-semibold">{loading ? "-" : pagination.total}</div>
                        </div>
                    </div>

                    {loading ? (
                        <div
                            className="h-[74.15vh] md:h-[79.75vh] bg-primary/30 overflow-auto w-full rounded-md flex justify-center items-center">
                            <div className="spinner"></div>
                        </div>
                    ) : (
                        <div className="h-[74.15vh] md:h-[79.75vh] bg-primary/30 overflow-auto w-full p-2 rounded-md scrollbar-minimal">
                            <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-10 2xl:grid-cols-12 gap-1 md:gap-2">
                                {films.map(film => (
                                    <div key={film.id} className="relative col-span-1 flex-shrink-0 flex flex-col items-center overflow-visible group">
                                        <Link to={`/film/${film.id}`}>
                                            <img className="card" alt={film.title} src={film.poster || DEFAULTS.image} onError={(e) => e.target.src = DEFAULTS.image}/>
                                        </Link>
                                        {film.in_cinemas &&
                                            <div className="text-xs bg-darker-primary/75 text-white absolute top-1 right-1 items-center justify-center text-center p-1 md:p-2 rounded-full">Now Showing</div>
                                        }
                                        {film.upcoming &&
                                            <div className="text-xs bg-accent/75 text-white absolute top-1 right-1 items-center justify-center text-center p-1 md:p-2 rounded-full">Upcoming</div>
                                        }
                                        <div className={`absolute bottom-1 right-1 bg-secondary rounded-md p-1.5 text-sm
                                        cursor-text text-center tracking-tighter ${alwaysVisible ? "block" : "hidden group-hover:block"}`}
                                        >
                                            {sortBy === 'release_date' || sortBy === 'pt_release_date' ? new Date(film[sortBy]).toLocaleDateString("pt-PT") :
                                                film[sortBy]
                                            }
                                        </div>
                                    </div>
                                ))}
                                {nextOffset !== null && nextOffset < pagination.total &&
                                    <div className="col-span-full flex justify-center items-center">
                                        <div className="my-2 flex flex-col justify-center items-center">
                                            <span className="tracking-tight mb-2">Load More Films</span>
                                            <More pagination={pagination} direction="next" loadPage={loadNextPage} rotation={270} />
                                        </div>
                                    </div>
                                }
                            </div>
                        </div>
                    )}
                </>
            )}
        </Body>
    );
}