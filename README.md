# Ponctualité du transport ferroviaire : projet BI

Projet personnel illustrant une chaîne data complète : ETL, modélisation en étoile, qualité de la donnée et dashboard

## Besoin métier (fictif)
La direction souhaite suivre la ponctualité et les annulations par liaison et par période, et identifier les liaisons problématiques

## KPI
- Taux de ponctualité
- Taux d'annulation
- Retard moyen (départ / arrivée)
- Top 10 des liaisons les moins ponctuelles
- Évolution mensuelle

## Architecture
CSV (open data SNCF) → Python/pandas → Snowflake (RAW → MART) → Power BI

## Statut
En cours 