import React, { useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

interface SearchSectionProps {
  onSearch: (params: any) => void;
  selectedIncludes: string[];
  onIncludeToggle: (dataType: string) => void;
}

export const SearchSection: React.FC<SearchSectionProps> = ({
  onSearch,
  selectedIncludes,
  onIncludeToggle
}) => {
  const { t } = useLanguage();
  const [searchForm, setSearchForm] = useState({
    city: '',
    lat: '',
    lon: '',
    country: ''
  });

  const dataTypes = [
    { key: 'weather', label: t.dataTypes.weather },
    { key: 'airQuality', label: t.dataTypes.airQuality },
    { key: 'pollution', label: t.dataTypes.pollution },
    { key: 'noise', label: t.dataTypes.noise },
    { key: 'radiation', label: t.dataTypes.radiation },
    { key: 'soil', label: t.dataTypes.soil }
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const params = {
      city: searchForm.city,
      lat: searchForm.lat ? parseFloat(searchForm.lat) : null,
      lon: searchForm.lon ? parseFloat(searchForm.lon) : null,
      country: searchForm.country,
      include: selectedIncludes
    };
    
    onSearch(params);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Search Input */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              City Search
            </label>
            <input
              type="text"
              placeholder={t.search.placeholder}
              value={searchForm.city}
              onChange={(e) => setSearchForm(prev => ({ ...prev, city: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.search.country}
            </label>
            <input
              type="text"
              placeholder="US, VN, etc."
              value={searchForm.country}
              onChange={(e) => setSearchForm(prev => ({ ...prev, country: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Coordinates */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t.search.coordinates}
          </label>
          <div className="grid grid-cols-2 gap-4">
            <input
              type="number"
              placeholder={t.search.latitude}
              value={searchForm.lat}
              onChange={(e) => setSearchForm(prev => ({ ...prev, lat: e.target.value }))}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              step="any"
            />
            <input
              type="number"
              placeholder={t.search.longitude}
              value={searchForm.lon}
              onChange={(e) => setSearchForm(prev => ({ ...prev, lon: e.target.value }))}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              step="any"
            />
          </div>
        </div>

        {/* Data Types Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            {t.dataTypes.title}
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {dataTypes.map(dataType => (
              <label key={dataType.key} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedIncludes.includes(dataType.key)}
                  onChange={() => onIncludeToggle(dataType.key)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{dataType.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={selectedIncludes.length === 0}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
        >
          {t.search.button}
        </button>
      </form>
    </div>
  );
};