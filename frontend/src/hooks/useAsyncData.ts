import { useState, useCallback, useEffect } from 'react';

interface UseAsyncDataOptions<T> {
  initialData?: T | null;
  immediate?: boolean;
}

export function useAsyncData<T, Args extends any[]>(
  asyncFn: (...args: Args) => Promise<T>,
  options: UseAsyncDataOptions<T> = {}
) {
  const [data, setData] = useState<T | null>(options.initialData ?? null);
  const [loading, setLoading] = useState<boolean>(!!options.immediate);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (...args: Args): Promise<T | null> => {
    setLoading(true);
    setError(null);
    try {
      const result = await asyncFn(...args);
      setData(result);
      return result;
    } catch (err: any) {
      const errMsg = err?.message || 'An unexpected execution error occurred during calculation.';
      setError(errMsg);
      return null;
    } finally {
      setLoading(false);
    }
  }, [asyncFn]);

  const reset = useCallback(() => {
    setData(options.initialData ?? null);
    setError(null);
    setLoading(false);
  }, [options.initialData]);

  useEffect(() => {
    if (options.immediate) {
      execute(...([] as unknown as Args));
    }
  }, [execute, options.immediate]);

  return { data, loading, error, execute, reset, setData };
}
