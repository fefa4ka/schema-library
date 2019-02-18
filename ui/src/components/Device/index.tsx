import { compose, IClassNameProps } from '@bem-react/core';
import { Device  as  Base } from './Device';

export type TDevice = {
    library: string,
    name: string,
    description: string,
    pins: {
        [name: string]: string[]
    },
    index: number
}

export interface IProps extends IClassNameProps {
    type: string,
    pins: string[],
    device: TDevice,
    onChange(source:any): void
}

export const Device = compose()(Base);