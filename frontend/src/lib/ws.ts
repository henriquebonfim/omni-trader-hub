import { useEffect, useRef, useState } from 'react'
import type { CycleMessage } from './api'

type WsStatus = 'connecting' | 'open' | 'closed' | 'error'

export function useLiveFeed() {
  const [message, setMessage] = useState<CycleMessage | null>(null)
  const [status, setStatus] = useState<WsStatus>('connecting')
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    let cancelled = false

    const connect = () => {
      if (cancelled) return

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      const ws = new WebSocket(`${protocol}//${host}/ws/live`)
      wsRef.current = ws

      ws.onopen = () => {
        if (!cancelled) setStatus('open')
      }

      ws.onmessage = (evt) => {
        if (!cancelled) {
          try {
            const data = JSON.parse(evt.data) as CycleMessage
            setMessage(data)
          } catch {
            // ignore malformed messages
          }
        }
      }

      ws.onclose = () => {
        if (!cancelled) {
          setStatus('closed')
          reconnectTimer.current = setTimeout(() => {
            if (!cancelled) connect()
          }, 3000)
        }
      }

      ws.onerror = () => {
        if (!cancelled) setStatus('error')
        ws.close()
      }
    }

    connect()

    return () => {
      cancelled = true
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [])

  return { message, status }
}
