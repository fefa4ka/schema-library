import { compose, IClassNameProps } from '@bem-react/core';
import { BlockLight as Base } from './BlockLight';
import { IBlock } from '../Block'
export interface IProps extends IClassNameProps {
    type: string,
    pins: string[],
    block: IBlock,
    onChange(block: IBlock): void
}

export const BlockLight = compose()(Base);