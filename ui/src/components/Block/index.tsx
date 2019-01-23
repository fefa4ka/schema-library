import { compose, IClassNameProps } from '@bem-react/core';
import { Block  as  Base } from './Block';

export interface IProps extends IClassNameProps {
    name?: string
    mods?: {
        [name:string]: string[]
    }  
}

export const Block = compose()(Base);