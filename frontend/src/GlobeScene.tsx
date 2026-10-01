import { Canvas, useFrame } from '@react-three/fiber'
import { Float, Line, Stars } from '@react-three/drei'
import { useMemo, useRef } from 'react'
import * as THREE from 'three'

function Route({ start, end }: { start: THREE.Vector3; end: THREE.Vector3 }) {
  const points = useMemo(() => {
    const middle = start.clone().add(end).multiplyScalar(.5).normalize().multiplyScalar(1.42)
    return new THREE.QuadraticBezierCurve3(start, middle, end).getPoints(34)
  }, [start, end])
  return <Line points={points} color="#f5b34d" lineWidth={1.3} transparent opacity={.9} />
}

function World() {
  const group = useRef<THREE.Group>(null)
  useFrame((_, delta) => { if (group.current) group.current.rotation.y += delta * .09 })
  const points = useMemo(() => [new THREE.Vector3(.31,.58,.78),new THREE.Vector3(-.7,.2,.67),new THREE.Vector3(.62,-.47,.6)].map(point => point.normalize().multiplyScalar(1.025)), [])
  return <group ref={group} rotation={[.18,-.65,0]}><mesh><sphereGeometry args={[1,64,64]}/><meshStandardMaterial color="#17606a" roughness={.64} metalness={.08}/></mesh><mesh scale={1.008}><sphereGeometry args={[1,32,32]}/><meshBasicMaterial color="#8bd0c1" wireframe transparent opacity={.22}/></mesh>{points.map((point,index)=><group key={index} position={point}><mesh><sphereGeometry args={[.035,16,16]}/><meshBasicMaterial color="#f4b54b"/></mesh><pointLight color="#f4b54b" intensity={2} distance={.5}/></group>)}<Route start={points[0]} end={points[1]}/><Route start={points[1]} end={points[2]}/></group>
}

export default function GlobeScene(){return <div className="globeCanvas" aria-label="Animated globe with travel routes"><Canvas camera={{position:[0,0,3.1],fov:40}} dpr={[1,1.5]} gl={{antialias:true,alpha:true}}><ambientLight intensity={1.1}/><directionalLight position={[3,2,4]} intensity={2.6} color="#d9f6de"/><Float speed={1.5} rotationIntensity={.12} floatIntensity={.3}><World/></Float><Stars radius={12} depth={18} count={280} factor={2} fade speed={.35}/></Canvas></div>}
