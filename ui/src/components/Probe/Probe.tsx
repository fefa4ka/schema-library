import * as React from 'react'
import { IProps, TProbe, TArgs } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Button, Select, TreeSelect} from 'antd'
import { Form, Divider, Spin, Tabs, Row, Col, Modal } from 'antd'
import './Probe.css'

import { Radio } from 'antd';

const RadioButton = Radio.Button;
const RadioGroup = Radio.Group;


const { Option } = Select

const cnPart = cn('Probe')

const initialState = {
    pins: {},
    parts: [],
}

// type State = typeof initialState

type TPart = {
    name: string,
    description: string,
    pins: string[],
    args: TArgs
}

type State = {
    parts: TPart[]
}


export class Part extends React.Component<IProps, {}> {
    state: State = initialState

    componentWillMount() {
        this.loadParts()

        return true
    }
    loadParts() {
        axios.get('http://localhost:3000/api/probes/')
            .then(res => {
                const parts = res.data
                this.setState({ parts })
            })
    }
    getCurrentProbe() {
        return this.props.probe
    }
    // loadProbe(pins:any) {
    //     this.setState({ pins })
    // }
    // componentDidUpdate(prevProps: IProps) {
    //     if (prevProps.probe.index !== this.props.probe.index) {
    //         this.loadProbe(this.props.probe)
    //     }
    // }
    render() { 
        const { onChange } = this.props
        const { parts } = this.state
      
        const formItemLayout = {
            labelCol: { span: 7 },
            wrapperCol: { span: 12 },
        }

        const Pins = <Form>
            {this.props.pins.map(pin => {
                const pin_state = this.props.probe && this.props.probe[pin]

                return (<Form.Item label={pin} {...formItemLayout} key={pin}>
                   <Select
                        style={{ width: '100%' }}
                        placeholder='Select Power Probe'
                        value={pin_state && pin_state.name}
                        onChange={name => onChange(({ probes }: any) => {
                            const pins = probes || {}
                            pins[pin] = pins[pin] || {}
                            pins[pin].name = name
                            return { probes: pins }
                        })}
                    >
                        {parts.map(item => <Option value={item.name} key={item.name}>{item.description}</Option>)}  
                    </Select>
                    
                    {pin_state &&
                        <RadioGroup onChange={e =>
                            onChange(({ probes }: any) => {
                                const pins = probes || {}
                                pins[pin] = pins[pin] || {}
                                pins[pin].channel = e.target.value
                                return { probes: pins }
                            })
                        } defaultValue="0">
                            <RadioButton value="0">None</RadioButton>
                            {this.state.parts.reduce((pins, item) => item.name === pin_state.name ? item.pins : pins, ['']).map(ch => <RadioButton value={ch} key={ch}>{ch}</RadioButton>)}
                        </RadioGroup>}
                </Form.Item>)
            })}
            </Form>

        
        return (
            <div className={cnPart()}>
                <Divider orientation="left">Pins</Divider>
                {this.props.loading 
                    ? <Spin size="large" />
                    : Pins
                }
            
            </div>
        )
    }
}