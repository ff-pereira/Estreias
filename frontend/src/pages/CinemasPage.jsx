import {useEffect} from "react";

import Body from "../components/Body.jsx";
import CinemaListMap from "../components/CinemaListMap.jsx";


/**
 * @author ffpereira
 */
export default function CinemasPage( {film_id} ) {
    useEffect(() => {document.title = "Estreias - Persons";}, []);

    return (
        <Body>
            <CinemaListMap additionalClassesTop={"mt-6"} additionalClasses={"bg-primary/30 p-2 rounded-md"} fullHeight={"h-[74.15vh] md:h-[79.75vh]"} mapHeight={"h-[78vh]"} film_id={film_id}/>
        </Body>
    );
}