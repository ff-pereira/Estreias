import { useNavigate } from "react-router-dom";
import {useRef, useState, useEffect, useMemo, useCallback} from "react";

import worldmapInfo from "./MapData.jsx";
import { getColor, darkenColor } from "./mapUtils.jsx";

/**
 * @author ffpereira
 */
export default function WorldMap({ films_by_country }) {
    const MAX_SCALE = 5;
    const MIN_SCALE = 0.95;

    const SVG_WIDTH = 2000;
    const SVG_HEIGHT = 860;
    const INITIAL_SCALE = 0.95;
    const initialTransform = {scale: INITIAL_SCALE, x: (1 - INITIAL_SCALE) * (SVG_WIDTH / 2), y: (1 - INITIAL_SCALE) * (SVG_HEIGHT / 2),};

    const svgRef = useRef(null);
    const [transform, setTransform] = useState(initialTransform);
    const isPanning = useRef(false);
    const lastMousePos = useRef({ x: 0, y: 0 });
    const [hoveredCountry, setHoveredCountry] = useState(null);

    const [tooltip, setTooltip] = useState({visible: false, x: 0, y: 0, name: "", count: 0, flag: ""});

    const navigate = useNavigate();
    const dragDistance = useRef(0);
    const isDragging = useRef(false);
    const DRAG_THRESHOLD = 5; // pixels

    const tooltipRef = useRef(null);
    tooltipRef.current = tooltip;
    const scheduleTooltipUpdate = useRef(null);
    const updateTooltip = (x, y) => {
        if (scheduleTooltipUpdate.current) return; // already scheduled
        scheduleTooltipUpdate.current = requestAnimationFrame(() => {
            setTooltip(prev => ({ ...prev, x, y }));
            scheduleTooltipUpdate.current = null;
        });
    };


    const countryCounts = useMemo(() => {
        const map = {};
        films_by_country.forEach(c => {map[c.country_id] = c.count;});
        return map;
    }, [films_by_country]);
    const maxCount = Math.max(1, ...films_by_country.map(c => c.count));

    const countryFlags = useMemo(() => {
        const map = {};
        films_by_country.forEach(c => { map[c.country_id] = c.flag_url; });
        return map;
    }, [films_by_country]);

    const colorCache = useMemo(() => {
        const cache = {};
        Object.entries(countryCounts).forEach(([code, count]) => {
            const base = getColor(count, maxCount);
            cache[code] = {base, dark: darkenColor(base, 0.8),};
        });
        return cache;
    }, [countryCounts, maxCount]);

    // Manual wheel handler to prevent page scroll
    useEffect(() => {
        const svg = svgRef.current;
        if (!svg) return;

        const handleWheel = (e) => {
            e.preventDefault();

            const svg = svgRef.current;
            const pt = svg.createSVGPoint();
            pt.x = e.clientX;
            pt.y = e.clientY;

            const svgPoint = pt.matrixTransform(svg.getScreenCTM().inverse());

            setTransform(prev => {
                const scaleFactor = e.deltaY < 0 ? 1.1 : 0.9;
                const newScale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, prev.scale * scaleFactor));

                const newX = svgPoint.x - (svgPoint.x - prev.x) * (newScale / prev.scale);
                const newY = svgPoint.y - (svgPoint.y - prev.y) * (newScale / prev.scale);

                return { scale: newScale, x: newX, y: newY };
            });
        };

        svg.addEventListener("wheel", handleWheel, { passive: false });
        return () => svg.removeEventListener("wheel", handleWheel);
    }, []);

    // Pan handlers
    // const handleMouseDown = (e) => {
    //     isPanning.current = true;
    //     lastMousePos.current = { x: e.clientX, y: e.clientY };
    //};
    const handleMouseDown = (e) => {
        isPanning.current = true;
        isDragging.current = false;
        dragDistance.current = 0;
        lastMousePos.current = { x: e.clientX, y: e.clientY };
    };

    /*
    const handleMouseMove = (e) => {
        if (!isPanning.current) return;
        const dx = e.clientX - lastMousePos.current.x;
        const dy = e.clientY - lastMousePos.current.y;
        setTransform(prev => ({ ...prev, x: prev.x + dx, y: prev.y + dy }));
        lastMousePos.current = { x: e.clientX, y: e.clientY };
    };
     */
    const handleMouseMove = (e) => {
        if (!isPanning.current) return;

        const dx = e.clientX - lastMousePos.current.x;
        const dy = e.clientY - lastMousePos.current.y;

        dragDistance.current += Math.abs(dx) + Math.abs(dy);
        if (dragDistance.current > DRAG_THRESHOLD) {
            isDragging.current = true;
        }

        setTransform(prev => ({ ...prev, x: prev.x + dx, y: prev.y + dy }));
        lastMousePos.current = { x: e.clientX, y: e.clientY };
    };

    // const handleMouseUp = () => { isPanning.current = false; };
    const handleMouseUp = () => {
        isPanning.current = false;
    };

    const handleMouseLeavePan = () => { isPanning.current = false; };

    const handleMouseEnter = useCallback((code, name, count) => (e) => {
        setHoveredCountry(code);
        const flag = countryFlags[code] || "";
        setTooltip({ visible: true, x: e.clientX, y: e.clientY, name:name, count:count, flag:flag});
    }, []);

    const handleMouseLeave = useCallback(() => {
        setHoveredCountry(null);
        setTooltip(prev => ({ ...prev, visible: false }));
    }, []);


    const resetZoom = () => setTransform(initialTransform);

    return (
        <>
            <div className="relative w-full h-full">
                <svg ref={svgRef} viewBox="0 0 2000 860" width="100%" className="rounded-md bg-gray-100/65"
                    style={{ cursor: isPanning.current ? "grabbing" : "grab" }}
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    onMouseUp={handleMouseUp}
                    onMouseLeave={handleMouseLeavePan}
                >
                    <g transform={`translate(${transform.x},${transform.y}) scale(${transform.scale})`}>
                        {Object.entries(worldmapInfo.paths).map(([code, d]) => {
                            const count = countryCounts[code] || 0;
                            const name = worldmapInfo.names[code];
                            const { base, dark } = colorCache[code] || { base: "rgb(238,238,238)", dark: "rgb(204,204,204)" };
                            const fillColor = hoveredCountry === code ? dark : base;
                            return (
                                <path key={code} d={d} fill={fillColor} stroke="#666" strokeWidth="0.5"
                                    onMouseEnter={handleMouseEnter(code, name, count)}
                                    onMouseMove={(e) => updateTooltip(e.clientX, e.clientY)}
                                    onMouseLeave={handleMouseLeave}
                                    onClick={() => {
                                        if (!isDragging.current && count > 0) {
                                            navigate(`/country/${code}`);
                                        }
                                    }}
                                >
                                </path>
                            );
                        })}
                    </g>
                </svg>
                <div onClick={resetZoom} className="absolute bottom-2 right-2 bg-accent text-white p-2 transform hover:scale-105 transition ease-in-out duration-200 rounded-xl cursor-pointer">Reset Zoom</div>
            </div>

            {tooltip.visible && (
                <div className="bg-gray-800/75 text-white px-2 py-1 rounded-md pointer-events-none text-xs whitespace-nowrap z-10"
                    style={{position: "fixed", top: tooltip.y, left: tooltip.x}}
                >
                    <div className="flex items-center mb-1">
                        {tooltip.flag && <img src={tooltip.flag} alt="flag" className="h-5 w-auto inline-block mr-2" />}
                        <span className="font-semibold">{tooltip.name}</span>
                    </div>
                    <div className="bg-gray-100 text-gray-800 text-center font-bold rounded-md">
                        {tooltip.count}
                    </div>
                </div>
            )}
        </>
    );
}
