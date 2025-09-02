import openai
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, ConfigurationError
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def validate_variables(key, uri, url):
    results = {}

    try:
        validate_key(key)
        results['openai'] = True
    except openai.AuthenticationError as e:
        results['openai'] = f"Autenticación fallida: {e}"
    except openai.OpenAIError as e:
        results['openai'] = f"Error OpenAI: {e}"

    try:
        validate_uri(uri)
        results['mongo'] = True
    except (ServerSelectionTimeoutError, ConnectionFailure, ConfigurationError) as e:
        results['mongo'] = f"Error MongoDB: {e}"


    try:
        validate_url(url)
        results['url'] = True
    except PlaywrightTimeoutError as e:
        results['url'] = f"URL inválida o inaccesible: {e}"

    return results

def validate_key(key):
    client = openai.OpenAI(api_key=key)
    client.models.list()

def validate_uri(uri):
    client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=1000)
    client.server_info()


def is_valid_format(url):
    parts = urlparse(url)
    return all([parts.scheme in ("http", "https"), parts.netloc])

def validate_url(url, timeout=5000):

    if not is_valid_format(url):
        raise Exception(f"Formato de URL inválido: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=timeout)
            browser.close()
            return True
        except PlaywrightTimeoutError as e:
            browser.close()
            raise Exception(f"No se pudo acceder a la URL en {timeout}ms: {e}")
        except Exception as e:
            browser.close()
            raise Exception(f"Error al acceder a la URL: {e}")
        
