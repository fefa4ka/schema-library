import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Slider, Divider, Tag, Button, Input, TreeSelect} from 'antd'
import { Icon, Tabs, Row, Col, Modal } from 'antd'
import Markdown from 'react-markdown'
import { Source, TSource } from '../Source'
import { Part } from '../Part'
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
    chartData: [],
    showLabels: {},
    simulationStartTime: 0,
    simulationStopTime: 0.01
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
    modalSourceVisible: boolean,
    modalLoadVisible: boolean,
    modalConfirmLoading: boolean,
    mods?: {
        [name:string]: string[]
    },
    example: string,
    files: string[],
    chartData: {
        [name:string]: number
    }[],
    showLabels: {
        [name: string]: boolean
    },
    simulationStartTime: number,
    simulationStopTime: number
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
        const { args, sources, load, simulationStopTime } = this.state

        axios.post('http://localhost:3000/api/blocks/' + this.props.name + '/simulate/',
        {
            mods: this.state.mods,
            args: Object.keys(args).reduce((result: { [name:string]: string | number }, arg) => {
                result[arg] = args[arg].value
                
                return result
            }, {}),
            sources,
            load,
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
                const codeArgs = Object.keys(args).map(arg => arg + ' = ' + args[arg].value + (args[arg].unit.suffix ? ' @ u_' + args[arg].unit.suffix : '')).join(',\n\t')
                const codeMods = Object.keys(mods).map((mod:string) => mod + "=['" + mods[mod].join("', '") + "']").join(', ')
                const codeExample = `from bem import ${name}, ${codeUnits}

${name}(${codeMods})${codeArgs ? `(
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
                const lastId = sources.reduce((id, source) => {
                    if (source.name.includes(editableSource.name)) {
                        let [name, number] = source.name.split('_')
                        if (number && parseInt(number) > id) {
                            id = parseInt(number)
                        }
                    }

                    return id
                }, 0)
                editableSource.name += '_' + (lastId + 1)
                sources = sources.concat([{
                    ...editableSource,
                    index: sources.length
                }])
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
    handleModalCancel = (name: string) => {
        this.setState({
            [`modal${name}Visible`]: false,
            editableSource: {},
            editableLoad: {}
        })
    }
    render() {
        const { mods } = this.props
        const { chartData } = this.state
        const description = this.state.description.map((description, index) =>
            <Markdown key={index} source={description}/>
        )
        function insertSpaces(string:string) {
            string = string.replace(/([a-z])([A-Z])/g, '$1 $2');
            string = string.replace(/([A-Z])([A-Z][a-z])/g, '$1 $2')
            return string
          }

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
                            {insertSpaces(this.props.name || '')}
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
                            <Col span={15} className={cnBlock('Description')}>
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
                            <Col span={8} push={1} className={cnBlock('Characteristics')}>
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
                            chartData={chartData}
                            showLabels={this.state.showLabels}
                            xRefStart={this.state.simulationStartTime}
                            xRefStop={this.state.simulationStopTime}
                            onLegendClick={(e: any) => this.setState(({ showLabels }:State) => {
                                showLabels[e.dataKey] = !showLabels[e.dataKey]
            
                                return showLabels
                            })}
                        />
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
                                        const { simulationStopTime, chartData } = this.state
                                        if (chartData.length && simulationStopTime > chartData[chartData.length - 1].time) {
                                            this.loadSimulation()
                                        }
                                    }}
                                />
                            </Col>
                        </Row>
                        
                    </TabPane>
                    <TabPane tab="Code" key="2" className={cnBlock('Code')}>
                        <Tabs key={'dsad'} type="card">
                        {this.state.files.map(file => 
                            <TabPane tab={file.replace('blocks/' + this.props.name + '/', '')} key={file}>
                                <Code
                                    file={file}
                                    onChange={(value:string) => axios.post('/api/files/', { name: file.replace('blocks/' + this.props.name + '/', ''), content: value})}
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
