import { compose, IClassNameProps } from '@bem-react/core';
import { Block  as  Base } from './Block';
import { TProbeState } from '../Probe'
export interface TParams {
    [name:string]: {
        value: number | string,
        unit: {
            name: string,
            suffix: string
        },
        description?: string
    }
}

export interface TDictList {
    [name:string]: string[] 
}

export interface IDevice {
    title: string,
    port: string,
    channels: string[]
}

export interface IBlock {
    name: string,
    description: string[],
    args: TParams,
    params: TParams,
    mods?: TDictList,
    props?: TDictList,
    nets: TDictList,
    pins: TDictList,
    devices?: {
        [name: string]: IDevice
    },
    probes: TProbeState,
    index: number
}

export const NullBlock = {
    name: '',
    description: [],
    args: {},
    params: {},
    nets: {},
    pins: {},
    probes: {},
    index: 0
}


export interface IProps extends IClassNameProps {
    name?: string
    mods?: TDictList 
}


export const Block = compose()(Base);
