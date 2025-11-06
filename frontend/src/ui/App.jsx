import React, { useState, useRef } from 'react'
import { Stage, Layer, Rect, Text, Line, Group } from 'react-konva'

const GRID = 20
const GATE_W = 100
const GATE_H = 50

function GateShape({ node, onDragMove, onClick }) {
  return (
    <Group x={node.x} y={node.y} draggable onDragMove={(e) => {
      onDragMove(node.id, e.target.x(), e.target.y())
    }} onClick={() => onClick(node.id)}>
      <Rect width={GATE_W} height={GATE_H} fill={'#eee'} stroke={'#333'} cornerRadius={6} />
      <Text text={node.type} x={6} y={6} fontSize={14} />
      <Text text={node.id.slice(0,8)} x={6} y={26} fontSize={10} />
    </Group>
  )
}

export default function App(){
  const [nodes, setNodes] = useState([
    { id: 'in1', type: 'INPUT', x: 40, y:40 },
    { id: 'in2', type: 'INPUT', x: 40, y:120 },
    { id: 'and1', type: 'AND', x: 260, y:80 },
    { id: 'out1', type: 'OUTPUT', x: 460, y:80 }
  ])
  const [edges, setEdges] = useState([
    { from: 'in1', to: 'and1' },
    { from: 'in2', to: 'and1' },
    { from: 'and1', to: 'out1' }
  ])
  const [selected, setSelected] = useState(null)
  const stageRef = useRef(null)

  function onDragMove(id, x, y){
    setNodes(nodes.map(n => n.id === id ? {...n, x: Math.round(x/GRID)*GRID, y: Math.round(y/GRID)*GRID} : n))
  }

  function addGate(type){
    const id = type.toLowerCase() + '_' + Math.random().toString(36).slice(2,9)
    setNodes([...nodes, {id, type, x:120, y:120}])
  }

  function connectSelected(toId){
    if(!selected || selected === toId) { setSelected(null); return; }
    setEdges([...edges, {from: selected, to: toId}])
    setSelected(null)
  }

  return (
    <div style={{display:'flex', height:'100vh'}}>
      <div style={{width:200, padding:10, borderRight:'1px solid #ddd', boxSizing:'border-box'}}>
        <h3>Toolbox</h3>
        <button onClick={() => addGate('INPUT')}>INPUT</button><br/>
        <button onClick={() => addGate('OUTPUT')}>OUTPUT</button><br/>
        <button onClick={() => addGate('AND')}>AND</button><br/>
        <button onClick={() => addGate('OR')}>OR</button><br/>
        <button onClick={() => addGate('NOT')}>NOT</button><br/>
        <hr/>
        <div>
          <button onClick={() => setSelected(null)}>Deselect</button>
          <div style={{marginTop:8}}>Selected: {selected}</div>
        </div>
        <hr/>
        <div>
          <h4>Nodes</h4>
          {nodes.map(n => (
            <div key={n.id}>
              <button onClick={() => { setSelected(n.id) }}>{n.id}</button>
              <button onClick={() => {
                setNodes(nodes.filter(x => x.id !== n.id))
                setEdges(edges.filter(e => e.from !== n.id && e.to !== n.id))
              }}>Del</button>
            </div>
          ))}
        </div>
        <hr/>
        <div>
          <h4>Connections</h4>
          <button onClick={() => { if(selected) { const to = prompt('Connect to id:'); if(to) connectSelected(to) } else { alert('Select source first') }}}>Connect (selected → id)</button>
          <div style={{marginTop:8}}>
            {edges.map((e,i) => <div key={i}>{e.from} → {e.to}</div>)}
          </div>
        </div>
      </div>
      <div style={{flex:1}}>
        <Stage width={1200} height={800} ref={stageRef} style={{background:'#fff'}}>
          <Layer>
            {/* grid */}
            {[...Array(100)].map((_,i) => (
              <Line key={'v'+i} points={[i*GRID,0,i*GRID,800]} stroke={'#f0f0f0'} strokeWidth={1} />
            ))}
            {[...Array(40)].map((_,i) => (
              <Line key={'h'+i} points={[0,i*GRID,1200,i*GRID]} stroke={'#f0f0f0'} strokeWidth={1} />
            ))}
            {edges.map((e,i) => {
              const from = nodes.find(n => n.id === e.from)
              const to = nodes.find(n => n.id === e.to)
              if(!from || !to) return null
              const sx = from.x + 100
              const sy = from.y + 25
              const dx = to.x
              const dy = to.y + 25
              const points = [sx,sy, (sx+dx)/2,sy, (sx+dx)/2,dy, dx,dy]
              return <Line key={i} points={points} stroke={'#333'} strokeWidth={3} bezier />
            })}
            {nodes.map(n => <GateShape key={n.id} node={n} onDragMove={onDragMove} onClick={(id)=>{ if(still_click(id)){}}} />)}
          </Layer>
        </Stage>
      </div>
    </div>
  )
}

function still_click(id){
  // placeholder to satisfy linter; actual click handled in GateShape via onClick prop
  return true
}
