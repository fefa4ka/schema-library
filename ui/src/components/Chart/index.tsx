
import { compose, IClassNameProps } from '@bem-react/core';
import { Chart as Base } from './Chart';

export interface IProps extends IClassNameProps {
    chartData: {
        [name:string]: number[]
    }[],
    showLabels: {
        [name: string]: boolean
    },
    onLegendClick: (event: React.SyntheticEvent) => void
}

export const Chart = compose()(Base);