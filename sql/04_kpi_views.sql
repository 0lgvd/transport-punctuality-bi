USE SCHEMA TRANSPORT_BI.MART;

-- KPI mensuels (qualité uniquement)
CREATE OR REPLACE VIEW V_KPI_MENSUEL AS
SELECT
  d.mois,
  d.annee,
  SUM(f.nb_circulations_prevues)    AS circulations_prevues,
  SUM(f.nb_annules)                 AS annules,
  SUM(f.nb_circulations_effectives) AS circulations_effectives,
  SUM(f.nb_annules) / NULLIF(SUM(f.nb_circulations_prevues), 0)            AS taux_annulation,
  1 - SUM(f.nb_retard_arrivee) / NULLIF(SUM(f.nb_circulations_effectives), 0) AS taux_ponctualite,
  SUM(f.retard_total_depart_min)  / NULLIF(SUM(f.nb_circulations_effectives), 0) AS retard_moyen_depart_min,
  SUM(f.retard_total_arrivee_min) / NULLIF(SUM(f.nb_circulations_effectives), 0) AS retard_moyen_arrivee_min
FROM FACT_REGULARITE f
JOIN DIM_DATE d ON d.date_key = f.date_key
WHERE f.qualite_ok
GROUP BY d.mois, d.annee;

-- KPI par liaison (pour le top 10 des moins ponctuelles)
CREATE OR REPLACE VIEW V_KPI_LIAISON AS
SELECT
  gd.nom_gare || ' → ' || ga.nom_gare AS liaison,
  SUM(f.nb_circulations_effectives)   AS circulations_effectives,
  1 - SUM(f.nb_retard_arrivee) / NULLIF(SUM(f.nb_circulations_effectives), 0) AS taux_ponctualite,
  SUM(f.nb_annules) / NULLIF(SUM(f.nb_circulations_prevues), 0)               AS taux_annulation,
  SUM(f.retard_total_arrivee_min) / NULLIF(SUM(f.nb_circulations_effectives), 0) AS retard_moyen_arrivee_min
FROM FACT_REGULARITE f
JOIN DIM_GARE gd ON gd.gare_key = f.gare_depart_key
JOIN DIM_GARE ga ON ga.gare_key = f.gare_arrivee_key
WHERE f.qualite_ok
GROUP BY 1
HAVING SUM(f.nb_circulations_effectives) >= 1000;  -- évite les liaisons à faible volume

-- Tests
SELECT * FROM V_KPI_MENSUEL ORDER BY mois DESC LIMIT 12;
SELECT * FROM V_KPI_LIAISON ORDER BY taux_ponctualite ASC LIMIT 10;