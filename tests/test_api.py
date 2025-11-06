"""
Tests for News Credibility Analyzer API
"""

import pytest
import json
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'version' in data


def test_version_endpoint(client):
    """Test version endpoint."""
    response = client.get('/api/version')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'version' in data
    assert data['service'] == 'news-credibility-analyzer'


def test_analyze_missing_data(client):
    """Test analyze endpoint with missing data."""
    response = client.post('/api/analyze', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_analyze_valid_article(client):
    """Test analyze endpoint with valid article."""
    payload = {
        'title': 'Research Study Confirms Climate Change Impact',
        'content': 'A peer-reviewed study published in a scientific journal provides evidence of climate change.',
        'source': 'Reuters'
    }
    response = client.post('/api/analyze', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'credibility_score' in data
    assert 0 <= data['credibility_score'] <= 100
    assert 'risk_factors' in data
    assert isinstance(data['risk_factors'], list)
    assert 'recommendations' in data
    assert isinstance(data['recommendations'], list)
    assert 'timestamp' in data
    assert 'version' in data


def test_analyze_suspicious_article(client):
    """Test analyze endpoint with suspicious article."""
    payload = {
        'title': 'SHOCKING SECRET Doctors Don\'t Want You to Know!',
        'content': 'You won\'t believe this one weird trick! Act now!',
        'source': 'Unknown'
    }
    response = client.post('/api/analyze', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Suspicious article should have lower score
    assert data['credibility_score'] < 50
    assert len(data['risk_factors']) > 0


def test_analyze_title_only(client):
    """Test analyze endpoint with title only."""
    payload = {
        'title': 'Breaking News: Official Statement Released',
        'content': ''
    }
    response = client.post('/api/analyze', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'credibility_score' in data


def test_analyze_content_only(client):
    """Test analyze endpoint with content only."""
    payload = {
        'title': '',
        'content': 'This is a verified news article with confirmed facts.'
    }
    response = client.post('/api/analyze', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'credibility_score' in data


def test_analyze_no_json(client):
    """Test analyze endpoint without JSON."""
    response = client.post('/api/analyze', data='not json')
    assert response.status_code == 400


def test_index_page(client):
    """Test index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'News Credibility Analyzer' in response.data

