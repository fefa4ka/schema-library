import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname';
import {
    Col,
    Row,
    Divider
    } from 'antd';
import { MathMarkdown } from '../Mathdown';
import { UnControlled as CodeMirror } from 'react-codemirror2';

require('codemirror/lib/codemirror.css')
require('codemirror/mode/python/python')

import './Block-Description.css';
const cnBlock = cn('Block-Description')

const initialState = {
    
}

type State = {
}

export class Description extends React.Component<IProps, {}> {
    state: State = initialState

    codeExample() {
        const { name, args, mods } = this.props

        const argsKeys = Object.keys(args).filter(arg => args[arg].unit.suffix)
        const codeUnits = argsKeys.map(arg => args[arg].unit.suffix).filter((value, index, self) => self.indexOf(value) === index).map(item => 'u_' + item).join(', ')
        const codeArgs =  argsKeys.map(arg => arg + ' = ' + args[arg].value + (args[arg].unit.suffix ? ' @ u_' + args[arg].unit.suffix : '')).join(',\n\t')
        const codeMods = Object.keys(mods).map((type: string) =>
                type + "=['" + 
                    (Array.isArray(mods[type]) 
                        ? mods[type].join("', '") 
                        : mods[type])
                + "']").join(', ')
        
        const blockQuery = name.split('.')
        const blockName = blockQuery[blockQuery.length - 1]
        const codeExample = `from bem.${blockQuery.slice(0, blockQuery.length - 1).join('.')} import ${blockName}${codeUnits ? '\nfrom bem import ' + codeUnits : ''}

${blockName}(${codeMods})${codeArgs ? `(
    ${codeArgs}
)` : '()'}`
        
        return codeExample
    }

    render() {
        const description = this.props.description.join('\n\n')
            
        return <>
            <Divider orientation="left">
                Description
            </Divider>
            <Row>
                <Col span={16} className={cnBlock('Text')}>
                    <MathMarkdown value={description}/>
                </Col>
                <Col span={8}>
                    <CodeMirror
                        className={cnBlock('CodeExample')}
                        options={{
                            mode: 'python',
                            lineNumbers: false,
                            indentWithTabs: false,
                            indentUnit: 4,
                            tabSize: 4
                        }}
                        value={'# Code Example\n\n' + this.codeExample()}
                    />
                </Col>
            </Row>
            </>
    }
}
