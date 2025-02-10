import json
import pandas as pd
import os


def read_json_files(json_folder):
    data = []

    for filename in os.listdir(json_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(json_folder, filename)
            try:
                with open(file_path, 'r') as file:
                    json_data = json.load(file)
                    for item in json_data.values():  # Iterar sobre os valores do dicionário
                        conjunto_componente = item.get(
                            'conjunto_componente', {})
                        filtro, valor = conjunto_componente.get(
                            'filtro'), conjunto_componente.get('valor')
                        if filtro and valor:
                            data.append({'filtro': filtro, 'valor': valor})
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON em {file_path}: {e}")

    return data


# Caminho da pasta onde estão os arquivos JSON
json_folder = 'data/conjunto_componente'

# Lê os dados dos arquivos JSON
data = read_json_files(json_folder)

# Cria um DataFrame e salva em um arquivo Excel, se houver dados
if data:
    df = pd.DataFrame(data)
    output_file = 'output.xlsx'
    df.to_excel(output_file, index=False)
    print(f'Arquivo Excel "{output_file}" criado com sucesso!')
else:
    print("Nenhum dado encontrado nos arquivos JSON.")
