
import { compose, IClassNameProps } from '@bem-react/core';
import { UnitInput  as  Base } from './UnitInput';

export interface IProps extends IClassNameProps {
    name: string,
    suffix: never,
    value: string | number,
    multiple?: boolean,
    onChange: (value: number | string) => void
}

export const UnitInput = compose()(Base);
