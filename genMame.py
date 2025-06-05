import os
import sys
import configparser
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Config files
COLOR_INIS = [
    'ledspicer-arcade-colors.ini',
    'ledblinky-arcade-colors.ini',
    'goldo-systems-colors.ini'
]
CONTROLS_INI = 'ledblinky-arcade-controls.ini'
OUTPUT_DIR = 'mame'

# NeoGeo ROM set
NEOGEO_ROMS = {
    '2020bb', '3countb', 'afighters', 'afighters2', 'aggressors',
    'alpham2', 'androdun', 'artoffight', 'bangbead', 'basebstars2',
    'basebpro', 'battlefs', 'blazingst', 'bluesjour', 'breakers',
    'breakrev', 'burningf', 'captomaday', 'crossswd', 'cyberlip',
    'ddragon', 'eightman', 'feast2', 'fatalfury', 'fatalfury2',
    'ffight2', 'ffightsp', 'fightfev', 'galaxyfg', 'ganryu',
    'garou', 'ghostpil', 'goalgoal', 'gururin', 'ironclad',
    'karnovr', 'kotm', 'kotm2', 'kizuna', 'lastres',
    'lgbowl', 'joemacr', 'magdrop2', 'magdrop3', 'maglord',
    'matrim', 'mslug', 'mslug2', 'mslug3', 'mslug4',
    'mslug5', 'mslugx', 'mexport', 'mutnat', 'nam1975',
    'neobombe', 'neodrift', 'neomrdo', 'neoturf', 'ngcup98',
    'nightd', 'ninjak', 'ninjams', 'overtop', 'pbot',
    'pgoal', 'poching', 'popbounc', 'spikes2', 'psio2',
    'pulstar', 'puzloop', 'puzloop2', 'puzlopn', 'puzlopnr',
    'puzzled', 'rotd', 'ragnagrd', 'rbffspec', 'rbff2',
    'rbffsp', 'rhero', 'roboarmy', 'samsho', 'samsho2',
    'samsho3', 'samsho4', 'samsho5', 'samsh5sp', 'savage',
    'sengoku', 'sengoku2', 'sengoku3', 'stoktroo', 'stoktroo2',
    'svcchaos', 'socbrawl', 'spinmast', 'stakevn', 'stakev2',
    'streetho', 'strik194', 'dodgebal', 'sskick', 'sskick2',
    'sskick3', 'tecmo96', 'kof2000', 'kof2001', 'kof2002',
    'kof2003', 'kof94', 'kof95', 'kof96', 'kof97',
    'kof98', 'kof99', 'lastblad', 'lastbld2', 'superspy',
    'ult11', 'thrash', 'tophuntr', 'tophuntr2', 'twinklest',
    'viewpoin', 'vf', 'waku7', 'windjamm', 'wh1',
    'wh2', 'wh2j', 'whp', 'zedblade', 'zupapa'
}

# Static positions (grid: top row then bottom row)
STATIC_POSITIONS = {
    '4': (30, 40), '3': (50, 40), '5': (70, 40), '7': (90, 40),
    '1': (30, 60), '2': (50, 60), '6': (70, 60), '8': (90, 60),
}

# Display layouts (top row then bottom row)
PANEL_IDS = {
    '2-Button': ['1', '2'],
    '4-Button': ['4', '3', '1', '2'],
    '6-Button': ['4', '3', '5', '1', '2', '6'],
    '8-Button': ['4', '3', '5', '7', '1', '2', '6', '8'],
}

# NeoGeo special mappings
NEO_GAMEBTN_MAP = {
    '2-Button': {'1': 'A', '2': 'B'},
    '4-Button': {'4': 'A', '3': 'B', '1': 'C', '2': 'D'},
    '6-Button': {'4': 'A', '3': 'B', '5': 'C', '1': 'D', '2': 'E', '6': 'F'},
    '8-Button': {'4': 'A', '3': 'B', '5': 'C', '7': 'D',
                 '1': 'E', '2': 'F', '6': 'G', '8': 'H'},
}
NEO_BUTTON_COLORS = {
    'A': 'Red', 'B': 'Yellow', 'C': 'Green', 'D': 'Blue',
    'E': 'Magenta', 'F': 'Cyan', 'G': 'Orange', 'H': 'Pink'
}

# RetroBat controller map
RB_CONTROLLER_MAP = {
    '1': 'A', '2': 'B', '3': 'X', '4': 'Y',
    '5': 'PAGEUP', '6': 'PAGEDOWN', '7': 'L2', '8': 'R2'
}

START_POS = (85, 90)
COIN_POS = (95, 90)
JOYSTICK_DEFAULT_COLOR = 'Gray'

# Load configurations
def load_configurations():
    color_cfg = configparser.ConfigParser()
    color_cfg.optionxform = str
    color_cfg.read(COLOR_INIS)

    func_cfg = configparser.ConfigParser(strict=False)
    func_cfg.optionxform = str
    func_cfg.read(CONTROLS_INI)

    return color_cfg, func_cfg

# Safe get
def get_value(cfg, section, option, fallback):
    try:
        return cfg.get(section, option)
    except:
        return fallback

# Pretty-print XML
def prettify_xml(elem):
    rough = ET.tostring(elem, 'utf-8')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent='  ', encoding='utf-8')

# Generate XML for one ROM
def generate_xml_for_rom(rom, color_cfg, func_cfg):
    rom_key = rom.lower()
    is_neo = (rom_key in NEOGEO_ROMS)
    panel_map = PANEL_IDS

    # Determine color section
    section = 'neogeo' if is_neo else rom_key
    cfg_section = next((s for s in color_cfg.sections() if s.lower() == section), None)

    # Determine default panel and build func_map_phys = {phys: (fonction, couleur)}
    default_panel = '2-Button'
    func_map_phys = {}
    if cfg_section and not is_neo:
        btn_opts = [k for k in color_cfg.options(cfg_section) if k.startswith('P1_BUTTON')]
        max_btn = max((int(k.replace('P1_BUTTON','')) for k in btn_opts), default=0)
        default_panel = (
            '2-Button' if max_btn <= 2 else
            '4-Button' if max_btn <= 4 else
            '6-Button' if max_btn <= 6 else
            '8-Button'
        )
        # → Si ≤ 4 boutons, on impose l’ordre phys=A,B,Y,X → ['1','2','4','3']
        if max_btn <= 4:
            phys_order = ['1','2','4','3'][:max_btn]
        elif max_btn <= 6 and max_btn > 4:
            phys_order = ['3','4','5','1','2','6'][:max_btn]
        else:
            # Pour 6 ou 8 boutons, on prend top→bottom
            phys_order = PANEL_IDS[default_panel][:max_btn]
        for idx, phys in enumerate(phys_order, start=1):
            func = get_value(func_cfg, rom_key, f'P1_BUTTON{idx}', 'None')
            if func != 'None':
                col = get_value(color_cfg, cfg_section, f'P1_BUTTON{idx}', 'Gray')
                func_map_phys[phys] = (func, col)

    # Build XML tree
    system = ET.Element('system', name='arcade')
    game_el = ET.SubElement(system, 'game', name=rom, rom=rom)
    layouts_el = ET.SubElement(game_el, 'layouts')

    # Joystick color (noir si NeoGeo, sinon depuis l'INI)
    joy_col = get_value(color_cfg, cfg_section, 'P1_JOYSTICK', JOYSTICK_DEFAULT_COLOR) if cfg_section else JOYSTICK_DEFAULT_COLOR
    joystick_color = 'Black' if is_neo else joy_col

    for layout_type, ids in panel_map.items():
        lay = ET.SubElement(layouts_el, 'layout', panelButtons=str(len(ids)), type=layout_type)
        ET.SubElement(lay, 'joystick', color=joystick_color)

        # --- Cas 2-Button : on prend les 2 premières touches actives
        if not is_neo and layout_type == '2-Button':
            active_two = []
            # On parcourt l’ordre top→bottom de default_panel
            for phys in PANEL_IDS[default_panel]:
                if phys in func_map_phys:
                    active_two.append((phys,) + func_map_phys[phys])
                if len(active_two) == 2:
                    break

            # Créer exactement deux boutons dans PHYS '1' et '2' (bottom-left, bottom-center)
            for idx, (phys, func, color) in enumerate(active_two, start=1):
                x, y = STATIC_POSITIONS[str(idx)]  # '1'→(30,60), '2'→(50,60)
                controller = RB_CONTROLLER_MAP[phys]
                game_btn = ('L1' if controller == 'PAGEUP'
                            else 'R1' if controller == 'PAGEDOWN'
                            else controller)
                ET.SubElement(
                    lay, 'button',
                    id=str(idx), physical=phys,
                    controller=controller, gameButton=game_btn,
                    x=str(x), y=str(y), color=color, function=func
                )
            # Si on a moins de 2 touches actives, ajouter un bouton « None » dans la ou les cases restantes
            for idx in range(len(active_two) + 1, 3):
                x, y = STATIC_POSITIONS[str(idx)]
                controller = RB_CONTROLLER_MAP[str(idx)]
                game_btn = ('L1' if controller == 'PAGEUP'
                            else 'R1' if controller == 'PAGEDOWN'
                            else controller)
                ET.SubElement(
                    lay, 'button',
                    id=str(idx), physical=str(idx),
                    controller=controller, gameButton=game_btn,
                    x=str(x), y=str(y), color='Black', function='None'
                )

        else:
            # --- Pour 4, 6, 8 boutons (ou NeoGeo) : on parcourt simplement ids
            for phys in ids:
                x, y = STATIC_POSITIONS[phys]
                if is_neo:
                    mapping = NEO_GAMEBTN_MAP.get(layout_type, {})
                    letter = mapping.get(phys)
                    if letter:
                        func = get_value(func_cfg, 'neogeo',
                                        f'P1_BUTTON{list(mapping.values()).index(letter)+1}', 'None')
                        color = NEO_BUTTON_COLORS.get(letter, 'Black')
                    else:
                        func = 'None'
                        color = 'Black'
                    controller = RB_CONTROLLER_MAP[phys]
                    game_btn = letter or 'NONE'
                else:
                    func, color = func_map_phys.get(phys, ('None', 'Black'))
                    controller = RB_CONTROLLER_MAP[phys]
                    game_btn = ('L1' if controller == 'PAGEUP'
                                else 'R1' if controller == 'PAGEDOWN'
                                else controller)

                ET.SubElement(
                    lay, 'button',
                    id=phys, physical=phys,
                    controller=controller, gameButton=game_btn,
                    x=str(x), y=str(y), color=color, function=func
                )

        # Ajouter toujours START & COIN
        sp = str(len(ids) + 1)
        cp = str(len(ids) + 2)
        ET.SubElement(
            lay, 'button',
            id='START', physical=sp,
            controller='START', gameButton='START',
            x=str(START_POS[0]), y=str(START_POS[1]),
            color=get_value(color_cfg, cfg_section, 'P1_START', 'White'),
            function='Start'
        )
        ET.SubElement(
            lay, 'button',
            id='COIN', physical=cp,
            controller='SELECT', gameButton='COIN',
            x=str(COIN_POS[0]), y=str(COIN_POS[1]),
            color=get_value(color_cfg, cfg_section, 'P1_COIN', 'White'),
            function='Coin'
        )

    return system

# Main
if __name__ == '__main__':
    color_cfg, func_cfg = load_configurations()
    func_roms = {s.lower() for s in func_cfg.sections() if s not in ('DEFAULT','neogeo')}
    all_roms = sorted(func_roms.union(NEOGEO_ROMS))
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for rom in all_roms:
        xml_root = generate_xml_for_rom(rom, color_cfg, func_cfg)
        xml_bytes = prettify_xml(xml_root)
        with open(os.path.join(OUTPUT_DIR, f'{rom}.xml'), 'wb') as f:
            f.write(xml_bytes)
    print('Génération terminée !')
