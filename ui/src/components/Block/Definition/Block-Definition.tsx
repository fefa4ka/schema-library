import * as React from 'react';
import { Unit } from '../../Unit';
import { cn } from '@bem-react/classname';
import {
    Col,
    Icon,
    Modal,
    Row,
    Select,
    Tooltip
    } from 'antd';
import { Device, TDevice } from '../../Device';
import { IProps } from './index';
import { IBlock, NullBlock } from '../index';
import { MathMarkdown } from '../Mathdown';
import { BlockLight } from '../../BlockLight';

import { TSource } from '../../Source';
import { UnitInput } from '../../UnitInput';
const Option = Select.Option
import { Divider, Tag, Button  } from 'antd'
const cnDefinition = cn('Block')


const initialState = {
    modalLoadVisible: false,
    modalDeviceVisible: false,
    editableDevice: {
        library: '',
        name: '',
        description: '',
        footprint: '',
        pins: {},
        index: -1
    },
    editableDeviceType: '',
    editableBlock: NullBlock
}

interface IState {
    editableBlock: IBlock,
    editableDevice: TDevice,
    editableDeviceType: string,
    modalLoadVisible: boolean,
    modalDeviceVisible: boolean,
}

export class Definition extends React.Component<IProps, {}> {
    state: IState = initialState
    
    showModal = (name:string) => {
        this.setState({
            [`modal${name}Visible`]: true,
        })
    }
    handleModalCancel = (name: string) => {
        this.setState({
            [`modal${name}Visible`]: false,
            [`editable${name}`]: {}
        })
    }

    handlePcbKit = () => {
        let pcb_body_kit = this.props.pcb_body_kit.slice()
        const editableDevice = this.state.editableDevice

        if (editableDevice.index >= 0) {
            editableDevice.name += '_' + 1
            pcb_body_kit[editableDevice.index] = editableDevice
        } else {
            const lastId = pcb_body_kit.reduce((id, device) => {
                if (device.name.includes(editableDevice.name)) {
                    let [name, number] = device.name.split('_')
                    if (number && parseInt(number) > id) {
                        id = parseInt(number)
                    }
                }

                return id
            }, 0)
            editableDevice.name += '_' + (lastId + 1)
            pcb_body_kit = pcb_body_kit.concat([{
                ...editableDevice,
                index: pcb_body_kit.length
            }])
        }

        this.props.onChange({ pcb_body_kit })
        this.setState({ modalDeviceVisible: false, editableDevice: {} })
    }

    handleSimulationKit = () => {
        let body_kit = this.props.body_kit.slice()
        const editableBlock = this.state.editableBlock
            
        if (editableBlock.index >= 0) {
            body_kit[editableBlock.index] = editableBlock
        } else {
            body_kit = body_kit.concat([editableBlock])
        }

        this.props.onChange({ body_kit })
        this.setState({ modalLoadVisible: false, editableBlock: {} })
    }
    
    render() {
        const { available, mods, props, body_kit, pcb_body_kit, params, args, pins, onChange } = this.props

        return (
            <Row className={cnDefinition('Characteristics')}>
                <Col span={5}>
                    <Divider orientation="left">Arguments</Divider>
                    <Arguments 
                        args={args}
                        onChange={onChange}
                    />
                </Col>
                <Col span={5}>
                    <Divider orientation="left">Characteristics</Divider>
                    <Params
                        params={params}
                        exclude={['Power', 'P', 'I', 'Z', 'Load', 'R_load', 'I_load', 'P_load', 'ref', 'footprint', 'model']}
                    />
                </Col>
                <Col span={6} push={1}>
                    {this.props.activeTab === 'pcb'
                        ? <>
                              <Divider orientation="left">PCB Body Kit</Divider>
                            <Modal
                                title="Add Device"
                                visible={this.state.modalDeviceVisible}
                                onOk={this.handlePcbKit}
                                onCancel={() => this.handleModalCancel('Device')}
                            >
                                    <Device 
                                        type={this.state.editableDeviceType}
                                        device={this.state.editableDevice}
                                        pins={Object.keys(pins)}
                                        onChange={(device:TDevice) =>
                                            this.setState({ editableDevice: device })
                                        }
                                    />
                            </Modal>

                            {this.props.pcb_body_kit.map((device, index) => 
                                <Tag
                                    key={device.name + index.toString()}
                                    closable
                                    onClick={_ => {
                                        this.setState({ editableDevice: { ...pcb_body_kit[index], index } }, () => this.showModal('Device'))
                                    }}
                                    onClose={() => {
                                        let pcb_body_kit = this.props.pcb_body_kit.slice()
                                        pcb_body_kit.splice(index, 1)
                                        onChange({ pcb_body_kit })
                                    }}
                                >
                                    {device.name}
                                </Tag>
                            )} <Tag className={cnDefinition('AddPart')} onClick={() => this.setState({ editableDeviceType: 'scheme', editableDevice: { index: -1 } }, () => this.showModal('Device'))}><Icon type="api" /> Add</Tag>

                            
                        </>
                        : <>
                             <Divider orientation="left">Body Kit</Divider>
                            {body_kit.map((source, index) => 
                                <Tag
                                    key={source.name + index.toString()}
                                    closable
                                    onClick={_ => {
                                        this.setState({ editableBlock: body_kit[index] }, () => this.showModal('Load'))
                                    }}
                                    onClose={() => {
                                        let body_kit = this.props.body_kit.slice()
                                        body_kit.splice(index, 1)
                                        onChange({ body_kit })
                                        // this.setState(({ body_kit }: IState) => {
                                        //     body_kit.splice(index, 1)
                                        //     console.log('close', body_kit)
                                            
                                        //     return { body_kit }
                                        // }, this.updateBlock)
                                }}>
                                    {source.name}
                                </Tag>
                            )}<Tag className={cnDefinition('AddPart')} onClick={() => this.setState({ editableBlock: { index: -1 } }, () => this.showModal('Load'))}><Icon type="api" /> Add block</Tag>
                            
                            <Modal
                                title="Add Block"
                                visible={this.state.modalLoadVisible}
                                onOk={this.handleSimulationKit}
                                onCancel={() => this.handleModalCancel('Load')}
                                width={'60%'}
                                >
                                    <BlockLight
                                        block={this.state.editableBlock}
                                        pins={Object.keys(pins)}
                                        onChange={(body_kit: TSource) =>
                                            this.setState({ editableBlock: body_kit })
                                        }
                                    />
                            </Modal>
                        </>
                    }
                   

                    <div className={cnDefinition('InlineParams')}>
                        <Params
                            params={params}
                            include={['R_load', 'I_load', 'P_load']}
                        />
                    </div> 
                    
                </Col>
            
                <Col span={6} push={1}>
                    {available.length 
                        ?
                        <>
                            <Divider orientation="left">PCB Part</Divider>
                            <Select
                                placeholder="Select a model"
                                value={args.model ? args.model.value : ''}
                                className={cnDefinition('AvailableParts')}
                                onChange={(value:any) => onChange({
                                    args: {
                                        ...args,
                                        model: { value, unit: { name: 'string', suffix: '' } }
                                    }
                                })}
                            >
                                {available.map(model =>
                                    <Option value={model.model} key={model.model}>{model.model} {model.footprint}</Option>)}
                            </Select>
                        </>
                        : null}
                    <div className={cnDefinition('InlineParams')}>
                        <Params
                            params={params}
                            include={['P', 'I', 'Z']}
                        />
                    </div>
                  
                </Col>
            </Row>)
    }
}

const Arguments:any = ({ args, onChange }: any) => Object.keys(args)
    .filter(name => name !== 'model').map(name =>
        Argument({
            name,
            argument: args[name],
            onChange: (value:any) => onChange({
                args: {
                    ...args,
                    [name]: {
                        ...args[name],
                        value
                    }
                }
            })
        })
    )
    
const Argument = ({ name, argument, onChange }: any) => {
    if (argument && argument.unit.name === 'network') {
        return null
    }

    const [arg_title, arg_sub] = name.split('_')

    return (
        <UnitInput
            key={name}
            name={<Tooltip
                    overlayClassName={cnDefinition('ParamTooltip')}
                    title={<MathMarkdown value={argument.description || name} />}
                >
                    {arg_title}<sub key='s'>{arg_sub}</sub>
                </Tooltip>
            }
            suffix={argument && argument.unit ? argument.unit.suffix : ''}
            value={argument ? argument.value.toString() : ''}
            onChange={(value:string) => onChange(value)}
            className={cnDefinition('ArgumentInput')}
        />
    ) 
}

const Params = ({ params, include, exclude }:{ params: any, include?:string[], exclude?: string[]}):any =>
    Object.keys(params).filter(name => include ? include.includes(name) : true)
        .filter(name => exclude ? exclude.includes(name) === false : true)
        .map((name, index) => ParamView({ name, param: params[name]}))

const ParamView = ({ name, param }: any) => {
    if (param && param.unit.name === 'network') {
        return null
    }

    return <Unit
        key={name}
        name={name}
        suffix={param ? param.unit.suffix : ''}
        value={param ? param.value : ''}
        description={param ? param.description : ''}
    />  
}
