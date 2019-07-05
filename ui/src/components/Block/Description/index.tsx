
import { compose, IClassNameProps } from '@bem-react/core';
import { Description as Base } from './Block-Description'
import { TParams, TDictList } from '../../Block';

export interface IProps extends IClassNameProps {
    name: string,
    description: string[],
    args: TParams,
    mods: TDictList
}

export const Description = compose()(Base);