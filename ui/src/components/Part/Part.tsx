import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import { Button, Select, TreeSelect} from 'antd'
import { Divider, Tabs, Row, Col, Modal } from 'antd'
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
    lib: '',
    device: '',
    args: {},
    pins: [],
    parts: []
}

// type State = typeof initialState
type Args = {
    [name:string]: {
        value: number,
        unit: {
            name: string,
            suffix: string
        }
    }
}
type State = {
    name: string,
    lib: string,
    device: string,
    pins: string[],
    args: Args,
    parts: {
        name: string,
        description: string,
        pins: string[],
        args: string[]
    }[]
}


export class Part extends React.Component<IProps, {}> {
    state: State = initialState

    componentWillMount() {
        this.loadParts()

        return true
    }
    loadParts() {
        axios.get('http://localhost:3000/api/sources/')
            .then(res => {
                const parts = res.data
                this.setState({ parts })
            })
    }
    render() { 
        const { parts, name } = this.state
        const current = parts.filter(part => part.description.toLowerCase().indexOf('current') !== -1)
        const voltage = parts.filter(part => part.description.toLowerCase().indexOf('current') === -1)
        const args:Args = this.state.parts.reduce((args, item) => item.name === name ? item.args : args, {})

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
            // const [arg_title, arg_sub] = name.split('_')

            // const save = (event: React.SyntheticEvent) => {
            //     const target = event.target as HTMLInputElement;

            //     this.setState((prevState: State) => {
            //         prevState.args[name].value = parseFloat(target.value)
                    
            //         return prevState
            //     }, () => {
            //         parseFloat(target.value) > 0 && this.loadBlock()
            //     })
            // }

            return <UnitInput
                key={name}
                name={name}
                suffix={suffix}
                value={value.toString()}
                onChange={(val:number) => console.log(val)}
                // onBlur={save}
                // onPressEnter={save}
            />
        })

        return (
            <div className={cnPart()}>
                <Select
                    style={{ width: '100%' }}
                    placeholder='Select Power Source'
                    onChange={name => this.setState({
                        name
                    })}
                >
                    <OptGroup label="Voltage">
                        {voltage.map(item => <Option value={item.name} key={item.name}>{item.description}</Option>)}
                    </OptGroup>
                    <OptGroup label="Current">
                        {current.map(item => <Option value={item.name} key={item.name}>{item.description}</Option>)}
                    </OptGroup>
                </Select>
                <Divider orientation="left">Properties</Divider>
                <div className={cnPart('Attributes')}>
                    {attributes}
                </div>
                <Divider orientation="left">Pins</Divider>

            </div>
        )
    }
}