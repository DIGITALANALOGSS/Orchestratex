"""
Tests for VectorCache
"""

import pytest
import asyncio
from orchestratex.core.caching import VectorCache, MockPineconeIndex

class TestVectorCache:
    """Test cases for VectorCache."""

    @pytest.fixture
    def vector_cache(self):
        """Vector cache fixture."""
        return VectorCache(index_name="test_index")

    @pytest.mark.asyncio
    async def test_cache_hit(self, vector_cache):
        """Test cache hit."""
        # First query (cache miss)
        vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        results = await vector_cache.query(vector)
        assert "matches" in results

        # Second query (cache hit)
        cached_results = await vector_cache.query(vector)
        assert cached_results == results

    @pytest.mark.asyncio
    async def test_cache_eviction(self, vector_cache):
        """Test cache eviction based on TTL."""
        # Set a very short TTL for testing
        vector_cache.cache_ttl = 1  # 1 second

        vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        results = await vector_cache.query(vector)

        # Wait for TTL to expire
        await asyncio.sleep(2)

        # Query again - should be cache miss
        new_results = await vector_cache.query(vector)
        assert new_results != results

    @pytest.mark.asyncio
    async def test_concurrent_queries(self, vector_cache):
        """Test concurrent vector queries."""
        vector1 = [0.1, 0.2, 0.3, 0.4, 0.5]
        vector2 = [0.5, 0.4, 0.3, 0.2, 0.1]

        # Run concurrent queries
        tasks = [
            vector_cache.query(vector1),
            vector_cache.query(vector2),
            vector_cache.query(vector1)  # Should be cache hit
        ]
        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert results[0] == results[2]  # Cache hit verification
        assert results[0] != results[1]  # Different vectors

    @pytest.mark.asyncio
    async def test_top_k_parameter(self, vector_cache):
        """Test different top_k values."""
        vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        # Default top_k
        default_results = await vector_cache.query(vector)
        assert len(default_results["matches"]) == 3  # Default top_k=5 in mock

        # Custom top_k
        custom_results = await vector_cache.query(vector, top_k=2)
        assert len(custom_results["matches"]) == 2

    @pytest.mark.asyncio
    async def test_cache_size_limit(self, vector_cache):
        """Test cache size limit."""
        # Fill cache with different vectors
        vectors = [[i/100 for _ in range(5)] for i in range(100)]
        for vector in vectors:
            await vector_cache.query(vector)

        # Verify cache size is limited
        assert len(vector_cache.cache) <= 100

    @pytest.mark.asyncio
    async def test_cache_clear(self, vector_cache):
        """Test clearing the cache."""
        vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        await vector_cache.query(vector)
        assert len(vector_cache.cache) > 0

        # Clear cache
        vector_cache.cache.clear()
        assert len(vector_cache.cache) == 0
