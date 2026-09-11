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
├── README.md               # Documentazione e linee guida del laboratorio
├── .gitignore              # Esclusioni git
├── data/
│   ├── comuni_pu.json      # Anagrafica e classificazione zonale dei 50 comuni di PU
│   └── raw/                # Dataset scaricati (ISTAT, Regione Marche)
├── scripts/
│   ├── fetch_demo_istat.py # Script di download/estrazione da ISTAT Demo
│   └── process_data.py     # Pipeline di elaborazione e calcolo indicatori
└── prototypes/             # Prototipi HTML/JS per mappe e visualizzazioni
```

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
