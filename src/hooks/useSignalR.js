/**
 * src/hooks/useSignalR.js — Azure SignalR real-time forbindelse
 *
 * Brug:
 *   const { connected } = useSignalR({
 *     onNyBesked:      (threadId, msg) => { ... },
 *     onNyNotifikation: (notif) => { ... },
 *     onNyAftale:       (aftale) => { ... },
 *   });
 *
 * Kræver @microsoft/signalr npm-pakken (tilføj til package.json i FASE 2).
 */

import { useEffect, useRef, useState } from 'react';

const API_URL = import.meta?.env?.VITE_API_URL || 'http://localhost:8000';

export function useSignalR({ onNyBesked, onNyNotifikation, onNyAftale } = {}) {
  const connRef     = useRef(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // FASE 2: Uncomment når @microsoft/signalr er installeret
    // import('@microsoft/signalr').then(({ HubConnectionBuilder, LogLevel }) => {
    //   const conn = new HubConnectionBuilder()
    //     .withUrl(`${API_URL}/hubs/brobygger`, {
    //       accessTokenFactory: () => localStorage.getItem('sos_token') || '',
    //     })
    //     .withAutomaticReconnect()
    //     .configureLogging(LogLevel.Warning)
    //     .build();
    //
    //   if (onNyBesked)       conn.on('nyBesked',      onNyBesked);
    //   if (onNyNotifikation) conn.on('nyNotifikation', onNyNotifikation);
    //   if (onNyAftale)       conn.on('nyAftale',       onNyAftale);
    //
    //   conn.start()
    //     .then(() => setConnected(true))
    //     .catch(err => console.warn('[SignalR]', err));
    //
    //   connRef.current = conn;
    // });
    //
    // return () => connRef.current?.stop();

    // FASE 1: BroadcastChannel fallback (samme enhed)
    const bc = new BroadcastChannel('sos_live_chat');
    bc.onmessage = (ev) => {
      if (onNyBesked && ev.data?.type === 'nyBesked') {
        onNyBesked(ev.data.threadId, ev.data.msg);
      }
    };
    return () => bc.close();
  }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  return { connected };
}
