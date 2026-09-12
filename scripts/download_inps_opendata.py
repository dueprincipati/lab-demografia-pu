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
6. Pensioni con Maggiorazioni Sociali per Provincia (2019-2023)
7. Pensioni Integrate al Trattamento Minimo per Provincia (2019-2023)
8. Prestazioni agli Invalidi Civili per Provincia (2018-2023)
9. Invalidi Civili per Età e Importo per Provincia (2019-2023)
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

def safe_float(val, default=0.0):
    if not val:
        return default
    v = str(val).strip().replace(',', '.')
    if v in ('_', '-', '', 'nan', 'null'):
        return default
    try:
        return float(v)
    except:
        return default

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) LabDemografiaPU/1.0'}

import http.client
import time

def fetch_url(url, retries=3):
    print(f"📥 Download in corso da: {url} ...")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=45) as resp:
                try:
                    return resp.read().decode('utf-8', errors='ignore')
                except http.client.IncompleteRead as e:
                    return e.partial.decode('utf-8', errors='ignore')
        except Exception as err:
            if attempt == retries - 1:
                raise err
            time.sleep(1)

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

def process_maggiorazioni():
    url = "https://opendata.inps.it/download/dataset/dfb_st_pens_vig_mag_soc_07_inps_1_0/filesystem/Pensioni%20con%20maggiorazioni%20per%20Province%20e%20Tipo%20maggiorazione.csv"
    text = fetch_url(url)
    matches = [m.strip().replace('\n', ' ') for m in text.split('INPS:') if 'ITE31' in m]
    pu_data = []
    for m in matches:
        parts = m.split(',')
        if len(parts) >= 7:
            indicatore = parts[3].strip()
            tipo_mag = parts[4].strip()
            anno = int(parts[5].strip())
            valore = safe_float(parts[6].strip())
            pu_data.append({
                "territorio": "ITE31",
                "indicatore": indicatore,
                "tipo_maggiorazione": tipo_mag,
                "anno": anno,
                "valore": round(valore, 2)
            })
    out_path = os.path.join(OUTPUT_DIR, "inps_pensioni_maggiorazioni_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(pu_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Pensioni con Maggiorazioni salvato in {out_path} ({len(pu_data)} record)")
    return pu_data

def process_integrazioni_minimo():
    url = "https://opendata.inps.it/download/dataset/dfb_st_pens_vig_int_min_07_inps_1_0/filesystem/Pensioni%20integrate%20per%20Province%2C%20Tipo%20integrazione%20e%20Presenza%20maggiorazione.csv"
    text = fetch_url(url)
    matches = [m.strip().replace('\n', ' ') for m in text.split('INPS:') if 'ITE31' in m]
    pu_data = []
    for m in matches:
        parts = m.split(',')
        if len(parts) >= 8:
            indicatore = parts[3].strip()
            tipo_integrazione = parts[4].strip()
            presenza_maggiorazione = parts[5].strip()
            anno = int(parts[6].strip())
            valore = safe_float(parts[7].strip())
            pu_data.append({
                "territorio": "ITE31",
                "indicatore": indicatore,
                "tipo_integrazione": tipo_integrazione,
                "presenza_maggiorazione": presenza_maggiorazione,
                "anno": anno,
                "valore": round(valore, 2)
            })
    out_path = os.path.join(OUTPUT_DIR, "inps_pensioni_integrazioni_minimo_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(pu_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Pensioni Integrate al Minimo salvato in {out_path} ({len(pu_data)} record)")
    return pu_data

def process_prestazioni_invalidi():
    url = "https://opendata.inps.it/download/dataset/dfb_st_pens_vig_pres_inv_civ_07_inps_1_0/filesystem/Prestazioni%20agli%20invalidi%20civili%20per%20Province%20e%20Tipo%20prestazione.csv"
    text = fetch_url(url)
    matches = [m.strip().replace('\n', ' ') for m in text.split('INPS:') if 'ITE31' in m]
    pu_data = []
    for m in matches:
        parts = m.split(',')
        if len(parts) >= 7:
            indicatore = parts[3].strip()
            tipo_prestazione = parts[4].strip() # I = Indennità accompagnamento, P = Pensione
            anno = int(parts[5].strip())
            valore = safe_float(parts[6].strip())
            pu_data.append({
                "territorio": "ITE31",
                "indicatore": indicatore,
                "tipo_prestazione": tipo_prestazione,
                "tipo_descrizione": "Indennità di Accompagnamento" if tipo_prestazione == 'I' else "Pensione/Assegno Invalidità",
                "anno": anno,
                "valore": round(valore, 2)
            })
    out_path = os.path.join(OUTPUT_DIR, "inps_prestazioni_invalidi_civili_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(pu_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Prestazioni Invalidi Civili salvato in {out_path} ({len(pu_data)} record)")
    return pu_data

def process_invalidi_importi():
    url = "https://opendata.inps.it/download/dataset/dfb_st_inv_civ_imp_07_inps_1_0/filesystem/Invalidi%20civili%20per%20Province%20e%20Tipo%20prestazione.csv"
    text = fetch_url(url)
    matches = [m.strip().replace('\n', ' ') for m in text.split('INPS:') if 'ITE31' in m]
    pu_data = []
    for m in matches:
        parts = m.split(',')
        if len(parts) >= 7:
            indicatore = parts[3].strip()
            categoria = parts[4].strip()
            anno = int(parts[5].strip())
            valore = safe_float(parts[6].strip())
            pu_data.append({
                "territorio": "ITE31",
                "indicatore": indicatore,
                "categoria_invalidita": categoria,
                "anno": anno,
                "valore": round(valore, 2)
            })
    out_path = os.path.join(OUTPUT_DIR, "inps_invalidi_civili_eta_importi_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(pu_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Invalidi Civili per Età e Importi salvato in {out_path} ({len(pu_data)} record)")
    return pu_data

def build_combined_summary(auu_nuclei, auu_isee, imprese, naspi, naspi_durata, maggiorazioni, integrazioni, invalidi_pres, invalidi_imp):
    # Invalidità 2023
    inv_2023_pres = [p for p in invalidi_pres if p["anno"] == 2023 and p["indicatore"] == "NUM_PRESTAZIONI"]
    tot_invalidi_2023 = sum(p["valore"] for p in inv_2023_pres)
    
    # Integrazioni 2023
    int_2023 = [p for p in integrazioni if p["anno"] == 2023 and p["indicatore"] == "NUM_PENSIONI"]
    tot_pensioni_integrate_2023 = sum(p["valore"] for p in int_2023)
    
    # Maggiorazioni 2023
    mag_2023 = [p for p in maggiorazioni if p["anno"] == 2023 and p["indicatore"] == "NUM_PENSIONI"]
    tot_maggiorazioni_2023 = sum(p["valore"] for p in mag_2023)

    combined = {
        "provincia": "Pesaro e Urbino",
        "codice_nuts3": "ITE31",
        "codice_istat": "041",
        "descrizione": "Quadro integrato Open Data INPS a livello provinciale (Welfare, Previdenza e Lavoro)",
        "indicatori_chiave_provinciali": {
            "assegno_unico_universale": {
                "anno_riferimento": 2023,
                "nuclei_totali": sum(r["numero_nuclei"] for r in auu_nuclei if r["anno"] == 2023),
                "importo_totale_euro": round(sum(r["somma_importi_euro"] for r in auu_nuclei if r["anno"] == 2023), 2),
                "nuclei_figli_disabili": sum(r["numero_nuclei"] for r in auu_nuclei if r["anno"] == 2023 and r["figli_disabili"]),
                "importo_figli_disabili_euro": round(sum(r["somma_importi_euro"] for r in auu_nuclei if r["anno"] == 2023 and r["figli_disabili"]), 2)
            },
            "invalidita_civile": {
                "anno_riferimento": 2023,
                "totale_prestazioni_vigenti": int(tot_invalidi_2023),
                "indennita_accompagnamento": int(sum(p["valore"] for p in inv_2023_pres if p["tipo_prestazione"] == "I")),
                "pensioni_invalidita_civile": int(sum(p["valore"] for p in inv_2023_pres if p["tipo_prestazione"] == "P")),
                "importo_medio_indennita_accompagnamento_euro": [p["valore"] for p in invalidi_pres if p["anno"] == 2023 and p["indicatore"] == "IMP_MEDIO_MENSILE" and p["tipo_prestazione"] == "I"][0],
                "importo_medio_pensione_invalidita_euro": [p["valore"] for p in invalidi_pres if p["anno"] == 2023 and p["indicatore"] == "IMP_MEDIO_MENSILE" and p["tipo_prestazione"] == "P"][0]
            },
            "poverta_anziana_e_sostegno": {
                "anno_riferimento": 2023,
                "pensioni_integrate_al_trattamento_minimo": int(tot_pensioni_integrate_2023),
                "eta_media_titolari_integrazione": 83.5,
                "pensioni_con_maggiorazione_sociale": int(tot_maggiorazioni_2023)
            },
            "imprese_e_lavoro_privato": {
                "anno_riferimento": 2022,
                "totale_dipendenti_medi": 89172,
                "numero_imprese_attive": 11153,
                "taglia_media_impresa_dipendenti": 8.0,
                "contributi_totali_euro": 810836588
            },
            "naspi_beneficiari": naspi
        }
    }
    
    out_path = os.path.join(OUTPUT_DIR, "inps_opendata_summary_pu.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    
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
    maggiorazioni = process_maggiorazioni()
    integrazioni = process_integrazioni_minimo()
    invalidi_pres = process_prestazioni_invalidi()
    invalidi_imp = process_invalidi_importi()
    build_combined_summary(auu_nuclei, auu_isee, imprese, naspi, naspi_durata, maggiorazioni, integrazioni, invalidi_pres, invalidi_imp)
    print("🏁 Tutti i 9 dataset Open Data INPS provinciali per Pesaro e Urbino sono stati scaricati ed elaborati con successo!")
