import { compose, IClassNameProps } from '@bem-react/core';
import { Part  as  Base } from './Part';

export type TSource = {
    name: string,
    args: {
        [name: string]: string
    },
    pins: {
        [name: string]: string[]
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