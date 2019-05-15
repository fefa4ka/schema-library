import * as React from 'react';
import axios from 'axios';
import Iframe from 'react-iframe';
import { canonise, siPrefix, Unit } from '../Unit';
import { cn } from '@bem-react/classname';
import { Code } from '../Code';
import {
    Col,
    Icon,
    Modal,
    Row,
    Select,
    Tabs,
    Tooltip
    } from 'antd';
import { Device, TDevice } from '../Device';
import { Diagram } from './Diagram';
import { IProps } from './index';
import { MathMarkdown } from './Mathdown';
import { Part } from '../Part';
import { Probe, TProbe } from '../Probe';
import { Source, TSource } from '../Source';
import { UnControlled as CodeMirror } from 'react-codemirror2';
import { UnitInput } from '../UnitInput';
import './Block.css';
const Option = Select.Option
import { Slider, Divider, Tag, Button, Input, TreeSelect } from 'antd'
const TabPane = Tabs.TabPane;
const TreeNode = TreeSelect.TreeNode;
const { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend, ReferenceLine} = require('recharts')
const ChartTooltip = require('recharts').Tooltip

require('codemirror/lib/codemirror.css')
require('codemirror/mode/python/python')

const cnBlock = cn('Block')


const initialState = {
    name: '',
    description: [''],
    available: [],
    params_description: {},
    selectedMods: [],
    args: {},
    nets: {},
    pins: {},
    params: {},
    props: {},
    spiceAttrs: {},
    debug: '',
    debugUrl: '',
    modalDebugVisible: false,
    modalSourceVisible: false,
    modalLoadVisible: false,
    modalDeviceVisible: false,
    modalTestVisible: false,
    modalConfirmLoading: false,
    editableSource: {
        name: '',
        description: '',
        args: {},
        pins: {},
        device: '',
        port: '',
        channel: 0,
        index: -1
    },
    editableSourceType: '',
    parts: [],
    sources: [],
    probeLoading: false,
    probes: {},
    editableDevice: {
        library: '',
        name: '',
        description: '',
        footprint: '',
        pins: {},
        index: -1
    },
    editableDeviceType: '',
    devices: [],
    editableLoad: {
        name: '',
        description: '',
        args: {},
        pins: {},
        device: '',
        port: '',
        channel: 0,
        index: -1
    },
    load: [],
    mods: {},
    example: '',
    files: [],
    simulationData: [],
    simulationCase: {},
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

type State = {
    name: string,
    description: string[],
    available: {
        footprint: string,
        model: string,
        id: number
    }[],
    params_description: {
        [name:string]: string
    },
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
    props: IProps['mods'],
    spiceAttrs: {
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
    parts : TSource[],
    sources: TSource[],
    probes: {
        [name: string]: {
            name: string,
            channel: string
        }
    },
    editableDevice: TDevice,
    editableDeviceType: string,
    devices: TDevice[],
    debug: string,
    debugUrl: string,
    modalDebugVisible: boolean,
    modalSourceVisible: boolean,
    modalLoadVisible: boolean,
    modalDeviceVisible: boolean,
    modalTestVisible: boolean,
    modalConfirmLoading: boolean,
    mods?: {
        [name:string]: string[]
    },
    example: string,
    files: string[],
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
                parts: [],
                devices: [],
                load: []
            }, this.loadBlock)
        }
        return true
    }
    loadSimulation() {
        const { args, sources, load, simulationStopTime } = this.state
        
        axios.post('/api/blocks/' + this.props.name + '/simulate/',
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
                const simulationData = res.data
                const labels = res.data && res.data.length > 0
                    ? Object.keys(res.data[0]).filter(label => label !== 'time')
                    : []
                
                this.loadSimulationCases() 
                
                this.setState(({ showLabels }:State) => {
                    return {
                        simulationData,
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
        const { args, sources, load, } = this.state
        
        axios.post('/api/blocks/' + this.props.name + '/simulate/cases/',
        {
            mods: this.state.mods,
            args: Object.keys(args).reduce((result: { [name:string]: string | number }, arg) => {
                result[arg] = args[arg].value
                
                return result
            }, {}),
            sources,
            load,
        })
            .then(res => {
                const simulationCase = res.data
                
                this.setState({ simulationCase })
            })//.catch(this.catchError)
    }
    loadProbes() {
        const { sources, probes, simulationStopTime } = this.state
        this.setState({
            probeLoading: true,
        })
        axios.post('/api/probes/',
        {
            sources,
            probes,
            simulationTime: simulationStopTime
        })
            .then(res => {
                const probeData = res.data
                const labels = res.data && res.data.length > 0
                    ? Object.keys(res.data[0]).filter(label => label !== 'time')
                    : []
                
                
                this.setState(({ showLabels }:State) => {
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
    urlParams() {
        const selectedMods: { [name:string]: string[] } = this.state.selectedMods.reduce((mods: { [name:string]: string[] }, mod) => {
            const [type, value] = mod.split(':')
            mods[type] = mods[type] || []
            mods[type].push(value)

            return mods
        }, {})

        const modsUrlParam = Object.keys(selectedMods).map((mod:string) => mod + '=' + selectedMods[mod].join(','))
        const argsUrlParam = Object.keys(this.state.args).filter(arg => this.state.args[arg].value).map(arg => arg + '=' + this.state.args[arg].value)
        
        return '?' + modsUrlParam.concat(argsUrlParam).join('&') 
    }
    loadBlock() {
        
        
        axios.get('/api/blocks/' + this.props.name + '/' + this.urlParams())
            .then(res => {
                const { name, description, available, params_description, args, params, mods, props, pins, files, nets, sources, parts, load, devices } = res.data               
                
                const selectedMods = Object.keys(mods).reduce((selected, type) =>
                    selected.concat(
                        Array.isArray(mods[type])
                            ? mods[type].map((value: string) => type + ':' + value)
                            : [type + ':' + mods[type]]
                    ), [])
                
                const codeUnits = Object.keys(args).map(arg => args[arg].unit.suffix).filter((value, index, self) => self.indexOf(value) === index).map(item => 'u_' + item).join(', ')
                const codeArgs = Object.keys(args).map(arg => arg + ' = ' + args[arg].value + (args[arg].unit.suffix ? ' @ u_' + args[arg].unit.suffix : '')).join(',\n\t')
                const codeMods = Object.keys(mods).map((type: string) =>
                        type + "=['" + 
                            (Array.isArray(mods[type]) 
                                ? mods[type].join("', '") 
                                : mods[type])
                        + "']").join(', ')
                
                const blockImportName = name.replace('.', '_')
                const codeExample = `from bem import ${blockImportName}${codeUnits ? '\nfrom bem import ' + codeUnits : ''}

${blockImportName}(${codeMods})${codeArgs ? `(
	${codeArgs}
)` : '()'}`

                this.setState((prevState:State) => {
                    const elements:any = {}
                    if (prevState.sources.length === 0 && sources.length) {
                        elements.sources = sources.map((item:any, index:number) => ({ ...item, description: '', index }))
                    }

                    if(prevState.load.length === 0 && load.length) {
                        elements.load = load.map((item:any, index:number) => ({ ...item, description: '', index }))
                    }


                    if(prevState.devices.length === 0 && devices.length) {
                        elements.devices = devices.map((item:any, index:number) => ({ ...item, description: '', index }))
                    }
                   
                    return {
                        description,
                        available, 
                        params_description,
                        mods,
                        props,
                        args,
                        params, 
                        nets,
                        pins,
                        parts,
                        example: codeExample,
                        files,
                        selectedMods,
                        ...elements
                    }
                }, this.loadSimulation)
            }).catch(this.catchError)
    }
    catchError = (error: any) => {
        const url = error.response.config.url
        
        function escapeRegExp(str: string) {
            return str.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
        }
        function replaceAll(str: string, find: string, replace: string) {
            return str.replace(new RegExp(escapeRegExp(find), 'g'), replace);
        }
        const html = replaceAll(error.response.data, '?__debugger__', error.response.config.url + '__debugger__')
        const base = `<base href='${url}'/>`

        
        this.setState({
            modalDebugVisible: true,
            debugUrl: url,
            debug: html + base
        })
    }
    showModal = (name:string) => {
        this.setState({
            [`modal${name}Visible`]: true,
        })
    }
    handleDebugOk = () => {
        this.setState({
            modalDebugVisible: false
        })
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
    handleDeviceOk = () => {
        this.setState(({ devices, editableDevice }: State) => {
            if (editableDevice.index >= 0) {
                editableDevice.name += '_' + 1
                devices[editableDevice.index] = editableDevice
            } else {
                const lastId = devices.reduce((id, device) => {
                    if (device.name.includes(editableDevice.name)) {
                        let [name, number] = device.name.split('_')
                        if (number && parseInt(number) > id) {
                            id = parseInt(number)
                        }
                    }

                    return id
                }, 0)
                editableDevice.name += '_' + (lastId + 1)
                devices = devices.concat([{
                    ...editableDevice,
                    index: devices.length
                }])
            }

            return {
                modalConfirmLoading: false,
                devices,
                editableDevice: {},
                modalDeviceVisible: false,
            }
        })
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
    handleTestOk = () => {
        this.loadProbes()
    }
    handleModalCancel = (name: string) => {
        this.setState({
            [`modal${name}Visible`]: false,
            [`editable${name}`]: {}
        })
    }
    downloadNetlist = () => {
        const { args, devices } = this.state
        const filename = this.props.name + '.net'

        axios.post('/api/blocks/' + this.props.name + '/netlist/',
        {
            mods: this.state.mods,
            args: Object.keys(args).reduce((result: { [name:string]: string | number }, arg) => {
                result[arg] = args[arg].value
                
                return result
            }, {}),
            devices
        })
            .then(response => {
                const url = window.URL.createObjectURL(new Blob([response.data]))
                const link = document.createElement('a')
                link.href = url
                link.setAttribute('download', filename)
                document.body.appendChild(link)
                link.click()
            }).catch(this.catchError)
        
    }
    // loadProps = () => {
    //     axios.get('/api/blocks/' + this.props.name + '/part_params/' + this.urlParams())
    //         .then(res => {
    //             const { spice, props } = res.data

    //             this.setState(({ params_description }: State) => ({
    //                 spiceAttrs: spice,
    //                 params_description: {
    //                     ...params_description,
    //                     ...Object.keys(spice).reduce((spiceDescription: State['params_description'], param:string) => { 
    //                         spiceDescription[param] = spice[param].description

    //                         return spiceDescription
    //                     }, {})
    //                 },
    //                 props: props
    //             }), this.loadSimulation)
    //         })
    // }
    render() {
        const { mods } = this.props
        const { simulationData, simulationCase, props } = this.state
        const simulationCases = Object.keys(simulationCase)
        const description = this.state.description.join('\n\n')

        const BlockMods: IProps['mods'] = { ...mods, ...props }
        // const description = this.state.description.map((description, index) =>
        //         <Markdown
        //             key={index}
        //             source={description}
        //             renderers={{
        //                 inlineCode: (props: { value: string }) =>
        //                     <MathJax math={'`' + props.value + '`'}/>
        //             }}
        //         />
        // )
        
        function insertSpaces(string:string) {
            string = string.replace(/([a-z])([A-Z])/g, '$1 $2');
            string = string.replace(/([A-Z])([A-Z][a-z])/g, '$1 $2')
            return string
          }

        const attributes = Object.keys(this.state.args).filter(name => name !== 'model').map(name => {
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

            return (
                <UnitInput
                    key={name}
                    name={<Tooltip
                            overlayClassName={cnBlock('ParamTooltip')}
                            title={<MathMarkdown value={this.state.params_description[name] || name} />}
                        >
                            {arg_title}<sub key='s'>{arg_sub}</sub>
                        </Tooltip>
                    }
                    suffix={suffix}
                    value={value.toString()}
                    onChange={save}
                    className={cnBlock('ArgumentInput')}
                />
            )
        })

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

        const allParams = {
            ...this.state.params,
            ...this.state.spiceAttrs
        }
        
        const Params = ({ include, exclude }:{ include?:string[], exclude?: string[]}):any =>
            Object.keys(this.state.params).filter(name => include ? include.includes(name) : true)
                .filter(name => exclude ? exclude.includes(name) === false : true)
                .map((name, index) => {
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
                    
                    return <Unit
                        key={name}
                        name={name}
                        suffix={suffix}
                        value={value}
                        description={this.state.params_description[name]}
                    /> 
            })

        return (
            <div className={this.props.className || cnBlock()}>
                <Modal
                    title="Debug Console"
                    visible={this.state.modalDebugVisible}
                    onOk={this.handleDebugOk}
                    onCancel={this.handleDebugOk}
                    className={cnBlock('DebugModal')}
               >
                    <IframeContainer content={this.state.debug} url={this.state.debugUrl} />
                </Modal>

                <Row>
                    SCRIPT
                    <Col span={12} className={cnBlock('Title')}>
                        <h1>
                            {insertSpaces(this.props.name || '')}
                        </h1>
                    </Col>

                    <Col span={12} className={cnBlock('Modificator')}>
                        {BlockMods && Object.keys(BlockMods).length
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
                                {Object.keys(BlockMods).map(type =>
                                    <TreeNode value={type} title={type} key={type}>
                                        {Array.isArray(BlockMods[type]) && BlockMods[type].map(value => 
                                            <TreeNode value={type + ':' + value} title={value} key={type + ':' + value} />
                                        )}
                                    </TreeNode>
                                )}
                            </TreeSelect>
                            : ''}
                    </Col>
                </Row>
            
                <Tabs defaultActiveKey="1" onChange={(key) => key === '1' && this.loadBlock()} className={cnBlock('BlockTabs')}>
                    <TabPane tab="Simulation" key="1">
                        <Divider orientation="left">
                            Description
                        </Divider>
                        <Row>
                            <Col span={16} className={cnBlock('Description')}>
                                <MathMarkdown value={description}/>
                            </Col>
                            <Col span={8}>
                                <CodeMirror
                                    className={cnBlock('CodeExample')}
                                    options={{
                                        mode: 'python',
                                        lineNumbers: false,
                                        indentWithTabs: false,
                                        indentUnit: 4,
                                        tabSize: 4
                                    }}
                                    value={'# Code Example\n\n' + this.state.example}
                                />
                            </Col>
                        </Row>
                        
   
                        <Row className={cnBlock('Characteristics')}>
                            <Col span={5}>
                                <Divider orientation="left">Attributes</Divider>
                                {attributes}
                            </Col>
                            <Col span={5}>
                                <Divider orientation="left">Characteristics</Divider>
                                <Params exclude={['Power', 'P', 'I', 'Z', 'Load', 'R_load', 'I_load', 'P_load', 'ref', 'footprint', 'model']}/>
                            </Col>
                            <Col span={6} push={1}>
                                <Divider orientation="left">
                                    Signal Sources 
                                </Divider>
                                
                                <Modal
                                    title="Add Signal Source"
                                    visible={this.state.modalSourceVisible}
                                    onOk={this.handleSourceOk}
                                    onCancel={() => this.handleModalCancel('Source')}
                                    >
                                        <Source
                                            type={this.state.editableSourceType}
                                            source={this.state.editableSource}
                                            pins={Object.keys(this.state.pins)}
                                            onChange={(source:TSource) =>
                                                this.setState({ editableSource: source }, () => console.log('change', this.state))
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
                                )} <Tag className={cnBlock('AddPart')} onClick={() => this.setState({ editableSourceType: 'source', editableSource: { index: -1 } }, () => this.showModal('Source'))}><Icon type="api" /> Add</Tag>

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

                                <div className={cnBlock('InlineParams')}>
                                    <Params include={['R_load', 'I_load', 'P_load']} />
                                </div> 
                                
                            </Col>
                       
                            <Col span={6} push={1}>
                                <Divider orientation="left">PCB Part</Divider>
                                <Select 
                                    placeholder="Select a model"
                                    value={this.state.args.model ? this.state.args.model.value : ''}
                                    className={cnBlock('AvailableParts')}
                                    onChange={value => this.setState(({ args }: State) => ({ args: { ...args, model: { value, unit: { name: 'string', suffix: '' }} }}), this.loadBlock)}
                                >
                                    {this.state.available.map(model =>
                                        <Option value={model.model} key={model.model}>{model.model} {model.footprint}</Option>)}
                                </Select>
                                <div className={cnBlock('InlineParams')}>
                                    <Params include={['P', 'I', 'Z']} />
                                </div>
                                <Divider orientation="left">Body Kit</Divider>
                                <Modal
                                    title="Add Device"
                                    visible={this.state.modalDeviceVisible}
                                    onOk={this.handleDeviceOk}
                                    onCancel={() => this.handleModalCancel('Device')}
                                >
                                        <Device 
                                            type={this.state.editableDeviceType}
                                            device={this.state.editableDevice}
                                            pins={Object.keys(this.state.pins)}
                                            onChange={(device:TDevice) =>
                                                this.setState({ editableDevice: device }, () => console.log('change', this.state))
                                            }
                                        />
                                </Modal>

                                {this.state.devices.map((device, index) => 
                                    <Tag
                                        key={device.name + index.toString()}
                                        closable
                                        onClick={_ => {
                                            this.setState({ editableDevice: { ...this.state.devices[index], index } }, () => this.showModal('Device'))
                                        }}
                                        onClose={() => {
                                            this.setState(({ devices }: State) => {
                                                devices.splice(index, 1)
                                                
                                                return { devices }
                                            })
                                    }}>
                                        {device.name}
                                    </Tag>
                                )} <Tag className={cnBlock('AddPart')} onClick={() => this.setState({ editableDeviceType: 'scheme', editableDevice: { index: -1 } }, () => this.showModal('Device'))}><Icon type="api" /> Add</Tag>

                                <br />
                                
                                <Button type='primary' onClick={this.downloadNetlist}>Download Netlist</Button>
                            </Col>
                        </Row>
                
                        <Row>
                            <Col span={12}>
                                <Divider orientation="left">Simulation</Divider>
                                <TransientChart 
                                    data={simulationData}
                                    showLabels={this.state.showLabels}
                                    startTime={this.state.simulationStartTime}
                                    stopTime={this.state.simulationStopTime}
                                    onLegendClick={(e: any) => this.setState(({ showLabels }:State) => {
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
                                                pins={Object.keys(this.state.pins).filter(pin => this.state.pins[pin].length)}
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
                                    onLegendClick={(e: any) => this.setState(({ showLabels }:State) => {
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

                        <Divider orientation="left">
                            Schematics
                        </Divider>

                        <Diagram
                            pins={this.state.pins}
                            nets={this.state.nets}
                            sources={this.state.sources}
                            load={this.state.load}
                            parts={this.state.parts}
                        />

                    
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

/**
 * React component which renders the given content into an iframe.
 * Additionally an array of stylesheet urls can be passed. They will 
 * also be loaded into the iframe.
 */

type IframeProps = {
    content: string,
    url?: string
}
export class IframeContainer extends React.Component<IframeProps, {}> {
     /**
     * Called after mounting the component. Triggers initial update of
     * the iframe
     */
    iframeRef = React.createRef<HTMLIFrameElement>()

    componentDidMount() {
        this._updateIframe();
    }

    // /**
    //  * Called each time the props changes. Triggers an update of the iframe to
    //  * pass the new content
    //  */
    componentDidUpdate() {
        this._updateIframe();
    }

    /**
     * Updates the iframes content and inserts stylesheets.
     * TODO: Currently stylesheets are just added for proof of concept. Implement
     * and algorithm which updates the stylesheets properly.
     */
    _updateIframe() {
        const iframe = this.iframeRef.current
        if (iframe && iframe.contentWindow) {
            const document = iframe.contentWindow.document 
            if (document) {
                if (this.props.url) {
                    iframe.src = this.props.url
                    // iframe.contentWindow.history.replaceState('', '', this.props.url)
                } else {
                    document.open()
                    document.write(this.props.content)
                    document.close()
                }
            }
        }
    }

    /**
     * This component renders just and iframe
     */
    render() {
        return <iframe className={cnBlock('DebugIframe')} ref={this.iframeRef}/>
    }

}

