import {useCallback, useMemo, useRef, useState} from "react";

import portugalMapInfo from "./PortugalMapData";
import { getColor, darkenColor } from "./mapUtils";

/**
 * @author ffpereira
 */
export default function PortugalMap({ cinemas_by_region, selectedCities, setSelectedCities, height, cityLocked=false }){
    const tooltipRef = useRef(null);
    const [tooltip, setTooltip] = useState({visible: false, x: 0, y: 0, name: "", count: 0});
    const [hoveredRegion, setHoveredRegion] = useState(null);

    tooltipRef.current = tooltip;
    const scheduleTooltipUpdate = useRef(null);
    const updateTooltip = (x, y) => {
        if(cityLocked) return;
        if (scheduleTooltipUpdate.current) return; // already scheduled
        scheduleTooltipUpdate.current = requestAnimationFrame(() => {
            setTooltip(prev => ({ ...prev, x, y }));
            scheduleTooltipUpdate.current = null;
        });
    };

    const handleMouseEnter = useCallback((code, name, count) => (e) => {
        if(cityLocked) return;
        setHoveredRegion(code);
        setTooltip({ visible: true, x: e.clientX, y: e.clientY, name:name, count:count});
    }, []);

    const handleMouseLeave = useCallback(() => {
        if(cityLocked) return;
        setHoveredRegion(null);
        setTooltip(prev => ({ ...prev, visible: false }));
    }, []);

    const regionCounts = useMemo(() => {
        if(cityLocked) return;
        const map = {};
        cinemas_by_region.forEach(c => {map[c.id.replaceAll(" ", "")] = c.count;});
        return map;
    }, [cinemas_by_region]);

    let maxCount;
    if (!cityLocked) maxCount = Math.max(1, ...cinemas_by_region.map(c => c.count));
    else maxCount = 0;


    const colorCache = useMemo(() => {
        if(cityLocked) return;
        const cache = {};
        Object.entries(regionCounts).forEach(([code, count]) => {
            const base = getColor(count, maxCount);
            cache[code] = {base, dark: darkenColor(base, 0.8),};
        });
        return cache;
    }, [regionCounts, maxCount]);

    const handleRegionClick = (code) => {
        if (cityLocked) return;
        const cityName = portugalMapInfo.names[code];

        setSelectedCities(prev => {
            if (prev.includes(cityName)) {
                return prev.filter(c => c !== cityName);
            } else {
                return [...prev, cityName];
            }
        });
    };

    return(
        <div className="relative flex justify-center items-center">
            <svg className={`bg-secondary rounded-md ${height} w-full`} fill="#6f9c76" stroke="#ffffff" strokeLinecap="round" strokeLinejoin="round" strokeWidth="0.5" version="1.2" viewBox="650 0 375 300" xmlns="http://www.w3.org/2000/svg">
                <g>
                    {Object.entries(portugalMapInfo.paths).map(([code, d]) => {
                        let count = 0;
                        if(!cityLocked) count = regionCounts[code] || 0;
                        const name = portugalMapInfo.names[code];

                        const { base, dark } = !cityLocked ? colorCache[code] || { base: "rgb(238,238,238)", dark: "rgb(204,204,204)" } : { base: "rgb(238,238,238)", dark: "rgb(204,204,204)" };
                        let fillColor = hoveredRegion === code ? dark : base;

                        let isSelected = false;
                        if(!cityLocked) isSelected = selectedCities.includes(code);

                        if(cityLocked === portugalMapInfo.names[code]) fillColor = "#5E4662";

                        return (
                            <path key={code} d={d} fill={fillColor} stroke="#666" strokeWidth={isSelected ? 1 : 0.5}
                                  onMouseEnter={handleMouseEnter(code, name, count)}
                                  onMouseLeave={handleMouseLeave}
                                  onMouseMove={(e) => updateTooltip(e.clientX, e.clientY)}
                                  onClick={() => handleRegionClick(code)}>
                            </path>
                        );
                    })}
                </g>
            </svg>

            {tooltip.visible && (
                <div className="bg-gray-800/75 text-white px-4 py-1 rounded-md pointer-events-none text-xs whitespace-nowrap z-10"
                    style={{position: "fixed", top: tooltip.y, left: tooltip.x}}
                >
                    <div className="flex items-center mb-1">
                        <span className="font-semibold">{tooltip.name}</span>
                    </div>
                    <div className="bg-gray-100 text-gray-800 text-center font-bold rounded-md">
                        {tooltip.count}
                    </div>
                </div>
            )}

        </div>
    );
}
