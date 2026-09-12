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
│   └── raw/                            # Dataset sorgente ISTAT (Bilancio 2024 e Popolazione per Età)
├── scripts/
│   ├── download_and_process.py         # Download ISTAT e quadratura contabile con RS 2025
│   └── generate_geojson.py             # Generazione confini GeoJSON, centroidi e altimetria
└── prototypes/
    ├── dashboard_territoriale.html     # Dashboard GIS e schede comunali con quadratura RS
    └── geospatial_lab.html             # Atelier Geospaziale (8 modelli della famiglia DataVizProject)
```

### 🗺️ Prototipi Interattivi Disponibili
1. **`dashboard_territoriale.html`**:
   - Mappa coropletica interattiva dei 50 comuni (Indice di vecchiaia, Popolazione, Saldo naturale, Dipendenza strutturale).
   - Matrice dei quadranti demografici (Dinamici costieri, Invecchiati stabili, Fragili montani, In transizione).
   - Piramidi d'età per singolo comune e tabella analitica completa.
   - Badge di quadratura contabile 100% con il Rendiconto Sociale 2025 (differenza = 0).

2. **`geospatial_lab.html` (Atelier Geospaziale DataVizProject)**:
   - Sperimentazione guidata delle forme visive della famiglia [DataVizProject Geospatial](https://datavizproject.com/family/geospatial/):
     - **Choropleth Map**: densità e indici con normalizzazione d'area.
     - **Bubble Map**: simboli proporzionali per evitare il bias visivo dei grandi territori montani spopolati.
     - **Dot Density Map**: simulazione stocastica puntiforme (1 punto = 100 residenti, coorti d'età).
     - **Pie Chart on Map**: micro-torte geolocalizzate delle tre grandi fasce generazionali (0-14, 15-64, 65+).
     - **Bar Chart on Map**: confronto visivo diretto su mappa tra Nati vs Decessi e Forze Lavoro vs Pensionati.
     - **Connection / Flow Map**: linee animate di gravitazione demografica e socio-sanitaria dai comuni periferici ai 3 Poli dei Distretti ATS (Pesaro, Urbino, Fano).
     - **Dorling Cartogram**: simulazione fisica D3.js a forze repulsive per rappresentare il vero peso demografico (Pesaro e Fano dominanti).
     - **Profile Map**: spaccato altimetrico e demografico dalla costa adriatica (0-15m) alla cresta appenninica (748m di Carpegna, Montefeltro e Catria/Nerone).

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
