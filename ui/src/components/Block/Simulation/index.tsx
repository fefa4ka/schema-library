
import { compose, IClassNameProps } from '@bem-react/core';
import { Simulation as Base } from './Block-Simulation'
import { IBlock, TParams, TDictList } from '../../Block';

export interface IProps extends IClassNameProps {
    name: string,
    description: string[],
    args: TParams,
    mods: TDictList,
    pins: TDictList,
    body_kit: IBlock[],
    shouldReload: any 
}

export const Simulation = compose()(Base);