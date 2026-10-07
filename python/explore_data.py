import pandas as pd
from pathlib import Path

CSV_PATH = Path("data/raw/regularite_tgv.csv")

df = pd.read_csv(CSV_PATH, sep=";", encoding="utf-8")

print("=== DIMENSIONS ===")
print(f"{df.shape[0]} lignes, {df.shape[1]} colonnes\n")

print("=== COLONNES ET TYPES ===")
print(df.dtypes, "\n")

print("=== APERÇU (5 premières lignes) ===")
print(df.head().to_string(), "\n")

print("=== VALEURS MANQUANTES (%) ===")
print((df.isna().mean() * 100).round(1).sort_values(ascending=False), "\n")

print(f"=== DOUBLONS COMPLETS : {df.duplicated().sum()} ===\n")

print("=== STATISTIQUES NUMÉRIQUES ===")
print(df.describe().T.to_string())