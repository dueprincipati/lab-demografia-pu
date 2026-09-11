#!/usr/bin/env python3
"""
Script di utilità per l'analisi territoriale dei comuni della Provincia di Pesaro e Urbino.
Permette di consultare l'anagrafica dei 50 comuni, aggregarli per zona e predisporre le query per Istat Demo.
"""

import json
import os
import argparse
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'comuni_pu.json')

def load_comuni():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_zones(comuni):
    zones = defaultdict(list)
    for c in comuni:
        zones[c['zona']].append(c['nome'])
    return zones

def print_summary():
    comuni = load_comuni()
    print("=" * 60)
    print(f"🏛️ PROVINCIA DI PESARO E URBINO - 50 COMUNI PER ZONA TERRITORIALE")
    print("=" * 60)
    zones = list_zones(comuni)
    for zone, names in sorted(zones.items()):
        print(f"\n📍 {zone} ({len(names)} comuni):")
        print(f"   {', '.join(sorted(names))}")
    print("\n" + "=" * 60)
    print("🌐 Fonti consigliate per il download dei dati:")
    print("   • Demo Istat: https://demo.istat.it/")
    print("   • IstatData:  https://esploradati.istat.it/")
    print("   • Regione Marche: https://statistica.regione.marche.it/")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Lab Demografia PU - Analisi Territoriale")
    parser.add_argument('--summary', action='store_true', default=True, help="Mostra riepilogo comuni e zone")
    args = parser.parse_args()
    if args.summary:
        print_summary()

if __name__ == "__main__":
    main()
