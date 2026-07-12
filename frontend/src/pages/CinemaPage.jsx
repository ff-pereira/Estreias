import {useEffect, useState} from "react";
import {Link, useParams} from "react-router-dom";

import ErrorPage from "./ErrorPage.jsx";
import Body from "../components/Body.jsx";
import {useApi} from "../contexts/ApiProvider.jsx";
import PortugalMap from "../map/PortugalMap.jsx";

import { STATUS } from "../constants/status.jsx";
import { DEFAULTS } from "../constants/assets.jsx";


/**
 * @author ffpereira
 */
export default function CinemaPage() {
    const api = useApi();
    const { cinema_id } = useParams();

    const [cinema, setCinema] = useState();
    const [status, setStatus] = useState("loading");
    const [nowShowing, setNowShowing] = useState();
    const [imageError, setImageError] = useState(false);

    useEffect(() => {
        (async () => {
            try{
                const response = await api.get(`/cinema/${cinema_id}`);
                if (response.ok) {
                    setCinema(response.body);
                    setStatus(STATUS.OK);
                } else if (response.status === 404) {
                    setStatus(STATUS.NOT_FOUND);
                }
                else{
                    setStatus(STATUS.ERROR);
                }
            } catch{
                setStatus(STATUS.ERROR);
            }
        })();
    }, [api, cinema_id]);

    useEffect(() => {
        (async () => {
            try {
                const response = await api.get(`/cinema/${cinema_id}/now_showing`);
                if (response.ok) {
                    setNowShowing(response.body);
                } else{
                    setNowShowing(null);
                }
            } catch{
                setNowShowing(null);
            }
        })();
    }, [api, cinema_id]);

    useEffect(() => {
        if (!cinema) document.title = "Cinema - Not found";
        else document.title = `Cinema - ${cinema.name}`;
        return () => { document.title = "Estreias"; };
    }, [cinema]);

    return (
        <Body>
            { status === STATUS.LOADING ? (
                <div className="mt-[5vh] h-[86.25vh] md:h-[85vh] bg-primary/30 w-full rounded-md flex justify-center items-center">
                    <div className="spinner"></div>
                </div>
            ) : status === STATUS.NOT_FOUND ? (<ErrorPage code={STATUS.NOT_FOUND} />
            ) : status === STATUS.ERROR ? (<ErrorPage code={STATUS.ERROR} />
            ) : (
                <>
                    {cinema === null ?
                        <ErrorPage code={STATUS.ERROR}/>
                        :
                        <div className="mt-[5vh] h-[86.25vh] md:h-[85vh] bg-primary/30 overflow-auto w-full rounded-md scrollbar-minimal">
                            <div className="grid grid-cols-10 gap-2 px-4 pt-2">
                                <div className="col-span-full md:col-span-8 text-balance text-2xl md:text-4xl font-semibold">{cinema.name.split(" - ")[0]}</div>
                                <div className="col-span-2 hidden md:flex justify-end items-center text-xl">{cinema.group}</div>

                                {cinema.picture && !imageError &&
                                    <div className="relative col-span-full md:col-span-5 xl:col-span-3">
                                        <img className="inset-0 w-full h-full shadow-md rounded-md " alt={cinema.name}
                                             src={cinema.picture || DEFAULTS.image} onError={() => setImageError(true)}/>

                                        {cinema.group && cinema.group_picture &&
                                            <img className="absolute bottom-4 right-4 bg-primary/75 rounded-md p-4  w-1/4"
                                                 src={cinema.group_picture} alt={cinema.group}/>
                                        }
                                    </div>
                                }

                                <div className="hidden xl:block md:col-span-3">
                                    <PortugalMap cityLocked={cinema.address_region} />
                                </div>

                                <div className={`col-span-full ${imageError ? "md:col-span-full xl:col-span-7" : "md:col-span-5 xl:col-span-4"} md:px-2`}>
                                    <div className="border-b border-primary/50 font-semibold tracking-tight text-lg md:text-xl">Location Details:</div>
                                    {cinema.street_address && <div><span className="font-semibold">Address:</span> {cinema.street_address}</div>}
                                    {cinema.postal_code && <div><span className="font-semibold">Postal Code:</span> {cinema.postal_code}</div>}
                                    {cinema.address_locality && <div><span className="font-semibold">Locality:</span> {cinema.address_locality}</div>}
                                    {cinema.address_region && <div><span className="font-semibold">Region:</span> {cinema.address_region}</div>}
                                    {cinema.address_country && <div><span className="font-semibold">Country:</span> {cinema.address_country}</div>}

                                    {cinema.longitude && cinema.latitude &&
                                        <>
                                            <div className="mt-4 border-b border-primary/50 font-semibold tracking-tight text-lg md:text-xl">Coordinates:</div>
                                            <div>{cinema.latitude}, {cinema.longitude}</div>
                                            <a href={`https://www.google.com/maps/search/?api=1&query=${cinema.latitude},${cinema.longitude}`}
                                               target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">
                                                Open in Google Maps
                                            </a>
                                        </>
                                    }

                                    {cinema.telephone &&
                                        <div>
                                            <div className="mt-4 border-b border-primary/50 font-semibold tracking-tight text-lg md:text-xl">Contact:</div>
                                            <span className="font-semibold">Telephone:</span> {cinema.telephone}
                                        </div>
                                    }
                                </div>

                                <div className="col-span-full">
                                    <div className="mt-0 border-b border-primary/50 font-semibold tracking-tight text-lg md:text-xl">Now Showing</div>

                                    {nowShowing && nowShowing.length > 0 ? (

                                        <div className="flex overflow-auto scrollbar-minimal space-x-2 py-2 px-1">

                                            {nowShowing.map(film => (
                                                <div key={film.id}
                                                     className="relative flex-shrink-0 flex flex-col items-center text-center overflow-visible group">
                                                    <Link to={`/film/${film.id}`}>
                                                        <img className="card w-28 md:w-36"
                                                             src={film.poster || DEFAULTS.image} alt={film.title}
                                                             onError={(e) => e.target.src = DEFAULTS.image}/>
                                                    </Link>
                                                    <div
                                                        className="text-base mt-1 flex flex-col justify-center items-center">
                                                        <div>Since</div>
                                                        <div
                                                            className="-mt-2 font-semibold tracking-tight">{new Date(film.first_seen).toLocaleDateString("pt-PT")}</div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="flex flex-col items-center justify-center py-4">
                                            <div className="md:text-lg font-semibold">No films currently showing</div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    }
                </>
            )}
        </Body>
    );}
