# Previsioni Meteo Province Italiane

Questo progetto fornisce uno script Python che ogni mattina scarica le previsioni di temperatura oraria per i prossimi cinque giorni di tutte le province italiane utilizzando l'API di [Open‑Meteo](https://open-meteo.com).

## Installazione

```bash
pip install -r requirements.txt
```

## Utilizzo

```bash
python extract_forecasts.py
```

I dati vengono salvati nella cartella `data/` con nome `previsioni_<data>.csv`.
La prima colonna del file contiene la provincia, mentre la prima riga riporta gli orari delle previsioni.

Per testare rapidamente si può limitare il numero di province elaborate:

```bash
python extract_forecasts.py --limit 3
```

## Esecuzione giornaliera automatica

Per eseguire lo script ogni giorno alle 7:00, aggiungere la seguente riga al proprio `crontab`:

```cron
0 7 * * * /usr/bin/python /percorso/assoluto/extract_forecasts.py >> /percorso/assoluto/log.txt 2>&1
```

Questa pianificazione scaricherà le previsioni ogni mattina e le registrerà in un file di log.
