import { compose, IClassNameProps } from '@bem-react/core';
import { Part  as  Base } from './Part';

export interface IProps extends IClassNameProps {
    type: string
}

export const Part = compose()(Base);