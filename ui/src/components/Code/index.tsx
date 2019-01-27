
import { compose, IClassNameProps } from '@bem-react/core';
import { Code  as  Base } from './Code';

export interface IProps extends IClassNameProps {
    file: string,
    value: string
    onChange: (value: number | string) => void
}

export const Code = compose()(Base);