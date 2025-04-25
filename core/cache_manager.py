# core/cache_manager.py

from django.core.cache import cache

DEFAULT_TIMEOUT = 60 * 60  # 1 hour timeout

class GlobalCacheManager:
    @classmethod
    def get(cls, key):
        return cache.get(key)

    @classmethod
    def set(cls, key, value, timeout=DEFAULT_TIMEOUT):
        cache.set(key, value, timeout)

    @classmethod
    def delete(cls, key):
        cache.delete(key)

    @classmethod
    def refresh(cls, key, value_func, timeout=DEFAULT_TIMEOUT):
        """
        Deletes old cache and sets fresh value.
        `value_func` must be a function returning fresh value.
        """
        cls.delete(key)
        fresh_data = value_func()
        cls.set(key, fresh_data, timeout)
        return fresh_data

    @classmethod
    def make_key(cls, *parts):
        """
        Example:
        make_key('beneficiary', 'detail', 5)
        Output: 'beneficiary:detail:5'
        """
        return ":".join(str(part) for part in parts)

    @classmethod
    def make_paginated_key(cls, base, page, **filters):
        """
        Example: 
        make_paginated_key('beneficiary:list', 2, gender='male')
        Output: 'beneficiary:list:page:2:gender=male'
        """
        key = f"{base}:page:{page}"
        if filters:
            filter_parts = [f"{k}={v}" for k, v in sorted(filters.items())]
            key += ":" + ":".join(filter_parts)
        return key

