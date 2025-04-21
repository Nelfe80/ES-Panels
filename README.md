# Arcade XML Generator

Ce dépôt contient un script Python qui génère, pour chaque ROM de jeu prise en charge, un fichier XML décrivant :

- Le layout des contrôles (joystick + boutons) sur écran.
- Le mapping des boutons pour EmulationStation / RetroBat (es_input.cfg).
- Les couleurs LED associées, pour pilotage RGB.

---

## 0. Contexte et bases

### RetroBat & EmulationStation

- **RetroBat** est une distribution clé en main pour émulation sur Windows, macOS et Linux, s’appuyant sur **EmulationStation (ES)** pour l’interface graphique.
- ES utilise des fichiers de configuration (`es_input.cfg`) pour mapper chaque bouton physique du pad aux touches virtuelles MAME (par exemple `A`, `B`, `X`, `Y`, `L1`, `R1`, etc.).
- Par défaut, RetroBat propose le mapping suivant pour un panel à 8 boutons :
  - **Première rangée (haut)** : boutons physiques 3,4,5,7 → touches ES `X`, `Y`, `L1`, `R1`
  - **Deuxième rangée (bas)** : boutons physiques 1,2,6,8 → touches ES `A`, `B`, `L2`, `R2`

Exemple dans ES (`es_input.cfg`) :
```xml
<pad index="0" device="0">
  <input name="a" type="button" id="1"/>
  <input name="b" type="button" id="2"/>
  <input name="x" type="button" id="3"/>
  <input name="y" type="button" id="4"/>
  <input name="pageup" type="button" id="5"/>   <!-- phys 5 (L1) -->
  <input name="pagedown" type="button" id="6"/> <!-- phys 6 (R1) -->
  <input name="l2" type="button" id="7"/>
  <input name="r2" type="button" id="8"/>
  <input name="start" type="button" id="9"/>
  <input name="select" type="button" id="10"/>
</pad>
```

### Objectifs du processus

Le script assure :

1. **Standardiser** un layout arcade de 1 à 8 boutons (+ Start, Select/Coin) adapté à la borne de l’utilisateur.
2. **Générer** un XML statique par jeu/machine (`<rom>.xml`) pour les thémers sous ES et pour l’afficheur de LED.
3. **Construire** dynamiquement la configuration MAME (`<rom>.cfg`) dans `bios/mame/cfg` avant lancement du jeu, puis restaurer le backup à la fin de la session.
4. **Piloter** l’afficheur LED RGB en cohérence avec les couleurs de boutons d’origine.

---

## 4. Logique de mapping et d’injection MAME

1. **Récupérer** la configuration utilisateur du panel (nombre de boutons, positions 3 4 5 7 / 1 2 6 8 + Start/Coin) via un fichier `config.ini` du plugin.
2. **Charger** :
   - Le XML `<rom>_inputs.cfg` extrait des ports MAME (toutes les entrées `<port>` existantes).
   - Le XML `<rom>.xml` issu du script (layout + mapping RetroBat).  
3. **Fusionner** ces deux sources pour générer un MAME CFG :
   - Pour chaque `<port tag=":P1" type="P1_BUTTONn">`, on remplace `<newseq>` par la touche ES correspondante via `RB_CONTROLLER_MAP` (voir § Mapping).  
   - Les ports joystick WA/WD/WS/WE sont positionnés selon `STATIC_POSITIONS`.  
4. **Écrire** le fichier `bios/mame/cfg/<rom>.cfg` et conserver `bios/mame/cfg/<rom>_backup.cfg`.

---

## 5. Mapping RetroBat → MAME

Chaque ID physique (1–8) est mappé sur une touche ES (nom ES) puis sur un `KEYCODE_…` dans MAME :

| Phys ID | ES name   | MAME KEYCODE      |
| ------- | --------- | ----------------- |
| 1       | a         | KEYCODE_1PAD      |
| 2       | b         | KEYCODE_2PAD      |
| 3       | x         | KEYCODE_3PAD      |
| 4       | y         | KEYCODE_4PAD      |
| 5       | pageup    | KEYCODE_5PAD      |
| 6       | pagedown  | KEYCODE_6PAD      |
| 7       | l2        | KEYCODE_7PAD      |
| 8       | r2        | KEYCODE_8PAD      |
| START   | start     | KEYCODE_9PAD      |
| COIN    | select    | KEYCODE_5PAD      |

- **pageup** (phys 5) et **pagedown** (phys 6) sont utilisés dans ES pour émuler L1/R1.
---

## 6. Processus complet

1. **Watchdog** du plugin surveille `ESEvent.arg` pour l’événement `game-selected`.
2. **Extraction** du nom de ROM (param3) et chemin de rom.
3. **Génération** du `<rom>.xml` (layout LED + bouton logique).
4. **Lecture** de `<rom>_inputs.cfg` (ports MAME) et fusion via le mapping.
5. **Écriture** de `bios/mame/cfg/<rom>.cfg` + backup.
6. **Lancement** de MAME standalone (mame64) avec la nouvelle config.

---

*Ce README est à jour avec la nouvelle logique d’injection MAME et de génération LED.*

