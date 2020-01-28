import * as React from 'react'
import { IProps } from './index'
import axios from 'axios'
import { Button, Input } from 'antd'
// const Designer:any = require('../../Designer').default
// const { Text, Rect, Image, Part } = require('../../Designer')
import './Block-PCB.css'
import Konva from 'konva'
import { Stage, Layer, Rect, Text, Circle, Line } from 'react-konva'

const initialState = {
    pcb: [
        {type: "part", xlinkHref: '/api/parts/footprint/?name=Capacitor_THT:CP_Radial_D6.3mm_P2.50mm', x: 10, y: 10 }
    ],
	components: [],
    height: 0,
    width: 0,
    canvasWidth: 0,
    canvasHeight: 0,
    zoom: 1
}

type State = {
    pcb: any,
	components: any,
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
        console.log('PCB Designer', nextProps)
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
					components,
                    pcb: components 
                        ? Object.keys(components).map(part => ({
                            type: 'part',
                            ref: part,
                            xlinkHref: 'http://localhost:3000/api/parts/footprint/?name=' + components[part].footprint,
                            x: components[part].location[0],
                            y: components[part].location[1],
                            width: components[part].size.width,
                            height: components[part].size.height,
                        }))
                        : []
                })
            })
        
    }
    render() {
        const { canvasWidth, canvasHeight, width, height, zoom, components } = this.state
		const scale = canvasWidth / (width * 10)

        return <div
            className="Block-PCB"
            ref={this.divRef}
        >
			<Stage width={width * 10 * scale} height={height * 10 * scale} scale={{ x: scale, y: scale }}>
					{Object.keys(components).map(part => 
                        <Part component={components[part]}/>
					)}
			</Stage>
        </div>
    }
}

const Part = ({ component }:any) => {
    const { location, size, pins } = component
    const scale = 10
    const Border = <Rect 
        x={location[0] * scale} 
        y={location[1] * scale}
        width={size.width * scale}
        height={size.height * scale}
        stroke='silver'
        strokeWidth={1}
    />
    const Pads = Object.keys(pins).map(pin => {
        const pad = pins[pin]

        return <Circle 
            key={pin}
            radius={0.5 * scale} 
            x={(location[0] + pad.location[0]) * scale + 5}  
            y={(location[1] + pad.location[1]) * scale + 5} 
            stroke='black'
            strokeWidth={1}
        />
    })

    return <><Layer>{Border}</Layer><Layer>{Pads}</Layer></>
}

