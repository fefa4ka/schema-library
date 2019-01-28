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
import { Chart } from '../Chart'
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
    sources: [],
    editableLoad: {
        name: '',
        description: '',
        args: {},
        pins: {},
        index: -1
    },
    load: [],
    mods: {},
    example: '',
    files: [],
    showLabels: {}
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
    files: string[],
    showLabels: {
        [name: string]: boolean
    }
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
                charData: [],
                sources: [],
                load: []
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
                const labels = res.data && res.data.length > 0
                    ? Object.keys(res.data[0]).filter(label => label !== 'time')
                    : []
                
                
                this.setState(({ showLabels }:State) => {
                    return {
                        chartData: res.data,
                        showLabels: labels.reduce((labels: any, label) => {
                            labels[label] = showLabels[label] === false 
                                ? false 
                                : true
    
                            return labels
                        }, {})
                    }
                })
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
                const { name, description, args, params, mods, pins, files, nets, sources, load } = res.data               
                
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

                this.setState((prevState:State) => {
                    const elements:any = {}
                    if (prevState.sources.length === 0) {
                        elements.sources = sources.map((item:any, index:number) => ({ ...item, description: '', index }))
                    }

                    if(prevState.load.length === 0) {
                        elements.load = load.map((item:any, index:number) => ({ ...item, description: '', index }))
                    }

                    return {
                        description,
                        mods,
                        args,
                        params, 
                        nets,
                        pins,
                        example: codeExample,
                        files,
                        selectedMods,
                        ...elements
                    }
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

            return {
                modalConfirmLoading: false,
                load,
                editableLoad: {},
                modalLoadVisible: false,
            }
        }, this.loadSimulation)
    }
    handleModalCancel = (name:string) => {
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
                    const floated = parseFloat(value)
                    prevState.args[name].value = isNaN(floated)
                        ? value
                        : floated
                    
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

        // const chartLabels = this.state.chartData.length > 0
        //     ? Object.keys(this.state.chartData[0]).filter(label => label !== 'time').map(label => {
        //         return {
        //             name: label,
        //             color: label.includes('I_')
        //                 ? 'red'
        //                 : label.includes('input')
        //                     ? "#1890ff"
        //                     : "#000",
        //             unit: label.includes('I_') ? 'A' : 'V',
        //             axis: label.includes('I_') ? 'right' : 'left'
        //         }
        //     })
        //     : []

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
                                onChange={selectedMods => this.setState({ selectedMods, sources: [], load: [] }, this.loadBlock)}
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
            
                <Tabs defaultActiveKey="1" onChange={(key) => key === '1' && this.loadBlock()} className={cnBlock('BlockTabs')}>
                    <TabPane tab="Simulation" key="1">
                        <Row>
                            <Col span={16} className={cnBlock('Description')}>
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
                                
                            </Col>
                            <Col span={8} className={cnBlock('Characteristics')}>
                                <Divider orientation="left">Characteristics</Divider>
                                {attributes}
                                {params}
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
                                                    this.setState({ editableSource: { ...this.state.sources[index], index } }, () => this.showModal('Source'))
                                                }}
                                                onClose={() => {
                                                    this.setState(({ sources }: State) => {
                                                        
                                                        sources.splice(index, 1)
                                                        
                                                        return { sources }
                                                    }, this.loadBlock)
                                            }}>
                                                {source.name}
                                            </Tag>
                                        )} <Tag className={cnBlock('AddPart')} onClick={() => this.setState({ editableSourceType: 'source', editableSource: { index: -1} }, () => this.showModal('Source')) }><Icon type="api" /> Add</Tag>
                                    </Col>
                                    <Col span={12}>
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
                                                    }, this.loadBlock)
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
                        <Chart
                            chartData={this.state.chartData}
                            showLabels={this.state.showLabels}
                            onLegendClick={(e: any) => this.setState(({ showLabels }:State) => {
                                showLabels[e.dataKey] = !showLabels[e.dataKey]
            
                                return showLabels
                            })}
                        />
                        {/* <ResponsiveContainer width='100%' aspect={4.0/1.0}>
                            <LineChart data={this.state.chartData}>
                                <Legend verticalAlign='top' onClick={(e: any) => this.setState(({ showLabels }:State) => {
                                    showLabels[e.dataKey] = !showLabels[e.dataKey]

                                    return showLabels
                                })}/>
                                <XAxis dataKey="time"/>
                                <YAxis yAxisId="left" label='Volt' />
                                <YAxis yAxisId="right" label='Ampere' orientation="right" />
                                <CartesianGrid strokeDasharray="3 3"/>
                                <Tooltip />
                                {chartLabels.map(label => <Line type="monotone" strokeOpacity={this.state.showLabels[label.name] ? 1 : 0.1} key={label.name} dataKey={label.name} stroke={label.color} dot={false} unit={label.unit} yAxisId={label.axis} />)}
                            </LineChart>
                        </ResponsiveContainer> */}
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
