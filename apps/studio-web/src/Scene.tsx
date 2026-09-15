import { Suspense, useEffect, useMemo, useRef } from 'react'
import { Canvas, useFrame, useLoader, useThree } from '@react-three/fiber'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import type { OrbitControls as OrbitControlsType } from 'three/addons/controls/OrbitControls.js'
import type { Design, ProductType } from './types'

function CameraControls() {
  const { camera, gl } = useThree()
  const controls = useRef<OrbitControlsType | null>(null)
  useEffect(() => {
    controls.current = new OrbitControls(camera, gl.domElement)
    controls.current.enablePan = false
    controls.current.minDistance = 5
    controls.current.maxDistance = 12
    controls.current.enableDamping = true
    return () => controls.current?.dispose()
  }, [camera, gl])
  useFrame(() => controls.current?.update())
  return null
}

function Garment() {
  return <group rotation={[0.1, 0.25, 0]}>
    <mesh castShadow><boxGeometry args={[3.2, 3.9, 0.42]} /><meshStandardMaterial color="#d7c9ae" roughness={0.85} /></mesh>
    <mesh position={[-2.05, 0.9, 0]} rotation={[0, 0, -0.35]}><boxGeometry args={[1.55, 1.15, 0.38]} /><meshStandardMaterial color="#d7c9ae" /></mesh>
    <mesh position={[2.05, 0.9, 0]} rotation={[0, 0, 0.35]}><boxGeometry args={[1.55, 1.15, 0.38]} /><meshStandardMaterial color="#d7c9ae" /></mesh>
    <mesh position={[0, 1.55, 0.23]}><torusGeometry args={[0.67, 0.16, 12, 28]} /><meshStandardMaterial color="#101613" /></mesh>
  </group>
}

function Bag() {
  return <group rotation={[0.1, -0.35, 0]}>
    <mesh castShadow><boxGeometry args={[4.8, 3.4, 0.9]} /><meshStandardMaterial color="#253d38" roughness={0.65} /></mesh>
    <mesh position={[0, 0.55, 0.5]}><boxGeometry args={[3.65, 1.55, 0.15]} /><meshStandardMaterial color="#d6a45a" roughness={0.75} /></mesh>
    <mesh position={[0, 2.05, 0]} rotation={[0, 0, 0]}><torusGeometry args={[1.32, 0.15, 10, 24, Math.PI]} /><meshStandardMaterial color="#d6a45a" /></mesh>
  </group>
}

function ExportedMockup({ url }: { url: string }) {
  const gltf = useLoader(GLTFLoader, url)
  const scene = useMemo(() => gltf.scene.clone(true), [gltf.scene])
  useEffect(() => {
    scene.traverse(object => {
      object.castShadow = true
      object.receiveShadow = true
    })
  }, [scene])
  return <primitive object={scene} scale={6} rotation={[0.12, -0.45, 0]} />
}

export default function DesignScene({ design, mockupUrl, productType }: { design: Design | null; mockupUrl: string | null; productType: ProductType }) {
  return <Canvas shadows camera={{ position: [0, 1.2, 9], fov: 44 }} dpr={[1, 1.5]}>
    <color attach="background" args={['#c7bca7']} />
    <ambientLight intensity={1.2} />
    <directionalLight position={[5, 7, 4]} intensity={2.4} castShadow />
    <directionalLight position={[-4, 3, -2]} intensity={0.7} />
    <group position={[0, -0.3, 0]}>{mockupUrl ? <Suspense fallback={null}><ExportedMockup url={mockupUrl} /></Suspense> : productType === 'laptop_bag' ? <Bag /> : <Garment />}</group>
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -2.4, 0]} receiveShadow><planeGeometry args={[20, 20]} /><meshStandardMaterial color="#b5aa97" roughness={1} /></mesh>
    <CameraControls />
  </Canvas>
}
