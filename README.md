# 🔬 Lab Demografia PU - Sperimentazioni Territoriali

> **Laboratorio sperimentale per l'analisi territoriale e sub-provinciale delle dinamiche demografiche della Provincia di Pesaro e Urbino.**

Questo repository è dedicato all'acquisizione, elaborazione e prototipazione visuale dei dati demografici a livello comunale e sub-provinciale, integrando fonti ufficiali come **ISTAT**, **Regione Marche (SNAI)** e **ANPR** a supporto della Dashboard Socio-Economica provinciale.

---

## 🎯 Obiettivi di Ricerca e Prototipazione

1. **Disaggregazione Comunale (50 Comuni)**:
   - Analisi granulare del bilancio demografico per i 50 comuni della provincia.
   - Indicatori di senilizzazione: indice di vecchiaia, indice di dipendenza strutturale, età media.
   - Saldo naturale vs saldo migratorio (interno ed estero).

2. **Divergenza Costa vs Aree Interne (SNAI)**:
   - Polarizzazione costiera (Pesaro, Fano, Gabicce, Mondolfo) ad alta densità abitativa.
   - Fasce vallive intermedie (Bassa/Media Valle del Foglia e del Metauro).
   - Zone montane e Aree Interne (Montefeltro, Catria e Nerone, Alta Valle del Metauro) con dinamiche di spopolamento e denatalità.

3. **Mappatura Cartografica e GIS**:
   - Generazione di mappe coropletiche (GeoJSON Istat / Leaflet / D3.js).
   - Visualizzazione territoriale degli indici demografici a livello comunale.

4. **Incrocio con Dati Previdenziali ed Economici**:
   - Messa in relazione dei dati demografici ISTAT con i volumi pensionistici e le prestazioni di sostegno al reddito registrati nel Rendiconto Sociale INPS.

---

## 📂 Struttura del Progetto

```
lab-demografia-pu/
├── README.md                           # Documentazione e linee guida del laboratorio
├── data/
│   ├── comuni_pu_geo.json / .js        # Poligoni GeoJSON ISTAT 50 comuni con centroidi ed elevazione
│   ├── demografia_comunale_conciliata.json / .js  # Dataset 50 comuni conciliato al 100% con il RS 2025
│   ├── inps_opendata/                  # 9 dataset ufficiali Open Data INPS provinciali (ITE31)
│   │   ├── inps_auu_nuclei_pu.json     # Assegno Unico nuclei e somme erogate (2022-2024)
│   │   ├── inps_auu_isee_disabilita_pu.json # AUU per 3 fasce ISEE, età e disabilità
│   │   ├── inps_imprese_dipendenti_pu.json  # Imprese, dipendenti e contributi privati (2013-2022)
│   │   ├── inps_naspi_beneficiari_pu.json   # Beneficiari NASpI annuali (2018-2022)
│   │   ├── inps_naspi_durata_pu.json        # NASpI per durata teorica in mesi (M0-M24)
│   │   ├── inps_prestazioni_invalidi_civili_pu.json # Invalidità civile e accompagnamento (2018-2023)
│   │   ├── inps_invalidi_civili_eta_importi_pu.json # Invalidità per età e classi d'importo (2019-2023)
│   │   ├── inps_pensioni_integrazioni_minimo_pu.json# Pensioni integrate al trattamento minimo (2019-2023)
│   │   ├── inps_pensioni_maggiorazioni_pu.json     # Pensioni con maggiorazioni sociali (2019-2023)
│   │   └── inps_opendata_summary_pu.json / .js     # Quadro riassuntivo integrato provinciale
│   └── raw/                            # Dataset sorgente ISTAT (Bilancio 2024 e Popolazione per Età)
├── scripts/
│   ├── download_and_process.py         # Download ISTAT e quadratura contabile con RS 2025
│   ├── download_inps_opendata.py       # Pipeline automatica di estrazione Open Data INPS provinciali
│   └── generate_geojson.py             # Generazione confini GeoJSON, centroidi e altimetria
└── prototypes/
    ├── dashboard_territoriale.html     # Dashboard GIS e schede comunali con quadratura RS
    ├── geospatial_lab.html             # Atelier Geospaziale (8 modelli della famiglia DataVizProject)
    └── connessione_demografia_welfare.html # Ponte Demografia ➔ Welfare INPS (Sankey Flow + Mappa Bivariata 3x3)
```

### 🗺️ Prototipi Interattivi Disponibili
1. **`dashboard_territoriale.html`**:
   - Mappa coropletica interattiva dei 50 comuni (Indice di vecchiaia, Popolazione, Saldo naturale, Dipendenza strutturale).
   - Matrice dei quadranti demografici (Dinamici costieri, Invecchiati stabili, Fragili montani, In transizione).
   - Piramidi d'età per singolo comune e tabella analitica completa.
   - Badge di quadratura contabile 100% con il Rendiconto Sociale 2025 (differenza = 0).

2. **`geospatial_lab.html` (Atelier Geospaziale DataVizProject)**:
   - Sperimentazione guidata delle 8 forme visive della famiglia [DataVizProject Geospatial](https://datavizproject.com/family/geospatial/):
     - Choropleth Map, Bubble Map, Dot Density Map, Pie Chart on Map, Bar Chart on Map, Connection/Flow Map verso i poli ATS, Dorling Cartogram force-directed, Profile Map Altimetrico Costa ➔ Appennino.

3. **`connessione_demografia_welfare.html` (Ponte Demografia ➔ Welfare & Previdenza INPS)**:
   - **Diagramma di Flusso Interattivo (Sankey)**: mostra come la popolazione ISTAT (349.558) genera flussi verso l'Assegno Unico (105,5 M€), l'occupazione e NASpI, le pensioni IVS (99.246), le integrazioni al minimo (18.664) e l'invalidità civile / indennità di accompagnamento (21.340).
   - **Mappa Coropletica Bivariata 3×3**: incrocio cartografico simultaneo tra l'Indice di Vecchiaia (Asse X) e l'Indice di Ricambio della Popolazione Attiva 60-64 / 15-19 (Asse Y), evidenziando i comuni dell'entroterra montano a "Doppia Vulnerabilità".
   - Scheda di dettaglio comunale con indicatori di pressione e raccordo con i dati provinciali INPS.

---

## 🌐 Fonti Dati Ufficiali di Riferimento

* **[Demo Istat](https://demo.istat.it/)**: Bilancio demografico mensile/annuale e popolazione residente comunale.
* **[IstatData](https://esploradati.istat.it/)**: Tavole di mortalità, fecondità e indicatori strutturali.
* **[Censimento Permanente ISTAT](https://www.istat.it/statistiche-per-temi/censimenti/)**: Famiglie, istruzione, pendolarismo.
* **[Regione Marche - Statistica](https://www.regione.marche.it/Entra-in-Regione/Statistica)**: Rapporto sulla popolazione e monitoraggio Aree Interne (SNAI).
* **[ANPR Open Data](https://www.anagrafenazionale.interno.it/dati-statistici/)**: Dati anagrafici aperti.

---

## 🚀 Utilizzo Rapido

```bash
# Clone autonomo
git clone https://github.com/dueprincipati/lab-demografia-pu.git
cd lab-demografia-pu

# Esecuzione script di prova
python3 scripts/fetch_demo_istat.py
```
