import os
import pytest
from superwand.studio.app import app, in_memory_storage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

def test_upload_mislabeled_avif_whale(client):
    # This file was originally an AVIF mislabeled as .jpg
    # We converted it to JPEG for the repo, but the test ensures 
    # the backend logic handles the normalization to PNG.
    file_path = 'src/superwand/assets/whale.jpg'
    if not os.path.exists(file_path):
        pytest.skip(f"{file_path} not found for testing")

    # 1. Test upload and normalization
    with open(file_path, 'rb') as f:
        data = {
            'file': (f, 'whale.jpg')
        }
        rv = client.post('/upload', data=data, content_type='multipart/form-data')
    
    assert rv.status_code == 200
    data = rv.get_json()
    filename = data['filename']
    
    # Ensure it was normalized to .png
    assert filename.endswith('.png')
    assert 'whale' in filename

    # 2. Test that the image is retrievable via the /image/ route
    rv = client.get(f'/image/{filename}')
    assert rv.status_code == 200
    assert rv.mimetype == 'image/png'
    assert len(rv.data) > 0

    # 3. Test that it can be processed
    process_data = {
        'image_name': filename,
        'k': 2,
        'apply_palette': True,
        'colors': [[0, 0, 0], [255, 255, 255]]
    }
    rv = client.post('/process', json=process_data)
    assert rv.status_code == 200
    assert 'image' in rv.get_json()
