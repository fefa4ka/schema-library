import React, { Component } from 'react';
import { Code } from '../Code'
import { Row, Col, Layout, Menu } from 'antd';
import { Chart } from '../Chart'
import { Slider, Divider } from 'antd'
import axios from 'axios'

const { Sider, Content } = Layout;
const { SubMenu } = Menu;

const initState = {
  code: `
from bem import *
from skidl import Net
from PySpice.Unit import * 

gnd = Net('0')
signal = Build('SINEV').spice(ref='VS', amplitude=10@u_V, frequency=120@u_Hz)
print(signal)
resistor = Resistor()(value=10)
divider = Divider()(V_in=10@u_V, V_out =3@u_V, I_out=5@u_mA)
gnd+= signal['n']
divider.gnd += gnd
divider.input += signal['p']

rc = divider & resistor & gnd

chart = divider.test_pins()
  `,
  circuits: {},
  selectedCircuit: '',
  chartData: [],
  showLabels: {},
  simulationStartTime: 0,
  simulationStopTime: 0.01
}
type State = {
  code: string,
  circuits: {
    [name: string]: {
      [mod:string]: string[]
    }
  },
  selectedCircuit: string,
  chartData: {
    [name:string]: number
  }[],
  showLabels: {
      [name: string]: boolean
  },
  simulationStartTime: number,
  simulationStopTime: number
}

export class Circuits extends Component {
  state: State = initState

  componentWillMount() {    
    axios.get('http://localhost:3000/api/circuits/')
        .then(res => {
            this.setState({
                circuits: res.data
            })
        })
  }

  loadSimulation() {
    const { code, simulationStopTime } = this.state

    axios.post('http://localhost:3000/api/circuit/',
    {
        code,
        simulationTime: simulationStopTime
    })
        .then(res => {
            const chartData = res.data
            const labels = res.data && res.data.length > 0
                ? Object.keys(res.data[0]).filter(label => label !== 'time')
                : []
            
            
            this.setState(({ showLabels }:State) => {
                return {
                    chartData,
                    showLabels: labels.reduce((labels: any, label) => {
                        labels[label] = showLabels[label] === false 
                            ? false 
                            : true

                        return labels
                    }, {}),
                    simulationStopTime: chartData.length ? chartData[chartData.length - 1].time : 0
                }
            })
        })
}
  render() {
    const circuits = Object.keys(this.state.circuits)
    const { chartData, selectedCircuit } = this.state
    
    let simulationMaxTime = chartData.length > 0
            ? chartData[chartData.length - 1].time
            : 0.02
        const simulationMarks: any = {}
        
        function getPrecision (num:number) {
            var numAsStr = num.toFixed(10); //number can be presented in exponential format, avoid it
            numAsStr = numAsStr.replace(/0+$/g, '');
          
            var precision = String(numAsStr).replace('.', '').length - String(numAsStr).replace('.', '').replace(/^0+/g, '').length
            return precision;  
          }
          
        const simulationTimeExponent = getPrecision(simulationMaxTime) * -1 
        const simulationValueScale = Math.pow(10, simulationTimeExponent * -1) * 100

        simulationMaxTime *= simulationValueScale
        const simulationStartTime = this.state.simulationStartTime * simulationValueScale 
        const simulationStopTime = this.state.simulationStopTime * simulationValueScale
        // const siPrefix:{[name:string]: string} = {
        //     '-24': 'y',
        //     '-21': 'z',
        //     '-18': 'a',
        //     '-15': 'f',
        //     '-12': 'p',
        //     '-9': 'n',
        //     '-6': 'μ',
        //     '-3': 'm',
        //     '-2': 'c',
        //     '-1': 'd',
        //     '0': '',
        //     '1': 'da',
        //     '2': 'h',
        //     '3': 'k',
        //     '6': 'M',
        //     '9': 'G',
        //     '12': 'T',
        //     '15': 'P',
        //     '18': 'E',
        //     '21': 'Z',
        //     '24': 'Y'
        // }
        const siPrefix:{[name:string]: string} = {
            '-24': 'y',
            '-21': 'z',
            '-18': 'a',
            '-15': 'f',
            '-12': 'p',
            '-9': 'n',
            '-6': 'μ',
            '-3': 'm',
            '0': '',
            '1': 'da',
            '2': 'h',
            '3': 'k',
            '6': 'M',
            '9': 'G',
            '12': 'T',
            '15': 'P',
            '18': 'E',
            '21': 'Z',
            '24': 'Y'
        }

        for (let step = 0; step < simulationMaxTime; step = step + simulationMaxTime / 5) {
            let exponent = simulationTimeExponent
            let labelStep = step / 100

            while (!siPrefix.hasOwnProperty(exponent) && exponent > -25) {
                exponent = labelStep > 1000 ? exponent + 1 : exponent - 1
                labelStep = step * Math.pow(10, (simulationTimeExponent - exponent) * -1) 
            }
            
            const prefix:string = siPrefix.hasOwnProperty(exponent)
                ? siPrefix[exponent]
                : ''
            
            simulationMarks[step] = (labelStep.toString().length - 2 - getPrecision(labelStep) > 3 ? labelStep.toFixed(3) : labelStep) + ' ' + prefix + 's'
        }


    
    return (
          <Layout>
            <Content>
            <Code
              value={this.state.code}
              onChange={(value:string) => this.setState({ code: value }, this.loadSimulation)}  
            />
                <Divider orientation="left">Waveforms</Divider>
                        
                <Chart
                    chartData={chartData}
                    showLabels={this.state.showLabels}
                    xRefStart={this.state.simulationStartTime}
                    xRefStop={this.state.simulationStopTime}
                    onLegendClick={(e: any) => this.setState(({ showLabels }:State) => {
                        showLabels[e.dataKey] = !showLabels[e.dataKey]
    
                        return showLabels
                    })}
                />
                <Row>
                    <Col push={1} span={22}>
                        <Slider
                            range min={0} max={simulationMaxTime} defaultValue={[0, simulationMaxTime]}
                            value={[simulationStartTime, simulationStopTime]}
                            marks={simulationMarks}
                            onChange={(value: any) =>
                                this.setState({
                                    simulationStartTime: parseFloat(value[0]) / simulationValueScale,
                                    simulationStopTime: parseFloat(value[1]) / simulationValueScale
                                })}
                            onAfterChange={(value: any) => {
                                const { simulationStopTime, chartData } = this.state
                                if (chartData.length && simulationStopTime > chartData[chartData.length - 1].time) {
                                    this.loadSimulation()
                                }
                            }}
                        />
                    </Col>
                </Row>
            </Content>
          </Layout>

    );
  }
}
