"""
Universe definitions for the momentum strategy.

Two pre-selected universes of 20 stocks each, chosen based on momentum 12-1
performance during the 2015-2018 period. This pre-selection avoids look-ahead
bias when running the strategy on 2019+ data.

Pre-selection method:
1. Compute monthly momentum 12-1 for all stocks in the broader universe
   (IBEX 35 full / S&P 500 representative sample of ~93 stocks) for 2015-2018
2. Average the monthly momentum values per stock
3. Take the top 20 by average momentum

Yahoo Finance ticker conventions:
- IBEX stocks: suffix ".MC" (Madrid)
- S&P 500 stocks: no suffix (NYSE/NASDAQ)
"""

# ============================================================================
# IBEX 35 — Top 20 by historical momentum 12-1 (2015-2018)
# ============================================================================
# Note: SAN ticker is unique in Spain (Santander).
# Some tickers differ between BME and Yahoo Finance.
IBEX_TOP20 = {
    "ROVI": "ROVI.MC",   # Laboratorios Farmacéuticos Rovi
    "ANE":  "ANE.MC",    # Corporación Acciona Energías Renovables
    "CLNX": "CLNX.MC",   # Cellnex Telecom
    "AENA": "AENA.MC",   # AENA
    "ACX":  "ACX.MC",    # Acerinox
    "FER":  "FER.MC",    # Ferrovial
    "UNI":  "UNI.MC",    # Unicaja Banco
    "ELE":  "ELE.MC",    # Endesa
    "REP":  "REP.MC",    # Repsol
    "FDR":  "FDR.MC",    # Fluidra
    "NTGY": "NTGY.MC",   # Naturgy
    "SCYR": "SCYR.MC",   # Sacyr
    "GRF":  "GRF.MC",    # Grifols
    "IBE":  "IBE.MC",    # Iberdrola
    "EBRO": "EBRO.MC",   # Ebro Foods
    "ANA":  "ANA.MC",    # Acciona
    "BKT":  "BKT.MC",    # Bankinter
    "CABK": "CABK.MC",   # CaixaBank
    "COL":  "COL.MC",    # Inmobiliaria Colonial
    "SAN":  "SAN.MC",    # Banco Santander
}

# ============================================================================
# S&P 500 — Top 20 by historical momentum 12-1 (2015-2018)
# ============================================================================
SP500_TOP20 = {
    "BA":    "BA",       # Boeing
    "NVDA":  "NVDA",     # NVIDIA
    "ADBE":  "ADBE",     # Adobe
    "NFLX":  "NFLX",     # Netflix
    "AVGO":  "AVGO",     # Broadcom
    "AMD":   "AMD",      # Advanced Micro Devices
    "MSFT":  "MSFT",     # Microsoft
    "MCD":   "MCD",      # McDonald's
    "INTU":  "INTU",     # Intuit
    "V":     "V",        # Visa
    "DIS":   "DIS",      # Walt Disney
    "NKE":   "NKE",      # Nike
    "TSLA":  "TSLA",     # Tesla
    "BAC":   "BAC",      # Bank of America
    "NOW":   "NOW",      # ServiceNow
    "MA":    "MA",       # Mastercard
    "TXN":   "TXN",      # Texas Instruments
    "ACN":   "ACN",      # Accenture
    "ABBV":  "ABBV",     # AbbVie
    "CRM":   "CRM",      # Salesforce
}

# ============================================================================
# Strategy configuration
# ============================================================================
CONFIG = {
    # Position counts
    "N_SP500_POSITIONS": 4,         # Number of S&P 500 stocks to hold
    "N_IBEX_POSITIONS": 2,          # Number of IBEX stocks to hold
    
    # Capital weights (must sum to 1.0)
    "WEIGHT_SP500": 0.65,           # 65% of capital in US stocks
    "WEIGHT_IBEX": 0.30,            # 30% of capital in Spanish stocks
    "WEIGHT_CASH": 0.05,            # 5% cash buffer for commissions and slippage
    
    # Momentum calculation
    "LOOKBACK_MONTHS": 12,          # Total lookback window
    "SKIP_MONTHS": 1,               # Skip the most recent month (short-term reversal)
    
    # Commissions (IBKR Tiered)
    "COMMISSION_IBEX_EUR": 3.0,     # EUR per trade for Madrid (BME) stocks
    "COMMISSION_SP500_USD": 1.0,    # USD per trade for US stocks
    
    # Currency
    "EUR_USD_REFERENCE": 1.1758,    # Reference rate (12 May 2026)
}
