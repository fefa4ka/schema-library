import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Divider, Tag, Button, Input, TreeSelect} from 'antd'
import { Icon, Tabs, Row, Col, Modal } from 'antd'
import Markdown from 'react-markdown'
import { Source, TSource } from '../Source'
import { Part } from '../Part'
const { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceArea } = require('recharts')
const TabPane = Tabs.TabPane;
import { UnitInput } from '../UnitInput'
import { Diagram } from './Diagram'
import { Code } from '../Code'
const TreeNode = TreeSelect.TreeNode;
import {UnControlled as CodeMirror} from 'react-codemirror2'

import './Block.css'
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
    modalSourceVisible: false,
    modalLoadVisible: false,
    chartData: [],
    modalConfirmLoading: false,
    editableSource: {
        name: '',
        description: '',
        args: {},
        pins: {},
        index: -1
    },
    editableSourceType: '',
    sources: [{
        'name': 'SINEV',
        'description': 'Sinusoidal voltage source',
        'args': {
            'amplitude': {
                value: '10',
                unit: {
                    name: 'volt',
                    suffix: 'V'
                }
            },
            'frequency': {
                value: 20,
                unit: {
                    name: 'volt',
                    suffix: 'A'
                }
            }
        },
        'pins': { 'p': ['input'], 'n': ['gnd'] },
        'index': 0
    }],
    editableLoad: {
        name: '',
        description: '',
        args: {},
        pins: {},
        index: -1
    },
    load: [{
        name: 'RLC',
        description: '',
        mods: {
            series: ['R']
        },
        args: {
            R_series: {
                value: '10',
                unit: {
                    name: 'ohm',
                    suffix: 'Ω'
                }
            }
        },
        pins: {
            input: ['output'],
            output: ['gnd']
        },
        index: 0
    }],
    mods: {},
    example: '',
    files: []
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
    load: TSource[],
    editableLoad: TSource,
    editableSource: TSource,
    editableSourceType: string,
    sources: TSource[],
    chartData: {
        [name:string]: number[]
    }[],
    modalSourceVisible: boolean,
    modalLoadVisible: boolean,
    modalConfirmLoading: boolean,
    mods?: {
        [name:string]: string[]
    },
    example: string,
    files: string[]
}


export class Block extends React.Component<IProps, {}> {
    state: State = initialState
    codeInstance: any
    componentWillMount() {
        this.loadBlock()
    }
    componentDidUpdate(prevProps: IProps, prevState: State) {
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
        const { args, sources, load } = this.state


        axios.post('http://localhost:3000/api/blocks/' + this.props.name + '/simulate/',
        {
            mods: this.state.mods,
            args: Object.keys(args).reduce((result: { [name:string]: string | number }, arg) => {
                result[arg] = args[arg].value
                
                return result
            }, {}),
            sources,
            load
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
                const { name, description, args, params, mods, pins, files, nets } = res.data
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
${name} = Build('${name}'${codeMods ? ', ' + codeMods: ''}).block
${name.toLowerCase()} = ${name}${codeArgs ? `(
    ${codeArgs}
)` : '()'}

# Inline
Build('${name}'${codeMods ? ', ' + codeMods: ''}).block${codeArgs ? `(
    ${codeArgs}
)` : '()'}`

                this.setState({
                    description,
                    mods,
                    args,
                    params, 
                    nets,
                    pins,
                    example: codeExample,
                    files,
                    selectedMods
                }, this.loadSimulation)
            })
    }
    showModal = (name:string) => {
        this.setState({
            [`modal${name}Visible`]: true,
        });
    }
    handleSourceOk = () => {
        this.setState(({ sources, editableSource }: State) => {
            if (editableSource.index >= 0) {
                sources[editableSource.index] = editableSource
            } else {
                sources = sources.concat([editableSource])
            }

            return {
                modalConfirmLoading: false,
                sources,
                editableSource: {},
                modalSourceVisible: false,
            }
        }, this.loadSimulation)
    }
    handleLoadOk = () => {
        this.setState(({ load, editableLoad }: State) => {
            
            if (editableLoad.index >= 0) {
                load[editableLoad.index] = editableLoad
            } else {
                load = load.concat([editableLoad])
            }

            console.log('modalok', load, editableLoad)

            return {
                modalConfirmLoading: false,
                load,
                editableLoad: {},
                modalLoadVisible: false,
            }
        }, this.loadSimulation)
    }
    handleModalCancel = (name:string) => {
        console.log(name, 'Clicked cancel button');
        this.setState({
            [`modal${name}Visible`]: false,
            editableSource: {},
            editableLoad: {}
        })
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
            
                <Tabs defaultActiveKey="1" onChange={_ => {console.log('tab')}}  className={cnBlock('BlockTabs')}>
                    <TabPane tab="Simulation" key="1">
                        <Row>
                            <Col span={17} className={cnBlock('Description')}>
                                <Divider orientation="left">
                                    Description
                                </Divider>
                                {description}
                                <Row className={cnBlock('Pins')}>
                                    
                                    <Col span={24}>
                                        <Divider orientation="left">
                                            Schematics
                                        </Divider>
                                        <Diagram pins={this.state.pins} nets={this.state.nets} sources={this.state.sources} load={this.state.load}/></Col>
                                </Row>
                                <Row>
                                <Col span={12}>
                                        <Divider orientation="left">
                                            Sources 
                                        </Divider>
                                        
                                        <Modal
                                            title="Add Power Source"
                                            visible={this.state.modalSourceVisible}
                                            onOk={this.handleSourceOk}
                                            onCancel={() => this.handleModalCancel('Source')}
                                            >
                                                <Source
                                                    type={this.state.editableSourceType}
                                                    source={this.state.editableSource}
                                                    pins={Object.keys(this.state.pins)}
                                                    onChange={(source:TSource) =>
                                                        this.setState(({ editableSource }:State) => ({ editableSource: source }), () => console.log('change', this.state))
                                                    }
                                                />
                                        </Modal>

                                        {this.state.sources.map((source, index) => 
                                            <Tag
                                                key={source.name + index.toString()}
                                                closable
                                                onClick={_ => {
                                                    this.setState({ editableSource: this.state.sources[index] }, () => this.showModal('Source'))
                                                }}
                                                onClose={() => {
                                                    this.setState(({ sources }: State) => {
                                                        
                                                        sources.splice(index, 1)
                                                        
                                                        return { sources }
                                                    })
                                            }}>
                                                {source.name}
                                            </Tag>
                                        )} <Tag className={cnBlock('AddPart')} onClick={() => this.setState({ editableSourceType: 'source', editableSource: { index: -1} }, () => this.showModal('Source')) }><Icon type="api" /> Add</Tag>
                                    </Col>
                                    <Col span={6}>
                                        <Divider orientation="left">Load</Divider>
                                        {this.state.load.map((source, index) => 
                                            <Tag
                                                key={source.name + index.toString()}
                                                closable
                                                onClick={_ => {
                                                    this.setState({ editableLoad: this.state.load[index] }, () => this.showModal('Load'))
                                                }}
                                                onClose={() => {
                                                    this.setState(({ load }: State) => {
                                                        
                                                        load.splice(index, 1)
                                                        
                                                        return { load }
                                                    })
                                            }}>
                                                {source.name}
                                            </Tag>
                                        )}<Tag className={cnBlock('AddPart')} onClick={() => this.setState({ editableLoad: { index: -1 } }, () => this.showModal('Load'))}><Icon type="api" /> Add</Tag>
                                        
                                        <Modal
                                            title="Add Load"
                                            visible={this.state.modalLoadVisible}
                                            onOk={this.handleLoadOk}
                                            onCancel={() => this.handleModalCancel('Load')}
                                            >
                                                <Part
                                                    source={this.state.editableLoad}
                                                    pins={Object.keys(this.state.pins)}
                                                onChange={(load: TSource) =>
                                                        this.setState({ editableLoad: load }, () => console.log('change', this.state))
                                                    }
                                                />
                                        </Modal>
                                        
                                    </Col>
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
                                <Legend verticalAlign='top'/>
                                <XAxis dataKey="time"/>
                                <YAxis yAxisId="left" label='Volt' />
                                <YAxis yAxisId="right" label='Ampere' orientation="right" />
                                <CartesianGrid strokeDasharray="3 3"/>
                                <Tooltip/>
                                <Line type="monotone" dataKey="V_in" stroke="#1890ff" dot={false} unit='V' yAxisId="left" />
                                <Line type="monotone" dataKey="V_out" stroke="#000000" dot={false} unit='V' yAxisId="left" />
                                <Line type="monotone" dataKey="I_out" stroke="red" dot={false} unit='A' yAxisId="right" />
                            </LineChart>
                        </ResponsiveContainer>
                    </TabPane>
                    <TabPane tab="Code" key="2" className={cnBlock('Code')}>
                        <Tabs key={'dsad'} type="card">
                        {this.state.files.map(file => 
                            <TabPane tab={file.replace('blocks/' + this.props.name + '/', '')} key={file}>
                                <Code
                                    file={file}
                                />
                            </TabPane>
                        )}
                        </Tabs>
                        
                    </TabPane>
                </Tabs>
            </div>
        )
    }
}
