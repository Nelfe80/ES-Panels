import os
import configparser
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ————————————————————————————————————————————
# Config file and output directory
SYSTEMS_INI   = 'goldo-systems-colors.ini'
RETROARCH_DIR = 'retroarch'
OUTPUT_DIR    = 'systems'

MACHINE_TO_EMUS = {
    '3do':            ['opera', '4do'],
    '3ds':            ['citra', 'citra2018'],
    'actionmax':      [],
    'adam':           [],
    'advision':       [],
    'amiga1200':      ['puae', 'uae4arm'],
    'amiga4000':      ['puae', 'uae4arm'],
    'amiga500':       ['puae', 'uae4arm'],
    'amigacd32':      ['puae', 'uae4arm'],
    'amigacdtv':      ['puae'],
    'amstradcpc':     ['caprice32'],
    'apfm1000':       [],
    'apple2':         ['apple2'],
    'apple2gs':       ['apple2'],
    'arcadia':        ['mame', 'mess', 'finalburn_neo', 'finalburn_alpha'],
    'archimedes':     ['emuscv'],
    'arduboy':        ['emux_chip8'],
    'astrocade':      ['mame'],
    'atari2600':      ['stella'],
    'atari5200':      ['a5200', 'atari800'],
    'atari7800':      ['prosystem'],
    'atari800':       ['atari800'],
    'atarist':        ['hatari'],
    'atom':           ['nestopia'],
    'atomiswave':     ['fbneo'],
    'bbcmicro':       ['beeb'],
    'c128':           ['vice'],
    'c20':            ['vice'],
    'c64':            ['vice', 'frodo'],
    'camplynx':       ['mame'],
    'cannonball':     ['cannonball'],
    'casloopy':       ['mame'],
    'cave':           ['fbneo'],
    'cavestory':      ['doukutsu-rs'],
    'cdi':            ['same_cdi'],
    'cdogs':          ['cdogs'],
    'cgenius':        ['mame'],
    'channelf':       ['mame'],
    'chihiro':        ['demulw'],
    'coco':           ['coco'],
    'colecovision':   ['blueMSX', 'gearcoleco'],
    'corsixth':       ['corsixth'],
    'cplus4':         ['vice'],
    'cps1':           ['mame_2003'],
    'cps2':           ['mame_2003'],
    'cps3':           ['mame_2003'],
    'crvision':       [],
    'daphne':         ['daphne'],
    'devilutionx':    ['devilutionx'],
    'dinothawr':      ['dinothawr'],
    'doom3':          ['prboom'],
    'dos':            ['dosbox', 'dosbox_pure', 'dosbox_svn'],
    'dreamcast':      ['redream', 'flycast'],
    'easyrpg':        ['easyrpg'],
    'ecwolf':         ['ecwolf'],
    'eduke32':        ['eduke32'],
    'electron':       ['m'],  
    'fbneo':          ['fbneo'],
    'fds':            ['fceumm', 'mesen', 'nestopia', 'higan', 'quicknes'],
    'flash':          ['ffmpeg'],
    'fm7':            ['fmsx'],
    'fmtowns':        [],
    'fpinball':       ['pinballfx'],
    'gaelco':         ['fbneo'],
    'gamate':         ['gambatte'],
    'gameandwatch':   ['emux_sms'],
    'gamecom':        ['blueMSX'],
    'gamecube':       ['dolphin'],
    'gamegear':       ['genesis_plus_gx', 'sms_plus_gx', 'gearsystem'],
    'gamepock':       ['gambatte'],
    'gb':             ['emux_gb', 'gambatte', 'sameboy', 'tgb_dual', 'higan', 'mesen_s'],
    'gb-msu':         ['gambatte'],
    'gb2players':     ['gambatte'],
    'gba':            ['mednafen', 'gpsp', 'meteor', 'mgba', 'visualboyadvance'],
    'gba2players':    ['mednafen', 'mgba'],
    'gbc':            ['emux_gb', 'gambatte', 'sameboy', 'tgb_dual', 'higan', 'mesen_s'],
    'gbc2players':    ['emux_gb', 'gambatte'],
    'gemrb':          ['gemrb'],
    'gmaster':        ['vice'],
    'gp32':           ['quicknes'],
    'gx4000':         ['pce_fast'],
    'gzdoom':         ['gzdoom'],
    'hbmame':         ['mame2003_plus'],
    'hikaru':         ['mame2003_plus'],
    'ikemen':         ['ikemen'],
    'intellivision':  ['freeintv'],
    'jaguar':         ['virtual_jaguar'],
    'jaguarcd':       ['virtual_jaguar'],
    'karaoke':        ['pocketcdg'],
    'lcdgames':       ['emux_chip8'],
    'love':           ['lutro'],
    'lowresnx':       ['lowres_nx'],
    'lutro':          ['lutro'],
    'lynx':           ['mednafen', 'handy'],
    'mame':           ['mame2003_plus', 'mame_2010'],
    'mastersystem':   ['picodrive','genesis_plus_gx','sms_plus_gx','gearsystem'],
    'megadrive':      ['genesis_plus_gx', 'blastem', 'picodrive'],
    'megadrive-msu':  ['genesis_plus_gx'],
    'megaduck':       ['sameduck'],
    'model2':         [],
    'model3':         ['mame_2003'],
    'msx1':           ['fmsx', 'blueMSX'],
    'msx2':           ['fmsx', 'blueMSX'],
    'msx2+':          ['fmsx', 'blueMSX'],
    'msxturbor':      ['fmsx'],
    'mugen':          ['mugen'],
    'multivision':    ['freeintv'],
    'n64':            ['mupen64plus', 'mupen64plus-next', 'paralleln64'],
    'n64dd':          ['mupen64plus'],
    'namco2x6':       ['naomi'],
    'naomi':          ['naomi'],
    'naomi2':         ['naomi2'],
    'nds':            ['desmume', 'desmume_2015', 'melonds'],
    'neogeo':         ['fbneo'],
    'neogeo64':       ['fbneo'],
    'neogeocd':       ['beetle_neogeo'],
    'nes':            ['fceumm', 'nestopia', 'higan', 'emux', 'nestopia_ue', 'quicknes', 'mesen'],
    'ngage':          [],
    'ngp':            ['mednafen-gp2x'],
    'ngpc':           ['gambatte'],
    'o2em':           ['o2em'],
    'openbor':        ['openbor'],
    'openlara':       ['openlara'],
    'pegasus':        [],
    'pet':            ['vice'],
    'pico8':          ['tic80'],
    'pinballfx':      ['pinballfx'],
    'pinballfx2':     ['pinballfx2'],
    'pinballfx3':     ['pinballfx3'],
    'pinballm':       ['pinballm'],
    'pokemini':       ['pokemini'],
    'prboom':         ['prboom'],
    'ps2':            ['play!', 'pcsx2'],
    'psp':            ['ppsspp'],
    'psx':            ['mednafen', 'pcsx_rearmed', 'duckstation'],
    'raze':           [],
    'reminiscence':   ['reminiscence'],
    'saturn':         ['uoyabause', 'mednafen', 'yabasanshiro', 'kronos'],
    'scummvm':        ['scummvm'],
    'sega32x':        ['picodrive'],
    'segacd':         ['genesis_plus_gx', 'picodrive'],
    'segastv':        ['kronos'],
    'sg1000':         ['blueMSX', 'gearsystem'],
    'sgb':            ['bsnes', 'snes9x', 'mesen_s'],
    'snes':           ['bsnes', 'snes9x', 'higan', 'mesen_s'],
    'snes-msu':       ['bsnes_mercury_accuracy', 'bsnes_mercury_balanced', 'bsnes_mercury_performance'],
    'solarus':        ['solarus'],
    'switch':         ['yuzu', 'yuzu_canary'],
    'teknoparrot':    ['teknoparrot'],
    'theodore':       [],
    'ti99':           ['ti99'],
    'tic80':          ['tic80'],
    'triforce':       ['dolphin'],
    'tyrquake':       ['tyrquake'],
    'uzebox':         ['uzem'],
    'vectrex':        ['vecx'],
    'vircon32':       ['vircon32'],
    'virtualboy':     ['mednafen'],
    'vitaquake2':     ['vitaquake2'],
    'vpinball':       ['pinballfx'],
    'wasm4':          ['wasm-4'],
    'wii':            ['dolphin'],
    'wiiu':           ['cemu'],
    'windows':        ['wine'],
    'wswan':          ['mednafen'],
    'wswanc':         ['mednafen'],
    'xbox':           ['xemu'],
    'xbox360':        ['xenia'],
    'zaccariapinball':['pinballfx'],
    'zinc':           ['vice'],
    'zx81':           ['eightone'],
    'zxspectrum':     ['fuse'],
}

# ————————————————————————————————————————————
# Positions fixes (%) par physical ID
STATIC_POSITIONS = {
    '1': (30, 60), '2': (50, 60),
    '3': (30, 40), '4': (50, 40),
    '5': (70, 40), '6': (70, 60),
    '7': (90, 40), '8': (90, 60),
}
START_POS = (85, 90)
COIN_POS  = (95, 90)

# ————————————————————————————————————————————
# Mapping par physical ID → nom de controleur RetroBat
RB_CONTROLLER_MAP = {
    '1': 'A', '2': 'B',
    '3': 'X', '4': 'Y',
    '5': 'PAGEUP',   # L1
    '6': 'PAGEDOWN', # R1
    '7': 'L2',       # L2
    '8': 'R2',       # R2
}

# ————————————————————————————————————————————
# Tableau de correspondance retropad_id → physical ID
# (inverse de la convention ABXY+L1/R1/L2/R2 sur les panels)
RETROPAD_TO_PHYSICAL = {
     0: 'B',  # B
     1: 'Y',  # Y
     2: 'SELECT',
     3: 'START',
     4: 'UP',
     5: 'DOWN',
     6: 'LEFT',
     7: 'RIGHT',
     8: 'A',
     9: 'X',
    10: 'L1',
    11: 'R1',
    12: 'L2',
    13: 'R2',
}
# On retourne uniquement ceux qui correspondent à de vrais boutons arcade
RETROPAD_TO_PHYSICAL = {
    0: '2',  # B  → physical "2"
    1: '4',  # Y  → physical "4"
    8: '1',  # A  → physical "1"
    9: '3',  # X  → physical "3"
   10: '5',  # L1 → physical "5"
   11: '6',  # R1 → physical "6"
   12: '7',  # L2 → physical "7"
   13: '8',  # R2 → physical "8"
}

# ————————————————————————————————————————————
# Définition des panels en termes de retropad_id, dans l'ordre bottom-left→bottom-right→...
PANEL_RETROPAD_IDS = {
    '2-Button': [8, 0],                    # A, B
    '4-Button': [8, 0, 9, 1],              # A, B, X, Y
    '6-Button': [8, 0, 11, 9, 1, 10],      # A, B, R1, X, Y, L1
    '8-Button': [8, 0, 11,13, 9, 1,10, 12], # A, B, R1,R2, X, Y, L1, L2
}

# ————————————————————————————————————————————
# Si un core RetroArch propose plusieurs <group>, on peut préciser
# par système lequel choisir.
GROUP_MAPPING = {
    'megadrive':    'MD Joypad 6 Button',
    'mastersystem': 'MS Joypad 2 Button',
}

def normalize_color(c: str) -> str:
    """Mappe DarkGreen→Green, Green→Lime, sinon passe la chaîne telle quelle."""
    if not c: return 'Gray'
    c0 = c.strip().lower()
    if c0 == 'darkgreen': return 'Green'
    if c0 == 'green':     return 'Lime'
    return c

def prettify_xml(elem: ET.Element) -> bytes:
    rough = ET.tostring(elem, 'utf-8')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ", encoding="utf-8")

def load_system_colors(path: str) -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(path)
    return cfg

def find_emulator_xml(system: str):
    """Retourne le premier fichier <core>.xml existant pour la machine."""
    from glob import glob
    for core in MACHINE_TO_EMUS.get(system, []):
        p = os.path.join(RETROARCH_DIR, f'{core}.xml')
        if os.path.isfile(p):
            return p
    return None

def select_group(root: ET.Element, system: str) -> ET.Element:
    """Choisit le <group> correspondant au panel (ou le premier)."""
    groups = root.findall('.//group')
    target = GROUP_MAPPING.get(system.lower())
    if target:
        for g in groups:
            if g.get('name') == target:
                return g
    return groups[0] if groups else None

def parse_emulator(path: str, system: str) -> dict:
    """
    Parse un core RetroArch, cherche le bon <group>, et construit
    port_map_by_retropad = { retropad_id: {'system_entry', 'value'} }
    """
    tree = ET.parse(path)
    root = tree.getroot()
    grp = select_group(root, system)
    m = {}
    if grp is None:
        return m
    for port in grp.findall('port'):
        ns = port.find('newseq')
        if ns is None: continue
        rid = ns.get('retropad_id')
        if rid is None: continue
        i = int(rid)
        m[i] = {
            'system_entry': ns.get('system_entry'),
            'value':        (ns.text or '').strip()
        }
    return m

def generate_system_xml(system: str, colors: configparser.ConfigParser) -> ET.Element:
    sys_lc = system.lower()
    xml_in = find_emulator_xml(sys_lc)
    port_map = parse_emulator(xml_in, sys_lc) if xml_in else {}

    root    = ET.Element('system', name=system)
    layouts = ET.SubElement(root, 'layouts')

    # couleur du joystick
    joy_col = normalize_color(colors[system].get('P1_JOYSTICK','White'))

    for panel, rid_list in PANEL_RETROPAD_IDS.items():
        n = len(rid_list)
        lay = ET.SubElement(layouts, 'layout',
                            panelButtons=str(n),
                            type=panel)
        ET.SubElement(lay, 'joystick', color=joy_col)

        # — boutons de jeu —
        for idx, rid in enumerate(rid_list, start=1):
            phys = RETROPAD_TO_PHYSICAL.get(rid)
            if not phys:
                continue
            x, y = STATIC_POSITIONS[phys]
            ctrl = RB_CONTROLLER_MAP[phys]
            info = port_map.get(rid, {})
            game_btn = info.get('system_entry') or 'NONE'
            func     = info.get('value')        or 'None'
            col      = normalize_color(colors[system].get(f'P1_BUTTON{phys}','Gray'))

            ET.SubElement(lay, 'button',
                          id=str(idx),
                          physical=phys,
                          controller=ctrl,
                          retropad_id=str(rid),
                          gameButton=game_btn,
                          function=func,
                          x=str(x), y=str(y),
                          color=col)

        # — START —
        s_inf = port_map.get(3, {})
        s_game = s_inf.get('system_entry') or 'START'
        s_func = s_inf.get('value')        or 'Start'
        s_col  = normalize_color(colors[system].get('P1_START','White'))
        ET.SubElement(lay, 'button',
                      id='START',
                      physical=str(n+1),
                      controller='START',
                      retropad_id='3',
                      gameButton=s_game,
                      function=s_func,
                      x=str(START_POS[0]), y=str(START_POS[1]),
                      color=s_col)

        # — COIN (Select) —
        c_inf = port_map.get(2, {})
        c_game = c_inf.get('system_entry') or 'COIN'
        c_func = c_inf.get('value')        or 'Coin'
        c_col  = normalize_color(colors[system].get('P1_COIN','White'))
        ET.SubElement(lay, 'button',
                      id='COIN',
                      physical=str(n+2),
                      controller='SELECT',
                      retropad_id='2',
                      gameButton=c_game,
                      function=c_func,
                      x=str(COIN_POS[0]), y=str(COIN_POS[1]),
                      color=c_col)

    return root

def main():
    cfg = load_system_colors(SYSTEMS_INI)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for system in cfg.sections():
        print(f"… Génération {system} …")
        xml_root = generate_system_xml(system, cfg)
        xml_bytes = prettify_xml(xml_root)
        with open(os.path.join(OUTPUT_DIR, f'{system}.xml'), 'wb') as f:
            f.write(xml_bytes)

    print("Terminé.")

if __name__ == '__main__':
    main()
