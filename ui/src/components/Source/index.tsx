import { compose, IClassNameProps } from '@bem-react/core';
import { Part  as  Base } from './Source';

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
    description: string,
    args: TArgs,
    pins: {
        [name: string]: string[]
    },
    device: string,
    port: string,
    channel: number,
    index: number
}

export interface IProps extends IClassNameProps {
    type: string,
    pins: string[],
    source: TSource,
    onChange(source:TSource): void
}

export const Source = compose()(Base);