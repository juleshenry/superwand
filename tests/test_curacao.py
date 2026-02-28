import io
import os
import pytest
from superwand.studio.app import app, in_memory_storage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

def test_upload_and_process_curacao(client):
    file_path = 'src/superwand/assets/curacao.jpg'
    if not os.path.exists(file_path):
        pytest.skip(f"{file_path} not found for testing")

    # Test file upload
    with open(file_path, 'rb') as f:
        data = {
            'file': (f, 'curacao.jpg')
        }
        rv = client.post('/upload', data=data, content_type='multipart/form-data')
    
    assert rv.status_code == 200
    filename = rv.get_json()['filename']
    assert 'curacao.png' in filename

    # Test process
    process_data = {
        'image_name': filename,
        'k': 4,
        'threshold': 50,
        'apply_palette': True,
        'colors': [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]]
    }
    rv = client.post('/process', json=process_data)
    
    if rv.status_code != 200:
        print(f"Error detail: {rv.get_json()}")
    
    assert rv.status_code == 200
    assert 'image' in rv.get_json()
    assert 'original_colors' in rv.get_json()
