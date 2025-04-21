
import os
import configparser
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Config files
COLOR_INIS   = [
    'ledspicer-arcade-colors.ini',
    'ledblinky-arcade-colors.ini',
    'goldo-systems-colors.ini'
]
CONTROLS_INI = 'ledblinky-arcade-controls.ini'
OUTPUT_DIR   = 'arcade'

# Static positions
STATIC_POSITIONS = {
    '1': (30,60),'2':(50,60),'6':(70,60),'8':(90,60),
    '3': (30,40),'4':(50,40),'5':(70,40),'7':(90,40),
}

# Panel orders
NON_NEO_PANEL_IDS = {
    '2-Button': ['1','2'],
    '4-Button': ['1','2','3','4'],
    '6-Button': ['1','2','6','3','4','5'],
    '8-Button': ['1','2','6','8','3','4','5','7'],
}
NEO_PANEL_IDS = {
    '2-Button': ['1','2'],
    '4-Button': ['3','4','1','2'],
    '6-Button': ['3','4','5','1','2','6'],
    '8-Button': ['3','4','5','7','1','2','6','8'],
}

# NeoGeo mappings
NEO_GAMEBTN_MAP = {
    '2-Button': {'1':'A','2':'B'},
    '4-Button': {'3':'C','4':'D','1':'A','2':'B'},
    '6-Button': {'3':'B','4':'C','5':'D','1':'A'},
    '8-Button': {'3':'A','4':'B','5':'C','7':'D'},
}
NEO_BUTTON_LETTER_ORDER = {'A':1,'B':2,'C':3,'D':4}

# RetroBat maps (controller pour es_input.cfg)
RB_PHYSICAL_ORDER = ['3','4','5','7','1','2','6','8']
RB_CONTROLLER_MAP  = {
    '1': 'A',
    '2': 'B',
    '3': 'X',
    '4': 'Y',
    '5': 'PAGEUP',
    '6': 'PAGEDOWN',
    '7': 'L2',
    '8': 'R2'
}

START_POS = (85,90)
COIN_POS  = (95,90)
JOYSTICK_DEFAULT_COLOR = 'Gray'

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

def load_configurations():
    color_cfg = configparser.ConfigParser(); color_cfg.optionxform=str
    color_cfg.read(COLOR_INIS)
    func_cfg  = configparser.ConfigParser(strict=False); func_cfg.optionxform=str
    func_cfg.read(CONTROLS_INI)
    return color_cfg, func_cfg

def get_value(cfg, section, option, fallback):
    try:    return cfg.get(section, option)
    except: return fallback

def prettify_xml(elem):
    rough  = ET.tostring(elem, 'utf-8')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ", encoding="utf-8")

def generate_xml_for_rom(rom, color_cfg, func_cfg):
    is_neo  = rom in NEOGEO_ROMS
    col_sec = 'neogeo' if is_neo else rom

    root    = ET.Element('system', name='arcade')
    game_el = ET.SubElement(root, 'game', name=rom, rom=rom)
    layouts = ET.SubElement(game_el, 'layouts')

    joy_col = get_value(color_cfg, col_sec, 'P1_JOYSTICK', JOYSTICK_DEFAULT_COLOR)
    panel_ids_map = NEO_PANEL_IDS if is_neo else NON_NEO_PANEL_IDS

    for layout_type, ids in panel_ids_map.items():
        lay = ET.SubElement(layouts, 'layout',
                            panelButtons=str(len(ids)), type=layout_type)
        ET.SubElement(lay, 'joystick', color=joy_col)

        for idx, phys_id in enumerate(ids, start=1):
            x, y     = STATIC_POSITIONS[phys_id]
            physical = phys_id   # on garde le numéro physique

            if is_neo:
                mapping = NEO_GAMEBTN_MAP[layout_type]
                if phys_id in mapping:
                    letter     = mapping[phys_id]
                    letter_idx = NEO_BUTTON_LETTER_ORDER[letter]
                    color_btn  = get_value(color_cfg, 'neogeo',
                                           f'P1_BUTTON{letter_idx}', 'Gray')
                    func_btn   = get_value(func_cfg, 'neogeo',
                                           f'P1_BUTTON{letter_idx}', 'None')
                    btn_id     = letter
                    controller = RB_CONTROLLER_MAP[phys_id]
                    game_btn   = letter
                else:
                    color_btn, func_btn = 'Gray','None'
                    btn_id, controller, game_btn = 'NONE','NONE','NONE'
            else:
                color_btn  = get_value(color_cfg, rom, f'P1_BUTTON{idx}', 'Gray')
                func_btn   = get_value(func_cfg, rom, f'P1_BUTTON{idx}', 'None')
                btn_id     = phys_id
                controller = RB_CONTROLLER_MAP[phys_id]
                game_btn   = phys_id

            ET.SubElement(lay, 'button',
                          id         = btn_id,
                          physical   = physical,
                          controller = controller,
                          gameButton = game_btn,
                          x          = str(x),
                          y          = str(y),
                          color      = color_btn,
                          function   = func_btn)

        ET.SubElement(lay, 'button',
                      id='START', physical=str(len(ids)+1),
                      controller='START', gameButton='START',
                      x=str(START_POS[0]), y=str(START_POS[1]),
                      color=get_value(color_cfg, col_sec,'P1_START','White'),
                      function='Start')
        ET.SubElement(lay, 'button',
                      id='COIN', physical=str(len(ids)+2),
                      controller='SELECT', gameButton='COIN',
                      x=str(COIN_POS[0]), y=str(COIN_POS[1]),
                      color=get_value(color_cfg, col_sec,'P1_COIN','White'),
                      function='Coin')

    return root

def generate_all_xmls():
    color_cfg, func_cfg = load_configurations()
    func_roms = {s.lower() for s in func_cfg.sections() if s not in ('DEFAULT','neogeo')}
    all_roms  = sorted(func_roms.union(NEOGEO_ROMS))
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for rom in all_roms:
        xml_root = generate_xml_for_rom(rom, color_cfg, func_cfg)
        pretty   = prettify_xml(xml_root)
        with open(os.path.join(OUTPUT_DIR, f'{rom}.xml'), 'wb') as f:
            f.write(pretty)

if __name__ == '__main__':
    generate_all_xmls()
    print("Génération terminée !")
