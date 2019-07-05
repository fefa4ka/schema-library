
import { compose, IClassNameProps } from '@bem-react/core';
import { Definition as Base } from './Block-Definition'
import { IBlock, TParams, TDictList } from '../index';
import { TDevice } from '../../Device'

export interface IProps extends IClassNameProps {
    name: string,
    available: {
        footprint: string,
        model: string,
        id: number
    }[],
    args: TParams,
    params: TParams,
    mods?: TDictList,
    props?: TDictList,
    pins: TDictList,
    body_kit: IBlock[],
    pcb_body_kit: TDevice[],
    onChange: any,
    activeTab: string
}

export const Definition = compose()(Base);