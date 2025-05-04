import re
from pathlib import Path
import xml.etree.ElementTree as ET
from xml.dom import minidom
from urllib.parse import unquote, urlparse

# Mapping machine → liste des émulateurs libretro officiels
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
    'electron':       ['m'],  # core "m" pour Electronika BK-0010/BK-0011
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
    'mastersystem':   ['picodrive', 'genesis_plus_gx', 'sms_plus_gx', 'gearsystem'],
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
    'nes':            ['higan', 'emux', 'fceumm', 'nestopia', 'nestopia_ue', 'quicknes', 'mesen'],
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

EMU_TO_MACHINES = {}
for machine, emus in MACHINE_TO_EMUS.items():
    for e in emus:
        EMU_TO_MACHINES.setdefault(e, []).append(machine)

#
# 2) Définitions RetroPad
#
RETRO_IDS = {
    'b':0, 'y':1, 'select':2, 'start':3,
    'dpad_up':4, 'dpad_down':5, 'dpad_left':6, 'dpad_right':7,
    'a':8, 'x':9, 'l1':10, 'r1':11, 'l2':12, 'r2':13, 'l3':14, 'r3':15,
}

RETRO_BUTTONS = {
    'a':('BUTTON1','A'), 'b':('BUTTON2','B'),
    'x':('BUTTON3','X'), 'y':('BUTTON4','Y'),
    'l1':('BUTTON5','L1'), 'l':('BUTTON5','L1'),
    'pageup':('BUTTON5','PAGEUP'), 'r1':('BUTTON6','R1'),
    'r':('BUTTON6','R1'), 'pagedown':('BUTTON6','PAGEDOWN'),
    'l2':('BUTTON7','L2'), 'r2':('BUTTON8','R2'),
    'start':('BUTTON9','START'), 'select':('BUTTON10','SELECT'),
}

DIRECTIONS = {
    'dpad_up':'P1_JOYSTICK_UP',
    'dpad_down':'P1_JOYSTICK_DOWN',
    'dpad_left':'P1_JOYSTICK_LEFT',
    'dpad_right':'P1_JOYSTICK_RIGHT',
}

def prettify(elem):
    raw = ET.tostring(elem, 'utf-8')
    return minidom.parseString(raw).toprettyxml(indent="  ")

def extract_table(lines, idx):
    rows = []
    for l in lines[idx+1:]:
        if not l.startswith('|'):
            break
        if set(l.strip()) <= set('|- '):
            continue
        rows.append(l.rstrip())
    return rows

def find_header_indices(headers):
    idx_desc = next((i for i,h in enumerate(headers)
                     if 'remap' in h.lower() or 'descriptor' in h.lower()), None)
    idx_rp   = next((i for i,h in enumerate(headers)
                     if 'retropad' in h.lower()), None)
    return idx_desc, idx_rp

def clean_group_name(raw):
    # enlève liens markdown et parenthèses
    s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', raw)
    s = re.sub(r'[\[\]\(\)]', '', s).strip()
    return s or 'default'

def fallback_scan(lines):
    seen = set()
    out = []
    for l in lines:
        for m in re.finditer(r'\.\./image/retropad/retro_([a-z0-9_]+)\.png', l):
            k = m.group(1).lower()
            if k in seen:
                continue
            seen.add(k)
            out.append((k, k.upper()))
    return out

def process_md(md_path, out_dir):
    lines = md_path.read_text(encoding='utf-8').splitlines()
    groups = []
    last_heading = 'default'
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith('####'):
            last_heading = clean_group_name(line.lstrip('#').strip())
            i += 1
            continue

        if line.startswith('|'):
            tbl = extract_table(lines, i)
            if any('../image/retropad/' in r for r in tbl):
                headers = [c.strip() for c in line.strip().strip('|').split('|')]
                idx_desc, idx_rp = find_header_indices(headers)
                if idx_rp is None and tbl:
                    first = [c.strip() for c in tbl[0].strip().strip('|').split('|')]
                    idx_rp = next((j for j,v in enumerate(first)
                                   if '../image/retropad/' in v), None)

                # nom de groupe : soit le dernier ####, soit la première cellule
                raw_name = last_heading if (i>0 and lines[i-1].startswith('####')) else headers[0]
                grp_name = clean_group_name(raw_name)

                mappings = []
                for row in tbl:
                    cells = [c.strip() for c in row.strip().strip('|').split('|')]
                    if idx_rp is None or idx_rp >= len(cells):
                        continue
                    mimg = re.search(r'/([^/]+?)\.(?:png|jpg|svg)', cells[idx_rp])
                    if not mimg:
                        continue
                    key = mimg.group(1).replace('retro_','').lower()

                    # descriptor ou input
                    text = ''
                    if idx_desc is not None and idx_desc < len(cells):
                        text = cells[idx_desc]
                    # si text contient balise image, on en extrait le label
                    m2 = re.search(r'/([^/]+?)\.(?:png|jpg|svg)', text)
                    if m2:
                        lbl = m2.group(1)
                        lbl = re.sub(r'^(PS3_|PS4_|retro_)','', lbl, flags=re.IGNORECASE)
                        text = lbl.replace('_',' ').strip()

                    if text:
                        mappings.append((key, text))

                if mappings:
                    groups.append({'name':grp_name, 'mappings':mappings})

                i += len(tbl) + 1
                continue

        i += 1

    # fallback si aucun groupe
    if not groups:
        fb = fallback_scan(lines)
        if fb:
            groups = [{'name':'default','mappings':fb}]

    # génération XML
    core = md_path.stem
    machines = EMU_TO_MACHINES.get(core, []) or [core]
    sys_name = ",".join(sorted(set(machines)))

    root = ET.Element('system', {'name':sys_name, 'emulator':core})
    inp  = ET.SubElement(root, 'input')

    only_def = len(groups)==1 and groups[0]['name'].lower().startswith('default')
    ok = False

    for grp in groups:
        attrs = {'name': grp['name']}
        if only_def or grp['name'].lower().startswith('default'):
            attrs['type'] = 'default'
        gnode = ET.SubElement(inp, 'group', attrs)

        for key, text in grp['mappings']:
            ok = True
            dev_id = RETRO_IDS.get(key)
            if key in DIRECTIONS:
                p = ET.SubElement(gnode, 'port', {'type': DIRECTIONS[key]})
                at = {'type':'standard'}
                if dev_id is not None:
                    at['retropad_id'] = str(dev_id)
                ET.SubElement(p, 'newseq', at).text = text

            elif key in RETRO_BUTTONS:
                bid, btn = RETRO_BUTTONS[key]
                p = ET.SubElement(gnode, 'port', {'type': f'P1_{bid}'})
                at = {'type':'standard'}
                if btn:
                    at['button'] = btn
                if dev_id is not None:
                    at['retropad_id'] = str(dev_id)
                ET.SubElement(p, 'newseq', at).text = text

    xml_str = prettify(root)
    xml_name = md_path.with_suffix('.xml').name
    (out_dir / xml_name).write_text(xml_str, encoding='utf-8')
    return xml_name, ok

def main():
    base    = Path('libreto')     # <-- dossier contenant vos .md
    out_dir = Path('retroarch')   # <-- dossier de sortie des .xml
    out_dir.mkdir(exist_ok=True)

    mds   = sorted(base.glob('*.md'))
    total = len(mds)

    for idx, md in enumerate(mds, 1):
        xml_name, ok = process_md(md, out_dir)
        status = 'OK' if ok else 'EMPTY'
        print(f"[{idx}/{total}] {md.name} → {xml_name} [{status}]")

    print(f"\nProcessed {total}/{total} MD files, generated {total} XML files in {out_dir.resolve()}")

if __name__ == '__main__':
    main()
