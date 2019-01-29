import * as React from 'react'
import { IProps, TSource, TArgs } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Button, Select, TreeSelect} from 'antd'
import { Form, Divider, Tabs, Row, Col, Modal } from 'antd'
import Markdown from 'react-markdown'
const { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceArea } = require('recharts')
const TabPane = Tabs.TabPane;
import './Part.css'
import { UnitInput } from '../UnitInput'

const nomnoml = require('nomnoml')
const TreeNode = TreeSelect.TreeNode;
const { Option, OptGroup } = Select

const cnPart = cn('Part')

const initialState = {
    name: '',
    pins: {},
    parts: {},
    selectedMods: [],
    index: -1
}

// type State = typeof initialState



type TPartList = {
    [name: string]: {
        [name: string]: string[]
    }
}
type State = {
    name: string,
    pins: TSource['pins'],
    parts: TPartList,
    part?: TSource,
    selectedMods: string[],
    index: number
}


export class Part extends React.Component<IProps, {}> {
    state: State = {
        ...initialState,
        name: this.props.source.name,
        index: this.props.source.index >= 0
            ? this.props.source.index 
            : -1,
        pins: this.props.source.pins,
        selectedMods: this.props.source.mods 
            ? Object.keys(this.props.source.mods).map((mod: string) => `${mod}=${this.props.source.mods && this.props.source.mods[mod]}`)
            : []
    }

    componentWillMount() {
        this.loadParts()
        this.state.name && this.loadPart()

        return true
    }
    loadParts() {
        axios.get('http://localhost:3000/api/blocks/')
            .then(res => {
                const parts = res.data
                this.setState({ parts })
            })
    }
    loadPart(callback?: any) {
        const selectedMods: { [name:string]: string[] } = this.state.selectedMods.reduce((mods: { [name:string]: string[] }, mod) => {
            const [type, value] = mod.split('=')
            mods[type] = mods[type] || []
            mods[type].push(value)

            return mods
        }, {})

        const args = this.state.part
            ? this.state.part.args
            : {}

        const modsUrlParam = Object.keys(selectedMods).map((mod:string) => mod + '=' + selectedMods[mod].join(','))
        const argsUrlParam = Object.keys(args).map(arg => arg + '=' + args[arg].value)
        let urlParams = '?' + modsUrlParam.concat(argsUrlParam).join('&')
        
        axios.get('http://localhost:3000/api/blocks/' + this.state.name + '/' + urlParams)
            .then(res => {
                const part = res.data
                const selectedMods = Object.keys(part.mods).reduce((selected, type) =>
                    selected.concat(
                        part.mods[type].map((value: string) => type + '=' + value)
                    ), [])
                        
                this.setState({
                    part,
                    selectedMods
                }, () => callback && callback())
            })
    }
    getCurrentLoad() {
        const { name, part } = this.state
    
        return {
            name,
            description: part ? part.description : [],
            args: part ? part.args : {},
            mods: part ? part.mods : {},
            pins: Object.assign({}, this.state.pins),
            nets: {},
            params: {},
            index: this.state.index
        }

    }
    loadSource({ name, args, pins, index, mods }: TSource) {
        if (index === -1 || index === undefined) {
            this.setState({
                name: undefined,
                part: undefined,
                index: -1,
                pins: {}
            })
        } else {
            const _mods: any = mods || {}
            const selectedMods = mods
                ? Object.keys(mods).reduce((selected, type) =>
                    selected.concat(
                        _mods[type].map((value: string) => type + '=' + value)
                    ), [])
            : []
            this.setState({
                name,
                part: {
                    pins: {},
                    args,
                    description: []
                },
                pins,
                index,
                selectedMods
            }, () =>
                    this.loadPart(() => 
                        this.setState(({ part }: State) => {
                            part && Object.keys(part.args).forEach(arg => {
                                const floated = parseFloat(args[arg].value.toString())
                                part.args[arg].value = isNaN(floated) ? args[arg].value : floated
                            })
                            
                            return {
                                part: {
                                    ...part,
                                    args
                                }
                            }
                        })
                ))
        }
    }
    componentDidUpdate(prevProps: IProps) {
        if (prevProps.source.index !== this.props.source.index) {
            this.loadSource(this.props.source)
        }
    }
    render() { 
        const { type, onChange } = this.props
        const { parts, part, name } = this.state

        const args: any = part
            ? part.args
            : {}
        const pins: string[] = part 
            ? Array.isArray(part.pins) ? part.pins : Object.keys(part.pins).filter(pin => part.pins[pin].length  > 0)
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
                    this.setState(({ part }: State) => {
                        if (part) {
                            part.args[name].value = val
                        }

                        return { part }
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
                </Form.Item>)
            })}
            </Form>

        const description = part && part.description.map((description, index) =>
            <Markdown key={index} source={description}/>
        )
        const mods = this.state.parts[name]

        return (
            <div className={cnPart()}>
                <Row>
                    <Col span={mods && Object.keys(mods).length ? 12 : 24}>
                    <Select
                        style={{ width: '100%' }}
                        placeholder='Select Load'
                        value={this.state.name}
                        onChange={name =>
                            this.setState({
                                name
                            }, () =>
                                    this.loadPart(
                                        () => onChange(this.getCurrentLoad())
                                    )
                            )
                        }
                    >   
                        {Object.keys(parts).map(item => <Option value={item} key={item}>{item}</Option>)}
                    </Select>
                    </Col>
                    {mods && Object.keys(mods).length  
                    ? <Col span={12} className={cnPart('Modificator')}>
                            <TreeSelect
                                showSearch
                                style={{ width: '100%' }}
                                value={this.state.selectedMods}
                                placeholder="Modificators"
                                treeCheckable={true}
                                multiple
                                treeDefaultExpandAll
                                onChange={selectedMods => this.setState({ selectedMods }, this.loadPart)}
                            >
                                {Object.keys(mods).map(type =>
                                    <TreeNode value={type} title={type} key={type}>
                                        {mods[type].map(value => 
                                            <TreeNode value={type + '=' + value} title={value} key={type + '=' + value} />
                                        )}
                                    </TreeNode>
                                )}
                            </TreeSelect>
                        </Col>
                    : ''}
                    
                </Row>
                
                {description}
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