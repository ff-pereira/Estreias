import {Link} from "react-router-dom";
import {useEffect, useState} from "react";

import ErrorPage from "../pages/ErrorPage.jsx";
import PortugalMap from "../map/PortugalMap.jsx";
import {useApi} from "../contexts/ApiProvider.jsx";
import {useDebounce} from "../hooks/UseDebounce.jsx";
import InputField from "../components/InputField.jsx";
import CheckboxDropdown from "../components/CheckboxDropdown.jsx";

import {STATUS} from "../constants/status.jsx";


/**
 * @author ffpereira
 */
function buildParams({ name, cities, cinema_groups, film_id, offset }) {
    const params = new URLSearchParams();
    if (name) params.append("name", name);
    if (cities?.length) params.append("cities", cities.join(","));
    if (cinema_groups?.length) params.append("groups", cinema_groups.join(","));
    if (film_id) params.append("film_id", film_id);
    if (offset !== undefined) params.append("offset", offset);
    return params.toString();
}

export default function CinemasPage( {film_id, fullHeight, mapHeight, additionalClasses, additionalClassesTop} ) {
    const api = useApi();
    const [cinemas, setCinemas] = useState();
    const [loading, setLoading] = useState(true);

    const [nameSearch, setNameSearch] = useState('');
    const debouncedNameSearch = useDebounce(nameSearch, 250);

    const [totalCitiesList, setTotalCitiesList] = useState([]);
    const [selectedCities, setSelectedCities] = useState([]);
    const [selectedGroups, setSelectedGroups] = useState([]);

    const [citiesList, setCitiesList] = useState([]);
    const [groupsList, setGroupsList] = useState([]);

    const clearFilters = () => {
        setNameSearch('');
        setSelectedCities([]);
        setSelectedGroups([]);
    };

    useEffect(() => {
        (async () => {
            try {
                const response = await api.get('/cities');
                if (response.ok) {
                    setTotalCitiesList(response.body.data);
                } else {
                    setTotalCitiesList(null);
                }
            } catch {
                setTotalCitiesList(null);
            }

        })();
    }, [api]);

    const fetchList = async (endpoint, setter) => {
        const query = buildParams({
            name: debouncedNameSearch,
            cities: selectedCities,
            cinema_groups: selectedGroups,
            film_id: film_id || undefined,
        });
        try{
            const response = await api.get(`${endpoint}?${query}`);
            setter(response.ok ? response.body.data : []);
        } catch {
            setter([]);
        }

    };

    useEffect(() => {
        fetchList("/portugal_regions", setCitiesList);
        fetchList("/cinema_groups", setGroupsList);
    }, [api, selectedGroups, selectedCities, film_id]);

    useEffect(() => {
        (async () => {
            setLoading(true);

            const params = buildParams({
                name: debouncedNameSearch,
                cities: selectedCities,
                cinema_groups: selectedGroups,
                film_id: film_id || undefined,
            });

            try{
                const response = await api.get(`/cinemas?${params}`);
                if (response.ok) {
                    setCinemas(response.body);
                } else{
                    setCinemas(null);
                }
            } catch{
                setCinemas(null);
            }

            setLoading(false);
        })();
    }, [api, selectedCities, selectedGroups, debouncedNameSearch]);


    return (
        <>
            {cinemas === null ? (
                <ErrorPage code={STATUS.ERROR}/>
            ) : (
                <>
                    {!additionalClassesTop &&
                        <div className="text-dark-primary mt-6 text-center text-2xl w-full border-b border-tealish/25 font-semibold tracking-tight">
                            Now Showing
                        </div>
                    }

                    <div className={`${additionalClassesTop} grid grid-cols-2 md:grid-cols-4 gap-2`}>

                        <div className="col-span-full md:col-span-1">
                            <InputField name="nameSearch" placeholder="Search by name" type="text"
                                        value={nameSearch}
                                        onChange={e => setNameSearch(e.target.value)}></InputField>
                        </div>


                        <CheckboxDropdown label="Filter by city" options={totalCitiesList} selected={selectedCities} setSelected={setSelectedCities}/>

                        <div className="flex mb-2 md:mb-0">
                            <div className="flex-1">
                                <CheckboxDropdown label="Filter by group"
                                                  options={groupsList}
                                                  selected={selectedGroups}
                                                  setSelected={setSelectedGroups}/>
                            </div>
                            {(nameSearch !== '' || selectedCities.length > 0 || selectedGroups.length > 0) &&
                                <button onClick={clearFilters} className="hidden md:flex ml-2 my-4 bg-accent text-white select-none
                                hover-text-colorless cursor-pointer rounded-md p-2 text-center items-center justify-center gap-2">
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12"/>
                                    </svg>
                                    <span>Clear Filters</span>
                                </button>
                            }
                        </div>

                        <div className="hidden md:flex flex-col items-center justify-center flex-1">
                            <div>Total Cinemas</div>
                            <div className="-mt-1 text-2xl font-semibold">
                                {(loading && !cinemas) ? "-" : cinemas.length}
                            </div>
                        </div>
                    </div>

                    {(loading && cinemas===undefined) ? (
                        <div className={`${fullHeight} ${additionalClasses} w-full flex justify-center items-center`}>
                            <div className="spinner"></div>
                        </div>
                    ) : (
                        <div className={`${fullHeight} ${additionalClasses} w-full grid grid-cols-1 md:grid-cols-2 gap-x-2`}>

                        <div className="content-start grid grid-cols-1 2xl:grid-cols-2 gap-1 md:gap-2 h-full overflow-y-auto overflow-x-hidden scrollbar-minimal">
                            {cinemas.map(cinema => (
                                <div key={cinema.id}
                                     className="flex-shrink-0 relative bg-primary/50 col-span-1 overflow-visible group h-16 rounded-md hover:bg-primary/60 tracking-tight hover:shadow-md transform hover:scale-98 transition ease-in-out duration-200">
                                    <Link to={`/cinema/${cinema.id}`}>
                                        <div className="rounded-md w-full h-full p-2 font-semibold">
                                            {cinema.name}
                                            {cinema.group &&
                                                <div
                                                    className="absolute w-16 bottom-0.5 right-0.5 flex justify-center items-center p-2">
                                                    <img src={cinema.brand} alt=""/>
                                                </div>
                                            }
                                        </div>
                                    </Link>
                                </div>
                            ))}
                        </div>

                        {citiesList &&
                            <div className="hidden md:block">
                                <PortugalMap height={mapHeight} cinemas_by_region={citiesList} selectedCities={selectedCities} setSelectedCities={setSelectedCities}/>
                            </div>
                        }
                    </div>
                    )}
                </>
            )}
        </>
    );
}
