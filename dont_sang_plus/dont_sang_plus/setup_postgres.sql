-- Script de création de la base de données PostgreSQL pour Don Sang Plus
-- À exécuter en tant que superuser postgres

-- Créer l'utilisateur
CREATE USER dont_sang_user WITH PASSWORD 'dontsang2025';

-- Créer la base de données
CREATE DATABASE dont_sang_plus_db
    WITH 
    OWNER = dont_sang_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Donner tous les privilèges à l'utilisateur
GRANT ALL PRIVILEGES ON DATABASE dont_sang_plus_db TO dont_sang_user;

-- Se connecter à la base de données
\c dont_sang_plus_db

-- Donner les privilèges sur le schéma public
GRANT ALL ON SCHEMA public TO dont_sang_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dont_sang_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dont_sang_user;

-- Afficher un message de confirmation
\echo 'Base de données dont_sang_plus_db créée avec succès!'
\echo 'Utilisateur: dont_sang_user'
\echo 'Mot de passe: dontsang2025'
\echo 'Host: localhost'
\echo 'Port: 5432'
