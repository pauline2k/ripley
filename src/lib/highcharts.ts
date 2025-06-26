import {cloneDeep} from 'lodash'
import * as Highcharts from 'highcharts'

type NonEmptyArray<T> = [T, ...T[]];

export interface PlotOptions extends Highcharts.PlotOptions {
  // Extend PlotOptions interface to require certain properties.
  series: CustomPlotSeriesOptions;
}

export interface CustomPlotSeriesOptions extends Highcharts.PlotSeriesOptions {
  // Extend PlotSeriesOptions interface to require certain properties.
  data: Array<any>
}

interface XAxisOptions extends Highcharts.XAxisOptions {
  // Extend XAxisOptions interface to require certain properties.
  categories: Array<string>;
  labels: Highcharts.XAxisLabelsOptions;
}

interface YAxisOptions extends Highcharts.YAxisOptions {
  // Extend YAxisOptions interface to require certain properties.
  labels: Highcharts.YAxisLabelsOptions;
}

export interface SeriesAreaOptions extends Highcharts.SeriesAreaOptions {
  color: string,
  data: Array<Highcharts.PointOptionsObject>
}

export interface SeriesColumnOptions extends Highcharts.SeriesColumnOptions {
  color: string,
  data: Array<Highcharts.PointOptionsObject>
}

export interface SeriesLineOptions extends Highcharts.SeriesLineOptions {
  color: string,
  data: Array<Highcharts.PointOptionsObject>
}

export interface HighchartsOptions extends Highcharts.Options {
  // Extend Options interface to require certain properties.
  legend: Highcharts.LegendOptions;
  plotOptions: PlotOptions,
  series: Array<
    // If we want a new 'chart.type' then find the corresponding interface under 'Highcharts.SeriesOptionsRegistry'
    // and add it to the list below.
    SeriesAreaOptions |
    SeriesColumnOptions |
    SeriesLineOptions
  >,
  tooltip: Highcharts.TooltipOptions;
  xAxis: NonEmptyArray<XAxisOptions>,
  yAxis: NonEmptyArray<YAxisOptions>
}

export interface SeriesMarker {
  fillColor: string,
  lineColor: string,
  lineWidth: number,
  radius: number,
  symbol: string
}

const DEFAULT_HIGHCHARTS_CHART_OPTIONS: HighchartsOptions = {
  // Highcharts API: https://api.highcharts.com/
  chart: {
    backgroundColor: 'transparent'
  },
  lang: {
    noData: 'No data available until final grades are returned.'
  },
  legend: {
    enabled: true,
    itemStyle: {
      fontSize: '1em'
    },
    labelFormat: '{name}',
    layout: 'horizontal',
    symbolPadding: 10,
    symbolRadius: 0,
    verticalAlign: 'bottom'
  },
  noData: {
    style: {
      fontSize: '18px',
      color: '#999'
    }
  },
  plotOptions: {
    column: {
      groupPadding: .1
    },
    series: {
      borderWidth: 0,
      data: [],
      dataLabels: {
        enabled: false
      }
    }
  },
  series: [],
  title: {
    align: 'left',
    margin: 45,
    style: {
      color: '#474747'
    },
    y: 23
  },
  tooltip: {
    shared: true,
    stickOnContact: true,
    useHTML: true
  },
  xAxis: [{
    categories: [],
    labels: {
      autoRotationLimit: 0,
      overflow: 'allow',
      style: {
        color: '#999',
        fontSize: '15'
      }
    },
    lineColor: '#CCC',
    lineWidth: 2,
    tickColor: '#CCC',
    tickmarkPlacement: 'on',
    tickWidth: 1
  }],
  yAxis: [{
    endOnTick: false,
    gridLineWidth: 0,
    labels: {
      style: {
        color: '#999',
        fontSize: '16'
      }
    },
    lineColor: '#999',
    lineWidth: 1,
    tickColor: '#CCC',
    tickWidth: 1,
    title: {
      text: undefined
    }
  }]
}

export const DEFAULT_SERIES_LINE_COLOR = '#8BBDDA'

export const CHART_COLORS = {
  primary: '#8BBDDA',
  secondary: '#DAB38B',
  tertiary: '#C5E1F2',
  quaternary: '#FCCE9F'
}

export const getDefaultChartOptions = () => cloneDeep(DEFAULT_HIGHCHARTS_CHART_OPTIONS)
