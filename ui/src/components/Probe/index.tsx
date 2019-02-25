import { compose, IClassNameProps } from '@bem-react/core';
import { Part  as  Base } from './Probe';

export type TArgs = {
    [name:string]: {
        value: number | string,
        unit: {
            name: string,
            suffix: string
        }
    }
}
export type TProbe = {
    name: string,
    description: string,
    args: TArgs,
    pins: {
        [name: string]: string[]
    },
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
export interface IProps extends IClassNameProps {
    type: string,
    pins: string[],
    probe: TProbePins,
    loading: boolean,
    onChange(probe:any): void
}

export const Probe = compose()(Base);