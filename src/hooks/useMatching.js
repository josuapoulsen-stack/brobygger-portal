/**
 * src/hooks/useMatching.js — Matching-hook til rådgiver/admin
 *
 * Henter match-forslag fra backend og håndterer bekræftelse.
 *
 * FASE 1: USE_BACKEND=false → returnerer tom liste + log-besked
 * FASE 2: Kalder GET /v1/matching/suggest/{menneskeId}
 *         og POST /v1/matching/confirm
 *
 * Brug:
 *   const { forslag, loading, error, hentForslag, bekræftMatch } = useMatching();
 *
 *   // Hent forslag til et bestemt menneske
 *   await hentForslag(menneskeId);
 *
 *   // Bekræft valgt brobygger
 *   const aftale = await bekræftMatch({ menneskeId, brobyggerId, dato, start, end });
 */

import { useState, useCallback } from 'react';
import { Matching } from '../api/index';

export function useMatching() {
  const [forslag,    setForslag]    = useState([]);
  const [loading,    setLoading]    = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error,      setError]      = useState(null);

  /**
   * Hent match-forslag til et menneske.
   * @param {string} menneskeId
   */
  const hentForslag = useCallback(async (menneskeId) => {
    if (!menneskeId) return;
    setLoading(true);
    setError(null);
    setForslag([]);
    try {
      const data = await Matching.suggest(menneskeId);
      setForslag(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e?.message ?? 'Kunne ikke hente matchforslag');
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Bekræft et match og opret aftale.
   *
   * @param {{ menneskeId: string, brobyggerId: string, dato?: string, start?: string, end?: string }} payload
   * @returns {Object|null}  Den oprettede aftale eller null ved fejl
   */
  const bekræftMatch = useCallback(async (payload) => {
    setConfirming(true);
    setError(null);
    try {
      const aftale = await Matching.confirm(payload);
      // Ryd forslagslisten efter bekræftelse
      setForslag([]);
      return aftale;
    } catch (e) {
      setError(e?.message ?? 'Kunne ikke bekræfte match');
      return null;
    } finally {
      setConfirming(false);
    }
  }, []);

  /** Nulstil state (f.eks. ved lukning af modal). */
  const reset = useCallback(() => {
    setForslag([]);
    setError(null);
  }, []);

  return {
    forslag,
    loading,
    confirming,
    error,
    hentForslag,
    bekræftMatch,
    reset,
  };
}

export default useMatching;
