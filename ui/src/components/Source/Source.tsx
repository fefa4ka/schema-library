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

const nomnoml = require('nomnoml')
const TreeNode = TreeSelect.TreeNode;
const { Option, OptGroup } = Select

const cnPart = cn('Source')

const initialState = {
    name: '',
    pins: {},
    parts: [],
    index: -1
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
    index: number
}


export class Part extends React.Component<IProps, {}> {
    state: State = {
        ...initialState,
        name: this.props.source.name,
        index: this.props.source.index >= 0
            ? this.props.source.index 
            : -1,
        pins: this.props.source.pins
    }

    componentWillMount() {
        this.loadParts()

        return true
    }
    loadParts() {
        axios.get('http://localhost:3000/api/sources/')
            .then(res => {
                const parts = res.data
                this.setState({ parts }, () => this.loadSource(this.props.source))
            })
    }
    getCurrentSource() {
        const { name } = this.state
        const source = this.state.parts.find(item => item.name === name)
        const description = source 
            ? source.description
            : ''
        const args: TArgs = source
            ? source.args
            : {}
       
        return {
            name,
            description,
            args,
            pins: Object.assign({}, this.state.pins),
            index: this.state.index
        }

    }
    loadSource({ name, args, pins, index }: TSource) {
        this.setState(({ parts }: State) => {
            if (index === -1 || index === undefined) {
                return {
                    name: undefined,
                    index: -1,
                    pins: {}
                }
            } else {
                const partArgs: TArgs = parts.reduce((args, item) => item.name === name ? item.args : args, {})
                Object.keys(args).forEach(arg => {
                    const floated = parseFloat(args[arg].value.toString())
                    partArgs[arg].value = isNaN(floated) ? '' : floated
                })

                return {
                    parts,
                    name,
                    index,
                    pins
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
        const { parts, name } = this.state
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
                onChange={(val: number) => {
                    this.setState(({ parts }: State) => {
                        const part = parts.find(item => item.name === this.state.name)
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
            </div>
        )
    }
}