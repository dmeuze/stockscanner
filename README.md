# StockScanner

Een eenvoudige webapplicatie voor het scannen van crypto- en NASDAQ-aandelen op basis van technische strategieën.

## Features

- **Crypto Scanner**: Analyseer geselecteerde crypto-symbolen op Binance met verschillende strategieën (RSI, Bollinger Bands, MACD, MA, Volume Spike, Golden/Death Cross).
- **NASDAQ Scanner**: Analyseer een vaste lijst van NASDAQ-symbolen op dagbasis.
- **Tijdframe-selectie**: Kies voor crypto uit 5m, 15m, 1h, 4h, 1d (voor NASDAQ alleen 1d).
- **Resultatenoverzicht**: Bekijk en download eerdere scanresultaten.
- **TradingView integratie**: Directe links naar grafieken op TradingView.
- **Webinterface**: Gebruiksvriendelijke Flask-app met moderne UI.

## Installatie

1. **Clone de repository**

   ```bash
   git clone https://github.com/dmeuze/stockscanner.git
   cd stockscanner
   ```

2. **Installeer de vereiste packages**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start de server**
   ```bash
   python integrated_server.py
   ```
   De app is bereikbaar op [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Gebruik

- Kies op de homepagina voor Crypto of NASDAQ.
- Selecteer een strategie en (voor crypto) een tijdframe.
- Bekijk de resultaten direct in de browser of download als JSON.
- Gebruik de TradingView-link voor grafiekanalyse.

## Projectstructuur

```
crypto_scanner/
  crypto_screener.py
nasdaq_scanner/
  nasdaq_screener.py
templates/
  index.html
  strategies.html
  results.html
  results_list.html
  processing.html
integrated_server.py
requirements.txt
```

## Licentie

MIT

---

_Gemaakt door [dmeuze](https://github.com/dmeuze) – feedback en bijdragen welkom!_
