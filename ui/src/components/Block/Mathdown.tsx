import * as React from 'react'
import { cn } from '@bem-react/classname'
const MathJax = require("./mathjax-preview").default
import Markdown from 'react-markdown'

const cnMath = cn('Math')

const initialState = {
    value: '',
    edited: ''
}

type State = {
    value: string,
    edited: string
}

type IProps = {
    value: string
}

export class MathMarkdown extends React.Component<IProps, {}> {
    state: State = initialState 

    shouldComponentUpdate(nextProps:IProps) {
        if (this.props.value !== nextProps.value) {
            return true
        } else {
            return false
        }
    }

    render() { 
        return (
            <Markdown
                source={this.props.value}
                renderers={{
                    inlineCode: (props: { value: string }) =>
                        <MathJax math={'`' + props.value + '`'}/>
                }}
            />
        )
    }
}