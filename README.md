# Arcade Layout XML Specification

Ce README décrit le contexte, les objectifs et la structure du fichier XML de layouts arcade, utilisé par RetroBat/ES, les services d’affichage LED RGB et les themers.

---

## Contexte

- **Plateformes** : RetroBat + EmulationStation (ES).  
- **Problème** : RetroBat propose une configuration manette générique, alors que chaque borne arcade possède un panel unique (1–8 boutons + Start + Coin).  
- **Solution** : créer un standard **XML** de layout par jeu et par machine, chargeable par les themers, injectable dans ES/RetroBat et compatible avec les afficheurs LED.

---

## Objectifs

1. **Flexibilité**  
   - Générer un panel adapté au nombre de boutons de l’utilisateur (1–8 boutons de jeu, plus Start/Coin).  
   - Respecter au mieux la disposition et les couleurs d’origine de chaque borne.  

2. **Sortie XML statique**  
   - Un fichier XML par jeu, utilisé directement par les themers.  

3. **Mapping complet**  
   - **Utilisateur** (panel physique)  
   - **Panel logique arcade** (MAME, MVS…)  
   - **Boutons RetroBat/ES**  
   - Au lancement :  
     1. Lecture du XML et de la config utilisateur (nombre + positions).  
     2. Génération ou override de `es_input.cfg` (avec sauvegarde `es_input_backup.cfg`).  
     3. Transmission des couleurs/positions au service LED.  

4. **Affichage LED**  
   - Envoi au contrôleur LED de `(x, y, color)` par bouton, en cohérence avec le XML.

---

## Critères du layout (non graphique)

Chaque bouton définit :

- **Position relative** : coordonnées `x`, `y` (pour visuel ou LED)  
- **Couleur** : nom ou code (compatibilité LED RGB)  
- **Fonction** : action (ex. `A`, `B`, `Start`, `Coin`, ou `None`)

---

## Processus d’intégration

1. **Récupération de la config utilisateur**  
   - Nombre de boutons de jeu (1–8), positions physiques.  
   - Start, Coin (hotkey/select).  

2. **Correspondance boutons**  
   - Disposition physique générique :  
     ```
       3   4   5   7
       1   2   6   8
       +Start +Select/Hotkey/Coin
     ```  
   - Mappage RetroBat par défaut :  
     - L1 → pageup  
     - R1 → pagedown  

3. **es_input.cfg** (Exemple)  
   ```xml
   <?xml version="1.0"?>
   <inputList>
     <inputConfig type="joystick" deviceName="Generic USB Controller" deviceGUID="">
       <input name="a"        type="button" id="0"  value="1"/>
       <input name="b"        type="button" id="1"  value="1"/>
       <input name="y"        type="button" id="2"  value="1"/>
       <input name="x"        type="button" id="3"  value="1"/>
       <input name="pageup"   type="button" id="4"  value="1"/>
       <input name="pagedown" type="button" id="5"  value="1"/>
       <input name="select"   type="button" id="6"  value="1"/>
       <input name="start"    type="button" id="7"  value="1"/>
       <input name="hotkey"   type="button" id="6"  value="1"/>
       <!-- … axes … -->
     </inputConfig>
   </inputList>
   ```

---

## Mappages RetroBat par défaut

- **8 boutons**  
  ```
    X   Y   L1  R1
    A   B   L2  R2
  ```  
- **Ordre de priorité** (physique → logique RB)  
  ```
    3   4   5   7
    1   2   6   8
  ```  
- **Exemples**  
  - 8 boutons → `3,4,5,7` = `X,Y,L1,R1`  ;  `1,2,6,8` = `A,B,L2,R2`  
  - 6 boutons → `3,4,5` = `X,Y,L1`  ;  `1,2,6` = `A,B,R1`  
  - 4 boutons → `3,4` = `X,Y`  ;  `1,2` = `A,B`  
  - 2 boutons → `1,2` = `A,B`

---

## Cas particuliers NeoGeo

Pour les ROMs NeoGeo, utiliser des dispositions custom et mappages spécifiques :

| Boutons | Disposition logique        |
|:-------:|:---------------------------|
| **2**   | A   B                      |
| **4**   | A   C                      |
|         | B   D                      |
| **6**   | B   C   D                  |
|         | A   –   –                  |
| **8**   | A   B   C   D              |
|         | –   –   –   –              |

Le mapping d’indices (`3,4,5,7 / 1,2,6,8`) s’aligne sur (`A,B,C,D / padding`).

```python
NEOGEO_ROMS = {
  '2020bb','3countb','afighters', … ,'zedblade','zupapa'
}
```

---

## Structure Générale du XML

```xml
<?xml version="1.0" encoding="utf-8"?>
<system name="arcade">
  <game name="IDENTIFIANT" rom="ROM_NAME">
    <layouts>
      <!-- pour chaque N = 1…8 -->
      <layout panelButtons="N" type="N-Button">
        <joystick color="COULEUR_JOYSTICK"/>
        <!-- P1_BUTTON1…P1_BUTTONN -->
        <button id="P1_BUTTON1" physical="1" controller="…" gameButton="P1_BUTTON1"
                x="…" y="…" color="…" function="…"/>
        …
        <button id="P1_START"  physical="N+1" controller="START"  gameButton="START"
                x="85" y="90" color="White" function="Start"/>
        <button id="P1_COIN"   physical="N+2" controller="SELECT" gameButton="COIN"
                x="95" y="90" color="White" function="Coin"/>
      </layout>
    </layouts>
  </game>
</system>
```

---

## Détail des Balises et Attributs

### `<layout>`

- `panelButtons` : nombre de boutons de jeu (hors Start/Coin)  
- `type` : libellé humain (ex. `6-Button`)

### `<joystick>`

- `color` : couleur LED du joystick

### `<button>`

| Attribut     | Description                                                               |
|--------------|---------------------------------------------------------------------------|
| `id`         | Identifiant (ex. `P1_BUTTON1`, `START`, `COIN`)                          |
| `physical`   | Indice physique (1…N)                                                     |
| `controller` | Touche RetroBat/ES (ex. `A`, `SELECT`, `START`)                           |
| `gameButton` | Nom logique dans l’émulateur/ROM                                          |
| `x`, `y`     | Coordonnées relatives (%)                                                 |
| `color`      | Couleur du LED / thème                                                    |
| `function`   | Fonction assignée (ex. `Kick`, `B`, `Start`, `Coin`, ou `None`)           |

> Les boutons **Start** et **Coin** sont ajoutés automatiquement aux indices `N+1` et `N+2`.

---

## Exemple Complet de Layout (4-Button)

```xml
<layout panelButtons="4" type="4-Button">
  <joystick color="Black"/>
  <button id="P1_BUTTON1" physical="1" controller="A"      gameButton="P1_BUTTON1" x="30" y="40" color="Red"    function="A"/>
  <button id="P1_BUTTON2" physical="2" controller="B"      gameButton="P1_BUTTON2" x="50" y="40" color="Yellow" function="B"/>
  <button id="P1_BUTTON3" physical="3" controller="C"      gameButton="P1_BUTTON3" x="30" y="60" color="Green"  function="C"/>
  <button id="P1_BUTTON4" physical="4" controller="D"      gameButton="P1_BUTTON4" x="50" y="60" color="Blue"   function="D"/>
  <button id="P1_START"   physical="5" controller="START"  gameButton="START"      x="85" y="90" color="White" function="Start"/>
  <button id="P1_COIN"    physical="6" controller="SELECT" gameButton="COIN"       x="95" y="90" color="White" function="Coin"/>
</layout>
```

---

## Exploitation

1. **Injection ES**  
   - Parser le XML et générer `es_input.cfg`.  
2. **Affichage LED**  
   - Envoyer chaque `(x, y, color)` au contrôleur LED.  
3. **Thèmes**  
   - Positionner/icôner via `x, y` et colorier selon `color`, lier l’action via `controller`.

---

## Bénéfices

- **Fidélité** à l’original (layout + couleurs)  
- **Flexibilité** (1–8 boutons + Start/Coin)  
- **Interopérabilité** (RetroBat/ES, afficheur LED, themers)

---

> **Astuce** : pour tout nouveau panel ou variante (NeoGeo MVS, Type 2…), ajustez simplement les dictionnaires `LAYOUTS` (positions) et `RB_ORDER` (mappages).
