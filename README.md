# Arcade Layout XML Specification

Ce document décrit la structure, la logique et l’utilisation du fichier XML de layouts arcade, utilisé pour piloter RetroBat/ES, l’affichage LED RGB et les thèmes.

---

## 1. Objectif Global

Ce fichier XML a pour but de fournir une **couche standardisée** et **extensible** par jeu d’arcade, permettant de :

1. Décrire le **panel physique** : nombre, position et couleur des boutons montés sur la borne  
2. Décrire le **panel logique** : correspondance entre les boutons physiques et les commandes attendues par RetroBat/ES  
3. Définir les **fonctions** (Start, Coin, actions de jeu) et transmettre ces infos à tous les services (thèmes statiques, injection ES, affichage LED)

Ces spécifications permettent :

- L’écriture automatique du mapping dans `es_input.cfg` au lancement du jeu  
- Le pilotage d’une matrice LED ou de boutons RGB selon les couleurs définies  
- La génération de thèmes statiques positionnant et coloriant les boutons leds correctement  

---

## 2. Structure Générale du Fichier XML

```xml
<?xml version="1.0" encoding="utf-8"?>
<system name="arcade">
  <game name="IDENTIFIANT" rom="NOM_ROM">
    <layouts>
      <layout panelButtons="N" type="N-Button">
        <joystick color="COULEUR_JOYSTICK"/>
        <button …/>      <!-- un bouton par balise -->
        …
        <button id="START" …/>
        <button id="COIN"  …/>
      </layout>
      <!-- autres layouts pour ce jeu -->
    </layouts>
  </game>
  <!-- autres jeux -->
</system>
```

- `<system name="arcade">` : racine, identifie le contexte “borne arcade”  
- `<game>` : définit un jeu ou une machine  
  - `name` : identifiant interne (ex. `mslug`)  
  - `rom` : nom du fichier ROM/émulateur (ex. `mslug`)  
- `<layouts>` : conteneur de toutes les variantes de panel pour ce jeu  
- `<layout>` : une variante selon le nombre de boutons physiques installés  

---

## 3. Détail des Balises et Attributs

### 3.1. `<layout>`

- **`panelButtons`** (entier) : nombre de boutons de jeu physiques (hors Start/Coin).  
- **`type`** (string) : libellé humain (ex. `2-Button`, `4-Button`, …).  

### 3.2. `<joystick>`

- **`color`** (string) : couleur LED du joystick, issue des fichiers `.ini` de couleurs.

### 3.3. `<button>` (chaque bouton de jeu, y compris Start et Coin)

| Attribut     | Description                                                                                  |
|--------------|----------------------------------------------------------------------------------------------|
| `id`         | Identifiant du bouton (ex. `P1_BUTTON1`, `A`, `START`, `COIN`).                              |
| `physical`   | Indice physique (1…N) correspondant à la broche USB/GPIO.                                    |
| `controller` | Touche RetroBat/ES à injecter (ex. `A`, `B`, `START`, `SELECT`).                             |
| `gameButton` | Nom logique dans l’émulateur/ROM (aligné sur le code interne du jeu).                        |
| `x`, `y`     | Coordonnées relatives (%) pour position visuelle ou matrice LED.                             |
| `color`      | Couleur du bouton (LED RGB ou habillage thème).                                              |
| `function`   | Fonction assignée (ex. `A`, `B`, `Start`, `Coin`, ou `None` si non utilisé).                 |

> **Remarque**  
> Les boutons **Start** et **Coin** sont automatiquement ajoutés en fin de panel aux indices `panelButtons+1` et `panelButtons+2`.

---

## 4. Exemple Complet de Fichier

```xml
<?xml version="1.0" encoding="utf-8"?>
<system name="arcade">
  <game name="mslug" rom="mslug">
    <layouts>

      <!-- Layout 2-Button -->
      <layout panelButtons="2" type="2-Button">
        <joystick color="Black"/>
        <button id="P1_BUTTON1" physical="1" controller="A" gameButton="A" x="30" y="60" color="Red"    function="A"/>
        <button id="P1_BUTTON2" physical="2" controller="B" gameButton="B" x="50" y="60" color="Yellow" function="B"/>
        <button id="P1_START"   physical="3" controller="START" gameButton="START" x="85" y="90" color="White" function="Start"/>
        <button id="P1_COIN"    physical="4" controller="SELECT" gameButton="COIN" x="95" y="90" color="White" function="Coin"/>
      </layout>

      <!-- Layout 4-Button -->
      <layout panelButtons="4" type="4-Button">
        <joystick color="Black"/>
        <button id="P1_BUTTON1" physical="1" controller="A" gameButton="A" x="30" y="40" color="Red"    function="A"/>
        <button id="P1_BUTTON2" physical="2" controller="B" gameButton="B" x="50" y="40" color="Yellow" function="B"/>
        <button id="P1_BUTTON3" physical="3" controller="C" gameButton="C" x="30" y="60" color="Green"  function="C"/>
        <button id="P1_BUTTON4" physical="4" controller="D" gameButton="D" x="50" y="60" color="Blue"   function="D"/>
        <button id="P1_START"   physical="5" controller="START" gameButton="START" x="85" y="90" color="White" function="Start"/>
        <button id="P1_COIN"    physical="6" controller="SELECT" gameButton="COIN" x="95" y="90" color="White" function="Coin"/>
      </layout>

      <!-- autres layouts (6-Button, 8-Button…)… -->

    </layouts>
  </game>
</system>
```

---

## 5. Processus d’Exploitation

1. **Injection dans ES**  
   - Parser le XML  
   - Pour chaque `<button>` :  
     - `physical` → broche matérielle  
     - `controller` → clé injectée dans `es_input.cfg`  

2. **Affichage LED**  
   - Pour chaque `<joystick>` et `<button>` :  
     - envoyer `(x, y, color)` au contrôleur LED  

3. **Génération de Thèmes**  
   - Positionner les icônes sur la vue selon `(x, y)`  
   - Appliquer la couleur `color`  
   - Lier l’action à la touche `controller`  

---

### Bénéfices

- **Fidélité** à la disposition et aux couleurs d’origine  
- **Flexibilité** pour 1 à 8 boutons, Start/Coin inclus  
- **Interopérabilité** entre RetroBat/ES, services LED et themers  

> **Astuce** : ajoutez ou ajustez les positions `(x, y)` dans `LAYOUTS` pour tout nouveau panel ou variante de borne (NeoGeo MVS, Type 2, etc.).
