import * as React from 'react';
import axios from 'axios';
import { canonise, siPrefix } from '../../Unit';
import { cn } from '@bem-react/classname';
import {
    Col,
    Modal,
    Row
    } from 'antd';
import { IProps } from './index';
import { MathMarkdown } from '../Mathdown';
import { Probe, TProbeState } from '../../Probe';

import './Block-Simulation.css';
import { Slider, Divider, Button } from 'antd'
const { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend, ReferenceLine} = require('recharts')
const ChartTooltip = require('recharts').Tooltip
const ButtonGroup = Button.Group

import { insertSpaces } from '../../Blocks/Blocks'

import { UnControlled as CodeMirror } from 'react-codemirror2';

require('codemirror/lib/codemirror.css')
require('codemirror/mode/python/python')



const cnBlock = cn('Block')

const initialState = {
    modalTestVisible: false,
    modalCircuitVisible: false,
    modalERCVisible: false,
    spiceCircuit: '',
    ERC: '',
    probeLoading: false,
    simulationData: [],
    simulationCase: {},
    probes: {},
    probeData: [],
    showLabels: {},
    simulationStartTime: 0,
    simulationStopTime: 0.01
}

type TSimulationCase = {
    field?: string,
    label: string,
    unit?: string,
    scale?: string,
    domain?: number[]
}

interface IState {
    modalTestVisible: boolean,
    modalCircuitVisible: boolean,
    modalERCVisible: boolean,
    spiceCircuit: string,
    ERC: string,
    simulationData: {
        [name:string]: number
    }[],
    simulationCase: {
        [name: string]: {
            x: TSimulationCase,
            y: TSimulationCase,
            data: {
                [name: string]: number
            }[],
            description: string
        }
    },
    probes: TProbeState,
    probeLoading: boolean,
    probeData: {
        [name:string]: number
    }[],
    showLabels: {
        [name: string]: boolean
    },
    simulationStartTime: number,
    simulationStopTime: number
}

export class Simulation extends React.Component<IProps, {}> {
    state: IState = initialState
    componentWillMount() {
        this.props.shouldReload(() => this.loadSimulation())
    }
    componentWillReceiveProps(nextProps: IProps) {
        nextProps.shouldReload(() => this.loadSimulation()) 
    }
    loadSimulation() {
        const { args, mods, body_kit } = this.props
        const { simulationStopTime } = this.state
        
        axios.post('/api/blocks/' + this.props.name + '/simulate/',
        {
            mods,
            args: Object.keys(args).reduce((result: { [name:string]: string | number }, arg) => {
                result[arg] = args[arg].value
                
                return result
            }, {}),
            body_kit,
            simulationTime: simulationStopTime
        })
            .then(res => {
                const simulation = res.data
                const simulationData = simulation.data
                const labels = res.data && res.data.length > 0
                    ? Object.keys(res.data[0]).filter(label => label !== 'time')
                    : []
                
                this.loadSimulationCases() 
                
                this.setState(({ showLabels }: IState) => {
                    return {
                        simulationData,
                        ERC: simulation.erc,
                        spiceCircuit: simulation.circuit,
                        showLabels: labels.reduce((labels: any, label) => {
                            labels[label] = showLabels[label] === false 
                                ? false 
                                : true
    
                            return labels
                        }, {}),
                        simulationStopTime: simulationData.length ? simulationData[simulationData.length - 1].time : 0
                    }
                })
            })//.catch(this.catchError)
    }
    loadSimulationCases() {
        const { name, args, body_kit, } = this.props
        
        axios.post('/api/blocks/' + name + '/simulate/cases/',
        {
            mods: this.props.mods,
            args: Object.keys(args).reduce((result: { [name:string]: string | number }, arg) => {
                result[arg] = args[arg].value
                
                return result
            }, {}),
            body_kit,
        })
            .then(res => {
                const simulationCase = res.data
                
                this.setState({ simulationCase })
            })//.catch(this.catchError)
    }
     
    loadProbes() {
        const { probes, simulationStopTime } = this.state
        const { body_kit } = this.props
        this.setState({
            probeLoading: true,
        })
        axios.post('/api/probes/',
        {
            body_kit,
            probes,
            simulationTime: simulationStopTime
        })
            .then(res => {
                const probeData = res.data
                const labels = res.data && res.data.length > 0
                    ? Object.keys(res.data[0]).filter(label => label !== 'time')
                    : []
                
                
                this.setState(({ showLabels }: IState) => {
                    return {
                        probeData,
                        probeLoading: false,
                        showLabels: labels.reduce((labels: any, label) => {
                            labels[label] = showLabels[label] === false 
                                ? false 
                                : true
    
                            return labels
                        }, {}),
                        modalTestVisible: false,
                        simulationStopTime: probeData.length ? probeData[probeData.length - 1].time : 0
                    }
                })
            })//.catch(this.catchError)
    }
    handleTestOk = () => {
        this.loadProbes()
    }
    showModal = (name:string) => {
        this.setState({
            [`modal${name}Visible`]: true,
        })
    }
    handleModalCancel = (name: string) => {
        this.setState({
            [`modal${name}Visible`]: false,
            [`editable${name}`]: {}
        })
    }

    render() {
        const { simulationData, simulationCase } = this.state
        const simulationCases = Object.keys(simulationCase)
        let simulationMaxTime = simulationData.length > 0
            ? simulationData[simulationData.length - 1].time
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


        return <>
             <Row>
                <Col span={12}>
                    <Divider orientation="left">
                        <ButtonGroup>
                            <Button onClick={() => this.showModal('Circuit')}>SPICE Circuit</Button>
                            <Button onClick={() => this.showModal('ERC')}>ERC</Button>
                        </ButtonGroup>
                    </Divider>

                    <Modal
                        title="SPICE Circuit"
                        visible={this.state.modalCircuitVisible}
                        onOk={() => this.handleModalCancel('Circuit')} 
                        onCancel={() => this.handleModalCancel('Circuit')}
                    >
                            <CodeMirror
                                className={cnBlock('CodeExample')}
                                options={{
                                    mode: 'spice',
                                    lineNumbers: false,
                                    indentWithTabs: false,
                                    indentUnit: 4,
                                    tabSize: 4
                                }}
                                value={this.state.spiceCircuit} 
                           />
                    </Modal>

                    <Modal
                        title="Electrical Rule Checker"
                        visible={this.state.modalERCVisible}
                        onOk={() => this.handleModalCancel('ERC')} 
                        onCancel={() => this.handleModalCancel('ERC')}
                    >
                        <pre>{this.state.ERC}</pre>
                    </Modal>
                
                    <TransientChart 
                        data={simulationData}
                        showLabels={this.state.showLabels}
                        startTime={this.state.simulationStartTime}
                        stopTime={this.state.simulationStopTime}
                        onLegendClick={(e: any) => this.setState(({ showLabels }: IState) => {
                            showLabels[e.dataKey] = !showLabels[e.dataKey]
        
                            return showLabels
                        })} 
                    />
                </Col>
                <Col span={12}>
                    <Divider orientation="left">Probes</Divider>
                    <div className={cnBlock('TestAction', { checked: this.state.probeData.length > 1 })}>
                        <Button type='primary' onClick={() => this.showModal('Test')}>Test Citcuit</Button>
                        <Modal
                            title="Circuit Test"
                            visible={this.state.modalTestVisible}
                            onOk={this.handleTestOk}
                            onCancel={() => this.handleModalCancel('Test')}
                        >
                                <Probe
                                    probe={this.state.probes}
                                    pins={Object.keys(this.props.pins).filter(pin => this.props.pins[pin].length)}
                                    loading={this.state.probeLoading}
                                    onChange={(probe:any) =>
                                        this.setState(probe)
                                    }
                                />
                                
                        </Modal>
                    </div>
                    <TransientChart 
                        data={this.state.probeData}
                        showLabels={this.state.showLabels}
                        startTime={this.state.simulationStartTime}
                        stopTime={this.state.simulationStopTime}
                        onLegendClick={(e: any) => this.setState(({ showLabels }: IState) => {
                            showLabels[e.dataKey] = !showLabels[e.dataKey]
        
                            return showLabels
                        })} 
                    />
                </Col>
            </Row>
            <Row className={cnBlock('WaveformTimeInput')}>
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
                            const { simulationStopTime, simulationData } = this.state
                            if (simulationData.length && simulationStopTime > simulationData[simulationData.length - 1].time) {
                                this.loadSimulation()
                            }
                        }}
                    />
                </Col>
            </Row>
            {simulationCases.map(name => 
                <React.Fragment key={name}>
                    <Divider orientation="left">{insertSpaces(name)}</Divider>
                    <Row>
                        <Col span={14} className={cnBlock('Description')}>
                            <MathMarkdown value={simulationCase[name].description}/>
                        </Col>
                        <Col span={10}>
                            <DiscreteChart
                                {...simulationCase[name]}
                            />
                        </Col>
                    </Row>
                </React.Fragment>
            )}

        </>
    }
}


function TransientChart(props: any) {
    const { data, showLabels, startTime, stopTime, onLegendClick } = props
    const chartLabels = data.length > 0
        ? Object.keys(data[0]).filter(label => label !== 'time').map(label => {
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
    
    return <ResponsiveContainer width='100%' height='auto' aspect={2/1.0} className={cnBlock('TransientChart')}>
        <LineChart data={data}>
            <Legend
                verticalAlign='top'
                onClick={onLegendClick}
                wrapperStyle={{
                    paddingBottom: "20px"
                }}
            />
            <XAxis
                dataKey={'time'}
                allowDataOverflow={true}
                domain={[startTime, stopTime]}
                label='Time'
                type='number'
                tickFormatter={(val: number) => canonise(val, 's')}
            />
            <YAxis
                yAxisId="left"
                label='Volt'
                tickFormatter={(val: number) => canonise(val, 'V')}
            />
            <YAxis
                yAxisId="right"
                label='Ampere'
                orientation="right"
                tickFormatter={(val: number) => canonise(val, 'A')}
            />
            <CartesianGrid strokeDasharrary="3 3"/>
            <ChartTooltip
                formatter={(value: number) => canonise(value, '')}
                labelFormatter={(value: number) => canonise(value, 's')}
            />
            {chartLabels.map(label =>
                <Line
                    type="monotone"
                    strokeOpacity={ showLabels[label.name] ? 1 : 0.1}
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

const { scaleSqrt, scaleLinear } =  require('d3-scale')


function DiscreteChart(props: any) {
    const { data, x, y } = props

    const chartLabels = data.length > 0
        ? Object.keys(data[0]).filter(label => label !== x.field).map(label => {
            return {
                name: label,
                color: "#" + ((1<<24) * Math.random() | 0).toString(16)
            }
        })
        : []
    const domainStart = data[0][x.field]
    const domainEnd = data[data.length - 1][x.field]

    return <ResponsiveContainer width='100%' height='auto' aspect={1.0/1.0} className={cnBlock('DiscreteChart')}>
        <LineChart data={data}>
            <Legend 
                verticalAlign='top'
                wrapperStyle={{
                    paddingBottom: "20px"
                }}
            />
            <XAxis
                dataKey={x.field}
                allowDataOverflow={true}
                label={x.label}
                domain={[domainStart, domainEnd]}
                tickFormatter={(val: number) => canonise(val, x.unit)}
                type='number'
            />
            <YAxis
                label={y.label}
                tickFormatter={(val: number) => canonise(val, y.unit)}
                type='number'
                domain={y.domain || ['auto', 'auto']}
                scale={y.scale || 'auto'}
            />
            <CartesianGrid strokeDasharray="3 3"/>
            <ChartTooltip
                formatter={(value: number) => canonise(value, y.unit)}
                labelFormatter={(value: number) => canonise(value, x.unit)}
            />
            <ReferenceLine x={0} stroke="black"/>
            <ReferenceLine y={0} stroke="black" />
            {chartLabels.map(label =>
                <Line
                    connectNulls
                    type="monotone"
                    key={label.name}
                    dataKey={label.name}
                    stroke={label.color}
                    dot={false}
                    animationDuration={300}
                />)}
        </LineChart>
    </ResponsiveContainer>
}
