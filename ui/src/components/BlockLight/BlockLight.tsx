import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Select, TreeSelect} from 'antd'
import { Form, Divider, Tabs, Row, Col, Modal } from 'antd'
import { MathMarkdown } from '../Block/Mathdown';
import './BlockLight.css'
import { UnitInput } from '../UnitInput'
import { TBlocksScope, BlocksMenu, loadBlocks, insertSpaces, resolveBlock } from '../Blocks/Blocks'
import { IBlock } from '../Block'
import { TProbeBlock } from '../Probe'
import { Radio } from 'antd'

const RadioButton = Radio.Button
const RadioGroup = Radio.Group

const TreeNode = TreeSelect.TreeNode
const { Option, OptGroup } = Select

const cnBlock = cn('BlockLight')

const initialState = {
    name: '',
    pins: {},
    blocks: {},
    selectedMods: [],
    index: -1,
    serial: [],
    probes: []
}

// type State = typeof initialState


type State = {
    name: string,
    pins: IBlock['pins'],
    blocks: TBlocksScope,
    block?: IBlock,
    selectedMods: string[],
    index: number,
    serial: {
        port: string,
        desc: string
    }[],
    probes: TProbeBlock[]
}

export class BlockLight extends React.Component<IProps, {}> {
    state: State = {
        ...initialState,
        name: this.props.block.name,
        index: this.props.block.index >= 0
            ? this.props.block.index 
            : -1,
        pins: this.props.block.pins,
        selectedMods: this.props.block.mods 
            ? Object.keys(this.props.block.mods).map((mod: string) => `${mod}=${this.props.block.mods && this.props.block.mods[mod]}`)
            : []
    }

    componentWillMount() {
        loadBlocks((blocks: TBlocksScope) =>
            this.setState({ blocks })
        )
        
        // this.state.name && this.loadBlock()
        this.loadSource(this.props.block)

        axios.get('/api/serial/')
            .then(res =>
                this.setState({ serial: res.data })
        )
        
        axios.get('/api/probes/')
            .then(res => {
                const probes = res.data
                this.setState({ probes })
            })
        

        return true
    }

    handleDeviceChange({ protocol, port, channel }: any) {
        this.setState(({ block }: State) => {
            if (block) {
                console.log(block)
                const device = block && block.args.device ? (block.args.device.value.toString()) : ':::'
                const [device_protocol = '', device_port = '', device_channel = ''] = device.split(':')
                const device_arg = block.args.device || {}
                if(protocol === 'off') {
                    device_arg.value = ''
                } else {
                    device_arg.value = (protocol || device_protocol) + ':' + (port || device_port) + ':' + (channel || device_channel)
                }
            }

            return { block }
        }, () => this.props.onChange(this.getCurrentLoad()))
    }

    loadBlock(callback?: any) {
        const selectedMods: { [name:string]: string[] } = this.state.selectedMods.reduce((mods: { [name:string]: string[] }, mod) => {
            const [type, value] = mod.split(':')
            mods[type] = mods[type] || []
            mods[type].push(value)

            return mods
        }, {})

        const args = this.state.block
            ? this.state.block.args
            : {}

        const modsUrlParam = Object.keys(selectedMods).map((mod:string) => mod + '=' + selectedMods[mod].join(','))
        const argsUrlParam = Object.keys(args).map(arg => arg + '=' + args[arg].value)
        let urlParams = '?' + modsUrlParam.concat(argsUrlParam).join('&')
        
        axios.get('/api/blocks/' + this.state.name + '/' + urlParams)
            .then(res => {
                const block = res.data
                const selectedMods = Object.keys(block.mods).reduce((selected, type) =>
                    selected.concat(
                        block.mods[type].map((value: string) => type + ':' + value)
                    ), [])
                        
                this.setState({
                    block,
                    selectedMods
                }, () => callback && callback())
            })
    }
    getCurrentLoad() {
        const { name, block } = this.state
    
        return {
            name,
            description: block ? block.description : [],
            args: block ? block.args : {},
            mods: block ? block.mods : {},
            pins: Object.assign({}, this.state.pins),
            nets: {},
            params: {},
            probes: block ? block.probes : {},
            index: this.state.index
        }

    }
    loadSource({ name, args, pins, index, mods, probes }: IBlock) {
        if (index === -1 || index === undefined) {
            this.setState({
                name: undefined,
                block: undefined,
                index: -1,
                pins: {}
            })
        } else {
            const _mods: any = mods || {}
            const selectedMods = mods
                ? Object.keys(mods).reduce((selected, type) =>
                    selected.concat(
                        _mods[type].map((value: string) => type + ':' + value)
                    ), [])
            : []
            this.setState({
                name,
                block: {
                    pins: {},
                    args,
                    description: []
                },
                pins,
                index,
                selectedMods
            }, () =>
                    this.loadBlock(() => 
                        this.setState(({ block }: State) => {
                            block && Object.keys(block.args).filter(arg => args[arg]).forEach(arg => {
                                const floated = parseFloat(args[arg].value.toString())
                                block.args[arg].value = isNaN(floated) ? args[arg].value : floated
                            })
                            const block_args = block ? block.args : {}
                            
                            return {
                                block: {
                                    ...block,
                                    probes,
                                    args: {
                                        ...block_args,
                                        ...args
                                    }
                                }
                            }
                        })
                ))
        }
    }
    componentDidUpdate(prevProps: IProps) {
        if (prevProps.block.index !== this.props.block.index) {
            this.loadSource(this.props.block)
        }
    }
    render() { 
        const { type, onChange } = this.props
        const { blocks, block, name } = this.state


        const args: any = block
            ? block.args
            : {}
        const pins: string[] = block 
            ? Array.isArray(block.pins) ? block.pins : Object.keys(block.pins).filter(pin => block.pins[pin].length  > 0)
            : []

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
                    this.setState(({ block }: State) => {
                        if (block) {
                            block.args[name].value = val
                        }

                        return { block }
                    }, () => onChange(this.getCurrentLoad()))
                }}
            />
        })

        const formItemLayout = {
            labelCol: { span: 7 },
            wrapperCol: { span: 12 },
        }
        
        const Pins = <Form>
            {pins.map(pin => {
                const probe = block && block.probes && block.probes[pin]

                return (<Form.Item label={pin} {...formItemLayout} key={pin}>
                    <Select
                        mode="multiple"
                        placeholder='Select Attached Block Pins'
                        value={this.state.pins && this.state.pins[pin]}
                        onChange={(value: string[]) => {
                            this.setState(({ pins }: State) => {
                                pins[pin] = value

                                return { pins }
                            }, () => onChange(this.getCurrentLoad()))
                        }}
                    >
                        {this.props.pins.map(pin => <Option key={pin} value={pin}>{pin}</Option>)}
                    </Select>
                    {this.state.probes &&
                        <Select
                            placeholder='Select probe'
                            value={probe && probe.name}
                            // defaultValue=''
                            onChange={name => {
                                this.setState(({ block }: State) => {
                                    console.log(name, block)
                                    if (block) {
                                        const probes = block.probes || {}
                                        const probe_pin = probes[pin] || {}
                                        probe_pin.name = name
                                        probes[pin] = probe_pin
                                        block.probes = probes
                                    }
    
                                    return { block }
                                }, () => onChange(this.getCurrentLoad()))
                            }}
                        >
                            {this.state.probes.map(item => <Option value={item.name} key={item.name}>{item.description}</Option>)}
                        </Select>}
                    {probe && probe.name &&
                        <RadioGroup onChange={e =>
                            this.setState(({ block }: State) => {
                                console.log(name, block)
                                if (block) {
                                    const probes =  block.probes || {}
                                    const probe_pin = probes[pin] || {}
                                    probe_pin.channel = e.target.value 
                                    probes[pin] = probe_pin
                                    block.probes = probes
                                }

                                return { block }
                            }, () => onChange(this.getCurrentLoad()))
                        } defaultValue={probe.channel}>
                            <RadioButton value="0">None</RadioButton>
                            {this.state.probes.reduce((pins, item) => item.name === probe.name ? item.pins : pins, ['']).map(ch => <RadioButton value={ch} key={ch}>{ch}</RadioButton>)}
                        </RadioGroup>}
                </Form.Item>)
            })}
            </Form>

        const description = block && block.description.map((description, index) =>
            <MathMarkdown key={index} value={description}/>
        )

        const device = block && block.args['device'] ? (block.args['device'].value.toString()) : ':::'
        const [device_protocol, device_port, device_channel] = device.split(':')
        const device_defenition = block && block.devices && block.devices[device_protocol]

        const Devices = block && block.devices && Object.keys(block.devices).length
            ? <>
                <Divider orientation="left">Device</Divider>
                <RadioGroup onChange={e => this.handleDeviceChange({ protocol: e.target.value })} defaultValue={device_protocol}>
                    <RadioButton value='off'>Off</RadioButton>
                    {Object.keys(block.devices).map(device => <RadioButton value={device}>{block.devices && block.devices[device] && block.devices[device].title}</RadioButton>)}
                </RadioGroup>
                {device_protocol &&
                    <>
                        <Select
                            className={cnBlock('SerialPort')}
                            defaultValue={device_port}
                            style={{ width: '100%' }}
                            placeholder='Select serial port'
                            onChange={port => this.handleDeviceChange({ port })}
                        >
                            {this.state.serial.map(item => <Option value={item.port} key={item.port}>{item.port} {item.desc}</Option>)}
                    
                        </Select>
                    </>}
                {device_defenition && device_defenition.channels.length 
                    ?
                    <RadioGroup onChange={e => this.handleDeviceChange({ channel: e.target.value })} defaultValue={device_channel}>
                        <RadioButton value="0">None</RadioButton>
                        {device_defenition.channels.map((channel, index) => <RadioButton value={(index + 1).toString()}>{channel}</RadioButton>)}
                    </RadioGroup>
                    : null}
            </>
            : null
        
        const mods:any = name && resolveBlock(name, blocks)

        return (
            <div className={cnBlock()}>
                <Row>
                    <Col span={8}>
                    <BlocksMenu
                        onClick={(param:any) => {
                            this.setState({
                                name: param.key
                            }, () =>
                                    this.loadBlock(
                                        () => onChange(this.getCurrentLoad())
                                    )
                            )
                        }}
                        onOpenChange={() => { }}
                        blocks={blocks}
                    /></Col>

                    <Col span={16} className={cnBlock('Modificator')}>
                        <Row>
                            <Col span={12} className={cnBlock('Title')}>
                                <h2>{insertSpaces(name || 'Select Block')}</h2>
                            </Col>
                            <Col span={12}>
                                {mods && Object.keys(mods).length  
                                ?  <TreeSelect
                                    showSearch
                                    style={{ width: '100%' }}
                                    value={this.state.selectedMods}
                                    placeholder="Modificators"
                                    treeCheckable={true}
                                    multiple
                                    treeDefaultExpandAll
                                    onChange={selectedMods => this.setState({ selectedMods }, this.loadBlock)}
                                >
                                    {Object.keys(mods).map(type =>
                                        <TreeNode value={type} title={type} key={type}>
                                            {mods[type].map((value:any) => 
                                                <TreeNode value={type + ':' + value} title={value} key={type + ':' + value} />
                                            )}
                                        </TreeNode>
                                    )}
                                </TreeSelect>
                                : ''}
                            </Col>
                        </Row>
                        
                        
                        {description}
                        <Divider orientation="left">Properties</Divider>
                        <div className={cnBlock('Attributes')}>
                            {attributes}
                        </div>
                        <Divider orientation="left">Pins</Divider>
                        {Pins}
                        
                        {Devices}
                        
                    </Col>
                </Row>
                
                
            </div>
        )
    }
}