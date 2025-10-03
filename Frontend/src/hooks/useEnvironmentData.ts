import { useState, useCallback } from 'react';
import { useNotification } from '../contexts/NotificationContext';

interface SearchParams {
  lat?: number | null;
  lon?: number | null;
  city?: string;
  country?: string;
  include: string[];
}

interface EnvironmentData {
  weather?: any;
  airQuality?: any;
  pollution?: any;
  noise?: any;
  radiation?: any;
  soil?: any;
}

export const useEnvironmentData = () => {
  const [data, setData] = useState<EnvironmentData>({});
  const [loading, setLoading] = useState<{ [key: string]: boolean }>({});
  const [error, setError] = useState<string>('');
  const { addNotification } = useNotification();

  const fetchData = useCallback(async (params: SearchParams) => {
    if (!params.include || params.include.length === 0) return;

    setError('');
    
    // Build query parameters
    const queryParams = new URLSearchParams();
    if (params.lat !== null && params.lat !== undefined) queryParams.append('lat', params.lat.toString());
    if (params.lon !== null && params.lon !== undefined) queryParams.append('lon', params.lon.toString());
    if (params.city) queryParams.append('city', params.city);
    if (params.country) queryParams.append('country', params.country);
    queryParams.append('include', params.include.join(','));

    // Fetch data for each include type
    for (const dataType of params.include) {
      setLoading(prev => ({ ...prev, [dataType]: true }));
      
      try {
        const response = await fetch(`http://localhost:8000/api/environment?${queryParams.toString()}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch ${dataType} data`);
        }

        const result = await response.json();
        
        setData(prev => ({
          ...prev,
          [dataType]: result[dataType] || result
        }));

        addNotification(`${dataType} data loaded successfully`, 'success');
        
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : `Failed to load ${dataType} data`;
        setError(errorMessage);
        addNotification(errorMessage, 'error');
      } finally {
        setLoading(prev => ({ ...prev, [dataType]: false }));
      }
    }
  }, [addNotification]);

  return {
    data,
    loading,
    error,
    fetchData
  };
};