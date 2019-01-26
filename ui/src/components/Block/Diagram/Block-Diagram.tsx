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
  
export class Diagram extends React.Component<IProps, {}> {
    state: State = initialState
    private canvasRef = React.createRef<HTMLCanvasElement>()

    componentDidUpdate() {
        const { nets, pins, sources } = this.props

        const get_name = (pin: string, index: number) => {
            const [_, data] = pin.split(' ')
            const vars = data.split('/')

            return vars[index]
        }

        const connectedPins = sources.reduce((pins:string[], source) => {
            const sourcePins: string[] = Object.keys(source.pins).reduce((pins: string[], pin) => 
                pins.concat(source.pins[pin])
            , [])

            return pins.concat(sourcePins)
        }, []).filter((value, index, self) => self.indexOf(value) === index)

        
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
                    connections.push(`[<note>Attach pins]->[${pin}]`)
            }
                return connections.join(';')
            }
        }).filter(item => item).join(';')

        
        const sourcesNet = sources.map(source => {
            const args = Object.keys(source.args).filter(arg => source.args[arg]).map(arg => `${arg} = ${source.args[arg]}`).join(';')
            
            const diagram = [`[${source.name}|${args}]`]
            Object.keys(source.pins).forEach(pin => {
                source.pins[pin].forEach(input =>
                    diagram.push(`[${source.name}]${pin}-[${input}]`)
                )
            })

            return diagram.join(';')
        }).join(';')
        const settings = ['#font: ISOCPEUR', '#stroke: #000000', '#fill: #ffffff', '#lineWidth: 1', '#.unwired: stroke=red visual=none bold', '#.unwiredgnd: stroke=red visual=end empty '].join('\n')
        const graph = settings + '\n' + [network, `[<${connectedPins.includes('gnd') ? 'end' : 'unwiredgnd'}>gnd]`, pinsNet, sourcesNet].filter(_=>_).join(';')
        
        nomnoml.draw(this.canvasRef.current, graph);
    }
    render() { 

       return <canvas ref={this.canvasRef} />
    }
}