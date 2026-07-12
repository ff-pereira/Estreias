import Chart from "react-apexcharts";


/**
 * @author ffpereira
 */
export default function RadarChart({ data }) {
    const order = ["Actor", "Sound", "Camera", "Director", "Writer"];

    const labels = order.filter(k => k in data);
    const seriesData = labels.map(k => data[k]);

    const options = {
        chart: {
            height: 230,
            fontFamily: "IBM Plex Sans",
            type: 'radar',
            toolbar: { show: false },
        },
        dataLabels: { enabled: true },
        plotOptions: {
            radar: {
                size: 70,
                polygons: {
                    strokeColors: '#e9e9e9',
                    fill: { colors: ['#f8f8f8', '#fff'] }
                }
            }
        },
        colors: ["#5E4662"],
        markers: { size: 5, strokeWidth: 2 },
        tooltip: {
            y: { formatter: val => val }
        },
        xaxis: {
            categories: labels,
            labels: {
                style: {
                    fontWeight: 'bold',
                    fontSize: '12px'
                }
            },
        },
        yaxis: {
            min: 0,
            max: Math.max(...seriesData, 5),
            tickAmount: 3,
            labels: {
                formatter: (val) => val > 0 ? Math.round(val) : ''
            }
        }
    };

    const series = [
        {
            name: 'Films',
            data: seriesData
        }
    ];

    return (
        <div className="flex justify-center items-center">
            <Chart options={options} series={series} type="radar" height={230} width={230} />
        </div>
    );
}
