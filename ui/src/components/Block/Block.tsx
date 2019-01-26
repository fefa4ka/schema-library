import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Divider, Tag, Button, Input, TreeSelect} from 'antd'
import { Icon, Tabs, Row, Col, Modal } from 'antd'
import Markdown from 'react-markdown'
import { Part } from '../Part'
const { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceArea } = require('recharts')
const TabPane = Tabs.TabPane;
import { UnitInput } from '../UnitInput'
import { Diagram } from './Diagram'
const TreeNode = TreeSelect.TreeNode;
import {UnControlled as CodeMirror} from 'react-codemirror2'

import './Block.css';
require('codemirror/lib/codemirror.css')
require('codemirror/mode/python/python')

const cnBlock = cn('Block')


const initialState = {
    name: '',
    description: [''],
    selectedMods: [],
    args: {},
    nets: {},
    pins: {},
    params: {},
    modalVisible: false,
    chartData: [],
    modalConfirmLoading: false,
    editableSource: {
        name: '',
        args: {},
        pins: {},
        index: -1
    },
    sources: [{
        'name': 'SINEV',
        'args': { 'amplitude': '10', 'frequency': '20' },
        'pins': { 'p': ['input'], 'n': ['output', 'gnd'] },
        'index': 0
    }],
    mods: {},
    example: ''
}

type Source = {
    name: string,
    args: {
        [name: string]: string 
    },
    pins: {
        [name: string]: string[]
    },
    index: number
}

type State = {
    name: string,
    description: string[],
    selectedMods: string[],
    nets: {
        [name:string]: string[]
    },
    pins: {
        [name:string]: string[]
    },
    args: {
        [name:string]: {
            value: number | string,
            unit: {
                name: string,
                suffix: string
            }
        }
    },
    params: {
        [name:string]: {
            value: number | string,
            unit: {
                name: string,
                suffix: string
            }
        }
    },
    editableSource: Source,
    sources: Source[],
    chartData: {
        [name:string]: number[]
    }[],
    modalVisible: boolean,
    modalConfirmLoading: boolean,
    mods?: {
        [name:string]: string[]
    },
    example: string
}


export class Block extends React.Component<IProps, {}> {
    state: State = initialState
    codeInstance: any

    componentDidUpdate(prevProps: IProps, prevState: State) {
        // console.log(prevProps.name, this.props.name)
        // console.log(prevState.selectedMods.join(''), this.state.selectedMods.join(''))
        if (prevProps.name !== this.props.name) {
            this.setState({
                selectedMods: [],
                args: {},
                charData: []
            }, this.loadBlock)
        }

        return true
    }
    loadSimulation() {
        const { args, sources } = this.state


        axios.post('http://localhost:3000/api/blocks/' + this.props.name + '/simulate/',
        {
            mods: this.state.mods,
            args: Object.keys(args).reduce((result: { [name:string]: string | number }, arg) => {
                result[arg] = args[arg].value
                
                return result
            }, {}),
            sources
        })
            .then(res => {
                this.setState({ chartData: res.data })
            })
    }
    loadBlock() {
        const selectedMods: { [name:string]: string[] } = this.state.selectedMods.reduce((mods: { [name:string]: string[] }, mod) => {
            const [type, value] = mod.split('=')
            mods[type] = mods[type] || []
            mods[type].push(value)

            return mods
        }, {})

        const modsUrlParam = Object.keys(selectedMods).map((mod:string) => mod + '=' + selectedMods[mod].join(','))
        const argsUrlParam = Object.keys(this.state.args).map(arg => arg + '=' + this.state.args[arg].value)
        
        let urlParams = '?' + modsUrlParam.concat(argsUrlParam).join('&')
        // if (argsUrlParam.length === 0) {
        //     urlParams = ''
        // }
    
            
        axios.get('http://localhost:3000/api/blocks/' + this.props.name + '/' + urlParams)
            .then(res => {
                const { name, description, args, params, mods, pins, parts, nets } = res.data
                const { sources } = this.state
               
                
                const selectedMods = Object.keys(mods).reduce((selected, type) =>
                    selected.concat(
                        mods[type].map((value: string) => type + '=' + value)
                    ), [])
                
                const codeUnits = Object.keys(args).map(arg => args[arg].unit.suffix).filter((value, index, self) => self.indexOf(value) === index).map(item => 'u_' + item).join(', ')
                const codeArgs = Object.keys(args).map(arg => arg + ' = ' + args[arg].value + ' @ u_' + args[arg].unit.suffix).join(',\n\t')
                const codeMods = Object.keys(mods).map((mod:string) => mod + "=['" + mods[mod].join("', '") + "']").join(', ')
                const codeExample = `from bem import Build
from PySpice.Unit import ${codeUnits}

# With variables
${name} = Build('${name}', ${codeMods}).block
${name.toLowerCase()} = ${name}(
    ${codeArgs}
)

# Inline
Build('${name}', ${codeMods}).block(
    ${codeArgs}
)`

                this.setState({
                    description,
                    mods,
                    args,
                    params, 
                    nets,
                    pins,
                    example: codeExample,
                    selectedMods
                }, this.loadSimulation)
            })
    }
    showModal = () => {
        console.log(this.state.editableSource)
        this.setState({
            modalVisible: true,
        });
    }
    handleOk = () => {
        this.setState(({ sources, editableSource }: State) => {
            console.log('modalok', editableSource)
            if (editableSource.index >= 0) {
                sources[editableSource.index] = editableSource
            } else {
                sources = sources.concat([editableSource])
            }

            return {
                modalConfirmLoading: false,
                sources,
                editableSource: {},
                modalVisible: false,
            }
        }, this.loadSimulation)
    }

    handleCancel = () => {
        console.log('Clicked cancel button');
        this.setState({
            modalVisible: false,
            editableSource: {},
            example: ''
        }, () => this.codeInstance.refresh())
    }
    render() {
        const { mods } = this.props
        
        const description = this.state.description.map((description, index) =>
            <Markdown key={index} source={description}/>
        )

        const attributes = Object.keys(this.state.args).map(name => {
            const isExists = this.state.args.hasOwnProperty(name)

            if (isExists && this.state.args[name].unit.name === 'network') {
                return null
            }

            const suffix = isExists
                ? this.state.args[name].unit.suffix
                : ''
            const value = isExists
                ? this.state.args[name].value
                : 0
            const [arg_title, arg_sub] = name.split('_')

            const save = (value:string) => {

                this.setState((prevState: State) => {
                    prevState.args[name].value = parseFloat(value)
                    
                    return prevState
                }, () => {
                    parseFloat(value) > 0 && this.loadBlock()
                })
            }

            return <UnitInput
                key={name}
                name={[arg_title, <sub key='s'>{arg_sub}</sub>]}
                suffix={suffix}
                value={value.toString()}
                onChange={save}
                className={cnBlock('ArgumentInput')}
            />
        })

        const params = Object.keys(this.state.params).map((name, index) => {
            const isExists = this.state.params.hasOwnProperty(name)

            if (isExists && this.state.params[name].unit.name === 'network') {
                return null
            }

            const suffix = isExists
                ? this.state.params[name].unit.suffix
                : ''
            const value = isExists
                ? this.state.params[name].value
                : 0
            const [arg_title, arg_sub] = name.split('_')
            
            return <Input
                key={name + index}
                addonBefore={[arg_title, <sub key='s'>{arg_sub}</sub>]}
                addonAfter={suffix}
                value={value.toString()}
                disabled={true}
                className={cnBlock('ParamInput')}
            />
        })

        return (
            <div className={this.props.className || cnBlock()}>
                <Row>
                    <Col span={12} className={cnBlock('Title')}>
                        <h1>
                            {this.props.name}
                        </h1>
                    </Col>
                        
                    <Col span={12} className={cnBlock('Modificator')}>
                        {mods && Object.keys(mods).length 
                            ? <TreeSelect
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
                                        {mods[type].map(value => 
                                            <TreeNode value={type + '=' + value} title={value} key={type + '=' + value} />
                                        )}
                                    </TreeNode>
                                )}
                            </TreeSelect>
                            : ''}
                    </Col>
                </Row>
            
                <Tabs defaultActiveKey="1" onChange={_ => {console.log('tab')}}>
                    <TabPane tab="Simulation" key="1">
                        <Row>
                            <Col span={17} className={cnBlock('Description')}>
                                <Divider orientation="left">
                                    Description
                                </Divider>
                                {description}
                                <Row className={cnBlock('Pins')}>
                                    <Col span={8}>
                                        <Divider orientation="left">
                                            Sources 
                                        </Divider>
                                        
                                        <Modal
                                            title="Title"
                                            visible={this.state.modalVisible}
                                            onOk={this.handleOk}
                                            onCancel={this.handleCancel}
                                            >
                                                <Part
                                                    type='source'
                                                    source={this.state.editableSource}
                                                    pins={Object.keys(this.state.pins)}
                                                    onChange={(source:Source) =>
                                                        this.setState(({ editableSource }:State) => ({ editableSource: source }), () => console.log('change', this.state))
                                                    }
                                                />
                                        </Modal>
                                        {this.state.sources.map((source, index) => 
                                            <Tag
                                                key={source.name + index.toString()}
                                                closable
                                                onClick={_ => {
                                                    this.setState({ editableSource: this.state.sources[index] }, this.showModal)
                                                }}
                                                onClose={() => {
                                                    this.setState(({ sources }: State) => {
                                                        
                                                        sources.splice(index, 1)
                                                        
                                                        return { sources }
                                                    })
                                            }}>
                                                {source.name}
                                            </Tag>
                                        )} <Tag className={cnBlock('AddPart')} onClick={() => this.setState({ editableSource: { index: -1} }, this.showModal) }><Icon type="api" /> Add</Tag>

                                        <Divider orientation="left">Load</Divider>
                                        <Tag className={cnBlock('AddPart')} onClick={() => this.setState({ editableSource: { index: -1} }, this.showModal) }><Icon type="api" /> Add</Tag>
                                    </Col>
                                    <Col span={16}>
                                        <Divider orientation="left">
                                            Schematics
                                        </Divider>
                                        <Diagram pins={this.state.pins} nets={this.state.nets} sources={this.state.sources} /></Col>
                                </Row>
                            </Col>
                            <Col span={7} className={cnBlock('Characteristics')}>
                                <Divider orientation="left">Characteristics</Divider>
                                {attributes}
                                {params}
                                <Divider orientation="left">Code Examples</Divider>
                                {this.state.example && <CodeMirror
                                    className={cnBlock('CodeExample')}
                                    options={{
                                        mode: 'python',
                                    }}
                                    value={this.state.example}
                                />}
                            </Col>
                        </Row> 
                        
                        <Divider orientation="left">Waveforms</Divider>
                        <ResponsiveContainer width='100%' aspect={4.0/1.0}>
                            <LineChart data={this.state.chartData}>
                                <XAxis dataKey="time"/>
                                <YAxis yAxisId="left" />
                                <YAxis yAxisId="right" orientation="right" />
                                <CartesianGrid strokeDasharray="3 3"/>
                                <Tooltip/>
                                <Legend />
                                <Line type="monotone" dataKey="V_in" stroke="#1890ff" dot={false} unit='V' yAxisId="left" />
                                <Line type="monotone" dataKey="V_out" stroke="#000000" dot={false} unit='V' yAxisId="left" />
                                <Line type="monotone" dataKey="I_out" stroke="red" dot={false} unit='A' yAxisId="right" />
                            </LineChart>
                        </ResponsiveContainer>
                    </TabPane>
                    <TabPane tab="Code" key="2">Code</TabPane>
                </Tabs>
            </div>
        )
    }
}
