import json
import logging
import pandas as pd
import requests
import concurrent.futures
from urllib.parse import urlencode
from pathlib import Path
from typing import Optional, Dict, Any
import threading  # Importar o módulo threading

# Importar classes de configuração
from ..config.service_config import ServiceConfig
from ..config.web_service import WebService

# Configuração do logger
logging.basicConfig(filename='meu_log.txt', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Inicialização das configurações
service = ServiceConfig()
auth = service.get_auth()
server = service.get_server()
environment_id = service.get_environment_id()
content_type = service.get_content_type()
field_name = service.get_field_name()

call = WebService(auth, content_type)

SCRIPT_DIR = Path(__file__).resolve().parent
FILE_PATH = SCRIPT_DIR / "../data/values.xlsx"

already_sent_urls = set()  # Conjunto para armazenar as URLs já enviadas
lock = threading.Lock()  # Criar um lock


def value_list(env_id: str, field_name: str, value: str, acronym: Optional[str] = None, parent_id: Optional[str] = None) -> None:
    """
    Envia uma requisição para a API para criar ou atualizar um valor de campo.

    Args:
        env_id: ID do ambiente.
        field_name: Nome do campo.
        value: Valor do campo.
        acronym: Sigla do valor (opcional).
        parent_id: ID do pai (opcional).
    """
    url = f"{server}api/v2/fieldValues"
    params = {
        "idAmbiente": env_id,
        "nome": field_name,
        "valor": value,
        "sigla": acronym,
        "idPai": parent_id
    }

    # Remove parâmetros vazios e None
    params = {k: v for k, v in params.items() if v}
    full_url = f"{url}?{urlencode(params)}"

    print(f"URL: {full_url}")

    try:
        response = call.request(full_url, method="POST")
        response.raise_for_status()  # Lança exceção para erros HTTP

        print(f"Código de status: {response.status_code}")
        print(f"Cabeçalhos da resposta: {response.headers}")

        content_type = response.headers.get('Content-Type')
        if content_type and 'application/json' in content_type:
            try:
                response_json = response.json()
                print(f"Resposta JSON: {response_json}")
            except json.JSONDecodeError as e:
                logging.error(
                    f"Erro ao decodificar JSON: {e}. Resposta: {response.text}")
                print(
                    "Erro ao decodificar JSON. Consulte o arquivo de log para detalhes.")
        else:
            print(f"Resposta (não JSON): {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(
            f"Erro na requisição: {e}. Resposta: {getattr(e.response, 'text', 'N/A')}")
        print(f"Erro na requisição: {e}")
        if e.response:
            print(f"Conteúdo da resposta: {e.response.text}")
    except Exception as e:
        logging.error(f"Erro geral: {e}")
        print(f"Ocorreu um erro geral: {e}")


def process_element(element: Dict[str, Any], env_id: str, field_name: str, already_sent_urls: set) -> None:
    """
    Processa um único elemento do arquivo Excel.

    Args:
        element: Um dicionário representando uma linha do Excel.
        env_id: ID do ambiente.
        field_name: Nome do campo.
        already_sent_urls: Conjunto para armazenar as URLs já enviadas.
    """
    try:
        if not element.get('valor'):
            return

        value = element['valor']
        acronym = element.get('sigla')
        parent_id = element.get('filtro')

        # Construir a URL completa
        url = f"{server}api/v2/fieldValues"
        params = {
            "idAmbiente": env_id,
            "nome": field_name,
            "valor": value,
            "sigla": acronym,
            "idPai": parent_id
        }
        params = {k: v for k, v in params.items() if v}
        full_url = f"{url}?{urlencode(params)}"

        # Proteger o acesso ao conjunto already_sent_urls com um lock
        with lock:
            # Verificar se a URL já foi enviada
            if full_url not in already_sent_urls:
                value_list(env_id, field_name, value, acronym, parent_id)
                # Adicionar a URL ao conjunto de URLs enviadas
                already_sent_urls.add(full_url)
            else:
                print(f"URL já enviada: {full_url}. Ignorando.")

    except Exception as e:
        logging.error(f"Erro ao processar elemento: {element}. Erro: {e}")
        print(f"Ocorreu um erro ao processar um elemento. Consulte o arquivo de log para mais detalhes.")


def excel_row_generator(file_path: str, nrows: int = 1000, skiprows: int = 0):
    """
    Gera linhas do arquivo Excel em partes para otimizar o uso de memória.

    Args:
        file_path: Caminho para o arquivo Excel.
        nrows: Número de linhas a serem lidas por vez.
        skiprows: Número de linhas a serem ignoradas no início do arquivo.
    """
    try:
        while True:
            df = pd.read_excel(file_path, nrows=nrows,
                               skiprows=skiprows, engine='openpyxl')
            if df.empty:
                break
            for _, row in df.iterrows():
                yield row.to_dict()
            skiprows += nrows
    except FileNotFoundError:
        print("O arquivo Excel não existe.")
    except Exception as e:
        logging.error(f"Erro ao ler arquivo Excel: {e}")
        print(f"Ocorreu um erro ao ler o arquivo Excel. Consulte o arquivo de log para mais detalhes.")


def main():
    """
    Função principal para ler o arquivo Excel e processar os elementos em paralelo.
    """
    already_sent_urls = set()  # Inicializa o conjunto de URLs enviadas
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for element in excel_row_generator(FILE_PATH):
            executor.submit(process_element, element,
                            environment_id, field_name, already_sent_urls)


if __name__ == "__main__":
    main()
