# To run tests with coverage:
#   pip install pytest pytest-cov
#   pytest --cov=url_injector_mcp --cov-report=term-missing

import pytest
from url_injector_mcp import extract_keywords, mcp
from starlette.testclient import TestClient
from unittest.mock import patch

# Existing tests

def test_extract_keywords():
    prompt = "How do I implement a REST API in Python using Flask?"
    keywords = extract_keywords(prompt)
    assert "rest" in keywords
    assert "api" in keywords
    assert "python" in keywords
    assert "flask" in keywords
    assert "how" not in keywords  # stopword

def test_health_check():
    client = TestClient(mcp.app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.text == "OK"

# New test for the tool endpoint

def fake_search_web(query):
    # Return a fixed set of URLs for testing
    return [
        "https://realpython.com/flask-rest-api/",
        "https://flask.palletsprojects.com/en/2.0.x/tutorial/",
        "https://stackoverflow.com/questions/12364942/developing-restful-apis-with-python-and-flask"
    ]

@patch("url_injector_mcp.search_web", side_effect=lambda q: fake_search_web(q))
def test_inject_urls_tool(mock_search):
    client = TestClient(mcp.app)
    headers = {"Authorization": "Bearer change-me-please"}
    data = {"user_prompt": "How do I implement a REST API in Python using Flask?"}
    response = client.post("/mcp/tool/inject_urls_into_prompt", json=data, headers=headers)
    assert response.status_code == 200
    body = response.text
    assert "realpython.com/flask-rest-api" in body
    assert "flask.palletsprojects.com" in body
    assert "stackoverflow.com" in body
    assert "Here are some relevant resources" in body 