
import { compose, IClassNameProps } from '@bem-react/core';
import { PCB as Base } from './Block-PCB'
import { TParams, TDictList } from '../../Block';
import { TDevice } from '../../Device'

export interface IProps extends IClassNameProps {
    name: string,
    args: TParams,
    mods?: TDictList,
    props?: TDictList,
    pcb_body_kit: TDevice[],
    shouldReload: any,
    activeTab: string
}

export const PCB = compose()(Base);