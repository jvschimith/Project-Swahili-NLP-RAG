"""
Optional integration smoke tests for endpoints that may depend on network access.
"""

import os

import pytest
from fastapi.testclient import TestClient

from src.web.api import app

RUN_OPTIONAL_INTEGRATION = os.getenv("RUN_OPTIONAL_INTEGRATION") == "1"


@pytest.mark.smoke
@pytest.mark.integration
@pytest.mark.optional_integration
@pytest.mark.skipif(
    not RUN_OPTIONAL_INTEGRATION,
    reason="Set RUN_OPTIONAL_INTEGRATION=1 to run optional external smoke tests.",
)
def test_analyze_url_with_real_fetch_path():
    """Exercise the real URL-analysis path against a public URL when explicitly enabled."""
    with TestClient(app) as client:
        response = client.post(
            "/analyze/url",
            json={"url": "https://www.bbc.com/swahili"},
            timeout=60,
        )

    assert response.status_code == 200
    payload = response.json()

    assert "success" in payload
    assert "error" in payload
