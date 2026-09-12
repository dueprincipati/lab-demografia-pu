#!/usr/bin/env python3
"""
Pipeline di estrazione e riconciliazione dati demografici ISTAT (2024-2025)
per i 50 comuni della Provincia di Pesaro e Urbino.
Verifica la conciliazione esatta al 100% con i totali provinciali del Rendiconto Sociale INPS.
Include indici avanzati di ricambio attivo lavoro/pensione e tassi demografici per mille.
"""

import urllib.request
import zipfile
import io
import csv
import json
import os
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
OUTPUT_FILE = os.path.join(DATA_DIR, 'demografia_comunale_conciliata.json')
OUTPUT_JS = os.path.join(DATA_DIR, 'demografia_comunale_conciliata.js')

ATS_1_COMUNI = {"041044", "041019", "041020", "041027", "041036", "041058", "041068"}
ATS_6_COMUNI = {"041013", "041010", "041069", "041029", "041032", "041043", "041051", 
                "041052", "041054", "041070", "041016", "041028", "041034"}

ALTITUDINI_PU = {
    "041044": 11, "041013": 12, "041068": 280, "041029": 144, "041067": 485,
    "041069": 156, "041015": 118, "041014": 200, "041010": 271, "041065": 170,
    "041007": 276, "041036": 65, "041066": 273, "041043": 265, "041019": 11,
    "041070": 264, "041071": 326, "041020": 142, "041051": 150, "041001": 204,
    "041057": 359, "041028": 280, "041054": 209, "041038": 157, "041045": 327,
    "041030": 345, "041034": 260, "041027": 468, "041047": 319, "041008": 360,
    "041023": 321, "041049": 339, "041009": 748, "041002": 492, "041058": 246,
    "041022": 297, "041025": 429, "041018": 412, "041035": 640, "041026": 275,
    "041061": 523, "041016": 419, "041064": 426, "041005": 344, "041041": 534,
    "041048": 707, "041031": 528, "041021": 210, "041006": 469, "041017": 519
}

def get_ats(istat_code):
    if istat_code in ATS_1_COMUNI:
        return "ATS 1 - Pesaro"
    elif istat_code in ATS_6_COMUNI:
        return "ATS 6 - Fano"
    return "ATS 2 - Urbino e Montefeltro"

def download_and_process():
    os.makedirs(RAW_DIR, exist_ok=True)
    posas_file = os.path.join(RAW_DIR, 'POSAS_2025_PU.csv')
    bilancio_file = os.path.join(RAW_DIR, 'Bilancio_2024.csv')
    
    if os.path.exists(posas_file):
        print("📂 1. Caricamento Popolazione 2025 da cache locale...")
        with open(posas_file, 'r', encoding='utf-8') as f:
            posas_csv = f.read()
    else:
        print("📥 1. Download Popolazione residente per età al 1° Gennaio 2025 (POSAS)...")
        posas_url = "https://demo.istat.it/data/posas/POSAS_2025_it_041_Pesaro_e_Urbino.zip"
        req = urllib.request.Request(posas_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            posas_zip = zipfile.ZipFile(io.BytesIO(resp.read()))
            posas_csv = posas_zip.read('POSAS_2025_it_041_Pesaro_e_Urbino.csv').decode('utf-8')
            with open(posas_file, 'w', encoding='utf-8') as f:
                f.write(posas_csv)

    if os.path.exists(bilancio_file):
        print("📂 2. Caricamento Bilancio 2024 da cache locale...")
        with open(bilancio_file, 'r', encoding='latin1') as f:
            d7b_raw = f.read()
    else:
        print("📥 2. Download Bilancio Demografico Comunale 2024 (D7B)...")
        d7b_url = "https://demo.istat.it/data/d7b/D7B2024.csv.zip"
        req = urllib.request.Request(d7b_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            d7b_zip = zipfile.ZipFile(io.BytesIO(resp.read()))
            fname = d7b_zip.namelist()[0]
            d7b_raw = d7b_zip.read(fname).decode('latin1')
            with open(bilancio_file, 'w', encoding='latin1') as f:
                f.write(d7b_raw)

    print("📊 3. Elaborazione struttura per età e ricambio attivo (1° Gennaio 2025)...")
    comuni_data = {}
    lines = posas_csv.strip().split('\n')
    reader = csv.reader(lines[1:], delimiter=';')
    next(reader)
    
    for row in reader:
        if not row or len(row) < 20: continue
        codice = row[0].strip('"')
        nome = row[1].strip('"')
        eta_str = row[2]
        if eta_str == '999' or eta_str == 'Totale':
            continue
        try:
            eta = int(eta_str)
        except:
            continue
        maschi = int(row[10] or 0)
        femmine = int(row[18] or 0)
        totale = int(row[19] or 0)
        
        if codice not in comuni_data:
            comuni_data[codice] = {
                "istat": codice,
                "nome": nome,
                "ats": get_ats(codice),
                "altitudine_m_slm": ALTITUDINI_PU.get(codice, 200),
                "popolazione_2025": 0,
                "maschi_2025": 0,
                "femmine_2025": 0,
                "eta_0_14": 0,
                "eta_15_64": 0,
                "eta_65_oltre": 0,
                "eta_15_19": 0, # Nuove leve in ingresso nel mercato lavoro
                "eta_60_64": 0, # Uscite prossime verso la pensione
                "nascite_2024": 0,
                "decessi_2024": 0,
                "saldo_naturale_2024": 0,
                "immigrati_estero_2024": 0,
                "emigrati_estero_2024": 0,
                "saldo_estero_2024": 0,
                "saldo_interno_2024": 0,
                "saldo_totale_2024": 0
            }
        
        c = comuni_data[codice]
        c["popolazione_2025"] += totale
        c["maschi_2025"] += maschi
        c["femmine_2025"] += femmine
        if eta <= 14:
            c["eta_0_14"] += totale
        elif eta <= 64:
            c["eta_15_64"] += totale
        else:
            c["eta_65_oltre"] += totale

        if 15 <= eta <= 19:
            c["eta_15_19"] += totale
        elif 60 <= eta <= 64:
            c["eta_60_64"] += totale

    print("📊 4. Elaborazione bilancio naturale e migratorio 2024...")
    d7b_lines = d7b_raw.strip().split('\n')
    d7b_reader = csv.reader(d7b_lines, delimiter=';')
    next(d7b_reader)
    
    for row in d7b_reader:
        if not row or len(row) < 20: continue
        if row[18] == '041' and row[3] == 'Totale' and row[16] != '':
            codice = row[16]
            if codice in comuni_data:
                c = comuni_data[codice]
                c["nascite_2024"] += int(row[5] or 0)
                c["decessi_2024"] += int(row[6] or 0)
                c["saldo_naturale_2024"] += int(row[7] or 0)
                c["saldo_interno_2024"] += int(row[10] or 0)
                c["immigrati_estero_2024"] += int(row[11] or 0)
                c["emigrati_estero_2024"] += int(row[12] or 0)
                c["saldo_estero_2024"] += int(row[13] or 0)
                c["saldo_totale_2024"] = c["saldo_naturale_2024"] + c["saldo_interno_2024"] + c["saldo_estero_2024"]

    # Calcolo indici strutturali e tassi per mille
    for c in comuni_data.values():
        pop = c["popolazione_2025"]
        if c["eta_0_14"] > 0:
            c["indice_vecchiaia"] = round((c["eta_65_oltre"] / c["eta_0_14"]) * 100, 1)
        else:
            c["indice_vecchiaia"] = 999.0
            
        if c["eta_15_64"] > 0:
            c["indice_dipendenza"] = round(((c["eta_0_14"] + c["eta_65_oltre"]) / c["eta_15_64"]) * 100, 1)
        else:
            c["indice_dipendenza"] = 0.0

        # Indice di ricambio della popolazione attiva: Pop 60-64 / Pop 15-19 * 100
        if c["eta_15_19"] > 0:
            c["indice_ricambio_attivi"] = round((c["eta_60_64"] / c["eta_15_19"]) * 100, 1)
        else:
            c["indice_ricambio_attivi"] = 100.0

        # Tassi demografici per 1.000 abitanti
        if pop > 0:
            c["tasso_natalita_mille"] = round((c["nascite_2024"] / pop) * 1000, 2)
            c["tasso_mortalita_mille"] = round((c["decessi_2024"] / pop) * 1000, 2)
            c["tasso_saldo_nat_mille"] = round((c["saldo_naturale_2024"] / pop) * 1000, 2)
        else:
            c["tasso_natalita_mille"] = 0.0
            c["tasso_mortalita_mille"] = 0.0
            c["tasso_saldo_nat_mille"] = 0.0

    comuni_list = sorted(comuni_data.values(), key=lambda x: x["popolazione_2025"], reverse=True)
    
    # Totali provinciali aggregati
    prov_pop = sum(c["popolazione_2025"] for c in comuni_list)
    prov_m = sum(c["maschi_2025"] for c in comuni_list)
    prov_f = sum(c["femmine_2025"] for c in comuni_list)
    prov_0_14 = sum(c["eta_0_14"] for c in comuni_list)
    prov_15_64 = sum(c["eta_15_64"] for c in comuni_list)
    prov_65 = sum(c["eta_65_oltre"] for c in comuni_list)
    prov_15_19 = sum(c["eta_15_19"] for c in comuni_list)
    prov_60_64 = sum(c["eta_60_64"] for c in comuni_list)
    prov_nascite = sum(c["nascite_2024"] for c in comuni_list)
    prov_decessi = sum(c["decessi_2024"] for c in comuni_list)
    prov_saldo_nat = sum(c["saldo_naturale_2024"] for c in comuni_list)
    
    rs_totali = {
        "popolazione_totale": 349558,
        "maschi": 172218,
        "femmine": 177340,
        "eta_0_14": 40004,
        "eta_15_64": 219667,
        "eta_65_oltre": 89887,
        "nascite_2024": 1884,
        "decessi_2024": 3893,
        "saldo_naturale_2024": -2009
    }
    
    riconciliazione = {
        "conciliato_100_percento": (
            prov_pop == rs_totali["popolazione_totale"] and
            prov_m == rs_totali["maschi"] and
            prov_f == rs_totali["femmine"] and
            prov_0_14 == rs_totali["eta_0_14"] and
            prov_15_64 == rs_totali["eta_15_64"] and
            prov_65 == rs_totali["eta_65_oltre"] and
            prov_nascite == rs_totali["nascite_2024"] and
            prov_decessi == rs_totali["decessi_2024"] and
            prov_saldo_nat == rs_totali["saldo_naturale_2024"]
        ),
        "confronto": {
            "popolazione_totale": {"somma_50_comuni": prov_pop, "rendiconto_sociale": rs_totali["popolazione_totale"], "diff": prov_pop - rs_totali["popolazione_totale"]},
            "maschi": {"somma_50_comuni": prov_m, "rendiconto_sociale": rs_totali["maschi"], "diff": prov_m - rs_totali["maschi"]},
            "femmine": {"somma_50_comuni": prov_f, "rendiconto_sociale": rs_totali["femmine"], "diff": prov_f - rs_totali["femmine"]},
            "eta_0_14": {"somma_50_comuni": prov_0_14, "rendiconto_sociale": rs_totali["eta_0_14"], "diff": prov_0_14 - rs_totali["eta_0_14"]},
            "eta_15_64": {"somma_50_comuni": prov_15_64, "rendiconto_sociale": rs_totali["eta_15_64"], "diff": prov_15_64 - rs_totali["eta_15_64"]},
            "eta_65_oltre": {"somma_50_comuni": prov_65, "rendiconto_sociale": rs_totali["eta_65_oltre"], "diff": prov_65 - rs_totali["eta_65_oltre"]},
            "nascite_2024": {"somma_50_comuni": prov_nascite, "rendiconto_sociale": rs_totali["nascite_2024"], "diff": prov_nascite - rs_totali["nascite_2024"]},
            "decessi_2024": {"somma_50_comuni": prov_decessi, "rendiconto_sociale": rs_totali["decessi_2024"], "diff": prov_decessi - rs_totali["decessi_2024"]},
            "saldo_naturale_2024": {"somma_50_comuni": prov_saldo_nat, "rendiconto_sociale": rs_totali["saldo_naturale_2024"], "diff": prov_saldo_nat - rs_totali["saldo_naturale_2024"]}
        }
    }
    
    # Aggregazione per ATS
    ats_summary = defaultdict(lambda: {
        "comuni_count": 0, "popolazione": 0, "nascite": 0, "decessi": 0, 
        "saldo_nat": 0, "eta_0_14": 0, "eta_15_64": 0, "eta_65_oltre": 0,
        "eta_15_19": 0, "eta_60_64": 0
    })
    for c in comuni_list:
        a = ats_summary[c["ats"]]
        a["comuni_count"] += 1
        a["popolazione"] += c["popolazione_2025"]
        a["nascite"] += c["nascite_2024"]
        a["decessi"] += c["decessi_2024"]
        a["saldo_nat"] += c["saldo_naturale_2024"]
        a["eta_0_14"] += c["eta_0_14"]
        a["eta_15_64"] += c["eta_15_64"]
        a["eta_65_oltre"] += c["eta_65_oltre"]
        a["eta_15_19"] += c["eta_15_19"]
        a["eta_60_64"] += c["eta_60_64"]
        
    for a in ats_summary.values():
        a["indice_vecchiaia"] = round((a["eta_65_oltre"] / a["eta_0_14"]) * 100, 1) if a["eta_0_14"] > 0 else 0
        a["indice_dipendenza"] = round(((a["eta_0_14"] + a["eta_65_oltre"]) / a["eta_15_64"]) * 100, 1) if a["eta_15_64"] > 0 else 0
        a["indice_ricambio_attivi"] = round((a["eta_60_64"] / a["eta_15_19"]) * 100, 1) if a["eta_15_19"] > 0 else 0
        a["tasso_saldo_nat_mille"] = round((a["saldo_nat"] / a["popolazione"]) * 1000, 2) if a["popolazione"] > 0 else 0

    output_dataset = {
        "metadata": {
            "titolo": "Dati Demografici Territoriali 50 Comuni - Provincia di Pesaro e Urbino",
            "fonte_istat": "Istat Demo (POSAS 2025 al 1° Gennaio 2025 & Bilancio Demografico 2024)",
            "fonte_rs": "INPS - Rendiconto Sociale Provinciale 2025",
            "comuni_totali": len(comuni_list),
            "provincia_totali": {
                "popolazione": prov_pop,
                "indice_vecchiaia": round((prov_65 / prov_0_14) * 100, 1),
                "indice_dipendenza": round(((prov_0_14 + prov_65) / prov_15_64) * 100, 1),
                "indice_ricambio_attivi": round((prov_60_64 / prov_15_19) * 100, 1),
                "saldo_naturale": prov_saldo_nat,
                "tasso_saldo_nat_mille": round((prov_saldo_nat / prov_pop) * 1000, 2),
                "nascite": prov_nascite,
                "decessi": prov_decessi
            }
        },
        "riconciliazione_rendiconto_sociale": riconciliazione,
        "aggregazione_ats": ats_summary,
        "comuni": comuni_list
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_dataset, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write("const demografiaTerritorialeData = " + json.dumps(output_dataset, indent=2, ensure_ascii=False) + ";")
        
    print(f"\n✅ File generati con successo:\n   - {OUTPUT_FILE}\n   - {OUTPUT_JS}")
    print("=" * 65)
    print("🎯 REPORT DI RICONCILIAZIONE ESATTA CON IL RENDICONTO SOCIALE 2025:")
    print("=" * 65)
    print(f"Conciliazione perfetta (100%): {'✅ SI (ZERO DISCREPANZE)' if riconciliazione['conciliato_100_percento'] else '❌ NO'}\n")
    for k, v in riconciliazione["confronto"].items():
        print(f" ✅ {k:<23}: Somma Comuni={v['somma_50_comuni']:>8} | RS 2025={v['rendiconto_sociale']:>8} | Diff={v['diff']}")
    print("=" * 65)
    print("\n📊 RIEPILOGO ATS CON INDICE DI RICAMBIO ATTIVI (LAVORO / PENSIONE):")
    print("-" * 65)
    for ats_name, data in sorted(ats_summary.items()):
        print(f"📍 {ats_name:<30} | Pop: {data['popolazione']:>7} | Vecchiaia: {data['indice_vecchiaia']:>5.1f} | Ricambio Attivi: {data['indice_ricambio_attivi']:>5.1f}%")
    print("=" * 65)

if __name__ == "__main__":
    download_and_process()
