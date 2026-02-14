import { useState, useEffect } from 'react';

export interface UseAsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useAsync<T>(
  asyncFunction: () => Promise<T>,
  immediate = true
): UseAsyncState<T> {
  const [state, setState] = useState<UseAsyncState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const execute = async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const response = await asyncFunction();
      setState({ data: response, loading: false, error: null });
      return response;
    } catch (error) {
      setState({ data: null, loading: false, error: error instanceof Error ? error : new Error(String(error)) });
      throw error;
    }
  };

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, []);

  return state;
}

export function usePoll<T>(
  asyncFunction: () => Promise<T>,
  interval = 5000,
  shouldPoll = true
): UseAsyncState<T> {
  const [state, setState] = useState<UseAsyncState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    if (!shouldPoll) return;

    const execute = async () => {
      try {
        const response = await asyncFunction();
        setState({ data: response, loading: false, error: null });
      } catch (error) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: error instanceof Error ? error : new Error(String(error)),
        }));
      }
    };

    execute();
    const timer = setInterval(execute, interval);
    return () => clearInterval(timer);
  }, [shouldPoll, interval]);

  return state;
}
