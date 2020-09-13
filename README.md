# Exercice d'évaluation pour le poste Inria / AP-HP

L'objectif de ce repository est de répondre à un exercice de mise en situation pour le poste Inria / AP-HP.

Nous utiliserons la base de données `data.db` qui contient deux tables : 
- une table de patients contenant des informations pour chacun d'entre-eux (nom, prénom, age, date de naissance, adresse, code postal, état, etc.) ;
- une table de tests PCR (test utlisé pour le diagnostic du Covid 19).

Ces données sont **synthétiques** et correspondent à la géographie de l'Australie.

## Dépendances

Ce projet requiert les librairies suivantes (toutes présentes dans l'écosystème PyPi) : 

- genderize
- pandas
- numpy
- jellyfish
- fuzzywuzzy
- python-levenshtein
- matplotlib
- descartes
- geopandas

Il est possible d'installer directement ces dépendances via le fichier `requirements.txt` grâce à la commande suivante :

```bash

pip install -r requirements.txt

```

## Mise en qualité des données 

Le premier jupyter notebook traite des problèmes
de qualité de données (données incohérentes, données manquantes, et données dupliquées).


### Données manquantes et incohérentes

La première partie de ce notebook met en évidences la part de valeurs manquantes ainsi que la cohérence de chacune des variables.

Plus précisément, on vérifie les éléments suivants :

- Le pourcentage de valeurs manquantes pour chacune des variables.

- La cohérence entre la date de naissance des patients et l'âge renseigné.

- La cohérence entre le code postal et l'état renseigné.

- Les erreurs de typographie concernant les modaltés de plusieurs variables (`suburb`, `state`, `address`, etc.)


### Gestion des données dupliquées

La seconde partie vise à supprimer les doublons. La difficulté réside dans le fait que les doublons ne sont pas identiques. On peut imaginer des problèmes de saisies de données (typos, information manquante etc.).

Pour répondre à cet objectif nous utiliserons la fonction `detect_duplicates` (de la classe `Duplicates`) qui prend
en parametère le dataframe `df_patient` et qui renvoit
un nouveau dataframe après suppression des doublons. 

L'attribut `removed` estime le pourcentage de données dupliquées.

Le procédé de déduplication consiste à : 

- Retenir tous les doublons à partir d'une variable distinguant au mieux un patient (par exemple le numéro de téléphone).

- Choisir un individu de référence (si possible dans la table `pcr`).

- Sélectionner les doublons selon un seuil de ressemblance (nombre d'autres valeurs identiques) et considérer que les valeurs très proches (potentiellement dues à une erreur de typographie) sont identiques.

- Recommencer le procédé pour d'autres variables (nom et prénom, adresse complète, etc.)

- Retirer les données dupliquées et les comptabiliser.


## Exploratory Data Analysis (EDA)

Ce second notebook a pour objectif de nettoyer la nouvelle base de données dé-dédupliquée et de produire une analyse exploratoire des données.

### Nettoyage des variables

Les actions suivantes sont effectuées :

- Grâce à la variable `given_name` il est possible d'inférer le genre du patient (homme ou femme).


- Création d'une variable tranche d'âge (pour mieux gérer les incohérences entre âge renseigné et date de naissance).

- Retenir les valeurs de la variable `state` seulement lorsqu'elles concordent avec la variable `postcode`.

### Analyse

La dernière étape consiste à la visualiation (carte, histogramme, graphique, etc.) afin de discuter de la prévalence de la maladie
dans la population.


## Aures modules


Les notebook précédents utilisent les modules `map`, `utils` et `tests`.

- `utils` : ce module contient des sous-modules pour appliquer les étapes de :

    - mise en cohérence des données (`coherence`) ;
    - d'ajout de données externes (`data`) ;
    - de visualisation (`eda`)
    - de déduplication (`deduplicate`)
    - de lecture des tables (`getting_started`)

- `map`: ce module contient la carte pour l'étape de visualisation.

- `tests` : ce module permet de tester la qualité de la fonction `detect_duplicate`.
