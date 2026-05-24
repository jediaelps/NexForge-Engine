# Importa biblioteca JSON
import json


# Classe responsável por carregar configurações
class ConfigLoader:

    # Carrega arquivo de configuração
    @staticmethod
    def load_config(file_path):

        # Abre o arquivo JSON
        with open(file_path, "r", encoding="utf-8") as file:

            # Retorna os dados do JSON
            return json.load(file)