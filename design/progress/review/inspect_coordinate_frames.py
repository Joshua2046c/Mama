"""Read-only reproduction of footprint-origin versus bounding-center calibration.

This diagnostic never modifies Circuit JSON, KiCad, rules or a release. Run from
the project root after pcb.run(check). It does not replace manufacturing checks.
"""
import hashlib
import json
import math
import re
from pathlib import Path


def sexpr(text):
    stack, root = [], []
    current = root
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if token == '(':
            child = []
            current.append(child)
            stack.append(current)
            current = child
        elif token == ')':
            current = stack.pop()
        else:
            current.append(json.loads(token) if token.startswith('"') else token)
    return root[0]


def child(node, tag):
    return next((x for x in node if isinstance(x, list) and x and x[0] == tag), None)


def inspect(design):
    base = Path('.work/pcb') / design
    cp = base / 'build/circuit.json'
    kp = base / f'kicad/{design}.kicad_pcb'
    circuit = json.loads(cp.read_text())
    names = {x['source_component_id']: x['name'] for x in circuit if x['type'] == 'source_component'}
    positions = {}
    for fp in sexpr(kp.read_text()):
        if not isinstance(fp, list) or not fp or fp[0] != 'footprint':
            continue
        reference = next(x[2] for x in fp if isinstance(x, list) and x[:2] == ['property', 'Reference'])
        at = child(fp, 'at')
        positions[reference] = (float(at[1]), float(at[2]))
    rows = []
    for comp in circuit:
        if comp['type'] != 'pcb_component':
            continue
        ref = names[comp['source_component_id']]
        if ref not in positions:
            continue
        kx, ky = positions[ref]
        origin, center = comp.get('footprint_origin', comp['center']), comp['center']
        rows.append({'ref': ref, 'layer': comp['layer'], 'kicad_at': [kx, ky],
                     'footprint_origin': origin, 'geometric_center': center,
                     'origin_translation': [origin['x'] - kx, origin['y'] + ky],
                     'center_translation': [center['x'] - kx, center['y'] + ky]})
    stats = {}
    for method in ['origin', 'center']:
        values = [r[method + '_translation'] for r in rows]
        mean = [sum(v[i] for v in values) / len(values) for i in (0, 1)]
        stats[method] = {'translation_mm': mean, 'matches': len(values),
                         'max_residual_mm': max(math.dist(v, mean) for v in values)}
    drc = json.loads((base / 'reports/independent-drc.json').read_text())
    counts = {'errors': 0, 'warnings': 0, 'unconnected': len(drc['unconnected_items'])}
    for violation in drc['violations']:
        counts['errors' if violation['severity'] == 'error' else 'warnings'] += 1
    return {'design': design, 'files': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [cp, kp]},
            'calibration_comparison': stats, 'noncoincident_origins': [r for r in rows if math.dist(r['origin_translation'], r['center_translation']) > 1e-6],
            'independent_kicad_drc': counts}


if __name__ == '__main__':
    print(json.dumps([inspect(b) for b in ['progress', 'power_entry']], ensure_ascii=False, indent=2))
