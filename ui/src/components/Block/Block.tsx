import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Button, Input, TreeSelect} from 'antd'
import { Tabs, Row, Col, Modal } from 'antd'
import Markdown from 'react-markdown'
import { Part } from '../Part'
const { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceArea } = require('recharts')
const TabPane = Tabs.TabPane;
import { UnitInput } from '../UnitInput'
const nomnoml = require('nomnoml')
const TreeNode = TreeSelect.TreeNode;

import './Block.css';

const cnBlock = cn('Block')


const initialState = {
    name: '',
    description: [''],
    selectedMods: [],
    args: {},
    pins: [],
    params: {},
    modalVisible: false,
    chartData: [],
    modalConfirmLoading: false
}

// type State = typeof initialState
type State = {
    name: string,
    description: string[],
    selectedMods: string[],
    pins: string[],
    args: {
        [name:string]: {
            value: number,
            unit: {
                name: string,
                suffix: string
            }
        }
    },
    params: {
        [name:string]: {
            value: number,
            unit: {
                name: string,
                suffix: string
            }
        }
    },
    chartData: {
        [name:string]: number[]
    }[],
    modalVisible: boolean,
    modalConfirmLoading: boolean
}


export class Block extends React.Component<IProps, {}> {
    state: State = initialState
    private canvasRef = React.createRef<HTMLCanvasElement>()
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
                const { description, args, params, mods, pins, parts, nets } = res.data

                // if (argsUrlParam.length > 0) {
                    const modsUrlParam = Object.keys(mods).map((mod:string) => mod + '=' + mods[mod].join(','))
                    const argsUrlParam = Object.keys(args).map(arg => arg + '=' + args[arg].value)
                    axios.get('http://localhost:3000/api/blocks/' + this.props.name + '/simulate/?' + modsUrlParam.concat(argsUrlParam).join('&'))
                        .then(res => {
                            this.setState({ chartData: res.data })
                        })
                // }

                const selectedMods = Object.keys(mods).reduce((selected, type) =>
                    selected.concat(
                        mods[type].map((value: string) => type + '=' + value)
                    ), [])
                
                const get_name = (pin: string, index: number) => {
            
                    const [_, data] = pin.split(' ')
                    const vars = data.split('/')

                    return vars[index]
                }
    
                const network = Object.keys(nets).map((net, index) => {
                    const pins: string[] = nets[net]
                    const wire = pins.map((pin, index, list) => {
                       
                        if (list.length - 1 > index) {
                            return `[${get_name(pin, 0)}]${get_name(pin, 2)}-${get_name(list[index + 1], 2)}[${get_name(list[index + 1], 0)}]`
                        }
                    }).join(';')

                    return wire
                }).join('')

                const pinsNet = Object.keys(pins).map((pin: string, index, list) => {
                    const isAlreadyExists = list.reduce((exists, sub_pin, sub_index) => {
                        if (index > sub_index && pins[pin][0] === pins[sub_pin][0]) {
                            return true
                        }

                        return exists
                    }, false)

                    if(pins[pin][0] && !isAlreadyExists) {
                        return `[<label>${pin}]-${get_name(pins[pin][0], 2)}[${get_name(pins[pin][0], 0)}]`
                    }
                }).filter(item => item).join(';')

                const settings = ['#font: ISOCPEUR', '#stroke: #000000', '#fill: #ffffff', '#leading: 0.8', '#lineWidth: 1'].join('\n')
                const graph = settings + '\n' + [network, '[<label>input]', '[<label>output]', '[<end>gnd]', pinsNet].filter(_=>_).join(';')
                nomnoml.draw(this.canvasRef.current, graph);
                
                this.setState({
                    description,
                    args,
                    params, 
                    pins: Object.keys(pins),
                    selectedMods
                })
            })
    }
    showModal = () => {
        this.setState({
            modalVisible: true,
        });
    }
    handleOk = () => {
        this.setState({
            modalConfirmLoading: true,
        });
        setTimeout(() => {
            this.setState({
             modalVisible: false,
             modalConfirmLoading: false,
            });
        }, 2000);
    }

    handleCancel = () => {
        console.log('Clicked cancel button');
        this.setState({
            modalVisible: false,
        });
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
                    <TabPane tab="Description" key="1">
                        <Row>
                            <Col span={14} className={cnBlock('Description')}>
                                {description}
                                <Row className={cnBlock('Pins')}>
                                    <Col span={5}>
                                        <Button onClick={this.showModal} type="primary" icon="api">Add Source</Button>
                                        <Modal
                                            title="Title"
                                            visible={this.state.modalVisible}
                                            onOk={this.handleOk}
                                            confirmLoading={this.state.modalConfirmLoading}
                                            onCancel={this.handleCancel}
                                            >
                                                <Part type='source'/>
                                            </Modal>
                                        {this.state.pins.filter(item => item.includes('output') === false).map(pin => 
                                            <Button type='dashed' key={pin}>{pin}</Button>)
                                        }
                                    </Col>
                                    <Col span={13}><canvas ref={this.canvasRef} /></Col>
                                    <Col span={4}>
                                        
                                        {this.state.pins.filter(item => item.includes('output')).map(pin => 
                                            <Button type='dashed' key={pin}>{pin}</Button>)
                                        }
                                    </Col>
                                </Row>
                            </Col>
                            <Col span={10} className={cnBlock('Characteristics')}>
                                <h2>Electrical Characteristics</h2>
                                {attributes}
                                {params}
                            </Col>
                        </Row> 
                        
                        <h2>Waveforms</h2>
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
