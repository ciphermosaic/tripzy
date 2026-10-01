import { useEffect, useState, type SyntheticEvent } from 'react'
import { createRoot } from 'react-dom/client'
import GlobeScene from './GlobeScene'
import Auth from './Auth'
import TripMap from './TripMap'
import TravelCard from './TravelCard'
import { supabase } from './lib/supabase'
import './styles.css'

type Place = {
  name: string
  category: string
  lat: number
  lon: number
}

type Trip = {
  destination: string
  center: Place
  days: number
  travelers: number
  weather: {
    temperature_c: number | null
    condition: string
    rain_probability: number | null
    tip: string
  }
  budget: {
    total: number
    accommodation: number
    food: number
    transport: number
    activities: number
    miscellaneous: number
    note: string
  }
  itinerary: {
    day: number
    title: string
    summary: string
    items: {
      time: string
      title: string
      kind: string
      description: string
      duration: string
      estimated_cost: number
      place?: Place
    }[]
  }[]
  places: Place[]
  route: number[][]
  notices: string[]
}

const api = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const format = (n: number) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(n)

function App() {
  const [session, setSession] = useState<any>(null)
  const [authLoading, setAuthLoading] = useState(true)

  const [prompt, setPrompt] = useState(
    'Plan a 4 day trip to Goa for two friends. Budget ₹15,000 each. We love beaches, food and sunsets.'
  )

  const [trip, setTrip] = useState<Trip | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [openDay, setOpenDay] = useState(1)

  const [message, setMessage] = useState('')
  const [chat, setChat] = useState<{ from: string; text: string }[]>([
    {
      from: 'ai',
      text: 'Tell me the feeling you want from your trip, and I’ll shape the details around it.',
    },
  ])
  const [sending, setSending] = useState(false)

  useEffect(() => {
    if (!supabase) {
      setSession({ preview: true })
      setAuthLoading(false)
      return
    }

    let mounted = true

    async function loadSession() {
      if (!supabase) {
        throw new Error('Supabase is not configured')
      }

      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (mounted) {
        setSession(session)
        setAuthLoading(false)
      }
    }

    loadSession()

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (mounted) {
        setSession(session)
        setAuthLoading(false)
      }
    })

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [])

  async function plan(e: SyntheticEvent<HTMLFormElement>) {
    e.preventDefault()

    setLoading(true)
    setError('')

    try {
      if (!supabase) {
        throw new Error('Connect Supabase to create and save trips.')
      }

      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        throw new Error('Your session has expired. Please log in again.')
      }

      const r = await fetch(`${api}/api/trips/plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          request: prompt,
          travelers: 2,
        }),
      })

    const data = await r.json()

      if (!r.ok) {
        throw new Error(data.detail || 'Could not plan this trip')
      }

      setTrip(data)
      setOpenDay(1)

      setChat([
        {
          from: 'ai',
          text: `Your ${data.days}-day ${data.destination} escape is ready. Want it slower, cheaper, or more food-focused?`,
        },
      ])
    } catch (e) {
      setError(
        e instanceof Error ? e.message : 'Something went wrong'
      )
    } finally {
      setLoading(false)
    }
  }

  async function send(e: SyntheticEvent<HTMLFormElement>) {
    e.preventDefault()

    if (!message.trim() || !trip) return

    const text = message

    setMessage('')
    setChat((c) => [...c, { from: 'you', text }])
    setSending(true)

    try {
      if (!supabase) {
        throw new Error('Connect Supabase to chat about this trip.')
      }

      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        throw new Error('Your session has expired. Please log in again.')
      }

      const r = await fetch(`${api}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          message: text,
          trip,
        }),
      })

      const data = await r.json()

      setChat((c) => [
        ...c,
        {
          from: 'ai',
          text: data.message,
        },
      ])

      if (data.trip) {
        setTrip(data.trip)
      }
    } catch {
      setChat((c) => [
        ...c,
        {
          from: 'ai',
          text: 'I lost the trail for a moment. Please try that again.',
        },
      ])
    } finally {
      setSending(false)
    }
  }

  if (authLoading) {
    return (
      <main className="authPage">
        <div className="authCard">
          <div className="authLogo">✦ tripzy</div>
          <p className="authSubtitle">Loading your journey...</p>
        </div>
      </main>
    )
  }

  if (!session) {
    return <Auth onAuth={() => {}} />
  }

  return (
    <main>
      <nav>
        <a className="brand" href="#top">
          <span>✦</span> tripzy
        </a>

        <div className="navlinks">
          <a href="#planner">Plan a trip</a>
          <a href="#how">How it works</a>
        </div>

        <div className="navActions">
          <button
            className="smallButton"
            onClick={() =>
              document
                .querySelector('#planner')
                ?.scrollIntoView({ behavior: 'smooth' })
            }
          >
            Start planning <b>↗</b>
          </button>

          <button
            className="logoutButton"
            onClick={() => supabase?.auth.signOut()}
          >
            Log out
          </button>
        </div>
      </nav>

      <section className="hero" id="top">
        <div className="orb orb1"></div>
        <div className="orb orb2"></div>

        <p className="eyebrow">YOUR TIME, WELL SPENT</p>

        <h1>
          Find the <i>feeling.</i>
          <br />
          We’ll find the way.
        </h1>

        <p className="lede">
          A thoughtful travel companion that turns a vague urge to go
          into a route worth remembering.
        </p>

        <div className="heroStats">
          <span>◎ Live local data</span>
          <span>◌ Built around your pace</span>
          <span>↗ ₹0 to start</span>
        </div>

        <TravelCard />
        <GlobeScene />
      </section>

      <section className="planner" id="planner">
        <div>
          <p className="eyebrow">THE FIRST STEP</p>

          <h2>
            Where does your
            <br />
            <i>mind wander?</i>
          </h2>

          <p>
            Give us the rough edges. We will make them a plan with local
            places, weather-aware suggestions, and room to breathe.
          </p>
        </div>

        <form onSubmit={plan} className="planCard">
          <label>
            Your trip, in your words

            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A quiet 3 days in…"
            />
          </label>

          <div className="examples">
            <button
              type="button"
              onClick={() =>
                setPrompt(
                  'Plan a relaxed 3 day trip to Jaipur for a couple. We like architecture and food.'
                )
              }
            >
              Jaipur · culture
            </button>

            <button
              type="button"
              onClick={() =>
                setPrompt(
                  'Plan a 4 day budget trip to Munnar. I like nature and slow mornings.'
                )
              }
            >
              Munnar · slow
            </button>
          </div>

          <button className="planButton" disabled={loading}>
            {loading ? 'Mapping your escape…' : 'Create my trip'} <b>→</b>
          </button>

          {error && <p className="error">{error}</p>}
        </form>
      </section>

      <section className="how" id="how">
        <p className="eyebrow">LESS TABS, MORE ANTICIPATION</p>

        <div className="steps">
          <article>
            <em>01</em>
            <h3>Say the thing</h3>
            <p>
              Share a city, a budget, or simply the kind of break you
              need.
            </p>
          </article>

          <article>
            <em>02</em>
            <h3>See the shape</h3>
            <p>
              We pair live place and weather signals with an unhurried
              day-by-day route.
            </p>
          </article>

          <article>
            <em>03</em>
            <h3>Make it yours</h3>
            <p>
              Keep talking. Ask for less travel, more food, a rainy-day
              switch, or a smaller spend.
            </p>
          </article>
        </div>
      </section>

      {trip && (
        <section className="result">
          <header>
            <div>
              <p className="eyebrow">YOUR ESCAPE, SKETCHED OUT</p>

              <h2>
                {trip.destination}
                <span> · {trip.days} days</span>
              </h2>
            </div>

            <div className="weather">
              ☀
              <div>
                <b>{trip.weather.temperature_c ?? '—'}°</b>
                <small>{trip.weather.condition}</small>
              </div>
            </div>
          </header>

          <p className="notice">{trip.weather.tip}</p>

          <div className="resultGrid">
            <div className="itinerary">
              <div className="days">
                {trip.itinerary.map((day) => (
                  <button
                    className={openDay === day.day ? 'active' : ''}
                    onClick={() => setOpenDay(day.day)}
                    key={day.day}
                  >
                    Day {day.day}
                  </button>
                ))}
              </div>

              {trip.itinerary
                .filter((d) => d.day === openDay)
                .map((day) => (
                  <div key={day.day}>
                    <h3>{day.title}</h3>

                    <p className="summary">{day.summary}</p>

                    {day.items.map((item) => (
                      <article
                        className="item"
                        key={item.time + item.title}
                      >
                        <time>{item.time}</time>

                        <div>
                          <b>{item.title}</b>
                          <p>{item.description}</p>

                          <small>
                            {item.duration}
                            {item.estimated_cost > 0 &&
                              ` · ${format(item.estimated_cost)}`}
                          </small>
                        </div>
                      </article>
                    ))}
                  </div>
                ))}
            </div>

            <aside>
              <TripMap
                destination={trip.destination}
                center={trip.center}
                places={trip.places}
                route={trip.route}
                activePlaces={
                  trip.itinerary
                    .find((day) => day.day === openDay)
                    ?.items.flatMap((item) => (item.place ? [item.place] : [])) ?? []
                }
              />

              <div className="budget">
                <p className="eyebrow">ESTIMATED PER PERSON</p>

                <b>{format(trip.budget.total)}</b>

                <div className="bar">
                  <i style={{ width: '38%' }} />
                  <i style={{ width: '22%' }} />
                  <i style={{ width: '16%' }} />
                  <i style={{ width: '14%' }} />
                </div>

                <small>Stay · Food · Transport · Activities</small>

                <p>{trip.budget.note}</p>
              </div>
            </aside>
          </div>
        </section>
      )}

      {trip && (
        <section className="chat">
          <div>
            <p className="eyebrow">YOUR TRIP, STILL IN MOTION</p>

            <h2>
              Ask the plan
              <br />
              anything.
            </h2>

            <p>
              “Make day two more relaxed.”
              <br />
              “What should I pack?”
              <br />
              “Can we do this for less?”
            </p>
          </div>

          <div className="chatBox">
            <div className="messages">
              {chat.map((m, i) => (
                <p key={i} className={m.from}>
                  <span>{m.from === 'ai' ? 'Tripzy' : 'You'}</span>
                  {m.text}
                </p>
              ))}

              {sending && (
                <p className="ai">
                  <span>Tripzy</span>
                  Thinking…
                </p>
              )}
            </div>

            <form onSubmit={send}>
              <input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Change the plan…"
              />

              <button aria-label="Send">↑</button>
            </form>
          </div>
        </section>
      )}

      <footer>
        <a className="brand" href="#top">
          <span>✦</span> tripzy
        </a>

        <p>
          Designed for the delicious possibility of going somewhere.
        </p>

        <p>Live-data MVP · Plan gently.</p>
      </footer>
    </main>
  )
}

createRoot(document.getElementById('root')!).render(<App />)
