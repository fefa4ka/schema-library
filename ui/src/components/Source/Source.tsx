import * as React from 'react'
import { IProps, TSource, TArgs } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Button, Select, TreeSelect} from 'antd'
import { Form, Divider, Tabs, Row, Col, Modal } from 'antd'
import Markdown from 'react-markdown'
const { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceArea } = require('recharts')
const TabPane = Tabs.TabPane;
import './Source.css'
import { UnitInput } from '../UnitInput'

import { Radio } from 'antd';

const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;


const TreeNode = TreeSelect.TreeNode;
const { Option, OptGroup } = Select

const cnPart = cn('Source')

const initialState = {
    name: '',
    pins: {},
    parts: [],
    port: '',
    channel: 0,
    index: -1,
    serial: []
}

// type State = typeof initialState

type TPart = {
    name: string,
    description: string,
    pins: string[],
    args: TArgs
}
type State = {
    name: string,
    pins: TSource['pins'],
    parts: TPart[],
    port: string,
    channel: number,
    index: number,
    serial: {
        port: string,
        desc: string
    }[]
}


export class Part extends React.Component<IProps, {}> {
    state: State = {
        ...initialState,
        name: this.props.source.name,
        index: this.props.source.index >= 0
            ? this.props.source.index 
            : -1
    }

    componentWillMount() {
        this.loadParts()

        return true
    }
    loadParts() {
        axios.get('/api/sources/')
            .then(res => {
                const parts = res.data
                this.setState({ parts }, () => this.loadSource(this.props.source))
            })
            
        axios.get('/api/serial/')
            .then(res => this.setState({ serial: res.data }))
    }
    getCurrentSource() {
        const { name, port, channel } = this.state
        const source = this.state.parts.find(item => item.name === name.split('_')[0])
        const description = source 
            ? source.description
            : ''
        const args: TArgs = source
            ? Object.assign({}, source.args)
            : {}
       
        Object.keys(args).forEach(arg => {
            args[arg] = Object.assign({}, args[arg])
        })

        return {
            name,
            description,
            args,
            pins: Object.assign({}, this.state.pins),
            port,
            channel,
            index: this.state.index,
        }

    }
    loadSource({ name, args, pins, index, port, channel }: TSource) {
        this.setState(({ parts }: State) => {
            if (index === -1 || index === undefined) {
                return {
                    name: undefined,
                    index: -1,
                    pins: {},
                    channel: 0
                }
            } else {
                const partArgs: TArgs = parts.reduce((args, item) => item.name === name.split('_')[0] ? item.args : args, {})
                Object.keys(args).forEach(arg => {
                    const floated = parseFloat(args[arg].value.toString())
                    if(partArgs[arg]) {
                        partArgs[arg].value = isNaN(floated) ? '' : floated
                    }
                })

                return {
                    parts,
                    name,
                    index,
                    pins,
                    port,
                    channel
                }
            }
        })
    }
    componentDidUpdate(prevProps: IProps) {
        if (prevProps.source.index !== this.props.source.index) {
            this.loadSource(this.props.source)
        }
    }
    render() { 
        const { onChange } = this.props
        const { parts } = this.state
        const name = this.state.name 
            ? this.state.name.split('_')[0]
            : undefined
        
        const current = parts.filter(part => part.description.toLowerCase().indexOf('current') !== -1)
        const voltage = parts.filter(part => part.description.toLowerCase().indexOf('current') === -1)
        const args:TArgs = this.state.parts.reduce((args, item) => item.name === name ? item.args : args, {})
        const pins:string[] = this.state.parts.reduce((pins, item) => item.name === name ? item.pins : pins, [''])

        const attributes = Object.keys(args).map(name => {
            const isExists = args.hasOwnProperty(name)

            if (isExists && args[name].unit.name === 'network') {
                return null
            }

            const suffix = isExists
                ? args[name].unit.suffix
                : ''
            const value = isExists
                ? args[name].value
                : 0
   
            return <UnitInput
                key={name}
                name={name}
                suffix={suffix}
                value={value.toString()}
                defaultValue={value.toString()}
                onChange={(val: number) => {
                    this.setState(({ parts }: State) => {
                        const part = parts.find(item => item.name === this.state.name.split('_')[0])

                        if (part) {
                            part.args[name].value = val
                        }

                        return { parts }
                    }, () => onChange(this.getCurrentSource()))
                }}
            />
        })

        const formItemLayout = {
            labelCol: { span: 7 },
            wrapperCol: { span: 12 },
        }
        
        const Pins = <Form>
            {pins.map(pin => {
                return (<Form.Item label={pin} {...formItemLayout} key={pin}>
                    <Select
                        mode="multiple"
                        placeholder='Select Attached Block Pins'
                        value={this.state.pins && this.state.pins[pin]}
                        onChange={(value: string[]) => {
                            this.setState(({ pins }: State) => {
                                pins[pin] = value

                                return { pins }
                            }, () => onChange(this.getCurrentSource()))
                        }}
                    >
                        {this.props.pins.map(pin => <Option key={pin} value={pin}>{pin}</Option>)}
                    </Select>
                </Form.Item>)
            })}
            </Form>

        
        return (
            <div className={cnPart()}>
                <Select
                    style={{ width: '100%' }}
                    placeholder='Select Power Source'
                    value={this.state.name}
                    onChange={name => this.setState({
                        name
                    }, () => onChange(this.getCurrentSource()))}
                >
                    <OptGroup label="Voltage">
                        {voltage.map(item => <Option value={item.name} key={item.name}>{item.description}</Option>)}
                    </OptGroup>
                    <OptGroup label="Current">
                        {current.map(item => <Option value={item.name} key={item.name}>{item.description}</Option>)}
                    </OptGroup>
                </Select>

                <Divider orientation="left">Properties</Divider>
                <div className={cnPart('Attributes')}>
                    {attributes}
                </div>

                <Divider orientation="left">Pins</Divider>
                {Pins}
                
                <Divider orientation="left">Signal Generator Channel</Divider>
                <Select
                    className={cnPart('SerialPort')}
                    value={this.state.port}
                    style={{ width: '100%' }}
                    onChange={port => this.setState({ port }, () => onChange(this.getCurrentSource()))}
                >
                    {this.state.serial.map(item => <Option value={item.port} key={item.port}>{item.port} {item.desc}</Option>)}
                    
                </Select>
                <RadioGroup onChange={e => this.setState({ channel: e.target.value }, () => onChange(this.getCurrentSource()))} defaultValue="0">
                    <RadioButton value="0">None</RadioButton>
                    <RadioButton value="1">CH1</RadioButton>
                    <RadioButton value="2">CH2</RadioButton>
                </RadioGroup>
            </div>
        )
    }
}