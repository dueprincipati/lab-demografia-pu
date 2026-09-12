#!/usr/bin/env python3
"""
Scarica i confini vettoriali ufficiali dei 50 comuni di Pesaro e Urbino
e genera il GeoJSON arricchito con i dati demografici riconciliati al 100% con il RS 2025.
"""

import urllib.request
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
DEMO_FILE = os.path.join(DATA_DIR, 'demografia_comunale_conciliata.json')
OUTPUT_GEOJSON = os.path.join(DATA_DIR, 'comuni_pu_geo.json')
OUTPUT_JS = os.path.join(DATA_DIR, 'comuni_pu_geo.js')

def get_centroid(coords):
    if isinstance(coords[0][0], list):
        ring = coords[0]
    else:
        ring = coords
    a = 0.0
    cx = 0.0
    cy = 0.0
    for i in range(len(ring) - 1):
        x0, y0 = ring[i][0], ring[i][1]
        x1, y1 = ring[i+1][0], ring[i+1][1]
        cross = (x0 * y1 - x1 * y0)
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a = a * 0.5
    if abs(a) < 1e-9:
        return [round(sum(p[1] for p in ring)/len(ring), 5), round(sum(p[0] for p in ring)/len(ring), 5)]
    cx = cx / (6.0 * a)
    cy = cy / (6.0 * a)
    return [round(cy, 5), round(cx, 5)]

def run():
    os.makedirs(RAW_DIR, exist_ok=True)
    marche_geo_file = os.path.join(RAW_DIR, 'limits_R_11_municipalities.geojson')
    
    if not os.path.exists(marche_geo_file):
        print("📥 Download confini Marche (openpolis)...")
        url = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_R_11_municipalities.geojson"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8')
            with open(marche_geo_file, 'w', encoding='utf-8') as f:
                f.write(content)
    else:
        print("📂 Caricamento confini da cache locale...")
        with open(marche_geo_file, 'r', encoding='utf-8') as f:
            content = f.read()

    geo_data = json.loads(content)
    with open(DEMO_FILE, 'r', encoding='utf-8') as f:
        demo_data = json.load(f)

    # Dizionario rapido per Istat code
    demo_by_istat = {c['istat']: c for c in demo_data['comuni']}

    pu_features = []
    matched_count = 0

    for f in geo_data['features']:
        props = f['properties']
        geom = f['geometry']
        cod = str(props.get('com_istat_code', ''))
        if props.get('prov_istat_code_num') == 41 or cod.startswith('041'):
            if cod in demo_by_istat:
                c_demo = demo_by_istat[cod]
                # Calcolo baricentro geografico (lat, lon)
                if geom['type'] == 'Polygon':
                    centroid = get_centroid(geom['coordinates'][0])
                elif geom['type'] == 'MultiPolygon':
                    largest = max(geom['coordinates'], key=lambda poly: len(poly[0]))
                    centroid = get_centroid(largest[0])
                else:
                    centroid = [43.7, 12.6]

                # Arricchisce i metadati geografici con i dati Istat/RS
                props.update({
                    'centroid': centroid,
                    'altitudine_m_slm': c_demo.get('altitudine_m_slm', 200),
                    'popolazione_2025': c_demo['popolazione_2025'],
                    'maschi_2025': c_demo['maschi_2025'],
                    'femmine_2025': c_demo['femmine_2025'],
                    'eta_0_14': c_demo['eta_0_14'],
                    'eta_15_64': c_demo['eta_15_64'],
                    'eta_65_oltre': c_demo['eta_65_oltre'],
                    'perc_0_14': round(c_demo['eta_0_14'] / c_demo['popolazione_2025'] * 100, 1),
                    'perc_65_oltre': round(c_demo['eta_65_oltre'] / c_demo['popolazione_2025'] * 100, 1),
                    'indice_vecchiaia': c_demo['indice_vecchiaia'],
                    'indice_dipendenza': c_demo['indice_dipendenza'],
                    'indice_ricambio_attivi': c_demo['indice_ricambio_attivi'],
                    'tasso_saldo_nat_mille': c_demo['tasso_saldo_nat_mille'],
                    'tasso_natalita_mille': c_demo['tasso_natalita_mille'],
                    'tasso_mortalita_mille': c_demo['tasso_mortalita_mille'],
                    'eta_15_19': c_demo['eta_15_19'],
                    'eta_60_64': c_demo['eta_60_64'],
                    'nascite_2024': c_demo['nascite_2024'],
                    'decessi_2024': c_demo['decessi_2024'],
                    'saldo_naturale_2024': c_demo['saldo_naturale_2024'],
                    'saldo_estero_2024': c_demo['saldo_estero_2024'],
                    'saldo_interno_2024': c_demo['saldo_interno_2024'],
                    'saldo_totale_2024': c_demo['saldo_totale_2024'],
                    'ats': c_demo['ats']
                })
                matched_count += 1
            pu_features.append(f)

    pu_geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "provincia": "Pesaro e Urbino",
            "codice_provincia": "041",
            "totale_comuni": len(pu_features)
        },
        "features": pu_features
    }

    with open(OUTPUT_GEOJSON, 'w', encoding='utf-8') as f:
        json.dump(pu_geojson, f, ensure_ascii=False)

    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write("const comuniGeoData = " + json.dumps(pu_geojson, ensure_ascii=False) + ";")

    print(f"✅ Generati con successo:\n   - {OUTPUT_GEOJSON}\n   - {OUTPUT_JS}")
    print(f"📍 Comuni inclusi e collegati: {matched_count} su {len(pu_features)}")

if __name__ == "__main__":
    run()
