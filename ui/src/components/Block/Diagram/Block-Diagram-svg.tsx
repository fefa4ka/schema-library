import * as React from 'react'
import { IProps } from './index'
import { cn } from '@bem-react/classname'
import './Block-Diagram.css'
const nomnoml = require('nomnoml')

const cnDiagram = cn('Block')('Diagram')
const initialState = {
    exponenta: 0,
    value: '',
    graph: ''
}

type State = {
    exponenta: number,
    value: string | number,
    graph: string
}

function convertReactSVGDOMProperty(str:string) {
    return str.replace(/[-|:]([a-z])/g, function (g) { return g[1].toUpperCase(); })
}

function startsWith(str:string, substring:string) {
    return str.indexOf(substring) === 0;
}

const DataPropPrefix = 'data-';

function serializeAttrs(map:any) {
    const ret:any = {};
    for (let prop, i = 0; i < map.length; i++) {
        const key = map[i].name;
        if (key == "class") {
            prop = "className";
        }
        else if (!startsWith(key, DataPropPrefix)) {
            prop = convertReactSVGDOMProperty(key);
        }
        else {
            prop = key;
        }

        ret[prop] = map[i].value;
    }
    return ret;
}

function getSVGFromSource(src:string) {
    const svgContainer = document.createElement('div');
    svgContainer.innerHTML = src
    const svg = svgContainer.firstElementChild
    svg && svg.remove 
        ? svg.remove()
        : svg && svgContainer.removeChild(svg); // deref from parent element
    
    return svg
}

// get <svg /> element props
function extractSVGProps(src: string) {
    const obj = getSVGFromSource(src)
    return (obj && obj.attributes && obj.attributes.length > 0) ? serializeAttrs(obj.attributes) : null;
}
  
export class Diagram extends React.Component<IProps, {}> {
    state: State = initialState
    private canvasRef = React.createRef<HTMLCanvasElement>()

    render() { 
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
                    connections.push(`[<note>Add source or load to pins]->[${pin}]`)
            }
                return connections.join(';')
            }
        }).filter(item => item).join(';')

        
        const sourcesNet = sources.map(source => {
            const name = source.description || source.name
            const args = Object.keys(source.args).filter(arg => source.args[arg].value).map(arg => `${arg} = ${source.args[arg].value} ${source.args[arg].unit.suffix}`).join(';')

            const diagram = [`[${name}|${args}]`]
            Object.keys(source.pins).forEach(pin => {
                source.pins[pin].forEach(input =>
                    diagram.push(`[${name}]${pin}-[${input}]`)
                )
            })

            return diagram.join(';')
        }).join(';')
        // const ids = ['#label: stroke=#000001']
        const settings = ['#font: ISOCPEUR', '#stroke: #000000', '#direction: down', '#fill: #ffffff', '#lineWidth: 1', '#.unwired: stroke=red visual=none bold', '#.unwiredgnd: stroke=red visual=end empty', '#.label: visual=none align=center'].join('\n')
        const graph = settings + '\n' + [network, `[<${connectedPins.includes('gnd') ? 'end' : 'unwiredgnd'}>gnd]`, pinsNet, sourcesNet].filter(_ => _).join(';')

        return (
            <div
                dangerouslySetInnerHTML={{ __html: nomnoml.renderSvg(graph) }}
                className={cnDiagram}
            >
            </div>)
    }
}