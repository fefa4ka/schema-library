import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import {UnControlled as CodeMirror} from 'react-codemirror2'

require('codemirror/lib/codemirror.css')
require('codemirror/mode/python/python')


const cnCode = cn('Code')

const initialState = {
    value: '',
    edited: ''
}

type State = {
    value: string,
    edited: string
}
  
export class Code extends React.Component<IProps, {}> {
    state: State = {
        ...initialState,
        value: this.props.value,
        edited: this.props.value
    }

    componentDidMount() {
        if (this.props.file) {
            axios.get('/api/files/?name=' + this.props.file)
                .then(res => {
                    this.setState({ value: res.data })
                })
        }
    }
    render() { 
       return (<CodeMirror
            options={{
                mode: 'python',
                lineNumbers: true,
                indentWithTabs: false,
                indentUnit: 4,
                tabSize: 4
            }}
           value={this.state.value}
           onBlur={() => this.props.onChange(this.state.edited)}
           onChange={(editor, data, value) => {
                this.setState({ edited: value })
           }}
        />)
    }
}