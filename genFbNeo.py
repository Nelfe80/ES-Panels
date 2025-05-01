import os
import sys
import configparser

# Attempt to import a YAML parser and define a unified load function
try:
    import yaml
    _load_yaml = yaml.safe_load
except ImportError:
    try:
        from ruamel.yaml import YAML
        yaml_parser = YAML()
        _load_yaml = yaml_parser.load
    except ImportError:
        print('Error: PyYAML or ruamel.yaml is required. Please install with pip install pyyaml ruamel.yaml')
        sys.exit(1)

import xml.etree.ElementTree as ET
from xml.dom import minidom

# Configuration files
COLOR_INIS = ['ledspicer-arcade-colors.ini', 'ledblinky-arcade-colors.ini']
CONTROLS_YAML = 'fbneo.yml'
OUTPUT_DIR = 'fbneo'

STATIC_POSITIONS = {
    '1': (30, 60), '2': (50, 60), '3': (30, 40), '4': (50, 40),
    '5': (70, 40), '6': (70, 60), '7': (90, 40), '8': (90, 60),
}
START_POS = (85, 90)
COIN_POS = (95, 90)

PHYS_TO_DINPUT = {
    '4': 'y', '3': 'x', '5': 'leftshoulder', '7': 'lefttrigger',
    '1': 'a', '2': 'b', '6': 'rightshoulder', '8': 'righttrigger',
}

DINPUT_TO_CONTROLLER = {
    'x': 'A', 'y': 'B', 'a': 'Y', 'b': 'X',
    'leftshoulder': 'PAGEUP', 'rightshoulder': 'PAGEDOWN',
    'lefttrigger': 'L2', 'righttrigger': 'R2',
}

CONTROLLER_TO_BUTTON_IDX = {
    'A': 1, 'B': 2,
    'X': 3, 'Y': 4,
    'PAGEUP': 5, 'PAGEDOWN': 6,
    'L2': 7, 'R2': 8,
}

PANEL_IDS = {
    '8-Button': ['4', '3', '5', '7', '1', '2', '6', '8'],
    '6-Button': ['4', '3', '5', '1', '2', '6'],
    '4-Button': ['4', '3', '1', '2'],
    '2-Button': ['1', '2'],
}


def load_color_config():
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(COLOR_INIS)
    return cfg


def load_controls():
    with open(CONTROLS_YAML, 'r') as f:
        data = _load_yaml(f)
    return {str(rom).lower(): mapping for rom, mapping in data.items()}


def prettify_xml(elem):
    rough = ET.tostring(elem, 'utf-8')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent='  ', encoding='utf-8')


def generate_xml_for_rom(rom, color_cfg, controls):
    rom_key = rom.lower()
    mapping = controls.get(rom_key)
    if not mapping:
        return None

    # Find INI section (case-insensitive)
    cfg_section = None
    for section in color_cfg.sections():
        if section.lower() == rom_key:
            cfg_section = section
            break

    # Inverse mapping for functions
    ignore = {'players', 'coin', 'start', 'noplayer', 'service'}
    inv = {val: str(key) for key, val in mapping.items()
           if isinstance(val, str) and str(key).lower() not in ignore}

    # Determine default panel from available colors
    max_btn = 0
    if cfg_section:
        for opt in color_cfg.options(cfg_section):
            if opt.startswith('P1_BUTTON'):
                try:
                    idx = int(opt.replace('P1_BUTTON', ''))
                    max_btn = max(max_btn, idx)
                except ValueError:
                    pass
    if max_btn <= 2:
        default_panel = '2-Button'
    elif max_btn <= 4:
        default_panel = '4-Button'
    elif max_btn <= 6:
        default_panel = '6-Button'
    else:
        default_panel = '8-Button'

    # Build default panel buttons_data
    def_phys_list = PANEL_IDS[default_panel]
    default_buttons = []
    for phys in def_phys_list:
        dinput = PHYS_TO_DINPUT[phys]
        ctrl = DINPUT_TO_CONTROLLER.get(dinput, 'UNKNOWN')
        func = inv.get(dinput, 'None')
        default_buttons.append((phys, ctrl, dinput, func))
    if default_panel == '2-Button':
        # pick first two active
        candidates = []
        for panel in ['8-Button', '6-Button', '4-Button']:
            for p in PANEL_IDS[panel]:
                dinput = PHYS_TO_DINPUT[p]
                ctrl = DINPUT_TO_CONTROLLER.get(dinput, 'UNKNOWN')
                func = inv.get(dinput, 'None')
                candidates.append((p, ctrl, dinput, func))
        active = [b for b in candidates if b[3] != 'None']
        if len(active) >= 2:
            default_buttons = active[:2]
        default_buttons.sort(key=lambda b: STATIC_POSITIONS[b[0]][0])
    # Map functions to colors based on default panel order
    function_to_color = {}
    for idx, (_, _, _, func) in enumerate(default_buttons[:max_btn], start=1):
        if func != 'None' and cfg_section:
            color_val = color_cfg.get(cfg_section, f'P1_BUTTON{idx}', fallback='Gray')
            function_to_color[func] = color_val

    # Create XML structure
    system = ET.Element('system', name='arcade')
    game_el = ET.SubElement(system, 'game', name=rom, rom=rom)
    layouts = ET.SubElement(game_el, 'layouts')
    joy_color = color_cfg.get(cfg_section, 'P1_JOYSTICK', fallback='Gray') if cfg_section else 'Gray'

    for layout_type, phys_list in PANEL_IDS.items():
        count = len(phys_list)
        layout_el = ET.SubElement(layouts, 'layout', panelButtons=str(count), type=layout_type)
        ET.SubElement(layout_el, 'joystick', color=joy_color)

        # Gather button data for this layout
        buttons_data = []
        for phys in phys_list:
            dinput = PHYS_TO_DINPUT[phys]
            ctrl = DINPUT_TO_CONTROLLER.get(dinput, 'UNKNOWN')
            func = inv.get(dinput, 'None')
            buttons_data.append((phys, ctrl, dinput, func))
        # 2-Button special
        if count == 2:
            candidates = []
            for panel in ['8-Button', '6-Button', '4-Button']:
                for p in PANEL_IDS[panel]:
                    dinput = PHYS_TO_DINPUT[p]
                    ctrl = DINPUT_TO_CONTROLLER.get(dinput, 'UNKNOWN')
                    func = inv.get(dinput, 'None')
                    candidates.append((p, ctrl, dinput, func))
            active = [b for b in candidates if b[3] != 'None']
            if len(active) >= 2:
                buttons_data = active[:2]
            buttons_data.sort(key=lambda b: STATIC_POSITIONS[b[0]][0])

        # Place buttons and apply colors by function
        override_phys = (count == 2)
        for idx, (phys, ctrl, dinput, func) in enumerate(buttons_data[:count], start=1):
            phys_id = str(idx) if override_phys else phys
            x, y = STATIC_POSITIONS[phys_id]
            if func != 'None':
                color = function_to_color.get(func, 'Gray')
            else:
                color = 'Black'
            ET.SubElement(
                layout_el, 'button',
                id=str(idx), physical=phys_id,
                controller=ctrl, gameButton=dinput,
                x=str(x), y=str(y), color=color, function=func
            )
        # START and COIN
        ET.SubElement(
            layout_el, 'button', id='START', physical=str(count+1), controller='START',
            gameButton=mapping.get('Start', 'start'),
            x=str(START_POS[0]), y=str(START_POS[1]),
            color=color_cfg.get(cfg_section, 'P1_START', fallback='White') if cfg_section else 'White',
            function='Start'
        )
        ET.SubElement(
            layout_el, 'button', id='COIN', physical=str(count+2), controller='SELECT',
            gameButton=mapping.get('Coin', 'back'),
            x=str(COIN_POS[0]), y=str(COIN_POS[1]),
            color=color_cfg.get(cfg_section, 'P1_COIN', fallback='White') if cfg_section else 'White',
            function='Coin'
        )
    return system


def generate_all_xmls():
    color_cfg = load_color_config()
    controls = load_controls()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for rom in controls:
        xml_el = generate_xml_for_rom(rom, color_cfg, controls)
        if xml_el is None:
            continue
        xml_bytes = prettify_xml(xml_el)
        with open(os.path.join(OUTPUT_DIR, f'{rom}.xml'), 'wb') as f:
            f.write(xml_bytes)

if __name__ == '__main__':
    generate_all_xmls()
    print('Génération fbneo XML terminée !')
