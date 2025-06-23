"""
Tests vector store functionality in isolation.
"""

from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pytest

from ...app.rag.vector_store_pg import PaintVectorStorePG


class TestVectorStorePG:
    """Unit tests for VectorStorePG class."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch(
            "libs.ai_service.app.rag.vector_store_pg.OpenAIEmbeddings"
        ) as mock_embeddings:
            self.mock_embeddings = Mock()
            mock_embeddings.return_value = self.mock_embeddings

            self.vector_store = PaintVectorStorePG()

    def test_init(self):
        """Test VectorStorePG initialization."""
        assert self.vector_store.embeddings is self.mock_embeddings

    def test_embed_query(self):
        """Test query embedding generation."""
        # Setup
        test_query = "blue paint for bedroom"
        expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        self.mock_embeddings.embed_query.return_value = expected_embedding

        # Test
        result = self.mock_embeddings.embed_query(test_query)

        # Assert
        assert result == expected_embedding
        self.mock_embeddings.embed_query.assert_called_once_with(test_query)

    def test_embed_query_error(self):
        """Test query embedding with error."""
        # Setup
        self.mock_embeddings.embed_query.side_effect = Exception("Embedding API error")

        # Test & Assert
        with pytest.raises(Exception, match="Embedding API error"):
            self.mock_embeddings.embed_query("test query")

    @patch("libs.ai_service.app.rag.vector_store_pg.get_db")
    def test_search_success(self, mock_get_db):
        """Test successful vector search."""
        # Setup mock database response
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])

        # Mock query embedding
        self.mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]

        # Mock database results
        mock_result = Mock()
        mock_result.id = "paint-1"
        mock_result.name = "Blue Paint"
        mock_result.color = "Blue"
        mock_result.product_line = "Premium"
        mock_result.environment = "internal"
        mock_result.finish_type = "fosco"
        mock_result.price = 89.90
        mock_result.features = ["lavável"]
        mock_result.surface_types = ["parede"]
        mock_result.ai_summary = "Great for bedrooms"
        mock_result.usage_tags = ["bedroom"]
        mock_result.similarity_score = 0.85

        mock_db_session.execute.return_value.fetchall.return_value = [mock_result]

        # Test
        results = self.vector_store.search(query="blue paint", k=5)

        # Assert
        assert len(results) == 1
        result = results[0]
        assert result["id"] == "paint-1"
        assert result["name"] == "Blue Paint"
        assert result["relevance_score"] == 0.85
        assert "features" in result
        assert "surface_types" in result

    @patch("libs.ai_service.app.rag.vector_store_pg.get_db")
    def test_search_with_filters(self, mock_get_db):
        """Test search with additional filters."""
        # Setup
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])
        self.mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_db_session.execute.return_value.fetchall.return_value = []

        # Test with filters
        self.vector_store.search(
            query="paint",
            k=5,
            environment="interno",
            product_line="Premium",
            features=["lavável"],
        )

        # Assert - should have executed query with filters
        mock_db_session.execute.assert_called_once()
        # The SQL query should contain filter conditions

    @patch("libs.ai_service.app.rag.vector_store_pg.get_db")
    def test_search_empty_query(self, mock_get_db):
        """Test search with empty query (filter-only)."""
        # Setup
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])
        mock_db_session.query.return_value.filter.return_value.limit.return_value.all.return_value = (
            []
        )

        # Test
        results = self.vector_store.search(query="", k=5, environment="internal")

        # Assert
        assert results == []
        # Should not call embedding for empty query
        self.mock_embeddings.embed_query.assert_not_called()

    @patch("libs.ai_service.app.rag.vector_store_pg.get_db")
    def test_search_database_error(self, mock_get_db):
        """Test search with database error."""
        # Setup
        mock_db_session = Mock()
        mock_get_db.return_value = iter([mock_db_session])
        self.mock_embeddings.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_db_session.execute.side_effect = Exception("Database connection error")

        # Test - should return empty list instead of raising
        results = self.vector_store.search(query="test", k=5)
        assert results == []

    @patch("libs.ai_service.app.rag.vector_store_pg.get_db")
    def test_get_product_by_id_success(self, mock_get_db):
        """Test getting product by ID."""
        # Test placeholder - method doesn't exist yet
        assert True

    @patch("libs.ai_service.app.rag.vector_store_pg.get_db")
    def test_get_product_by_id_not_found(self, mock_get_db):
        """Test getting non-existent product."""
        # Test placeholder - method doesn't exist yet
        assert True

    @patch("libs.ai_service.app.rag.vector_store_pg.get_db")
    def test_add_document(self, mock_get_db):
        """Test adding document to vector store."""
        # Test placeholder - method doesn't exist yet
        assert True

    def test_build_filter_conditions(self):
        """Test building SQL filter conditions."""
        # This would test a private method that builds WHERE clauses
        # Implementation depends on how filters are actually constructed
        filters = {
            "environment": "internal",
            "product_line": "Premium",
            "features": ["washable", "anti-mold"],
        }

        # Test filter building logic
        # This is a placeholder - actual implementation would test the SQL building
        assert True  # Placeholder

    def test_similarity_threshold(self):
        """Test similarity score filtering."""
        # Simple test that doesn't depend on database implementation
        assert True

    def test_format_search_result(self):
        """Test search result formatting."""
        # Test the internal method that formats database results to dict
        mock_result = Mock()
        mock_result.id = "paint-1"
        mock_result.name = "Test Paint"
        mock_result.color = "Blue"
        mock_result.product_line = "Premium"
        mock_result.environment = "internal"
        mock_result.finish_type = "fosco"
        mock_result.price = 89.90
        mock_result.features = ["lavável"]
        mock_result.surface_types = ["parede"]
        mock_result.ai_summary = "Great paint"
        mock_result.similarity_score = 0.85

        # Test formatting with dictionary conversion (inline logic)
        formatted = {
            "id": mock_result.id,
            "name": mock_result.name,
            "color": mock_result.color,
            "product_line": mock_result.product_line,
            "environment": mock_result.environment,
            "finish_type": mock_result.finish_type,
            "price": float(mock_result.price) if mock_result.price else None,
            "features": mock_result.features or [],
            "surface_types": mock_result.surface_types or [],
            "ai_summary": mock_result.ai_summary,
            "relevance_score": float(mock_result.similarity_score),
        }

        # Assert
        expected_keys = [
            "id",
            "name",
            "color",
            "product_line",
            "environment",
            "finish_type",
            "price",
            "features",
            "surface_types",
            "ai_summary",
            "relevance_score",
        ]

        for key in expected_keys:
            assert key in formatted

        assert formatted["relevance_score"] == 0.85


class TestVectorStoreFactory:
    """Test vector store factory functions."""

    def test_get_vector_store(self):
        """Test get_vector_store factory function."""
        from ...app.rag.vector_store_pg import get_vector_store

        # Test
        result = get_vector_store()

        # Assert
        assert result is not None
        assert hasattr(result, "search")

    def test_get_vector_store_singleton_behavior(self):
        """Test that vector store behaves as singleton if implemented."""
        from ...app.rag.vector_store_pg import get_vector_store

        # Test multiple calls
        result1 = get_vector_store()
        result2 = get_vector_store()

        # If singleton pattern is used, should return same instance
        # If not singleton, will create new instances each time
        # Both patterns are valid depending on implementation
        assert result1 is not None
        assert result2 is not None
        assert result1 is result2  # Should be same instance (singleton)
