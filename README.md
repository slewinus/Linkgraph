# Change Log et Fonctionnalités pour les Utilisateurs Finaux

### Application : Report Generator 📝
### Version : BETA V0.2.0 🚀
### Date de Publication : 20 Juin 2024

---

## Change Log 🛠️

### BETA V0.2.0
- **Nouvelle fonctionnalité** : Sélection de la feuille Excel lors de l'ouverture du fichier.
- **Nouvelle fonctionnalité** : Option pour générer des rapports PDF.
- **Nouvelle fonctionnalité** : Sélection des types de graphiques pour plusieurs colonnes.
- **Amélioration** : Les colonnes "Unnamed" ne sont plus sélectionnables.
- **Amélioration** : Interface utilisateur mise à jour avec des boutons en bas de l'interface.
- **Correction de bugs** : Correction des erreurs de génération de PDF.
- **Correction de bugs** : Correction des erreurs liées aux colonnes GPS dans les cartes interactives.

### BETA V0.1.9
- **Nouvelle fonctionnalité** : Génération de cartes interactives 🗺️.
- **Nouvelle fonctionnalité** : Sélection multiple de colonnes pour les graphiques 📊.
- **Nouvelle fonctionnalité** : Dialog de sélection des types de graphiques 🎨.
- **Amélioration** : Interface utilisateur améliorée pour une meilleure navigation 🧭.
- **Amélioration** : Gestion des erreurs améliorée avec des messages d'erreur plus détaillés 🚧.
- **Correction de bugs** : Correction de divers bugs mineurs liés au chargement de fichiers Excel 🐛.
- **Mise à jour** : Ajout d'un nouveau logo et d'icônes de meilleure qualité 🌟.

---

## Fonctionnalités 🌟

### 1. **Ouverture de Fichiers Excel**
- Permet à l'utilisateur de sélectionner et d'ouvrir un fichier Excel (.xlsx, .xls, .xlsm) 📂.
- Charge les données du fichier sélectionné et affiche les colonnes disponibles 📋.
- Nouvelle option pour sélectionner la feuille Excel spécifique lors de l'ouverture du fichier.

### 2. **Sélection du Dossier de Sortie**
- Permet à l'utilisateur de choisir un dossier où les rapports générés seront enregistrés 🗂️.
- Affiche le chemin du dossier sélectionné dans la console pour confirmation 🖥️.

### 3. **Sélection de Colonnes et Types de Graphiques**
- Affiche une boîte de dialogue permettant de sélectionner les colonnes et de choisir le type de graphique à générer pour chaque colonne 🖌️.
- Types de graphiques disponibles : Camembert 🥧, Histogramme 📊, Graphique Linéaire 📈, Nuage de Points ☁️.
- Les colonnes "Unnamed" ne sont plus sélectionnables.
- Option pour générer des rapports PDF incluse.

### 4. **Génération de Rapports PDF**
- Génère des graphiques pour les colonnes sélectionnées selon les types choisis et les sauvegarde en tant qu'images 📷.
- Crée un rapport PDF incluant tous les graphiques générés avec des titres et des informations de date 📅.
- Ajoute un logo et des informations de configuration au PDF 🖼️.
- Option pour activer ou désactiver la génération de PDF.

### 5. **Génération de Cartes Interactives**
- Détecte les colonnes latitude et longitude dans les données pour créer une carte interactive 🌍.
- Utilise les données supplémentaires pour enrichir les informations des marqueurs sur la carte 📍.
- Sauvegarde la carte interactive au format HTML dans le dossier de sortie sélectionné 📁.

### 6. **Interface Utilisateur Personnalisée**
- Utilise `customtkinter` pour une interface utilisateur moderne et réactive 🖌️.
- Propose une navigation simplifiée avec des cadres et des boutons bien disposés 📐.
- Les boutons sont maintenant placés en bas de l'interface pour une meilleure accessibilité.

### 7. **Gestion des Erreurs**
- Affiche des messages d'erreur spécifiques en cas de problème, par exemple si aucun fichier n'est sélectionné ou si aucune colonne n'est choisie pour la génération de graphiques 🚫.
- Logs détaillés pour faciliter le débogage et la résolution des problèmes 🛠️.

---

## Instructions pour l'Utilisateur 📘

1. **Ouvrir un fichier Excel** : Cliquez sur le bouton "Ouvrir le fichier Excel" et sélectionnez votre fichier. 📂
2. **Sélectionner le dossier de sortie** : Cliquez sur "Choisir le dossier de sortie" et choisissez le dossier où vous souhaitez enregistrer vos rapports. 🗂️
3. **Sélectionner la feuille Excel** : Si votre fichier Excel contient plusieurs feuilles, sélectionnez celle que vous souhaitez utiliser.
4. **Sélectionner les colonnes et types de graphiques** : Après avoir chargé les données, sélectionnez les colonnes et les types de graphiques souhaités en utilisant la boîte de dialogue de sélection. 📋🖌️
5. **Générer le rapport** : Cliquez sur "Generer le rappport" pour créer les graphiques et le rapport PDF. 📄
6. **Générer une carte interactive** : Cliquez sur "Generer la carte interactive" pour créer une carte interactive des données GPS si disponibles. 🌍

❗️Attention pour avoir des synthèses de la FTTO c'est à vous de traiter les données en amont. ❗

---

## Instructions d'Installation 📦

1. **Télécharger l'exécutable** : Téléchargez le fichier .exe fourni.
2. **Exécuter le fichier** : Double-cliquez sur le fichier .exe pour lancer l'application. Pas besoin de se prendre la tête avec des installations compliquées ! 🤓

Attention pour le moment le logiciel n'est pas signé par un certificat. Il est donc possible que cela soit detecter comme un virus par Windows. Pas d'inquiétude

---

Pour toute question : https://googlethatforyou.com?q=COMMENT%20FUSIONNER%20DES%20PDF ou xoscar.robertbesle@lintk.fr 📧

---
