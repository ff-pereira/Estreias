/**
 * @author ffpereira
 */
export function getColor(count, maxCount) {
    if (!count) return "rgb(238,238,238)";
    const intensity = Math.log10(count + 1) / Math.log10(maxCount + 1);

    const start = [238, 238, 238];

    const end = [94, 70, 98];        // #5E4662
    // const end = [125, 136, 120];  // #7D8878

    const r = Math.floor(start[0] + (end[0] - start[0]) * intensity);
    const g = Math.floor(start[1] + (end[1] - start[1]) * intensity);
    const b = Math.floor(start[2] + (end[2] - start[2]) * intensity);

    return `rgb(${r}, ${g}, ${b})`;
}

export function darkenColor(color, factor = 0.8) {
    const rgbValues = color.match(/\d+/g).map(Number);
    return `rgb(${Math.floor(rgbValues[0] * factor)}, ${Math.floor(rgbValues[1] * factor)}, ${Math.floor(rgbValues[2] * factor)})`;
}