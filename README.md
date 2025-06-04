# CillyBot Swing Analyse

Dieses Projekt enthält ein einfaches Skript zur Analyse von Aktien anhand historischer Kursdaten.

## Nutzung

1. Installiere die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```
2. Setze optional die Umgebungsvariable `SHEET_URL`, um den Ort deiner Watchlist (CSV-Format) anzugeben. Standardmäßig wird eine öffentliche Google-Sheet-URL verwendet.
3. Starte das Skript:
   ```bash
   python main.py
   ```

Das Skript erzeugt die Datei `swing_signale.csv` mit den Ergebnissen.

