import os
import tempfile
import pytest
from superwand.studio.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'SuperWand Studio' in rv.data

def test_upload_and_process(client):
    # Test file upload
    data = {
        'file': (open('examples/images/charizard.png', 'rb'), 'test_charizard.png')
    }
    rv = client.post('/upload', data=data, content_type='multipart/form-data')
    assert rv.status_code == 200
    filename = rv.get_json()['filename']
    assert filename == 'test_charizard.png'

    # Check if file exists in temp directory
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    assert os.path.exists(upload_path)
    
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

def test_upload_folder_is_temp():
    import tempfile
    assert app.config['UPLOAD_FOLDER'].startswith(tempfile.gettempdir())
