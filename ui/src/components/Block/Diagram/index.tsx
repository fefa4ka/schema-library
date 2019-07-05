
import { compose, IClassNameProps } from '@bem-react/core';
import { Diagram as Base } from './Block-Diagram';
import { IBlock } from '../../Block';

export interface IProps extends IClassNameProps {
    name: string,
    nets: {
        [name:string]: string[]
    },
    pins: {
        [name:string]: string[]
    },
    load: IBlock[]
    parts: {
        [name: string]: IBlock
    } 
}

export const Diagram = compose()(Base);