const fs = require('fs')

const {
    Color,
    Fill,
    SVGPlotter,
    PCBPlotter,
    Pcb,
} = require("kicad-utils")


const args = process.argv.slice(2)
const filename = args[0]

class ModulePlotter extends PCBPlotter {
    plotModule(mod) {
        for (let edge of mod.graphics) {
            if (edge instanceof Pcb.EdgeModule) {
                this.plotEdgeModule(edge, mod);
            }
        }
        for (let pad of mod.pads) {
            this.plotPad(true, pad, Color.BLACK, Fill.FILLED_SHAPE)
        }
    }
    getModuleSize(mod) {
        const outline = {
            width: { min: 0, max: 0 },
            height: { min: 0, max: 0 }
        }
        mod.graphics.forEach(graph => {
            const points = [graph.start, graph.end]
    
            points.forEach(el => {
                if (!el) return
                if (el.x < outline.width.min) outline.width.min = el.x;
                if (el.x > outline.width.max) outline.width.max = el.x;
                if (el.y < outline.height.min) outline.height.min = el.y;
                if (el.y > outline.height.max) outline.height.max = el.y;
            })
        })


        return outline 
    }
}



const footprint = fs.readFileSync(filename).toString()
const kicad = Pcb.PCB.load(footprint)

const plotter = new SVGPlotter();
const pcbPlotter = new ModulePlotter(plotter)
const outline = pcbPlotter.getModuleSize(kicad)
// console.log(outline)
plotter.pageInfo = {
    width: Math.abs(outline.width.min) + Math.abs(outline.width.max),
    height: Math.abs(outline.height.min) + Math.abs(outline.height.max)
}

plotter.startPlot();

plotter.save();
plotter.translate(outline.width.min * -1, outline.height.min * -1);
// plotter.setColor(Color.WHITE);
pcbPlotter.plotModule(kicad) 

// plotter.restore();
plotter.endPlot();

console.log(plotter.output)