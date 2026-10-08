-- Environnement
CREATE WAREHOUSE IF NOT EXISTS WH_XS
  WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
USE WAREHOUSE WH_XS;

CREATE DATABASE IF NOT EXISTS TRANSPORT_BI;
CREATE SCHEMA IF NOT EXISTS TRANSPORT_BI.RAW;
CREATE SCHEMA IF NOT EXISTS TRANSPORT_BI.MART;
USE SCHEMA TRANSPORT_BI.RAW;

-- Format de fichier et stage
CREATE OR REPLACE FILE FORMAT FF_CSV
  TYPE = CSV SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  NULL_IF = ('', 'NULL');

CREATE OR REPLACE STAGE STG_REGULARITE FILE_FORMAT = FF_CSV;

-- Table brute
CREATE OR REPLACE TABLE REGULARITE_RAW (
  mois DATE,
  service VARCHAR,
  gare_depart VARCHAR,
  gare_arrivee VARCHAR,
  duree_moyenne_min NUMBER,
  nb_circulations_prevues NUMBER,
  nb_annules NUMBER,
  nb_retard_depart NUMBER,
  retard_moyen_trains_retard_depart_min FLOAT,
  retard_moyen_tous_depart_min FLOAT,
  nb_retard_arrivee NUMBER,
  retard_moyen_trains_retard_arrivee_min FLOAT,
  retard_moyen_tous_arrivee_min FLOAT,
  nb_retard_sup_15 NUMBER,
  retard_moyen_retard_sup_15_min FLOAT,
  nb_retard_sup_30 NUMBER,
  nb_retard_sup_60 NUMBER,
  pct_cause_externe FLOAT,
  pct_cause_infrastructure FLOAT,
  pct_cause_gestion_trafic FLOAT,
  pct_cause_materiel_roulant FLOAT,
  pct_cause_gestion_gare FLOAT,
  pct_cause_voyageurs FLOAT,
  nb_circulations_effectives NUMBER,
  flag_comptage_negatif BOOLEAN,
  flag_moyenne_aberrante BOOLEAN,
  flag_circulations_ou_duree_nulle BOOLEAN,
  flag_volumes_incoherents BOOLEAN,
  flag_seuils_incoherents BOOLEAN,
  flag_causes_hors_100 BOOLEAN,
  qualite_ok BOOLEAN
);