import { useState, useEffect } from 'react';
export function useAsync(asyncFunction, immediate = true) {
    const [state, setState] = useState({
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
        }
        catch (error) {
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
export function usePoll(asyncFunction, interval = 5000, shouldPoll = true) {
    const [state, setState] = useState({
        data: null,
        loading: true,
        error: null,
    });
    useEffect(() => {
        if (!shouldPoll)
            return;
        const execute = async () => {
            try {
                const response = await asyncFunction();
                setState({ data: response, loading: false, error: null });
            }
            catch (error) {
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
