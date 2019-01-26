
import { compose, IClassNameProps } from '@bem-react/core';
import { Diagram  as  Base } from './Block-Diagram';

export interface IProps extends IClassNameProps {
    name: string,
    nets: {
        [name:string]: string[]
    },
    pins: {
        [name:string]: string[]
    },
    sources: {
        name: string,
        args: {
            [name:string]: number | string
        },
        pins: {
            [name: string]: string[]
        }
    }[]
}

export const Diagram = compose()(Base);