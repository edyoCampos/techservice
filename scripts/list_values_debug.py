# --- START OF FILE list_values_debug_refactored.py ---
# filename: list_values_debug_refactored.py

import json
import logging
import pandas as pd
import requests
import concurrent.futures
from urllib.parse import urlencode
from pathlib import Path
from typing import Optional, Dict, Any
import threading

# Importar classes de configuração
from ..config.service_config import ServiceConfig
from ..config.web_service import WebService

# Configuração do logger - LEVEL CHANGED TO DEBUG for detailed logging
logging.basicConfig(filename='meu_log_debugged.txt', level=logging.DEBUG,  # Log file name changed
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

already_sent_urls = set()
lock = threading.Lock()
sent_urls_count = 0  # Contador para URLs enviadas
skipped_urls_count = 0  # Contador para URLs ignoradas
api_error_count = 0  # Contador para erros de API


def value_list(env_id: str, field_name: str, value: str, acronym: Optional[str] = None, parent_id: Optional[str] = None) -> None:
    """
    Envia uma requisição para a API para criar ou atualizar um valor de campo.
    (Com logging ainda mais detalhado para debug)
    """
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

    logging.debug(f"value_list - URL construída: {full_url}")  # DEBUG LOG
    print(f"Enviando URL: {full_url}")  # Console output

    try:
        response = call.request(full_url, method="POST")
        response.raise_for_status()

        logging.debug(
            # DEBUG LOG
            f"value_list - Código de status: {response.status_code} para URL: {full_url}")
        # Console output
        print(f"Status Code: {response.status_code} para URL: {full_url}")
        logging.debug(
            # DEBUG LOG
            f"value_list - Cabeçalhos da resposta: {response.headers} para URL: {full_url}")

        content_type = response.headers.get('Content-Type')
        if content_type and 'application/json' in content_type:
            try:
                response_json = response.json()
                logging.debug(
                    # DEBUG LOG
                    f"value_list - Resposta JSON: {response_json} para URL: {full_url}")
            except json.JSONDecodeError as e:
                logging.error(
                    f"value_list - Erro ao decodificar JSON: {e}. Resposta: {response.text} para URL: {full_url}")
                print(
                    "Erro ao decodificar JSON. Consulte o arquivo de log para detalhes.")
        else:
            logging.debug(
                # DEBUG LOG
                f"value_list - Resposta (não JSON): {response.text} para URL: {full_url}")

    except requests.exceptions.RequestException as e:
        global api_error_count
        api_error_count += 1
        logging.error(
            f"value_list - Erro na requisição: {e}. Resposta: {getattr(e.response, 'text', 'N/A')} para URL: {full_url}")
        print(f"Erro na requisição: {e}")
        if e.response:
            print(f"Conteúdo da resposta: {e.response.text}")
    except Exception as e:
        logging.error(f"value_list - Erro geral: {e} para URL: {full_url}")
        print(f"Ocorreu um erro geral: {e}")


def process_element(element: Dict[str, Any], env_id: str, field_name: str, already_sent_urls: set) -> None:
    """
    Processa um único elemento do arquivo Excel.
    (Com logging e contadores adicionados)
    """
    global sent_urls_count, skipped_urls_count  # Access global counters
    try:
        if not element.get('valor'):
            return

        value = element['valor']
        acronym = element.get('sigla')
        parent_id = element.get('filtro')

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

        # Debug log before uniqueness check
        logging.debug(f"process_element - URL gerada: {full_url}")

        with lock:
            if full_url not in already_sent_urls:
                # Debug log before sending
                logging.debug(
                    f"process_element - URL nova, enviando: {full_url}")
                print(f"Enviando nova URL: {full_url}")  # Console output
                value_list(env_id, field_name, value, acronym, parent_id)
                already_sent_urls.add(full_url)
                sent_urls_count += 1  # Increment sent counter
                # Debug log after sending
                logging.debug(
                    f"process_element - URL enviada e adicionada: {full_url}")
            else:
                skipped_urls_count += 1  # Increment skipped counter
                logging.info(
                    # INFO LOG
                    f"process_element - URL já enviada: {full_url}. Ignorando.")
                # Console output
                print(f"URL já enviada: {full_url}. Ignorando.")

    except Exception as e:
        logging.error(
            f"process_element - Erro ao processar elemento: {element}. Erro: {e}")
        print(f"Ocorreu um erro ao processar um elemento. Consulte o arquivo de log para mais detalhes.")


def excel_row_generator(file_path: str, nrows: int = 1000, skiprows: int = 0):
    """
    Gera linhas do arquivo Excel em partes para otimizar o uso de memória.
    (Com logging DEBUG para cada linha gerada)
    """
    try:
        row_index_base = skiprows  # Keep track of the base index for logging
        while True:
            df = pd.read_excel(file_path, nrows=nrows,
                               skiprows=skiprows, engine='openpyxl')
            if df.empty:
                break
            for index, row in df.iterrows():
                row_dict = row.to_dict()
                row_number = index + skiprows  # Calculate the actual row number
                logging.debug(
                    # DEBUG LOG with row number
                    f"excel_row_generator - Gerando linha {row_number}: {row_dict}")
                yield row_dict
            skiprows += nrows
    except FileNotFoundError:
        print("O arquivo Excel não existe.")
    except Exception as e:
        logging.error(f"excel_row_generator - Erro ao ler arquivo Excel: {e}")
        print(f"Ocorreu um erro ao ler o arquivo Excel. Consulte o arquivo de log para mais detalhes.")


def main():
    """
    Função principal para ler o arquivo Excel e processar os elementos em paralelo.
    """
    global sent_urls_count, skipped_urls_count, api_error_count  # Access global counters
    already_sent_urls = set()
    row_count = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        futures = []
        for element in excel_row_generator(FILE_PATH):
            row_count += 1
            future = executor.submit(process_element, element,
                                     environment_id, field_name, already_sent_urls)
            futures.append(future)

        concurrent.futures.wait(futures)

    processed_count = len(already_sent_urls)
    print(f"Total rows in Excel: {row_count}")
    print(
        f"Total rows processed and sent to API (unique URLs): {processed_count}")
    # Counter output
    print(f"URLs Ignoradas (Duplicadas): {skipped_urls_count}")
    print(f"Erros na API: {api_error_count}")  # Counter output
    print("Script finished.")
    # IMPORTANT MESSAGE
    # Changed log file name
    print("Verifique o arquivo de log 'meu_log_debugged.txt' para detalhes e diagnóstico.")


if __name__ == "__main__":
    main()

# --- END OF FILE list_values_debug_refactored.py ---
