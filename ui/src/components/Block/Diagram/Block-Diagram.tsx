import * as React from 'react'
import { IProps } from './index'
const nomnoml = require('nomnoml')

const initialState = {
    exponenta: 0,
    value: '',
}

type State = {
    exponenta: number,
    value: string | number
}

const LibTest = `EESchema-LIBRARY Version 2.3
#encoding utf-8
#
# Amperemeter_AC
#
DEF Amperemeter_AC MES 0 1 N N 1 F N
F0 "MES" -130 40 50 H V R CNN
F1 "Amperemeter_AC" -130 -30 50 H V R CNN
F2 "" 0 100 50 V I C CNN
F3 "" 0 100 50 V I C CNN
DRAW
A -20 -54 21 -1633 -167 0 1 0 N -40 -60 0 -60
A 20 -65 21 140 1660 0 1 0 N 40 -60 0 -60
C 0 0 100 0 1 10 N
T 0 0 25 100 0 0 0 A Normal 0 C C
P 2 0 0 0 -125 -125 -75 -75 N
P 2 0 0 0 75 75 125 125 N
P 3 0 0 0 75 125 125 125 125 75 N
X ~ 1 0 -200 100 U 50 50 1 1 P
X ~ 2 0 200 100 D 50 50 1 1 P
ENDDRAW
ENDDEF
#
# Amperemeter_DC
#
DEF Amperemeter_DC MES 0 1 N N 1 F N
F0 "MES" -130 40 50 H V R CNN
F1 "Amperemeter_DC" -130 -30 50 H V R CNN
F2 "" 0 100 50 V I C CNN
F3 "" 0 100 50 V I C CNN
DRAW
C 0 0 100 0 1 10 N
T 0 0 0 100 0 0 0 A Normal 0 C C
P 2 0 0 0 -125 -125 -75 -75 N
P 2 0 0 0 75 75 125 125 N
P 3 0 0 0 75 125 125 125 125 75 N
P 2 0 1 0 10 150 30 150 N
P 2 0 1 0 20 160 20 140 N
X - 1 0 -200 100 U 50 50 1 1 P
X + 2 0 200 100 D 50 50 1 1 P
ENDDRAW
ENDDEF`
export class Diagram extends React.Component<IProps, {}> {
    state: State = initialState
    private canvasRef = React.createRef<HTMLCanvasElement>()

    componentDidUpdate() {
        const { nets, pins, load } = this.props

        const get_name = (pin: string, index: number) => {
            const [_, data] = pin.split(' ')
            const vars = data.split('/')

            return vars[index]
        }

        // const connectedSourcePins = sources.reduce((pins:string[], source) => {
        //     const sourcePins: string[] = Object.keys(source.pins).reduce((pins: string[], pin) => 
        //         pins.concat(source.pins[pin])
        //         , [])

        //     return pins.concat(sourcePins)
        // }, []).filter((value, index, self) => self.indexOf(value) === index)

        const connectedLoadPins = load.reduce((pins:string[], source) => {
            const sourcePins: string[] = Object.keys(source.pins).reduce((pins: string[], pin) => 
                pins.concat(source.pins[pin])
                , [])

            return pins.concat(sourcePins)
        }, []).filter((value, index, self) => self.indexOf(value) === index)
        
        const connectedPins = connectedLoadPins

        
        const network = Object.keys(nets).map((net, index) => {
            const pins: string[] = nets[net]
            const wire = pins.map((pin, index, list) => {
               
                if (list.length - 1 > index) {
                    return `[${get_name(pin, 0)}]${get_name(pin, 2)}-${get_name(list[index + 1], 2)}[${get_name(list[index + 1], 0)}]`
                }
            }).join(';')

            return wire
        }).join('')

        const pinsNet = Object.keys(pins).map((pin: string, index, list) => {
            const isAlreadyExists = ['input', 'output'].includes(pin) === false && list.reduce((exists, sub_pin, sub_index) => {
                if (index > sub_index && pins[pin][0] === pins[sub_pin][0]) {
                    return true
                }

                return exists
            }, false)

            if(pins[pin][0] && !isAlreadyExists) {
                const connections = [`[<${connectedPins.includes(pin) ? 'label' : 'unwired'}>${pin}]-${get_name(pins[pin][0], 2)}[${get_name(pins[pin][0], 0)}]`]
                if (connectedPins.includes(pin) === false) {
                    connections.push(`[<note>Add source or load to pins]->[${pin}]`)
            }
                return connections.join(';')
            }
        }).filter(item => item).join(';')

        
        // const sourcesNet = sources.map(source => {
        //     const name = source.name
        //     const args = Object.keys(source.args).filter(arg => source.args[arg].value).map(arg => `${arg} = ${source.args[arg].value} ${source.args[arg].unit.suffix}`).join(';')
            
        //     const diagram = [`[<source>${name}${source.description ? '|' + source.description : ''}|${args}]`]
        //     Object.keys(source.pins).forEach(pin => {
        //         source.pins[pin].forEach((input:string) =>
        //             diagram.push(`[${name}]${pin}-[${input}]`)
        //         )
        //     })

        //     return diagram.join(';')
        // }).join(';')

        const loadNet = load.map((source, index) => {
            let { name } = source
            const args = Object.keys(source.args).filter(arg => source.args[arg].value).map(arg => `${arg} = ${source.args[arg].value} ${source.args[arg].unit.suffix}`).join(';')
            
            const diagram = [`[<load>${name}|${args}]`]
            Object.keys(source.pins).forEach(pin => {
                source.pins[pin].forEach((input:string) =>
                    diagram.push(`[${name}]${pin}-[${input}]`)
                )
            })

            return diagram.join(';')
        }).join(';')

        const settings = ['#font: routed', "#fontSize: 10", '#stroke: #000000', '#.load: stroke=#b9b9b9 fill=#fafafa', '#.source: stroke=#1890ff fill=#fafafa', '#direction: right', '#fill: #ffffff', '#lineWidth: 1', '#.unwired: stroke=red visual=none bold', '#.unwiredgnd: stroke=red visual=end empty '].join('\n')
        const graph = settings + '\n' + [network, `[<${connectedPins.includes('gnd') ? 'end' : 'unwiredgnd'}>gnd]`, pinsNet, loadNet].filter(_=>_).join(';')
        
        nomnoml.draw(this.canvasRef.current, graph);
    }
    render() {

        // const lib = Lib.Library.load(LibTest)
        // console.log({lib})

		return <canvas ref={this.canvasRef} />
      
    }

}