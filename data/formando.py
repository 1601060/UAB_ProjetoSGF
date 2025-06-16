# data/formando.py
import pandas as pd
import os


def carregar_formandos():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(base_dir, "Formandos.csv")

    try:
        df = pd.read_csv(caminho_csv, sep=';', encoding='utf-16', low_memory=False) #Codificação do ficheiro
        return df
    except Exception as e:
        print(f"Erro ao carregar formandos: {e}")
        return None

