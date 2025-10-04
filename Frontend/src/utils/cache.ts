interface CacheItem {
  data: any;
  timestamp: number;
  expiresIn: number; // in milliseconds
}

interface CacheKey {
  dataType: string;
  lat?: number | null;
  lon?: number | null;
  city?: string;
  country?: string;
}

export class LocalStorageCache {
  private static readonly CACHE_PREFIX = 'env_data_';
  private static readonly DEFAULT_EXPIRY = 15 * 60 * 1000; // 15 minutes

  /**
   * Generate cache key from search parameters
   */
  private static generateCacheKey(params: CacheKey): string {
    const keyParts = [params.dataType];
    
    if (params.city) keyParts.push(`city:${params.city.toLowerCase()}`);
    if (params.country) keyParts.push(`country:${params.country.toLowerCase()}`);
    if (params.lat !== null && params.lat !== undefined) keyParts.push(`lat:${params.lat.toFixed(4)}`);
    if (params.lon !== null && params.lon !== undefined) keyParts.push(`lon:${params.lon.toFixed(4)}`);
    
    return this.CACHE_PREFIX + keyParts.join('_');
  }

  /**
   * Store data in cache
   */
  static set(params: CacheKey, data: any, customExpiry?: number): void {
    try {
      const cacheItem: CacheItem = {
        data,
        timestamp: Date.now(),
        expiresIn: customExpiry || this.DEFAULT_EXPIRY
      };
      
      const key = this.generateCacheKey(params);
      localStorage.setItem(key, JSON.stringify(cacheItem));
      
      console.log(`Cached data for: ${params.dataType} (${key})`);
    } catch (error) {
      console.warn('Failed to cache data:', error);
    }
  }

  /**
   * Get data from cache
   */
  static get(params: CacheKey): any | null {
    try {
      const key = this.generateCacheKey(params);
      const cached = localStorage.getItem(key);
      
      if (!cached) {
        console.log(`No cache found for: ${params.dataType}`);
        return null;
      }

      const cacheItem: CacheItem = JSON.parse(cached);
      const now = Date.now();
      
      // Check if cache is expired
      if (now - cacheItem.timestamp > cacheItem.expiresIn) {
        console.log(`⏰ Cache expired for: ${params.dataType}, removing...`);
        localStorage.removeItem(key);
        return null;
      }

      const remainingTime = Math.round((cacheItem.expiresIn - (now - cacheItem.timestamp)) / 1000 / 60);
      console.log(`Cache hit for: ${params.dataType} (expires in ${remainingTime}m)`);
      
      return cacheItem.data;
    } catch (error) {
      console.warn('Failed to get cached data:', error);
      return null;
    }
  }

  /**
   * Check if data exists in cache and is valid
   */
  static has(params: CacheKey): boolean {
    return this.get(params) !== null;
  }

  /**
   * Remove specific cache entry
   */
  static remove(params: CacheKey): void {
    try {
      const key = this.generateCacheKey(params);
      localStorage.removeItem(key);
      console.log(`Removed cache for: ${params.dataType}`);
    } catch (error) {
      console.warn('Failed to remove cache:', error);
    }
  }

  /**
   * Clear all environment data cache
   */
  static clearAll(): void {
    try {
      const keys = Object.keys(localStorage).filter(key => 
        key.startsWith(this.CACHE_PREFIX)
      );
      
      keys.forEach(key => localStorage.removeItem(key));
      console.log(`🧹 Cleared ${keys.length} cache entries`);
    } catch (error) {
      console.warn('Failed to clear cache:', error);
    }
  }

  /**
   * Get cache statistics
   */
  static getStats(): { total: number; expired: number; active: number } {
    try {
      const keys = Object.keys(localStorage).filter(key => 
        key.startsWith(this.CACHE_PREFIX)
      );
      
      let expired = 0;
      let active = 0;
      const now = Date.now();
      
      keys.forEach(key => {
        try {
          const cached = localStorage.getItem(key);
          if (cached) {
            const cacheItem: CacheItem = JSON.parse(cached);
            if (now - cacheItem.timestamp > cacheItem.expiresIn) {
              expired++;
            } else {
              active++;
            }
          }
        } catch {
          expired++;
        }
      });

      return { total: keys.length, expired, active };
    } catch (error) {
      console.warn('Failed to get cache stats:', error);
      return { total: 0, expired: 0, active: 0 };
    }
  }

  /**
   * Clean expired cache entries
   */
  static cleanExpired(): number {
    try {
      const keys = Object.keys(localStorage).filter(key => 
        key.startsWith(this.CACHE_PREFIX)
      );
      
      let cleaned = 0;
      const now = Date.now();
      
      keys.forEach(key => {
        try {
          const cached = localStorage.getItem(key);
          if (cached) {
            const cacheItem: CacheItem = JSON.parse(cached);
            if (now - cacheItem.timestamp > cacheItem.expiresIn) {
              localStorage.removeItem(key);
              cleaned++;
            }
          }
        } catch {
          localStorage.removeItem(key);
          cleaned++;
        }
      });

      if (cleaned > 0) {
        console.log(`Cleaned ${cleaned} expired cache entries`);
      }
      
      return cleaned;
    } catch (error) {
      console.warn('Failed to clean expired cache:', error);
      return 0;
    }
  }
}

// Auto-clean expired cache on page load
document.addEventListener('DOMContentLoaded', () => {
  LocalStorageCache.cleanExpired();
});