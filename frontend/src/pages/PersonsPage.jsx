import {Link} from "react-router-dom";
import {useEffect, useState} from "react";

import ErrorPage from "./ErrorPage.jsx";
import Body from "../components/Body.jsx";
import More from "../components/More.jsx";
import {useApi} from "../contexts/ApiProvider.jsx";
import {useDebounce} from "../hooks/UseDebounce.jsx";
import InputField from "../components/InputField.jsx";
import SortDropdown from "../components/SortDropdown.jsx";

import { STATUS } from "../constants/status.jsx";
import { DEFAULTS } from "../constants/assets.jsx";
import { ROLE_OPTIONS, GENDER_OPTIONS } from "../constants/options.jsx";


function buildParams({ name, role, gender, offset }) {
    const params = new URLSearchParams();
    if (name) params.append("name", name);
    if (role) params.append("role", role);
    if (gender) params.append("gender", gender)
    if (offset !== undefined) params.append("offset", offset);
    return params.toString();
}

/**
 * @author ffpereira
 */
export default function PersonsPage() {
    const api = useApi();

    const [role, setRole] = useState("Actor");
    const [gender, setGender] = useState(null);
    const url = role === "Actor" ? "/cast" : "/crew";

    const [persons, setPersons] = useState([]);
    const [loading, setLoading] = useState(true);
    const [pagination, setPagination] = useState({ offset: 0, limit: 60, total: 0 });
    const [nextOffset, setNextOffset] = useState(null);
    const [isLoadingNext, setIsLoadingNext] = useState(false);

    const [titleSearch, setTitleSearch] = useState('');
    const debouncedTitleSearch = useDebounce(titleSearch, 250);

    const roleIcons = {
        Actor: (
                <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z"/>
        ),
        Director: (
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.34 15.84c-.688-.06-1.386-.09-2.09-.09H7.5a4.5 4.5 0 1 1 0-9h.75c.704 0 1.402-.03 2.09-.09m0 9.18c.253.962.584 1.892.985 2.783.247.55.06 1.21-.463 1.511l-.657.38c-.551.318-1.26.117-1.527-.461a20.845 20.845 0 0 1-1.44-4.282m3.102.069a18.03 18.03 0 0 1-.59-4.59c0-1.586.205-3.124.59-4.59m0 9.18a23.848 23.848 0 0 1 8.835 2.535M10.34 6.66a23.847 23.847 0 0 0 8.835-2.535m0 0A23.74 23.74 0 0 0 18.795 3m.38 1.125a23.91 23.91 0 0 1 1.014 5.395m-1.014 8.855c-.118.38-.245.754-.38 1.125m.38-1.125a23.91 23.91 0 0 0 1.014-5.395m0-3.46c.495.413.811 1.035.811 1.73 0 .695-.316 1.317-.811 1.73m0-3.46a24.347 24.347 0 0 1 0 3.46"/>
        ),
        Writer: (
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25"/>
        ),
        Composer: (
                <path strokeLinecap="round" strokeLinejoin="round" d="m9 9 10.5-3m0 6.553v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32.377a1.803 1.803 0 1 1-.99-3.467l2.31-.66a2.25 2.25 0 0 0 1.632-2.163Zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32.377a1.803 1.803 0 0 1-.99-3.467l2.31-.66A2.25 2.25 0 0 0 9 15.553Z"/>
        ),
        Cinematographer: (
            <>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z"/>
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z"/>
            </>
        )
    }


    useEffect(() => {
        (async () => {
            setLoading(true);

            setPagination({ offset: 0, limit: 60, total: 0 });
            setNextOffset(null);

            const params = buildParams({
                name: debouncedTitleSearch,
                role: role,
                gender: gender,
            })
            const response = await api.get(`${url}?${params}`);
            if (response.ok) {
                setPersons(response.body.data);
                setPagination(response.body.pagination);
                setNextOffset(response.body.pagination.offset + response.body.pagination.limit);
            } else{
                setPersons(null);
            }

            setLoading(false);
        })();
    }, [api, role, gender, debouncedTitleSearch]);


    const loadNextPage = async () => {
        if (nextOffset === null || nextOffset >= pagination.total || isLoadingNext) return;

        setIsLoadingNext(true);
        const params = buildParams({
            name: debouncedTitleSearch,
            role: role,
            gender: gender,
            offset: nextOffset
        })

        try {
            const response = await api.get(`${url}?${params}`);
            if (response.ok) {
                setPersons(prev => [...prev, ...response.body.data]);
                setPagination(response.body.pagination);
                setNextOffset(nextOffset + pagination.limit);
            }
        } finally {
            setIsLoadingNext(false);
        }
    };

    useEffect(() => {document.title = "Estreias - Persons";}, []);

    return (
        <Body>
            {persons === null ? (
                <ErrorPage code={STATUS.ERROR}/>
            ) : (
                <>
                    <div className="mt-6 grid grid-cols-5 gap-x-2 md:gap-x-4 items-center mb-2 md:mb-0">
                            <div className="col-span-full md:col-span-2 flex items-center gap-2">
                                <div className="mt-2 md:mt-0 flex items-center gap-2 bg-primary/30 p-2 rounded-md text-dark-primary">
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
                                        {roleIcons[role] || roleIcons.Actor}
                                    </svg>
                                </div>
                                <div className="flex-1">
                                    <InputField name="titleSearch" placeholder="Search by name" type="text" value={titleSearch}
                                        onChange={e => setTitleSearch(e.target.value)}></InputField>
                                </div>
                            </div>

                        <div className="col-span-full md:col-span-2 grid grid-cols-2 gap-x-2">
                            <SortDropdown
                                label="Role"
                                options={ROLE_OPTIONS}
                                selected={role}
                                setSelected={setRole}
                            />

                            <SortDropdown
                                label="Gender"
                                options={GENDER_OPTIONS}
                                selected={gender}
                                setSelected={setGender}
                            />
                        </div>


                            <div className="hidden md:flex flex-col justify-center items-center">
                                <div>Total Persons</div>
                                <div className="-mt-1 text-2xl font-semibold">{loading ? "-" : pagination.total}</div>
                            </div>
                        </div>

                    {loading ? (
                        <div className="h-[74.15vh] md:h-[79.75vh] bg-primary/30 overflow-auto w-full rounded-md flex justify-center items-center">
                            <div className="spinner"></div>
                        </div>
                    ) : (
                        <div className="h-[74.15vh] md:h-[79.75vh] bg-primary/30 overflow-auto w-full p-2 rounded-md scrollbar-minimal">
                            <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-10 2xl:grid-cols-12 gap-1 md:gap-2">
                                {persons.map(person => (
                                    <div key={person.id} className="relative col-span-1 flex-shrink-0 flex flex-col items-center text-center overflow-visible group">
                                        <Link to={`/person/${person.id}`}>
                                            <img className="card" src={person.portrait || DEFAULTS.image} alt={person.name} onError={(e) => e.target.src = DEFAULTS.image}/>
                                        </Link>
                                        <div className="absolute bottom-0 text-xs md:text-sm font-semibold bg-secondary/75 py-0.5 md:py-1.5 px-1 md:px-2 rounded-md">{person.name}</div>
                                        <div className="absolute top-1 right-1 w-7 h-7 md:w-8 md:h-8 text-sm md:text-base flex items-center justify-center bg-accent/85 text-secondary border border-secondary/50 font-bold shadow-sm p-1 md:p-2 rounded-full select-none">{person.count}</div>
                                    </div>
                                ))}

                                {nextOffset !== null && nextOffset < pagination.total &&
                                    <div className="col-span-full flex justify-center items-center">
                                        <div className="my-2 flex flex-col justify-center items-center">
                                            <span className="tracking-tight mb-2">Load More Persons</span>
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