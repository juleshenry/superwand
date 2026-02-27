import os
import io
import pytest
from superwand.studio.app import app, in_memory_storage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Clear in-memory storage before each test
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'SuperWand Studio' in rv.data

def test_upload_and_process(client):
    # Test file upload
    with open('examples/images/charizard.png', 'rb') as f:
        data = {
            'file': (f, 'test_charizard.png')
        }
        rv = client.post('/upload', data=data, content_type='multipart/form-data')
    
    assert rv.status_code == 200
    filename = rv.get_json()['filename']
    assert filename == 'test_charizard.png'

    # Check if file exists in memory
    assert filename in in_memory_storage
    assert len(in_memory_storage[filename]) > 0
    
    # Test process
    process_data = {
        'image_name': filename,
        'k': 4,
        'threshold': 50,
        'apply_palette': True,
        'colors': [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]]
    }
    rv = client.post('/process', json=process_data)
    assert rv.status_code == 200
    assert 'image' in rv.get_json()

def test_upload_css_and_retheme(client):
    css_content = b"body { color: #ff0000; }"
    data = {
        'file': (io.BytesIO(css_content), 'test.css')
    }
    rv = client.post('/upload', data=data, content_type='multipart/form-data')
    assert rv.status_code == 200
    filename = rv.get_json()['filename']
    
    retheme_data = {
        'filename': filename,
        'colors': [[0, 255, 0]]
    }
    rv = client.post('/retheme_css', json=retheme_data)
    assert rv.status_code == 200
    assert 'css' in rv.get_json()
    assert '#00ff00' in rv.get_json()['css']
