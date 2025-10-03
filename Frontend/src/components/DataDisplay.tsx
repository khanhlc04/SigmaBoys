import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';

interface DataDisplayProps {
  data: any;
  loading: { [key: string]: boolean };
  error: string;
  selectedIncludes: string[];
}

export const DataDisplay: React.FC<DataDisplayProps> = ({
  data,
  loading,
  error,
  selectedIncludes
}) => {
  const { t } = useLanguage();

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p className="text-red-800">{t.error}: {error}</p>
      </div>
    );
  }

  if (selectedIncludes.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-600">Select data types above to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {selectedIncludes.map(dataType => (
        <DataCard
          key={dataType}
          dataType={dataType}
          data={data[dataType]}
          loading={loading[dataType]}
        />
      ))}
    </div>
  );
};

interface DataCardProps {
  dataType: string;
  data: any;
  loading: boolean;
}

const DataCard: React.FC<DataCardProps> = ({ dataType, data, loading }) => {
  const { t } = useLanguage();

  const getDataTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      weather: t.dataTypes.weather,
      airQuality: t.dataTypes.airQuality,
      pollution: t.dataTypes.pollution,
      noise: t.dataTypes.noise,
      radiation: t.dataTypes.radiation,
      soil: t.dataTypes.soil
    };
    return labels[type] || type;
  };

  const getCardColor = (type: string) => {
    const colors: { [key: string]: string } = {
      weather: 'border-blue-200 bg-blue-50',
      airQuality: 'border-green-200 bg-green-50',
      pollution: 'border-red-200 bg-red-50',
      noise: 'border-purple-200 bg-purple-50',
      radiation: 'border-yellow-200 bg-yellow-50',
      soil: 'border-amber-200 bg-amber-50'
    };
    return colors[type] || 'border-gray-200 bg-gray-50';
  };

  return (
    <div className={`border rounded-lg p-6 ${getCardColor(dataType)}`}>
      <h3 className="text-lg font-semibold mb-4">{getDataTypeLabel(dataType)}</h3>
      
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">{t.loading}</span>
        </div>
      ) : data ? (
        <div className="bg-white rounded-md p-4">
          <pre className="text-sm text-gray-700 whitespace-pre-wrap overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      ) : (
        <div className="text-center py-4">
          <p className="text-gray-500">{t.noData}</p>
        </div>
      )}
    </div>
  );
};