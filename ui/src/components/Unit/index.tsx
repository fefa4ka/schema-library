
import * as React from 'react'
import { IClassNameProps } from '@bem-react/core'
import { cn } from '@bem-react/classname'
import { MathMarkdown } from '../Block/Mathdown'
import { Tooltip } from 'antd'
export interface IProps extends IClassNameProps {
    name: string,
    suffix?: string,
    description?: string,
    value: string | number
}
import './Unit.css'
const cnUnit = cn('Unit')


export const siPrefix:{[name:string]: string} = {
    '-24': 'y',
    '-21': 'z',
    '-18': 'a',
    '-15': 'f',
    '-12': 'p',
    '-9': 'n',
    '-6': 'μ',
    '-3': 'm',
    '-2': 'c',
    '-1': 'd',
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

export const canonise = (value:number, suffix?: string) => {
    const absoluteValue = Math.abs(value)
    const log = Math.log(absoluteValue) / Math.log(1000)
    let power = Math.floor(log)
    let fixedValue: string = value.toFixed(2)
    
    if(value !== 0) {
        power *= 3
        
        if (power !== 0) {
            value = value / 10 ** power
        }
        
        if (value.toFixed(2) != Math.round(value).toFixed(2)) {
            fixedValue = value.toFixed(1)
        } else {
            fixedValue = Math.round(value).toString()
        }
    } 

    if(fixedValue === 'NaN') {
        fixedValue = '?'
    }

    const prefix = suffix !== undefined
        ? (siPrefix[power] || '') + suffix
        : power !== 0 && fixedValue !== '?' && value !== 0
            ? ' * 10^' + power
            : ''
    
    return `${fixedValue} ${prefix || ''}`
}

export const Unit = ({ name, suffix, value, description }: IProps): any => {
    const [unit_title, unit_subscript] = name.indexOf('_') !== -1 
        ? name.split('_')
        : [name[0], name.slice(1)]
    
    const canonised = typeof value === 'number'
        ? canonise(value)
        : value

    return (
        <span className={cnUnit('Param')} key={name}> 
            <Tooltip
                overlayClassName={cnUnit('Tooltip')}
                title={<MathMarkdown value={description || name + ' is not described'} />}
            >
                <strong>{unit_title}<sub key='s'>{unit_subscript}</sub></strong> = {canonised} {suffix}
            </Tooltip>
        </span>
    )
}
        
