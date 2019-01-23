import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Button, Input, TreeSelect} from 'antd'
import { Row, Col } from 'antd'
import Markdown from 'react-markdown'
const nomnoml = require('nomnoml')
const TreeNode = TreeSelect.TreeNode;

import './Block.css';
require("storm-react-diagrams/dist/style.min.css");

const cnBlock = cn('Block')


const initialState = {
    name: '',
    description: [''],
    selectedMods: [],
    args: {},
    pins: [],
    params: {}
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
    }
}


export class Block extends React.Component<IProps, {}> {
    state: State = initialState
    private canvasRef = React.createRef<HTMLCanvasElement>()

    componentDidUpdate(prevProps: IProps, prevState: State) {
        if (prevProps.name !== this.props.name
            || prevState.selectedMods.join('') !== this.state.selectedMods.join('')) {
                this.loadBlock()
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
        
        axios.get('http://localhost:3000/api/blocks/' + this.props.name + '/?' + modsUrlParam.concat(argsUrlParam).join('&'))
            .then(res => {
                const { description, args, params, mods, pins, parts, nets } = res.data

                const selectedMods = Object.keys(mods).reduce((selected, type) =>
                    selected.concat(
                        mods[type].map((value: string) => type + '=' + value)
                    ), [])
                
                // const elements = parts.map((item: { [name: string]: string }, index: number) =>
                //     `[${item.name}${index}]`).join(';')
                const get_name = (pin: string, index: number) => {
                    console.log(pin)
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

                const pinsNet = Object.keys(pins).map((pin: string) => {
                    if(pins[pin][0]) {
                        return `[${pin}]-${get_name(pins[pin][0], 2)}[${get_name(pins[pin][0], 0)}]`
                    }
                }).filter(item => item).join(';')

                const graph = `[${this.props.name}|` + [network, '[<sender>input]', '[<receiver>output]', '[<reference>gnd]', pinsNet].filter(_=>_).join(';') + ']'
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

            return <Input
                key={name}
                addonBefore={[arg_title, <sub key='s'>{arg_sub}</sub>]}
                addonAfter={suffix}
                value={value ? value.toString() : ''}
                onChange={({ target }) => this.setState((prevState: State) => {
                    prevState.args[name].value = parseFloat(target.value) 

                    return prevState
                }, () => {
                    parseFloat(target.value) > 0 && this.loadBlock()
                })}
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
   
        const src = '[nomnoml] is -> [awesome]';
        
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
                                onChange={selectedMods => this.setState({ selectedMods })}
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
                <Row>
                    <Col span={14} className={cnBlock('Description')}>
                        {description}
                        <canvas ref={this.canvasRef}/>
                    </Col>
                    <Col span={10} className={cnBlock('Arguments')}>
                        {attributes}
                        {params}
                    </Col>
                </Row> 
                <h2>Simulation</h2>
                <Row className={cnBlock('Pins')}>
                    {this.state.pins.map(pin => 
                        <Button type='dashed' key={pin}>{pin}</Button>)
                    }
                </Row>
            </div>
        )
    }
}
