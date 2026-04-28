/**
 * src/hooks/usePush.js — Web Push subscription management
 *
 * Brug:
 *   const { subscribed, subscribe, unsubscribe } = usePush();
 *
 * Registrerer brugerens enhed til push-notifikationer og
 * gemmer subscription på backend via POST /v1/push/subscribe.
 */

import { useState, useEffect } from 'react';
import { Notifikationer } from '../api/index';

const VAPID_PUBLIC_KEY = import.meta?.env?.VITE_VAPID_PUBLIC_KEY || '';

function urlBase64ToUint8Array(base64String) {
  const padding  = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64   = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData  = atob(base64);
  return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)));
}

export function usePush() {
  const [subscribed, setSubscribed] = useState(false);
  const [supported,  setSupported]  = useState(false);

  useEffect(() => {
    setSupported('serviceWorker' in navigator && 'PushManager' in window);
  }, []);

  const subscribe = async () => {
    if (!supported || !VAPID_PUBLIC_KEY) return false;
    try {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') return false;

      const reg  = await navigator.serviceWorker.ready;
      const sub  = await reg.pushManager.subscribe({
        userVisibleOnly:      true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      });

      // Gem subscription på backend
      const subJson = sub.toJSON();
      await Notifikationer.subscribeTouch({
        endpoint: subJson.endpoint,
        keys:     subJson.keys,
      });

      setSubscribed(true);
      localStorage.setItem('sos_push_subscribed', '1');
      return true;
    } catch (e) {
      console.warn('[Push] Fejl ved subscribe:', e);
      return false;
    }
  };

  const unsubscribe = async () => {
    const reg = await navigator.serviceWorker.ready;
    const sub = await reg.pushManager.getSubscription();
    if (sub) await sub.unsubscribe();
    setSubscribed(false);
    localStorage.removeItem('sos_push_subscribed');
  };

  return { subscribed, supported, subscribe, unsubscribe };
}
