import Chart from "react-apexcharts"
import { useNavigate } from "react-router-dom";


/**
 * @author ffpereira
 */
export default function ColumnChart({ type, title, categories, countData, avgRuntimeData, height, zoomEnabled=false, idMap, additionalStyles="" }) {
    const navigate = useNavigate();
    let original_categories = categories;

    if(type === 'month'){
        categories = categories.map(m =>
            ['January','February','March','April','May','June','July','August','September','October','November','December'][m-1]
        )
    }

    const series = type === 'runtime' ?
        [{
            name: 'Film Count',
            type: 'column',
            data: countData
        }]
        :
        [
            {
                name: 'Film Count',
                type: 'column',
                data: countData
            },
            {
                name: 'Average Runtime',
                type: 'line',
                data: avgRuntimeData
            }
        ];

    const options = {
        chart: {
            height: 350,
            fontFamily: "IBM Plex Sans",
            type: 'line',
            zoom: {
              enabled: zoomEnabled,
            },
            toolbar: {
              show: false,
            },
            animations:{
                enabled: true,
            },
            events: {
                dataPointSelection: (event, chartContext, config) => {
                    if(!type) return
                    let value = categories[config.dataPointIndex];
                    if(type === 'genre' || type === 'language') value = idMap[value];
                    else if(type === 'month') value = original_categories[config.dataPointIndex];
                    const encodedValue = encodeURIComponent(value);
                    navigate(`/${type}/${encodedValue}`);
                },
            },
        },
        plotOptions: {
            bar: {
                columnWidth: '80%',
                endingShape: 'rounded',
                borderRadius: 4,
                dataLabels: {
                    enabled: true,
                    position: 'bottom',
                },
            },
        },
        stroke: {
            width: [0, 2]
        },
        title: {
            text: title
        },
        dataLabels: {
            enabled: true,
        },
        colors: ["#7D8878", "#5E4662", "#EBDBC1"],
        xaxis: {
            type: 'category',
            categories: categories,
            tooltip: {
                enabled: true,
            }
        },
        yaxis: [
            {
                labels: {
                    formatter: (value) => Math.round(value),
                },
            },
            {
                show: true,
                opposite: true,
            }
        ],
    };

    return (
        <div className={`bg-secondary px-2 pt-2 ${additionalStyles}`}>
          <Chart options={options} categories={categories} series={series} type="line" height={height}/>
        </div>
    );
}