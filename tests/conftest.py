import sys
import os
import pytest

# Adiciona o diretório 'app' ao path do Python para que as importações funcionem corretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client
