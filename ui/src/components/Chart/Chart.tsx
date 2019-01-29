import * as React from 'react'
import { IProps } from './index'

import { cn } from '@bem-react/classname'
import { Divider, Tag, Button, Input, TreeSelect} from 'antd'
import { Icon, Tabs, Row, Col, Modal } from 'antd'
const { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceArea } = require('recharts')
import './Chart.css'

const cnChart = cn('Chart')

const initialState = {
    showLabels: {},
    hoverLabels: {}
}

type State = {
    showLabels: {
        [name:string]: boolean
    },
    hoverLabels: {
        [name:string]: number
    }

}

export class Chart extends React.Component<IProps, {}> {
    state: State = initialState

    componentDidUpdate(prevProps: IProps) {
        const { chartData } = this.props
        
        chartData.forEach((data, index) => {
            const labels = Object.keys(data)

            labels.forEach((key) => {
                if (!prevProps.chartData[index] || prevProps.chartData[index][key] !== data[key]) {
                    this.setState({
                        hoverLabels: labels.reduce((labels: any, label) => {
                            labels[label] = this.props.showLabels[label] ? 1 : 0.1

                            return labels
                        }, {})
                    })
                }
            })
        })
    }
    handleMouseEnter(o:any) {
        const { dataKey } = o
        const { hoverLabels } = this.state
        
          this.setState({
            hoverLabels: { ...hoverLabels, [dataKey]: 0.5 }
        })
      }
      
    handleMouseLeave(o:any) {
          const { dataKey } = o
        const { hoverLabels } = this.state
        
          this.setState({
            hoverLabels: { ...hoverLabels, [dataKey]: 1 },
        })
    }
    
    render() {
        const { showLabels, hoverLabels } = this.state
        const { chartData } = this.props

        const chartLabels = chartData.length > 0
        ? Object.keys(chartData[0]).filter(label => label !== 'time').map(label => {
            return {
                name: label,
                color: label.includes('I_')
                    ? 'red'
                    : label.includes('input')
                        ? "#1890ff"
                        : "#000",
                unit: label.includes('I_') ? 'A' : 'V',
                axis: label.includes('I_') ? 'right' : 'left'
            }
        })
        : []
// console.log({this.props.xRefStart,- {this.props.xRefStop})
    
       return  <ResponsiveContainer width='100%' height='auto' aspect={4.0/1.0} className={cnChart()}>
            <LineChart data={chartData}>
               <Legend verticalAlign='top' onClick={this.props.onLegendClick}/>
               <XAxis dataKey="time" allowDataOverflow={true} domain={[this.props.xRefStart, this.props.xRefStop]} type='number'/>
                <YAxis yAxisId="left" label='Volt' />
                <YAxis yAxisId="right" label='Ampere' orientation="right" />
                <CartesianGrid strokeDasharray="3 3"/>
                <Tooltip />
               {chartLabels.map(label =>
                   <Line
                       type="monotone"
                       strokeOpacity={ this.props.showLabels[label.name] ? 1 : 0.1}
                       key={label.name}
                       dataKey={label.name}
                       stroke={label.color}
                       dot={false}
                       unit={label.unit}
                       yAxisId={label.axis}
                       animationDuration={300}
                    />)}
           </LineChart>
        </ResponsiveContainer>
    }
}