import { useState, useEffect } from 'react';
import { getBaseUrl } from '@/lib/api';

export function useBaseUrl() {
  const [baseUrl, setBaseUrl] = useState<string>('http://localhost:8000');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadBaseUrl = async () => {
      try {
        const url = await getBaseUrl();
        setBaseUrl(url);
      } catch (error) {
        console.error('Failed to get base URL:', error);
        setBaseUrl('http://localhost:8000');
      } finally {
        setIsLoading(false);
      }
    };

    loadBaseUrl();
  }, []);

  return { baseUrl, isLoading };
}