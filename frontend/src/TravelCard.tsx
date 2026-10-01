import { useState, type PointerEvent } from 'react'

export default function TravelCard() {
  const [tilt, setTilt] = useState({ x: 0, y: 0 })

  function move(event: PointerEvent<HTMLDivElement>) {
    const bounds = event.currentTarget.getBoundingClientRect()
    setTilt({
      x: ((event.clientY - bounds.top) / bounds.height - .5) * -10,
      y: ((event.clientX - bounds.left) / bounds.width - .5) * 12,
    })
  }

  return (
    <div
      className="travelCardStage"
      onPointerMove={move}
      onPointerLeave={() => setTilt({ x: 0, y: 0 })}
    >
      <div className="travelCard" style={{ transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)` }}>
        <span className="cardGlow" />
        <p>TRIPZY / LIVE PLAN</p>
        <strong>Anywhere<br />feels closer.</strong>
        <div className="cardRoute"><i /> <em>GO</em> <i /></div>
        <small>Places · weather · route</small>
      </div>
    </div>
  )
}
