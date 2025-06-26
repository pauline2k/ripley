import {cloneDeep} from 'lodash'
import * as Highcharts from 'highcharts'

type NonEmptyArray<T> = [T, ...T[]];

type CustomSeriesOptionsType = Highcharts.SeriesOptionsType & {
  color: string,
  data: Array<any>,
  name: string
}

export interface CustomPlotOptions extends Highcharts.PlotOptions {
  series: Highcharts.PlotSeriesOptions;
}

export interface HighchartsOptions extends Highcharts.Options {
  plotOptions: CustomPlotOptions,
  series: Array<CustomSeriesOptionsType>,
  xAxis: NonEmptyArray<Highcharts.XAxisOptions>,
  yAxis: NonEmptyArray<Highcharts.YAxisOptions>
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
