import * as React from 'react';
import axios from 'axios';
import { cn } from '@bem-react/classname';
import { Code } from '../Code';
import {
    Col,
    Modal,
    Row,
    Tabs,
    Button
    } from 'antd';
import { TDevice } from '../Device';
import { Definition } from './Definition'
import { Description } from './Description'
import { Diagram } from './Diagram';
import { Simulation } from './Simulation'
import { PCB } from './PCB'
import { IProps, IBlock, NullBlock } from './index';

import './Block.css';
import { Divider, TreeSelect } from 'antd'
const TabPane = Tabs.TabPane;
const TreeNode = TreeSelect.TreeNode;

import { insertSpaces } from '../Blocks/Blocks'

require('codemirror/lib/codemirror.css')
require('codemirror/mode/python/python')

const cnBlock = cn('Block')


const initialState = {
    available: [],
    selectedMods: [],
    params: {},
    spiceAttrs: {},
    debug: '',
    debugUrl: '',
    modalDebugVisible: false,
    modalLoadVisible: false,
    modalDeviceVisible: false,
    modalTestVisible: false,
    modalConfirmLoading: false,
    parts: {},
    pcb_body_kit: [],
    body_kit: [],
    files: [],
    activeTab: 'info',
    mods: {},
    simulationShouldUpdate: false,
    pcbShouldUpdate: false,
    pcbNetlist: {}
}

interface IState extends IBlock {
    available: {
        footprint: string,
        model: string,
        id: number
    }[],
    selectedMods: string[],
    spiceAttrs: {
        [name:string]: {
            value: number | string,
            unit: {
                name: string,
                suffix: string
            }
        }
    },
    body_kit: IBlock[],
    parts: { [name:string]: IBlock },
    pcb_body_kit: TDevice[],
    debug: string,
    debugUrl: string,
    modalDebugVisible: boolean,
    modalTestVisible: boolean,
    modalConfirmLoading: boolean,
    files: string[],
    activeTab: string,
    simulationShouldUpdate: boolean,
    pcbShouldUpdate: boolean,
    pcbNetlist: any
}


export class Block extends React.Component<IProps, {}> {
    state: IState = {
        ...NullBlock,
        ...initialState
    }
    codeInstance: any
    loadBlockTimeout: any = 0 

    componentWillMount() {
        this.loadBlock()
    }
    componentDidUpdate(prevProps: IProps, prevState: IState) {
        const isModChanged = JSON.stringify(prevState.selectedMods) !== JSON.stringify(this.state.selectedMods)

        const emptyBlock = {
            selectedMods: [],
            args: {},
            charData: [],
            parts: [],
            pcb_body_kit: [],
            body_kit: [],
            simulationShouldUpdate: false,
            pcbShouldUpdate: false
        }
        if (isModChanged) {
            delete emptyBlock.selectedMods
        }
        if (prevProps.name !== this.props.name || isModChanged) {
		
            this.setState(emptyBlock, this.updateBlock)
        }
        return true
    }
   
    urlParams() {
        const selectedMods: { [name:string]: string[] } = this.state.selectedMods.reduce((mods: { [name:string]: string[] }, mod) => {
            const [type, value] = mod.split(':')
            mods[type] = mods[type] || []
            mods[type].push(value)

            return mods
        }, {})

        const modsUrlParam = Object.keys(selectedMods).map((mod:string) => mod + '=' + selectedMods[mod].join(','))
        const argsUrlParam = Object.keys(this.state.args).filter(arg => this.state.args[arg].value).map(arg => arg + '=' + this.state.args[arg].value)
        
        return '?' + modsUrlParam.concat(argsUrlParam).join('&') 
    }
    updateBlock() {
        if (this.loadBlockTimeout === 0) {
            this.loadBlockTimeout = setTimeout(() => this.loadBlock(), 2000)
        }
    }
    loadBlock() {
        axios.get('/api/blocks/' + this.props.name + '/' + this.urlParams())
            .then(res => {
                this.loadBlockTimeout = 0

                const { description, available, args, params, mods, props, pins, files, nets, parts, body_kit, pcb_body_kit } = res.data               

                const modKeys = this.props.mods 
                    ? Object.keys(this.props.mods)
                    : []

                const selectedMods = Object.keys(mods).filter(mod => modKeys.indexOf(mod) !== -1).reduce((selected, type) =>
                    selected.concat(
                        Array.isArray(mods[type])
                            ? mods[type].map((value: string) => type + ':' + value)
                            : [type + ':' + mods[type]]
                    ), [])
                
                this.setState((prevState: IState) => {
                    const elements:any = {}
                    if(prevState.body_kit.length === 0 && body_kit.length) {
                        elements.body_kit = body_kit.map((item:any, index:number) => ({ ...item, description: '', index }))
                    }


                    if(prevState.pcb_body_kit.length === 0 && pcb_body_kit.length) {
                        elements.pcb_body_kit = pcb_body_kit.map((item:any, index:number) => ({ ...item, description: '', index }))
                    }
                   
                    return {
                        description,
                        available, 
                        mods,
                        props,
                        args,
                        params, 
                        nets,
                        pins,
                        parts,
                        files,
                        selectedMods,
                        ...elements,
                        simulationShouldUpdate: true,
                        pcbShouldUpdate: true
                    }
                })
            }).catch(this.catchError)
    }
    catchError = (error: any) => {
        this.loadBlockTimeout = 0

        const url = error.response.config.url
        
        function escapeRegExp(str: string) {
            return str.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
        }
        function replaceAll(str: string, find: string, replace: string) {
            return str.replace(new RegExp(escapeRegExp(find), 'g'), replace);
        }
        const html = replaceAll(error.response.data, '?__debugger__', error.response.config.url + '__debugger__')
        const base = `<base href='${url}'/>`

        
        this.setState({
            modalDebugVisible: true,
            debugUrl: url,
            debug: html + base
        })
    }
    showModal = (name:string) => {
        this.setState({
            [`modal${name}Visible`]: true,
        })
    }
    handleDebugOk = () => {
        this.setState({
            modalDebugVisible: false
        })
    }
   
    
    handleModalCancel = (name: string) => {
        this.setState({
            [`modal${name}Visible`]: false,
            [`editable${name}`]: {}
        })
    }

    
    downloadNetlist = () => {
        const { args, pcb_body_kit } = this.state
        const filename = this.props.name + '.net'

        axios.post('/api/blocks/' + this.props.name + '/netlist/kicad/',
        {
            mods: this.state.mods,
            args: Object.keys(args).reduce((result: { [name:string]: string | number }, arg) => {
                result[arg] = args[arg].value
                
                return result
            }, {}),
            pcb_body_kit
        })
            .then(response => {
                const url = window.URL.createObjectURL(new Blob([response.data]))
                const link = document.createElement('a')
                link.href = url
                link.setAttribute('download', filename)
                document.body.appendChild(link)
                link.click()
            }).catch(this.catchError)
        
    }

    // loadProps = () => {
    //     axios.get('/api/blocks/' + this.props.name + '/part_params/' + this.urlParams())
    //         .then(res => {
    //             const { spice, props } = res.data

    //             this.setState(({ params_description }: IState) => ({
    //                 spiceAttrs: spice,
    //                 params_description: {
    //                     ...params_description,
    //                     ...Object.keys(spice).reduce((spiceDescription: IState['params_description'], param:string) => { 
    //                         spiceDescription[param] = spice[param].description

    //                         return spiceDescription
    //                     }, {})
    //                 },
    //                 props: props
    //             }), this.loadSimulation)
    //         })
    // }
    render() {
        const { props, args, params, pins, body_kit, pcb_body_kit } = this.state
        const { name, mods } = this.props
        const BlockMods:IProps['mods'] = { 
            ...props,
            ...mods
        }

        return (
            <div className={this.props.className || cnBlock()}>
                <Modal
                    title="Debug Console"
                    visible={this.state.modalDebugVisible}
                    onOk={this.handleDebugOk}
                    onCancel={this.handleDebugOk}
                    className={cnBlock('DebugModal')}
               >
                    <IframeContainer content={this.state.debug} url={this.state.debugUrl} />
                </Modal>

                <Row>
                    <Col span={12} className={cnBlock('Title')}>
                        <h1>
                            {insertSpaces(this.props.name || '')}
                        </h1>
                    </Col>

                    <Col span={12} className={cnBlock('Modificator')}>
                        {BlockMods && Object.keys(BlockMods).length
                            ? <TreeSelect
                                showSearch
                                style={{ width: '100%' }}
                                value={this.state.selectedMods}
                                placeholder="Modificators"
                                treeCheckable={true}
                                multiple
                                treeDefaultExpandAll
                                onChange={selectedMods => this.setState({ selectedMods, body_kit: [] }, this.updateBlock)}
                            >
                                {Object.keys(BlockMods).map(type =>
                                    <TreeNode value={type} title={type} key={type}>
                                        {Array.isArray(BlockMods[type]) && BlockMods[type].map(value => 
                                            <TreeNode value={type + ':' + value} title={value} key={type + ':' + value} />
                                        )}
                                    </TreeNode>
                                )}
                            </TreeSelect>
                            : ''}
                    </Col>
                </Row>

                {this.state.activeTab !== 'code'
                    ? <Definition
                        name={name}
                        available={this.state.available}
                        args={args}
                        params={params}
                        mod={this.state.mods}
                        props={props}
                        pins={pins}
                        body_kit={body_kit}
                        pcb_body_kit={pcb_body_kit}
                        activeTab={this.state.activeTab}
                        onChange={(blockDef: any) =>
                            this.setState({ ...blockDef }, () => {
                                this.updateBlock()
                          
                            })
                        }
                    />
                    : ''}
                
            
                <Tabs defaultActiveKey="info" onChange={(key) => this.setState({ activeTab: key }) } className={cnBlock('BlockTabs')}>
                    <TabPane tab="Info" key="info">
                        <Description
                            name={name}
                            description={this.state.description}
                            args={args}
                            mods={this.state.mods}
                        />
   
                     

                        <Divider orientation="left">
                            Schematics
                        </Divider>
                        <Row className={cnBlock('Schematics')}> 
                            <Diagram
                                pins={pins}
                                nets={this.state.nets}
                                load={body_kit.map((block, index) => ({ 
                                    ...block,
                                    name: block.name + '_' + index
                                }))}
                                parts={this.state.parts}
                            />
                        </Row>

                  
                    </TabPane>
                    <TabPane tab="Simulation" key="simulation" className={cnBlock('Simulation')}>
                        <Simulation
                            name={name}
                            description={this.state.description}
                            args={args}
                            mods={this.state.mods}
                            pins={pins}
                            body_kit={body_kit}
                            shouldReload={(callback:any) => {
                                if (name && this.state.activeTab === 'simulation' && this.state.simulationShouldUpdate) {
                                    this.setState({ simulationShouldUpdate: false }, callback)

                                    return true
                                } 

                                return false
                            }}
                        /> 
                    </TabPane>
                    <TabPane tab="PCB" key="pcb" className={cnBlock('PCB')}>
                        <Row className={cnBlock('DownloadNetlist')}>
                            <Button
                                type='primary'
                                onClick={this.downloadNetlist}
                            >
                                Download Netlist
                            </Button>
                        </Row>
                        <PCB
                            name={name}
                            args={args}
                            mods={this.state.mods}
                            pcb_body_kit={pcb_body_kit}
                            activeTab={this.state.activeTab}
                            shouldReload={(callback:any) => {
								console.log('PCB Should reload', this.state.pcbShouldUpdate, this.state)
                                if (name && this.state.activeTab === 'pcb' && this.state.pcbShouldUpdate) {
								console.log('PCB LOADING')
                                    this.setState({ pcbShouldUpdate: false }, callback)

                                    return true
                                } 

                                return false
                            }}
                        />
                        
                    </TabPane>
                    <TabPane tab="Code" key="code" className={cnBlock('Code')}>
                        <Tabs type="card">
                        {this.state.files.map(file => 
                            <TabPane tab={file.replace('blocks/' + this.props.name + '/', '')} key={file}>
                                <Code
                                    file={file}
                                    onChange={(value: string) =>
                                        axios.post('/api/files/', { name: file.replace('blocks/' + this.props.name + '/', ''), content: value })}
                                />
                            </TabPane>
                        )}
                        </Tabs>
                        
                    </TabPane>
                </Tabs>
            </div>
        )
    }
}


/**
 * React component which renders the given content into an iframe.
 * Additionally an array of stylesheet urls can be passed. They will 
 * also be loaded into the iframe.
 */

type IframeProps = {
    content: string,
    url?: string
}
export class IframeContainer extends React.Component<IframeProps, {}> {
     /**
     * Called after mounting the component. Triggers initial update of
     * the iframe
     */
    iframeRef = React.createRef<HTMLIFrameElement>()

    componentDidMount() {
        this._updateIframe();
    }

    // /**
    //  * Called each time the props changes. Triggers an update of the iframe to
    //  * pass the new content
    //  */
    componentDidUpdate() {
        this._updateIframe();
    }

    /**
     * Updates the iframes content and inserts stylesheets.
     * TODO: Currently stylesheets are just added for proof of concept. Implement
     * and algorithm which updates the stylesheets properly.
     */
    _updateIframe() {
        const iframe = this.iframeRef.current
        if (iframe && iframe.contentWindow) {
            const document = iframe.contentWindow.document 
            if (document) {
                if (this.props.url) {
                    iframe.src = this.props.url
                    // iframe.contentWindow.history.replaceState('', '', this.props.url)
                } else {
                    document.open()
                    document.write(this.props.content)
                    document.close()
                }
            }
        }
    }

    /**
     * This component renders just and iframe
     */
    render() {
        return <iframe className={cnBlock('DebugIframe')} ref={this.iframeRef}/>
    }

}

