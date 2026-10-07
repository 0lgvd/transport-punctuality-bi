# Rapport de qualité des données

- Lignes brutes : **12907**
- Doublons sur la clé métier (mois, service, gare_depart, gare_arrivee) supprimés : **0**
- Lignes après nettoyage : **12907**
- Colonnes exclues (vides ou texte libre) : commentaire_annulations, commentaire_retards_depart, commentaire_retards_arrivee
- Lignes avec `qualite_ok = True` : **12370** (95.8 %)
- `retard_moyen_retard_sup_15_min` identique à `retard_moyen_tous_arrivee_min` dans **16.5 %** des lignes

## Anomalies détectées (lignes marquées, non supprimées)

| Contrôle | Lignes | % |
|---|---|---|
| flag_comptage_negatif | 43 | 0.33 |
| flag_moyenne_aberrante | 18 | 0.14 |
| flag_circulations_ou_duree_nulle | 73 | 0.57 |
| flag_volumes_incoherents | 63 | 0.49 |
| flag_seuils_incoherents | 357 | 2.77 |
| flag_causes_hors_100 | 89 | 0.69 |