"""Nettoyage du jeu SNCF "Régularité mensuelle TGV par liaisons"."""
from pathlib import Path
import pandas as pd

RAW_PATH = Path("data/raw/regularite_tgv.csv")
CLEAN_PATH = Path("data/clean/regularite_tgv_clean.csv")
REPORT_PATH = Path("docs/data_quality.md")

RENAME = {
    "Date": "mois",
    "Service": "service",
    "Gare de départ": "gare_depart",
    "Gare d'arrivée": "gare_arrivee",
    "Durée moyenne du trajet": "duree_moyenne_min",
    "Nombre de circulations prévues": "nb_circulations_prevues",
    "Nombre de trains annulés": "nb_annules",
    "Commentaire annulations": "commentaire_annulations",
    "Nombre de trains en retard au départ": "nb_retard_depart",
    "Retard moyen des trains en retard au départ": "retard_moyen_trains_retard_depart_min",
    "Retard moyen de tous les trains au départ": "retard_moyen_tous_depart_min",
    "Commentaire retards au départ": "commentaire_retards_depart",
    "Nombre de trains en retard à l'arrivée": "nb_retard_arrivee",
    "Retard moyen des trains en retard à l'arrivée": "retard_moyen_trains_retard_arrivee_min",
    "Retard moyen de tous les trains à l'arrivée": "retard_moyen_tous_arrivee_min",
    "Commentaire retards à l'arrivée": "commentaire_retards_arrivee",
    "Nombre trains en retard > 15min": "nb_retard_sup_15",
    "Retard moyen trains en retard > 15 (si liaison concurrencée par vol)": "retard_moyen_retard_sup_15_min",
    "Nombre trains en retard > 30min": "nb_retard_sup_30",
    "Nombre trains en retard > 60min": "nb_retard_sup_60",
    "Prct retard pour causes externes": "pct_cause_externe",
    "Prct retard pour cause infrastructure": "pct_cause_infrastructure",
    "Prct retard pour cause gestion trafic": "pct_cause_gestion_trafic",
    "Prct retard pour cause matériel roulant": "pct_cause_materiel_roulant",
    "Prct retard pour cause gestion en gare et réutilisation de matériel": "pct_cause_gestion_gare",
    "Prct retard pour cause prise en compte voyageurs (affluence, gestions PSH, correspondances)": "pct_cause_voyageurs",
}
DROP_COLS = ["commentaire_annulations", "commentaire_retards_depart", "commentaire_retards_arrivee"]
COUNT_COLS = ["duree_moyenne_min", "nb_circulations_prevues", "nb_annules", "nb_retard_depart",
              "nb_retard_arrivee", "nb_retard_sup_15", "nb_retard_sup_30", "nb_retard_sup_60"]
CAUSE_COLS = ["pct_cause_externe", "pct_cause_infrastructure", "pct_cause_gestion_trafic",
              "pct_cause_materiel_roulant", "pct_cause_gestion_gare", "pct_cause_voyageurs"]
KEY = ["mois", "service", "gare_depart", "gare_arrivee"]


def main():
    df = pd.read_csv(RAW_PATH, sep=";", encoding="utf-8")
    n_raw = len(df)

    # 1. Colonnes : vérification puis renommage
    missing = set(RENAME) - set(df.columns)
    if missing:
        raise SystemExit(f"Colonnes introuvables (apostrophes ?) : {missing}")
    df = df.rename(columns=RENAME)
    df = df.drop(columns=DROP_COLS)

    # 2. Types et normalisation
    df["mois"] = pd.to_datetime(df["mois"], format="%Y-%m").dt.date  # 1er jour du mois
    for col in ["service", "gare_depart", "gare_arrivee"]:
        df[col] = df[col].str.strip().str.upper()

    # 3. Doublons sur la clé métier
    n_dup = int(df.duplicated(subset=KEY).sum())
    df = df.drop_duplicates(subset=KEY, keep="first")

    # 4. Colonne dérivée
    df["nb_circulations_effectives"] = df["nb_circulations_prevues"] - df["nb_annules"]

    # 5. Contrôles qualité : ne pas supprimer mais marquer
    flags = pd.DataFrame(index=df.index)
    flags["flag_comptage_negatif"] = (df[COUNT_COLS] < 0).any(axis=1)
    flags["flag_moyenne_aberrante"] = (
        (df["retard_moyen_tous_depart_min"] < -30)
        | (df["retard_moyen_tous_arrivee_min"] < -30)
        | (df["retard_moyen_trains_retard_depart_min"] < 0)
        | (df["retard_moyen_trains_retard_arrivee_min"] < 0)
        | (df["retard_moyen_retard_sup_15_min"] < 0)
    )
    flags["flag_circulations_ou_duree_nulle"] = (df["nb_circulations_prevues"] == 0) | (df["duree_moyenne_min"] == 0)
    flags["flag_volumes_incoherents"] = (
        (df["nb_annules"] > df["nb_circulations_prevues"])
        | (df["nb_retard_arrivee"] > df["nb_circulations_effectives"])
    )
    flags["flag_seuils_incoherents"] = (
        (df["nb_retard_sup_60"] > df["nb_retard_sup_30"])
        | (df["nb_retard_sup_30"] > df["nb_retard_sup_15"])
    )
    somme_causes = df[CAUSE_COLS].sum(axis=1)
    flags["flag_causes_hors_100"] = (df["nb_retard_arrivee"] > 0) & ((somme_causes - 100).abs() > 1)

    df = pd.concat([df, flags], axis=1)
    df["qualite_ok"] = ~flags.any(axis=1)

    # 6. Vérification d'une colonne suspecte
    identiques = ((df["retard_moyen_retard_sup_15_min"] - df["retard_moyen_tous_arrivee_min"]).abs() < 1e-6).mean()

    # 7. Export
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False, encoding="utf-8")

    # 8. Rapport qualité
    lines = [
        "# Rapport de qualité des données", "",
        f"- Lignes brutes : **{n_raw}**",
        f"- Doublons sur la clé métier ({', '.join(KEY)}) supprimés : **{n_dup}**",
        f"- Lignes après nettoyage : **{len(df)}**",
        f"- Colonnes exclues (vides ou texte libre) : {', '.join(DROP_COLS)}",
        f"- Lignes avec `qualite_ok = True` : **{int(df['qualite_ok'].sum())}** "
        f"({df['qualite_ok'].mean() * 100:.1f} %)",
        f"- `retard_moyen_retard_sup_15_min` identique à `retard_moyen_tous_arrivee_min` "
        f"dans **{identiques * 100:.1f} %** des lignes",
        "", "## Anomalies détectées (lignes marquées, non supprimées)", "",
        "| Contrôle | Lignes | % |", "|---|---|---|",
    ]
    for col in flags.columns:
        lines.append(f"| {col} | {int(flags[col].sum())} | {flags[col].mean() * 100:.2f} |")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    print(f"\nFichier nettoyé : {CLEAN_PATH}")


if __name__ == "__main__":
    main()