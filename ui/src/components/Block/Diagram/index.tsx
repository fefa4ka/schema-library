
import { compose, IClassNameProps } from '@bem-react/core';
import { Diagram as Base } from './Block-Diagram';
import { TSource } from '../../Part';

export interface IProps extends IClassNameProps {
    name: string,
    nets: {
        [name:string]: string[]
    },
    pins: {
        [name:string]: string[]
    },
    sources: TSource[],
    load: TSource[]
    parts: TSource[]
}

export const Diagram = compose()(Base);