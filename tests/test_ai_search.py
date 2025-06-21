"""
Integration tests for AI search endpoints.
"""

import pytest


def test_search_paints_success(ai_client, auth_headers, mock_vector_store):
    """Test searching paints with vector store integration."""
    from unittest.mock import Mock, patch

    with patch(
        "libs.ai_service.app.api.dependencies.get_vector_store_instance"
    ) as mock_store:
        mock_store.return_value = mock_vector_store

        response = ai_client.post(
            "/api/v1/search",
            json={"query": "tinta azul para quarto", "limit": 5},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data


def test_search_paints_empty_query(ai_client, auth_headers):
    """Test search with empty query."""
    response = ai_client.post(
        "/api/v1/search", json={"query": "", "limit": 5}, headers=auth_headers
    )

    assert response.status_code == 200


def test_filter_paints_success(ai_client, auth_headers, mock_vector_store):
    """Test filtering paints by criteria."""
    response = ai_client.post(
        "/api/v1/filter",
        json={
            "environment": "internal",
            "product_line": "Premium",
            "features": ["washable"],
            "limit": 10,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_filter_paints_no_filters(ai_client, auth_headers, mock_vector_store):
    """Test filter with no criteria (should return all)."""
    response = ai_client.post("/api/v1/filter", json={"limit": 5}, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_search_paints_with_vector_store_error(ai_client, auth_headers):
    """Test search when vector store fails."""
    from unittest.mock import Mock, patch

    with patch(
        "libs.ai_service.app.api.dependencies.get_vector_store_instance"
    ) as mock_store:
        mock_store_instance = Mock()
        mock_store_instance.search.side_effect = Exception("Vector store error")
        mock_store.return_value = mock_store_instance

        response = ai_client.post(
            "/api/v1/search",
            json={"query": "tinta azul", "limit": 5},
            headers=auth_headers,
        )

        assert response.status_code in [200, 500]
