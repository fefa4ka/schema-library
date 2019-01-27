import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import axios from 'axios'
import {UnControlled as CodeMirror} from 'react-codemirror2'

require('codemirror/lib/codemirror.css')
require('codemirror/mode/python/python')


const cnCode = cn('Code')

const initialState = {
    value: ''
}

type State = {
    value: string
}
  
export class Code extends React.Component<IProps, {}> {
    state: State = {
        ...initialState,
        value: this.props.value
    }

    componentDidMount() {
        axios.get('/api/files/?name=' + this.props.file)
            .then(res => {
                this.setState({ value: res.data })
            })
    }
    render() { 
       return (<CodeMirror
            options={{
                mode: 'python',
               lineNumbers: true,
                lint: true
            }}
            value={this.state.value}
        />)
    }
}