USE SCHEMA TRANSPORT_BI.MART;

-- Dimensions
CREATE OR REPLACE TABLE DIM_DATE AS
SELECT DISTINCT
  YEAR(mois) * 100 + MONTH(mois) AS date_key,
  mois,
  YEAR(mois)    AS annee,
  QUARTER(mois) AS trimestre,
  MONTH(mois)   AS mois_num
FROM TRANSPORT_BI.RAW.REGULARITE_RAW;

CREATE OR REPLACE TABLE DIM_SERVICE AS
SELECT ROW_NUMBER() OVER (ORDER BY service) AS service_key, service
FROM (SELECT DISTINCT service FROM TRANSPORT_BI.RAW.REGULARITE_RAW);

-- Une seule dimension gare, utilisée deux fois dans la table de faits (départ / arrivée)
CREATE OR REPLACE TABLE DIM_GARE AS
SELECT ROW_NUMBER() OVER (ORDER BY nom_gare) AS gare_key, nom_gare
FROM (
  SELECT gare_depart  AS nom_gare FROM TRANSPORT_BI.RAW.REGULARITE_RAW
  UNION
  SELECT gare_arrivee AS nom_gare FROM TRANSPORT_BI.RAW.REGULARITE_RAW
);

-- Table de faits : grain = mois x service x gare de départ x gare d'arrivée
CREATE OR REPLACE TABLE FACT_REGULARITE AS
SELECT
  YEAR(r.mois) * 100 + MONTH(r.mois) AS date_key,
  s.service_key,
  gd.gare_key AS gare_depart_key,
  ga.gare_key AS gare_arrivee_key,
  r.duree_moyenne_min,
  r.nb_circulations_prevues,
  r.nb_annules,
  r.nb_circulations_effectives,
  r.nb_retard_depart,
  r.nb_retard_arrivee,
  r.nb_retard_sup_15,
  r.nb_retard_sup_30,
  r.nb_retard_sup_60,
  -- Mesures additives : permettent des moyennes pondérées correctes à tout niveau d'agrégation
  r.retard_moyen_tous_depart_min  * r.nb_circulations_effectives AS retard_total_depart_min,
  r.retard_moyen_tous_arrivee_min * r.nb_circulations_effectives AS retard_total_arrivee_min,
  r.qualite_ok
FROM TRANSPORT_BI.RAW.REGULARITE_RAW r
JOIN DIM_SERVICE s ON s.service    = r.service
JOIN DIM_GARE gd   ON gd.nom_gare  = r.gare_depart
JOIN DIM_GARE ga   ON ga.nom_gare  = r.gare_arrivee;

-- Contrôles d'intégrité
SELECT COUNT(*) AS nb_faits FROM FACT_REGULARITE;  -- attendu : 12907
SELECT COUNT(*) AS faits_sans_date
FROM FACT_REGULARITE f LEFT JOIN DIM_DATE d ON d.date_key = f.date_key
WHERE d.date_key IS NULL;   -- attendu : 0