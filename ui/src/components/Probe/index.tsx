import { compose, IClassNameProps } from '@bem-react/core';
import { Part  as  Base } from './Probe';
import { TParams, TDictList } from '../Block'
export type TProbe = {
    name: string,
    description: string,
    args: TParams,
    pins: TDictList,
    port: string,
    channel: number,
    index: number
}

type TProbePin = {
    name: string,
    channel: string
}

type TProbePins = {
    [name:string]: TProbePin
}

export type TProbeBlock = {
    name: string,
    description: string,
    pins: string[],
    args: TParams 
}

export type TProbeState = {
    [name: string]: {
        name: string,
        channel: string
    }
}

export interface IProps extends IClassNameProps {
    type: string,
    pins: string[],
    probe: TProbePins,
    loading: boolean,
    onChange(probe:any): void
}

export const Probe = compose()(Base);