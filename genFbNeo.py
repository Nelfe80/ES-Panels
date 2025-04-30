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
        print("Error: PyYAML or ruamel.yaml is required. Please install with 'pip install pyyaml ruamel.yaml'")
        sys.exit(1)

import xml.etree.ElementTree as ET
from xml.dom import minidom

# Config files
COLOR_INIS = [
    'ledspicer-arcade-colors.ini',
    'ledblinky-arcade-colors.ini'
]
CONTROLS_YAML = 'fbneo.yml'
OUTPUT_DIR = 'fbneo'

# Static positions (copy from gen.py)
STATIC_POSITIONS = {
    '1': (30, 60), '2': (50, 60), '6': (70, 60), '8': (90, 60),
    '3': (30, 40), '4': (50, 40), '5': (70, 40), '7': (90, 40),
}
START_POS = (85, 90)
COIN_POS = (95, 90)

# Panel orders for RetroBat (fixed layouts)
PANEL_IDS = {
    '8-Button': ['3', '4', '5', '7', '1', '2', '6', '8'],
    '6-Button': ['3', '4', '5', '1', '2', '6'],
    '4-Button': ['3', '4', '1', '2'],
    '2-Button': ['1', '2'],
}

# Mapping physical -> controller constant
RB_CONTROLLER_MAP = {
    '1': 'A', '2': 'B', '3': 'X', '4': 'Y',
    '5': 'PAGEUP', '6': 'PAGEDOWN', '7': 'L2', '8': 'R2'
}


def load_color_config():
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read(COLOR_INIS)
    return cfg


def load_controls():
    """Load controls from YAML, ensuring game keys are strings."""
    with open(CONTROLS_YAML, 'r') as f:
        data = _load_yaml(f)
    # Cast rom keys to str and lowercase
    return {str(rom).lower(): mapping for rom, mapping in data.items()}


def prettify_xml(elem):
    rough = ET.tostring(elem, 'utf-8')
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ", encoding="utf-8")


def generate_xml_for_rom(rom, color_cfg, controls):
    rom_key = rom.lower()
    mapping = controls.get(rom_key)
    if not mapping:
        return None

    # Build inverse mapping: DInput name -> function label, ignoring non-buttons
    ignore_keys = {'players', 'coin', 'start', 'noplayer', 'service'}
    inv = {}
    for key, val in mapping.items():
        key_str = str(key)
        if key_str.lower() in ignore_keys:
            continue
        if isinstance(val, str):
            inv[val] = key_str

    root = ET.Element('system', name='arcade')
    game_el = ET.SubElement(root, 'game', name=rom, rom=rom)
    layouts = ET.SubElement(game_el, 'layouts')

    # Joystick color
    joy_col = color_cfg.get(rom, 'P1_JOYSTICK', fallback='Gray')

    for layout_type, ids in PANEL_IDS.items():
        lay = ET.SubElement(layouts, 'layout', panelButtons=str(len(ids)), type=layout_type)
        ET.SubElement(lay, 'joystick', color=joy_col)

        # Buttons
        for phys in ids:
            # id and physical both physical
            btn_id = phys
            x, y = STATIC_POSITIONS[phys]
            ctrl = RB_CONTROLLER_MAP.get(phys, 'NONE')
            # Map to DInput name
            if ctrl in ('A', 'B', 'X', 'Y'):
                dinput = ctrl.lower()
            else:
                dinput = {'PAGEUP': 'leftshoulder', 'PAGEDOWN': 'rightshoulder'}.get(ctrl, ctrl.lower())
            func = inv.get(dinput, 'None')
            # color per physical mapping
            color = color_cfg.get(rom, f'P1_BUTTON{phys}', fallback='Gray')
            # if no function, force black
            if func == 'None':
                color = 'Black'

            ET.SubElement(lay, 'button',
                          id=btn_id,
                          physical=phys,
                          controller=ctrl,
                          gameButton=dinput,
                          x=str(x), y=str(y),
                          color=color,
                          function=func)

        # START and COIN buttons
        ET.SubElement(lay, 'button',
                      id='START', physical=str(len(ids)+1),
                      controller='START', gameButton='START',
                      x=str(START_POS[0]), y=str(START_POS[1]),
                      color=color_cfg.get(rom, 'P1_START', fallback='White'),
                      function='Start')
        ET.SubElement(lay, 'button',
                      id='COIN', physical=str(len(ids)+2),
                      controller='SELECT', gameButton='COIN',
                      x=str(COIN_POS[0]), y=str(COIN_POS[1]),
                      color=color_cfg.get(rom, 'P1_COIN', fallback='White'),
                      function='Coin')

    return root


def generate_all_xmls():
    color_cfg = load_color_config()
    controls = load_controls()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for rom in controls.keys():
        xml_root = generate_xml_for_rom(rom, color_cfg, controls)
        if xml_root is None:
            continue
        pretty = prettify_xml(xml_root)
        with open(os.path.join(OUTPUT_DIR, f'{rom}.xml'), 'wb') as f:
            f.write(pretty)


if __name__ == '__main__':
    generate_all_xmls()
    print("Génération fbneo XML terminée !")
