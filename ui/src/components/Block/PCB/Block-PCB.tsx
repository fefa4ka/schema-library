import * as React from 'react'
import { IProps } from './index'
import axios from 'axios'
import { Button, Input } from 'antd'
const Designer:any = require('../../Designer').default
const { Text, Rect, Image, Part } = require('../../Designer')
import './Block-PCB.css'

const initialState = {
    pcb: [
        {type: "part", xlinkHref: 'http://localhost:3000/api/parts/footprint/?name=Capacitor_THT:CP_Radial_D6.3mm_P2.50mm', x: 10, y: 10 }
    ],
    height: 0,
    width: 0,
    canvasWidth: 0,
    canvasHeight: 0,
    zoom: 1
}

type State = {
    pcb: any,
    width: number,
    height: number,
    canvasWidth: number,
    canvasHeight: number,
    zoom: number
}

export class PCB extends React.Component<IProps, {}> {
    private divRef = React.createRef<HTMLDivElement>()
    state: State = initialState
    componentWillMount() {
        this.props.activeTab === 'pcb' && this.props.shouldReload(() => this.loadSchemaPcbNetlist())
    }
    componentDidMount() {
        const divRef = this.divRef.current || { clientHeight: 0, clientWidth: 0}
        const { clientHeight, clientWidth } = divRef
        this.setState({
            canvasHeight: clientHeight,
            canvasWidth: clientWidth
        })
        
    }
    componentWillReceiveProps(nextProps: IProps) {
        nextProps.activeTab === 'pcb' && nextProps.shouldReload(() => this.loadSchemaPcbNetlist()) 
    }
    loadSchemaPcbNetlist = () => {
        const { name, args, mods, pcb_body_kit } = this.props
        
        axios.post('/api/blocks/' + name + '/netlist/default/',
        {
            mods: mods,
            args: Object.keys(args).reduce((result: { [name:string]: string | number }, arg) => {
                result[arg] = args[arg].value
                
                return result
            }, {}),
            pcb_body_kit
        })
            .then(response => {
                const { width, height, components } = response.data
                this.setState({
                    width, height,
                    zoom: 1,
                    pcb: components 
                        ? Object.keys(components).map(part => ({
                            type: 'part',
                            ref: part,
                            xlinkHref: 'http://localhost:3000/api/parts/footprint/?name=' + components[part].footprint,
                            x: components[part].location[0],
                            y: components[part].location[1],
                            width: components[part].size.width,
                            height: components[part].size.height
                        }))
                        : []
                })
            })
        
    }
    render() {
        const { canvasWidth, canvasHeight, width, height, zoom } = this.state
        return <div 
            className="Block-PCB"
            ref={this.divRef}
        >
            <Button
                type="primary"
                shape="circle"
                icon="plus"
                onClick={() =>
                    this.setState(({ pcb, zoom }: State) => ({
                        zoom: zoom + 1,
                        pcb: pcb.map((part:any) => ({
                            ...part,
                            x: (part.x / zoom) * (zoom + 1),
                            y: (part.y / zoom) * (zoom + 1),
                            width: (part.width / zoom) * (zoom + 1),
                            height: (part.height / zoom) * (zoom + 1)
                        }))
                    }))}
            />
            <Button
                type="primary"
                shape="circle"
                icon="minus"
                onClick={() =>
                    this.setState(({ pcb, zoom }: State) => ({
                        zoom: zoom - 1,
                        pcb: pcb.map((part:any) => ({
                            ...part,
                            x: (part.x / zoom) * (zoom - 1),
                            y: (part.y / zoom) * (zoom - 1),
                            width: (part.width / zoom) * (zoom - 1),
                            height: (part.height / zoom) * (zoom - 1),
                            zoom
                        }))
                    }))}
            />
            <Input
                placeholder="Width"
                value={width}
                onChange={e => this.setState({ width: e.target.value })} />
            <Input
                placeholder="Height"
                value={height}
                onChange={e => this.setState({ height: e.target.value })} />
            <Designer
                // canvasWidth={canvasWidth}
                // canvasHeight={canvasHeight}
                width={width * zoom || 100}
                height={height * zoom || 100}
                objectTypes={{
                    'text': Text,
                    'rect': Rect,
                    'part': Part
                }}
                onUpdate={(pcb:any) => this.setState({pcb})}
                objects={this.state.pcb}
            />
        </div>
    }
}
