import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import { Input, Select, Tooltip } from 'antd'
import Markdown from 'react-markdown'

const { Option } = Select

const cnUnit = cn('UnitInput')

const initialState = {
    exponenta: 0,
    value: '',
}

type State = {
    exponenta: number,
    value: string | number
}
  
export class UnitInput extends React.Component<IProps, {}> {
    state: State = initialState

    onChange(value: string) {        
        this.state.value !== value && this.setState({ value })
        
        return parseFloat(value) * Math.pow(10, this.state.exponenta)
    }
    render() { 
        const { name, suffix, value } = this.props
        const scale: { [name:string]: (string | number)[]} = {
            pico: ['p', -12],
            nano: ['n', -9],
            micro: ['μ', -6],
            milli: ['m', -3],
            base: ['', 0],
            kilo: ['k', 3],
            mega: ['M', 6],
            giga: ['G', 9],
            tera: ['T', 12]
        }

        const selectAfter = (
            <Select
                defaultValue="base"
                style={{ width: 80 }}
                onChange={unit =>
                    this.setState({ exponenta: scale[unit][1] },
                        () => this.props.onChange(this.onChange(this.state.value.toString())))}>
                {Object.keys(scale).map(unit => {
                    const exponent = parseInt(scale[unit][1].toString(), 10)
                    let fixed: string | number = Math.pow(10, exponent)
                    
                    if (exponent < 0) {
                        fixed = fixed.toFixed(Math.abs(exponent))
                    }
                    
                    return <Option value={unit}>
                        <Tooltip title={<span>10<sup>{scale[unit][1]}</sup> = {fixed.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")}</span>}>
                            <span>{scale[unit][0]}{suffix}</span>
                        </Tooltip>
                    </Option>
                })}
            </Select>
        )

        return (
            <Input
                key={name}
                addonBefore={name}
                addonAfter={selectAfter}
                defaultValue={value.toString()}
                onBlur={event => this.props.onChange(this.onChange(event.target.value))}
                onPressEnter={(event: React.SyntheticEvent) => {
                    const target = event.target as HTMLInputElement
                    this.props.onChange(this.onChange(target.value))
                }}
            />)
    }
}