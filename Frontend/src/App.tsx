import { useState } from 'react';
import { Globe, Search, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import './App.css';

interface SearchParams {
  lat?: number | null;
  lon?: number | null;
  city?: string;
  country?: string;
}

interface DataState {
  data: any;
  loading: boolean;
  error: string | null;
  apiPath?: string;
}

interface DataStates {
  [key: string]: DataState;
}

const DATA_TYPES = [
  { key: 'weather', label: 'Weather', icon: '🌤️', color: 'blue' },
  { key: 'air', label: 'Air Quality', icon: '🌬️', color: 'green' },
  { key: 'water', label: 'Water Quality', icon: '💧', color: 'cyan' },
  { key: 'noise', label: 'Noise Level', icon: '🔊', color: 'purple' },
  { key: 'soil', label: 'Soil Quality', icon: '🌱', color: 'amber' },
  { key: 'light', label: 'Light Level', icon: '💡', color: 'yellow' },
  { key: 'heat', label: 'Heat Index', icon: '🌡️', color: 'red' },
  { key: 'radiation', label: 'Radiation', icon: '☢️', color: 'orange' },
  // { key: 'environmental_quality', label: 'AI Analysis', icon: '🤖', color: 'indigo', special: true }
];

function App() {
  const [language, setLanguage] = useState<'en' | 'vi'>('en');
  const [searchParams, setSearchParams] = useState<SearchParams>({});
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [dataState, setDataState] = useState<DataStates>({});
  const [hasSearched, setHasSearched] = useState(false);

  // Notifications
  const [notifications, setNotifications] = useState<Array<{
    id: string;
    message: string;
    type: 'success' | 'error' | 'info';
  }>>([]);

  const addNotification = (message: string, type: 'success' | 'error' | 'info') => {
    const id = Date.now().toString();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 3000);
  };

  const fetchDataType = async (dataType: string, params: SearchParams) => {
    setDataState(prev => ({
      ...prev,
      [dataType]: { ...prev[dataType], loading: true, error: null }
    }));

    try {
      const queryParams = new URLSearchParams();
      if (params.lat) queryParams.append('lat', params.lat.toString());
      if (params.lon) queryParams.append('lon', params.lon.toString());
      if (params.city) queryParams.append('city', params.city);
      if (params.country) queryParams.append('country', params.country);
      dataType !== 'heat' && queryParams.append('include', dataType);

      const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/environment?${queryParams}`;
      const response = await fetch(apiUrl);
      
      if (!response.ok) throw new Error(`Failed to fetch ${dataType}`);
      
      const result = await response.json();
      
      setDataState(prev => ({
        ...prev,
        [dataType]: { 
          data: result[dataType] || result, 
          loading: false, 
          error: null,
          apiPath: apiUrl 
        }
      }));

      addNotification(`${dataType} data loaded successfully`, 'success');
      
      // If this is environmental_quality (AI analysis), fetch with all available data
      if (dataType === 'environmental_quality') {
        await fetchAIAnalysis(searchParams);
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : `Failed to load ${dataType}`;
      setDataState(prev => ({
        ...prev,
        [dataType]: { data: null, loading: false, error: errorMessage, apiPath: undefined }
      }));
      addNotification(errorMessage, 'error');
    }
  };

  const fetchAIAnalysis = async (params: SearchParams) => {
    setDataState(prev => ({
      ...prev,
      environmental_quality: { ...prev.environmental_quality, loading: true, error: null }
    }));

    try {
        const queryParams = new URLSearchParams();
      if (params.lat) queryParams.append('lat', params.lat.toString());
      if (params.lon) queryParams.append('lon', params.lon.toString());
      if (params.city) queryParams.append('city', params.city);
      if (params.country) queryParams.append('country', params.country);

      // Simple API call without any query parameters
      const apiUrl = `${import.meta.env.VITE_API_BASE_URL}/environment?${queryParams}`;
      const response = await fetch(apiUrl);
      
      if (!response.ok) throw new Error('Failed to fetch AI analysis');
      
      const result = await response.json();
      
      // Extract environmental_quality field from the response
      const aiAnalysisData = result.environmental_quality || {};
      
      setDataState(prev => ({
        ...prev,
        environmental_quality: { 
          data: aiAnalysisData,
          loading: false, 
          error: null,
          apiPath: apiUrl
        }
      }));

      addNotification('AI Environmental Analysis completed', 'success');
      
      // Log AI analysis results for development
      console.log('AI Analysis Results:', aiAnalysisData);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to complete AI analysis';
      setDataState(prev => ({
        ...prev,
        environmental_quality: { data: null, loading: false, error: errorMessage, apiPath: undefined }
      }));
      addNotification(errorMessage, 'error');
    }
  };

  const handleSearch = () => {
    if (selectedTypes.length === 0) {
      addNotification('Please select at least one data type', 'error');
      return;
    }

    setHasSearched(true);
    
    // Fetch selected data types
    selectedTypes.forEach(type => {
      fetchDataType(type, searchParams);
    });
    
    // Always automatically fetch AI Analysis
    fetchAIAnalysis(searchParams);
  };

  const toggleDataType = (dataType: string) => {
    setSelectedTypes(prev => {
      const newTypes = prev.includes(dataType)
        ? prev.filter(t => t !== dataType)
        : [...prev, dataType];
      
      // Auto fetch if already searched and adding new type
      if (hasSearched && !prev.includes(dataType)) {
        setTimeout(() => fetchDataType(dataType, searchParams), 100);
      }
      
      return newTypes;
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-white/20 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Environment Data Platform</h1>
                <p className="text-sm text-gray-600">Real-time environmental monitoring</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Search Section */}
        <div className="bg-white/70 backdrop-blur-lg rounded-2xl shadow-lg border border-white/30 p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <Search className="w-6 h-6 mr-3 text-blue-600" />
            Search Location
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <input
              type="text"
              placeholder="City name..."
              value={searchParams.city || ''}
              onChange={(e) => setSearchParams(prev => ({ ...prev, city: e.target.value }))}
              className="px-4 py-3 bg-white/80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
            <input
              type="text"
              placeholder="Country code (VN, US...)"
              value={searchParams.country || ''}
              onChange={(e) => setSearchParams(prev => ({ ...prev, country: e.target.value }))}
              className="px-4 py-3 bg-white/80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
            <input
              type="number"
              placeholder="Latitude"
              value={searchParams.lat || ''}
              onChange={(e) => setSearchParams(prev => ({ ...prev, lat: e.target.value ? parseFloat(e.target.value) : null }))}
              className="px-4 py-3 bg-white/80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
            <input
              type="number"
              placeholder="Longitude"
              value={searchParams.lon || ''}
              onChange={(e) => setSearchParams(prev => ({ ...prev, lon: e.target.value ? parseFloat(e.target.value) : null }))}
              className="px-4 py-3 bg-white/80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </div>

          {/* Data Types Selection */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Select Data Types</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
              {DATA_TYPES.map(type => (
                <button
                  key={type.key}
                  onClick={() => toggleDataType(type.key)}
                  className={`p-3 rounded-xl border-2 transition-all duration-200 ${
                    selectedTypes.includes(type.key)
                      ? `border-${type.color}-500 bg-${type.color}-50 text-${type.color}-700`
                      : 'border-gray-200 bg-white/50 hover:border-gray-300 text-gray-600'
                  }`}
                >
                  <div className="text-2xl mb-1">{type.icon}</div>
                  <div className="text-xs font-medium">{type.label}</div>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={handleSearch}
            disabled={selectedTypes.length === 0}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-400 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2"
          >
            <Search className="w-5 h-5" />
            <span>Search Environmental Data</span>
          </button>
        </div>

        {/* Results Section */}
        {!hasSearched ? (
          // Welcome/Skeleton Screen
          <div className="text-center py-16">
            <div className="w-24 h-24 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full mx-auto mb-6 flex items-center justify-center">
              <Globe className="w-12 h-12 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-4">
              {language === 'vi' ? 'Chào mừng đến với Nền tảng Dữ liệu Môi trường' : 'Welcome to Environment Data Platform'}
            </h3>
            <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
              {language === 'vi' 
                ? 'Chọn loại dữ liệu môi trường và vị trí để bắt đầu khám phá thông tin chi tiết về môi trường xung quanh bạn.'
                : 'Select environmental data types and location to start exploring detailed information about your surroundings.'
              }
            </p>
            
            {/* Preview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
              {DATA_TYPES.slice(0, 4).map((type) => (
                <div key={type.key} className="bg-white/50 backdrop-blur-sm rounded-2xl p-6 border border-white/30">
                  <div className="text-4xl mb-4">{type.icon}</div>
                  <h4 className="font-semibold text-gray-800 mb-2">{type.label}</h4>
                  <div className="space-y-2">
                    <div className="h-3 bg-gray-200 rounded-full animate-pulse"></div>
                    <div className="h-3 bg-gray-200 rounded-full w-3/4 animate-pulse"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          // Data Display
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {selectedTypes.filter(typeKey => typeKey !== 'environmental_quality').map(typeKey => {
              const type = DATA_TYPES.find(t => t.key === typeKey);
              const state = dataState[typeKey] || { data: null, loading: false, error: null, apiPath: undefined };
              
              return (
                <div key={typeKey} className="bg-white/70 backdrop-blur-lg rounded-2xl shadow-lg border border-white/30 p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="text-3xl">{type?.icon}</div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-800">{type?.label}</h3>
                      <div className="flex items-center space-x-2">
                        {state.loading && (
                          <>
                            <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                            <span className="text-sm text-blue-600">Loading...</span>
                          </>
                        )}
                        {state.error && (
                          <>
                            <AlertCircle className="w-4 h-4 text-red-500" />
                            <span className="text-sm text-red-600">Error</span>
                          </>
                        )}
                        {state.data && !state.loading && !state.error && (
                          <>
                            <CheckCircle2 className="w-4 h-4 text-green-500" />
                            <span className="text-sm text-green-600">Loaded</span>
                          </>
                        )}
                      </div>
                      {/* API Path Display */}
                      {state.apiPath && (
                        <div className="mt-2 p-2 bg-gray-50 rounded-lg border">
                          <div className="flex items-center space-x-2">
                            <Globe className="w-4 h-4 text-gray-500" />
                            <span className="text-xs font-medium text-gray-600">API Endpoint:</span>
                          </div>
                          <code className="text-xs text-gray-700 break-all block mt-1">
                            {decodeURIComponent(state.apiPath)}
                          </code>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="bg-white/60 rounded-xl p-4 max-h-96 overflow-auto">
                    {state.loading ? (
                      <div className="space-y-3">
                        {[...Array(5)].map((_, i) => (
                          <div key={i} className="flex space-x-3">
                            <div className="w-16 h-4 bg-gray-200 rounded animate-pulse"></div>
                            <div className="flex-1 h-4 bg-gray-200 rounded animate-pulse"></div>
                          </div>
                        ))}
                      </div>
                    ) : state.error ? (
                      <div className="text-center py-8">
                        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
                        <p className="text-red-600 font-medium">{state.error}</p>
                        <button
                          onClick={() => fetchDataType(typeKey, searchParams)}
                          className="mt-3 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                        >
                          Retry
                        </button>
                      </div>
                    ) : state.data ? (
                      // Regular Data Display
                      <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                        {JSON.stringify(state.data, null, 2)}
                      </pre>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        No data available
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
            
            {/* AI Analysis Block - Always show when hasSearched */}
            {(() => {
              const aiState = dataState['environmental_quality'] || { data: null, loading: false, error: null, apiPath: undefined };
              
              return (
                <div key="ai-analysis" className="bg-white/70 backdrop-blur-lg rounded-2xl shadow-lg border border-white/30 p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="text-3xl">🤖</div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-800">AI Analysis</h3>
                      <div className="flex items-center space-x-2">
                        {aiState.loading && (
                          <>
                            <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                            <span className="text-sm text-blue-600">Loading...</span>
                          </>
                        )}
                        {aiState.error && (
                          <>
                            <AlertCircle className="w-4 h-4 text-red-500" />
                            <span className="text-sm text-red-600">Error</span>
                          </>
                        )}
                        {aiState.data && !aiState.loading && !aiState.error && (
                          <>
                            <CheckCircle2 className="w-4 h-4 text-green-500" />
                            <span className="text-sm text-green-600">Loaded</span>
                          </>
                        )}
                      </div>
                      {/* API Path Display */}
                      {aiState.apiPath && (
                        <div className="mt-2 p-2 bg-gray-50 rounded-lg border">
                          <div className="flex items-center space-x-2">
                            <Globe className="w-4 h-4 text-gray-500" />
                            <span className="text-xs font-medium text-gray-600">API Endpoint:</span>
                          </div>
                          <code className="text-xs text-gray-700 break-all block mt-1">
                            {decodeURIComponent(aiState.apiPath)}
                          </code>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="bg-white/60 rounded-xl p-4 max-h-96 overflow-auto">
                    {aiState.loading ? (
                      <div className="space-y-3">
                        {[...Array(5)].map((_, i) => (
                          <div key={i} className="flex space-x-3">
                            <div className="w-16 h-4 bg-gray-200 rounded animate-pulse"></div>
                            <div className="flex-1 h-4 bg-gray-200 rounded animate-pulse"></div>
                          </div>
                        ))}
                      </div>
                    ) : aiState.error ? (
                      <div className="text-center py-8">
                        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
                        <p className="text-red-600 font-medium">{aiState.error}</p>
                        <button
                          onClick={() => fetchAIAnalysis(searchParams)}
                          className="mt-3 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                        >
                          Retry
                        </button>
                      </div>
                    ) : aiState.data ? (
                      // AI Analysis Raw Data Display
                      <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                        {JSON.stringify(aiState.data, null, 2)}
                      </pre>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        No AI analysis data available
                      </div>
                    )}
                  </div>
                </div>
              );
            })()}
          </div>
        )}
      </main>

      {/* Notifications */}
      <div className="fixed bottom-6 right-6 space-y-3 z-50">
        {notifications.map(notification => (
          <div
            key={notification.id}
            className={`px-6 py-4 rounded-xl shadow-lg backdrop-blur-lg border border-white/30 transition-all duration-300 transform animate-in slide-in-from-right ${
              notification.type === 'success' ? 'bg-green-500/90 text-white' :
              notification.type === 'error' ? 'bg-red-500/90 text-white' :
              'bg-blue-500/90 text-white'
            }`}
          >
            <div className="flex items-center space-x-3">
              {notification.type === 'success' && <CheckCircle2 className="w-5 h-5" />}
              {notification.type === 'error' && <AlertCircle className="w-5 h-5" />}
              {notification.type === 'info' && <Globe className="w-5 h-5" />}
              <span className="font-medium">{notification.message}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
