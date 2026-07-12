import Chart from "react-apexcharts";
import { useNavigate } from "react-router-dom";


/**
 * @author ffpereira
 */
export default function PieChart({ title, labels, countData, avgRuntimeData }) {
    const navigate = useNavigate();

    const options = {
        chart: {
            type: "pie",
            fontFamily: "IBM Plex Sans",
            events: {
                dataPointSelection: (event, chartContext, config) => {
                    const selectedLabel = labels[config.dataPointIndex];
                    const encodedLabel = encodeURIComponent(selectedLabel);
                    navigate(`/content_rating/${encodedLabel}`);
                }
            },
        },
        labels,
        colors: [ "#5E4662", "#2E2231", "#4A3450", "#7A5A80", "#9A6FA3", "#B784C2", "#D3A0DD", "#EBC6F4"],
        title: {
            text: title,
        },
        legend: {
            position: "bottom",
        },
        tooltip: {
            custom: ({ seriesIndex }) => {
                const label = labels[seriesIndex];
                const count = countData[seriesIndex];
                const avgRuntime = avgRuntimeData[seriesIndex];

                return `
                    <div class="bg-gray-100 flex flex-col gap-2 text-sm text-dark-primary p-2">
                        <div class="-mx-2 -mt-2 pl-2 bg-gray-200 p-1 border-b border-gray-300"><strong>${label}</strong></div>
                        <div>Films:  <strong>${count}</strong></div>
                        <div>Avg Runtime:  <strong>${Number(avgRuntime).toFixed(1)}</strong></div>
                    </div>
                `;
            },
        },
        dataLabels: {
            formatter: (val, opts) => {
                const value = opts.w.config.series[opts.seriesIndex];
                return Math.round(value);
            },
        },
    };

    return (
        <div className="bg-secondary px-2 pt-2">
            <Chart options={options} series={countData} type="pie" height={350} />
        </div>
    );
}
