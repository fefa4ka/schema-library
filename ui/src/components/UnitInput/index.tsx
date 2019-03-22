
import { compose, IClassNameProps } from '@bem-react/core';
import { UnitInput  as  Base } from './UnitInput';

export interface IProps extends IClassNameProps {
    name: string,
    suffix: never,
    value: string | number,
    multiple?: boolean,
    onChange: (value: number | string) => void
}


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

export const UnitInput = compose()(Base);
export const canonise = (value:number) => {
    const absoluteValue = Math.abs(value)
    const log = Math.log(absoluteValue) / Math.log(1000)
    let power = Math.floor(log)
    let fixedValue:string = value.toFixed(2)
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
    } else {
        fixedValue = '0'
    }

    return `${fixedValue} ${siPrefix[power] || ''}`
}

