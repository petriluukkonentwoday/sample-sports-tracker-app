import { useState, useCallback, useRef, useEffect } from 'react';

export interface UseTimerResult {
  seconds: number;
  isRunning: boolean;
  start: () => void;
  pause: () => void;
  resume: () => void;
  stop: () => number;
  reset: () => void;
}

export function useTimer(): UseTimerResult {
  const [seconds, setSeconds] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  
  const intervalRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const accumulatedRef = useRef<number>(0);

  const clearTimer = useCallback(() => {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const start = useCallback(() => {
    setIsRunning(true);
    accumulatedRef.current = 0;
    startTimeRef.current = Date.now();
    
    intervalRef.current = window.setInterval(() => {
      if (startTimeRef.current !== null) {
        const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
        setSeconds(accumulatedRef.current + elapsed);
      }
    }, 1000);
  }, []);

  const pause = useCallback(() => {
    if (startTimeRef.current !== null) {
      accumulatedRef.current += Math.floor((Date.now() - startTimeRef.current) / 1000);
    }
    clearTimer();
    setIsRunning(false);
    startTimeRef.current = null;
  }, [clearTimer]);

  const resume = useCallback(() => {
    setIsRunning(true);
    startTimeRef.current = Date.now();
    
    intervalRef.current = window.setInterval(() => {
      if (startTimeRef.current !== null) {
        const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
        setSeconds(accumulatedRef.current + elapsed);
      }
    }, 1000);
  }, []);

  const stop = useCallback((): number => {
    let finalSeconds = seconds;
    if (startTimeRef.current !== null) {
      finalSeconds = accumulatedRef.current + Math.floor((Date.now() - startTimeRef.current) / 1000);
    }
    clearTimer();
    setIsRunning(false);
    startTimeRef.current = null;
    return finalSeconds;
  }, [seconds, clearTimer]);

  const reset = useCallback(() => {
    clearTimer();
    setIsRunning(false);
    setSeconds(0);
    accumulatedRef.current = 0;
    startTimeRef.current = null;
  }, [clearTimer]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearTimer();
    };
  }, [clearTimer]);

  return {
    seconds,
    isRunning,
    start,
    pause,
    resume,
    stop,
    reset,
  };
}
