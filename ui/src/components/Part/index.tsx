import { compose, IClassNameProps } from '@bem-react/core';
import { Part  as  Base } from './Part';

export type TArgs = {
    [name:string]: {
        value: number | string,
        unit: {
            name: string,
            suffix: string
        }
    }
}
export type TSource = {
    name: string,
    description: string[],
    args: TArgs,
    mods?: {
        [name:string]: string[]
    },
    nets: {
        [name:string]: string[]
    },
    pins: {
        [name: string]: string[]
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
    index: number
}

export interface IProps extends IClassNameProps {
    type: string,
    pins: string[],
    source: TSource,
    onChange(source:TSource): void
}

export const Part = compose()(Base);