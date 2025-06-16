# data/inscricoes.py
import pandas as pd
import os

def carregar_inscricoes():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    caminho_csv = os.path.join(base_dir, "Inscricoes.csv")

    try:
        df = pd.read_csv(caminho_csv, sep=';', encoding='utf-16', low_memory=False)
        return df
    except Exception as e:
        print(f"Erro ao carregar inscrições: {e}")
        return None