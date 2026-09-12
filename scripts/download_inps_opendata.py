#!/usr/bin/env python3
"""
Script per il download e l'estrazione mirata dei dataset Open Data INPS a livello provinciale
per la Provincia di Pesaro e Urbino (Codice NUTS3: ITE31 / Codice ISTAT: 041).

Fonti Open Data ufficiali INPS (opendata.inps.it / dati.gov.it):
1. Assegno Unico Universale (AUU) - Nuclei e Figli (2022-2024)
2. Assegno Unico Universale (AUU) - Fasce ISEE, Età e Disabilità (2022-2024)
3. Imprese e Dipendenti del Settore Privato non agricolo (2013-2022)
4. NASpI Beneficiari per Provincia (2018-2022)
5. NASpI Durata Teorica dei Trattamenti (2018-2022)
"""

import urllib.request
import json
import csv
import ssl
import re
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "inps_opendata")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) LabDemografiaPU/1.0'}

def fetch_url(url):
    print(f"📥 Download in corso da: {url} ...")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=ssl_ctx, timeout=45) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def process_auu_nuclei():
    url = "https://opendata.inps.it/download/dataset/migr2024/dataset_6008.csv"
    text = fetch_url(url)
    lines = text.splitlines()
    reader = csv.DictReader(lines)
    pu_data = []
    for r in reader:
        if 'pesaro' in r.get('provincia', '').lower():
            pu_data.append({
                "anno": int(r.get('Anno', 0)),
                "regione": r.get('Regione'),
                "provincia": r.get('provincia'),
                "figli_disabili": bool(float(r.get('figli_disabili', 0))),
                "numero_nuclei": int(float(r.get('numero_nuclei', 0))),
                "numero_figli": int(float(r.get('numero_figli', 0))),
                "somma_importi_euro": round(float(r.get('somma_importi', 0)), 2),
                "somma_mesi_erogati": int(float(r.get('somma_mesi', 0)))
            })
    
    out_path = os.path.join(OUTPUT_DIR, "inps_auu_nuclei_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(pu_data, f, indent=2, ensure_ascii=False)
    print(f"✅ AUU Nuclei salvato in {out_path} ({len(pu_data)} record)")
    return pu_data

def process_auu_isee():
    url = "https://opendata.inps.it/download/dataset/migr2024/dataset_6007.csv"
    text = fetch_url(url)
    lines = text.splitlines()
    reader = csv.DictReader(lines)
    pu_data = []
    for r in reader:
        if 'pesaro' in r.get('provincia', '').lower():
            pu_data.append({
                "anno": int(r.get('Anno', 0)),
                "classe_isee": r.get('classe_isee'),
                "classe_eta": r.get('classe_eta'),
                "figli_disabili": bool(float(r.get('figli_disabili', 0))),
                "numero_figli": int(float(r.get('numero_figli', 0))),
                "somma_importi_euro": round(float(r.get('somma_importi', 0)), 2),
                "somma_mesi": int(float(r.get('somma_mesi', 0)))
            })
    
    out_path = os.path.join(OUTPUT_DIR, "inps_auu_isee_disabilita_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(pu_data, f, indent=2, ensure_ascii=False)
    print(f"✅ AUU ISEE e Disabilità salvato in {out_path} ({len(pu_data)} record)")
    return pu_data

def process_imprese():
    url = "https://opendata.inps.it/download/dataset/dfb_st_imprese_set_priv_non_agric_05_inps_1_0/filesystem/Imprese%20per%20Provincia.csv"
    text = fetch_url(url)
    matches = [m.strip().replace('\n', ' ') for m in text.split('INPS:') if 'ITE31' in m]
    pu_data = []
    for m in matches:
        parts = m.split(',')
        if len(parts) >= 6:
            var_name = parts[3].strip()
            anno = int(parts[4].strip())
            val = float(parts[5].strip())
            pu_data.append({
                "territorio": "ITE31",
                "provincia": "Pesaro e Urbino",
                "indicatore": var_name,
                "anno": anno,
                "valore": val
            })
    
    # Organizziamo per anno
    per_anno = {}
    for item in pu_data:
        a = item["anno"]
        if a not in per_anno:
            per_anno[a] = {"anno": a, "provincia": "Pesaro e Urbino", "codice_nuts3": "ITE31"}
        ind = item["indicatore"]
        if ind == "NUM_IMPRESE":
            per_anno[a]["numero_imprese"] = int(item["valore"])
        elif ind == "MEDIA_DIP_12_IMP":
            per_anno[a]["totale_dipendenti_medi"] = int(item["valore"])
        elif ind == "MEDIA_DIP_12_XIMP":
            per_anno[a]["dipendenti_medi_per_impresa"] = round(item["valore"], 2)
        elif ind == "TOT_CONTR_IMP":
            per_anno[a]["contributi_totali_euro"] = int(item["valore"])
            
    summary_list = sorted(list(per_anno.values()), key=lambda x: x["anno"])
    out_path = os.path.join(OUTPUT_DIR, "inps_imprese_dipendenti_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(summary_list, f, indent=2, ensure_ascii=False)
    print(f"✅ Imprese e Dipendenti salvato in {out_path} ({len(summary_list)} anni)")
    return summary_list

def process_naspi():
    url = "https://opendata.inps.it/download/dataset/dfb_st_naspi_beneficiari_04_inps_1_0/filesystem/NASPI%20Beneficiari%20per%20Provincia.csv"
    text = fetch_url(url)
    matches = re.findall(r'([A-Za-z0-9_():.]+),([A-Z]),(ITE31),(\d{4}),([0-9.]+)', text)
    pu_data = []
    for m in matches:
        pu_data.append({
            "territorio": "ITE31",
            "provincia": "Pesaro e Urbino",
            "anno": int(m[3]),
            "beneficiari_naspi": int(float(m[4]))
        })
    pu_data.sort(key=lambda x: x["anno"])
    out_path = os.path.join(OUTPUT_DIR, "inps_naspi_beneficiari_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(pu_data, f, indent=2, ensure_ascii=False)
    print(f"✅ NASpI Beneficiari salvato in {out_path} ({len(pu_data)} anni)")
    return pu_data

def process_naspi_durata():
    url = "https://opendata.inps.it/download/dataset/dfb_st_naspi_trattamenti_05_inps_1_0/filesystem/NASPI%20Trattamenti%20per%20Provincia%20e%20Durata%20teorica%20in%20mesi%20della%20prestazione.csv"
    text = fetch_url(url)
    matches = [m.strip().replace('\n', ' ') for m in text.split('INPS:') if 'ITE31' in m]
    pu_data = []
    for m in matches:
        parts = m.split(',')
        if len(parts) >= 6:
            durata = parts[3].strip()
            anno = int(parts[4].strip())
            trattamenti = int(float(parts[5].strip()))
            pu_data.append({
                "territorio": "ITE31",
                "anno": anno,
                "durata_teorica_mesi": durata,
                "numero_trattamenti": trattamenti
            })
    pu_data.sort(key=lambda x: (x["anno"], x["durata_teorica_mesi"]))
    out_path = os.path.join(OUTPUT_DIR, "inps_naspi_durata_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(pu_data, f, indent=2, ensure_ascii=False)
    print(f"✅ NASpI Durata Trattamenti salvato in {out_path} ({len(pu_data)} record)")
    return pu_data

def build_combined_summary(auu_nuclei, auu_isee, imprese, naspi, naspi_durata):
    combined = {
        "provincia": "Pesaro e Urbino",
        "codice_nuts3": "ITE31",
        "codice_istat": "041",
        "descrizione": "Estrazione mirata di Open Data INPS a livello provinciale integrabili con il Rendiconto Sociale",
        "dataset_disponibili": {
            "assegno_unico_universale": {
                "nuclei_totali_2023": sum(r["numero_nuclei"] for r in auu_nuclei if r["anno"] == 2023),
                "importo_totale_erogato_2023_euro": round(sum(r["somma_importi_euro"] for r in auu_nuclei if r["anno"] == 2023), 2),
                "nuclei_con_figli_disabili_2023": sum(r["numero_nuclei"] for r in auu_nuclei if r["anno"] == 2023 and r["figli_disabili"]),
                "importo_disabili_2023_euro": round(sum(r["somma_importi_euro"] for r in auu_nuclei if r["anno"] == 2023 and r["figli_disabili"]), 2)
            },
            "imprese_settore_privato_2022": [i for i in imprese if i["anno"] == 2022][0] if any(i["anno"] == 2022 for i in imprese) else {},
            "naspi_beneficiari": naspi
        }
    }
    out_path = os.path.join(OUTPUT_DIR, "inps_opendata_summary_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    
    # Also save as JS for direct client-side consumption
    js_path = os.path.join(OUTPUT_DIR, "inps_opendata_summary_pu.js")
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(f"window.INPS_OPENDATA_PU = {json.dumps(combined, indent=2, ensure_ascii=False)};\n")
    print(f"🌟 Summary provinciale combinato salvato in {out_path} e {js_path}")

if __name__ == "__main__":
    print("🚀 Avvio download dataset Open Data INPS per la Provincia di Pesaro e Urbino...")
    auu_nuclei = process_auu_nuclei()
    auu_isee = process_auu_isee()
    imprese = process_imprese()
    naspi = process_naspi()
    naspi_durata = process_naspi_durata()
    build_combined_summary(auu_nuclei, auu_isee, imprese, naspi, naspi_durata)
    print("🏁 Tutti i dataset Open Data INPS provinciali per Pesaro e Urbino sono stati scaricati ed elaborati con successo!")
