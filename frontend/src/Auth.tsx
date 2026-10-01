import { useState, type FormEvent } from 'react'
import { supabase } from './lib/supabase'

type Props = {
  onAuth: () => void
}

export default function Auth({ onAuth }: Props) {
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')

    try {
      if (!supabase) {
        throw new Error('Supabase is not configured yet. Add the VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY values to frontend/.env.')
      }

      if (mode === 'login') {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        })

        if (error) {
          throw error
        }

        onAuth()
      } else {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        })

        if (error) {
          throw error
        }

        if (data.session) {
          onAuth()
        } else {
          setMessage(
            'Account created. Check your email to confirm your account.'
          )
        }
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Authentication failed'
      )
    } finally {
      setLoading(false)
    }
  }

  function switchMode() {
    setMode(mode === 'login' ? 'signup' : 'login')
    setError('')
    setMessage('')
  }

  return (
    <main className="authPage">
      <div className="authCard">
        <div className="authLogo">✦ tripzy</div>

        <p className="eyebrow">
          {mode === 'login'
            ? 'WELCOME BACK'
            : 'START YOUR JOURNEY'}
        </p>

        <h1>
          {mode === 'login' ? (
            <>
              Welcome <i>back.</i>
            </>
          ) : (
            <>
              Plan something <i>beautiful.</i>
            </>
          )}
        </h1>

        <p className="authSubtitle">
          {mode === 'login'
            ? 'Your trips are waiting for you.'
            : 'Create an account and keep your trips with you.'}
        </p>

        <form onSubmit={submit} className="authForm">
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete={
                mode === 'login'
                  ? 'current-password'
                  : 'new-password'
              }
              minLength={6}
              required
            />
          </label>

          {error && <p className="error">{error}</p>}

          {message && (
            <p className="authMessage">{message}</p>
          )}

          <button
            type="submit"
            className="planButton"
            disabled={loading}
          >
            {loading
              ? 'Please wait…'
              : mode === 'login'
                ? 'Log in'
                : 'Create account'}

            <b>→</b>
          </button>
        </form>

        <button
          type="button"
          className="authSwitch"
          onClick={switchMode}
        >
          {mode === 'login'
            ? "Don't have an account? Sign up"
            : 'Already have an account? Log in'}
        </button>
      </div>
    </main>
  )
}
