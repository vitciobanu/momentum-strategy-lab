"""
Universe definitions for the momentum strategy.

<<<<<<< HEAD
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
=======
The strategy operates on TWO COMPLETE universes that are scanned dynamically
each quarter to find the stocks with the strongest momentum:

  1. IBEX_35: all 35 components of the Spanish IBEX 35 index
  2. SP500_LARGE_CAP: the ~100 largest constituents of the S&P 500 by market cap

There is NO static pre-selection of "best stocks". Each rebalance computes
12-1 momentum on every stock in these universes and picks the top performers.

WHY NOT THE FULL S&P 500?
  - The top 100 represent ~80% of total S&P 500 market cap
  - These stocks have deep liquidity (important for execution)
  - Smaller S&P 500 components have noisier momentum signals
  - It keeps the data download fast (~135 vs. ~500 tickers each rebalance)

These lists should be reviewed periodically:
  - IBEX 35: index composition is reviewed twice a year (June, December) by BME.
    Update this file after each review.
  - SP500_LARGE_CAP: review yearly. The top 100 by market cap shifts gradually,
    but new entrants (e.g. recent IPOs, sector rotations) can be missed if the
    list goes stale.

LAST UPDATED: May 2026
  - IBEX 35: based on BME composition effective from September 2024
  - SP500_LARGE_CAP: based on market cap rankings as of Q1 2026

Yahoo Finance ticker conventions:
  - IBEX stocks: suffix ".MC" (Madrid)
  - S&P 500 stocks: no suffix (NYSE/NASDAQ); some use "-" for class shares
    (e.g. BRK-B for Berkshire Hathaway Class B)
"""

# ============================================================================
# IBEX 35 — All 35 components (official BME composition)
# Source: BME, last review September 2024
# ============================================================================
IBEX_35 = {
    "ACS":  "ACS.MC",    # ACS - Construction
    "ACX":  "ACX.MC",    # Acerinox - Steel
    "AENA": "AENA.MC",   # AENA - Aviation
    "AMS":  "AMS.MC",    # Amadeus IT Group - Tourism
    "ANA":  "ANA.MC",    # Acciona - Construction
    "ANE":  "ANE.MC",    # Acciona Energía - Energy
    "BBVA": "BBVA.MC",   # BBVA - Banking
    "BKT":  "BKT.MC",    # Bankinter - Banking
    "CABK": "CABK.MC",   # CaixaBank - Banking
    "CLNX": "CLNX.MC",   # Cellnex Telecom - Telecoms
    "COL":  "COL.MC",    # Inmobiliaria Colonial - Real Estate
    "ELE":  "ELE.MC",    # Endesa - Energy
    "ENG":  "ENG.MC",    # Enagás - Energy
    "FDR":  "FDR.MC",    # Fluidra - Manufacturing
    "FER":  "FER.MC",    # Ferrovial - Infrastructure
    "GRF":  "GRF.MC",    # Grifols - Pharmaceuticals
    "IAG":  "IAG.MC",    # International Airlines Group - Aviation
    "IBE":  "IBE.MC",    # Iberdrola - Energy
    "IDR":  "IDR.MC",    # Indra - IT
    "ITX":  "ITX.MC",    # Inditex - Textile
    "LOG":  "LOG.MC",    # Logista - Logistics
    "MAP":  "MAP.MC",    # Mapfre - Insurance
    "MRL":  "MRL.MC",    # Merlin Properties - Real Estate
    "MTS":  "MTS.MC",    # ArcelorMittal - Steel
    "NTGY": "NTGY.MC",   # Naturgy - Energy
    "PUIG": "PUIG.MC",   # Puig - Cosmetics
    "RED":  "RED.MC",    # Redeia Corporación - Energy
    "REP":  "REP.MC",    # Repsol - Oil & Gas
    "ROVI": "ROVI.MC",   # Laboratorios Rovi - Pharmaceuticals
    "SAB":  "SAB.MC",    # Banco Sabadell - Banking
    "SAN":  "SAN.MC",    # Santander - Banking
    "SCYR": "SCYR.MC",   # Sacyr - Construction
    "SLR":  "SLR.MC",    # Solaria - Solar Energy
    "TEF":  "TEF.MC",    # Telefónica - Telecoms
    "UNI":  "UNI.MC",    # Unicaja Banco - Banking
}

# ============================================================================
# S&P 500 LARGE CAP — Top 100 by market capitalization (~80% of index weight)
# Source: market cap rankings as of Q1 2026
# Sectorially diversified across all 11 GICS sectors
# ============================================================================
SP500_LARGE_CAP = {
    # Technology
    "NVDA":  "NVDA",     # NVIDIA
    "AAPL":  "AAPL",     # Apple
    "MSFT":  "MSFT",     # Microsoft
    "AVGO":  "AVGO",     # Broadcom
    "ORCL":  "ORCL",     # Oracle
    "CRM":   "CRM",      # Salesforce
    "ADBE":  "ADBE",     # Adobe
    "AMD":   "AMD",      # AMD
    "CSCO":  "CSCO",     # Cisco
    "NOW":   "NOW",      # ServiceNow
    "INTU":  "INTU",     # Intuit
    "QCOM":  "QCOM",     # Qualcomm
    "TXN":   "TXN",      # Texas Instruments
    "IBM":   "IBM",      # IBM
    "PLTR":  "PLTR",     # Palantir
    "PANW":  "PANW",     # Palo Alto Networks
    "MU":    "MU",       # Micron
    "ANET":  "ANET",     # Arista Networks
    "ADP":   "ADP",      # ADP
    "KLAC":  "KLAC",     # KLA Corp
    "LRCX":  "LRCX",     # Lam Research
    "APH":   "APH",      # Amphenol

    # Communications
    "GOOGL": "GOOGL",    # Alphabet Class A
    "META":  "META",     # Meta
    "NFLX":  "NFLX",     # Netflix
    "TMUS":  "TMUS",     # T-Mobile
    "DIS":   "DIS",      # Disney
    "CMCSA": "CMCSA",    # Comcast
    "VZ":    "VZ",       # Verizon
    "T":     "T",        # AT&T

    # Consumer Discretionary
    "AMZN":  "AMZN",     # Amazon
    "TSLA":  "TSLA",     # Tesla
    "HD":    "HD",       # Home Depot
    "MCD":   "MCD",      # McDonald's
    "NKE":   "NKE",      # Nike
    "LOW":   "LOW",      # Lowe's
    "SBUX":  "SBUX",     # Starbucks
    "TJX":   "TJX",      # TJX
    "BKNG":  "BKNG",     # Booking Holdings

    # Consumer Staples
    "WMT":   "WMT",      # Walmart
    "PG":    "PG",       # Procter & Gamble
    "KO":    "KO",       # Coca-Cola
    "PEP":   "PEP",      # PepsiCo
    "COST":  "COST",     # Costco
    "MDLZ":  "MDLZ",     # Mondelez
    "CL":    "CL",       # Colgate-Palmolive
    "PM":    "PM",       # Philip Morris

    # Healthcare
    "LLY":   "LLY",      # Eli Lilly
    "JNJ":   "JNJ",      # Johnson & Johnson
    "UNH":   "UNH",      # UnitedHealth
    "ABBV":  "ABBV",     # AbbVie
    "MRK":   "MRK",      # Merck
    "ABT":   "ABT",      # Abbott
    "TMO":   "TMO",      # Thermo Fisher
    "DHR":   "DHR",      # Danaher
    "PFE":   "PFE",      # Pfizer
    "AMGN":  "AMGN",     # Amgen
    "BMY":   "BMY",      # Bristol-Myers
    "ISRG":  "ISRG",     # Intuitive Surgical

    # Financials
    "BRK-B": "BRK-B",    # Berkshire Hathaway
    "JPM":   "JPM",      # JPMorgan
    "V":     "V",        # Visa
    "MA":    "MA",       # Mastercard
    "BAC":   "BAC",      # Bank of America
    "WFC":   "WFC",      # Wells Fargo
    "GS":    "GS",       # Goldman Sachs
    "MS":    "MS",       # Morgan Stanley
    "C":     "C",        # Citigroup
    "AXP":   "AXP",      # American Express
    "BLK":   "BLK",      # BlackRock
    "SCHW":  "SCHW",     # Schwab
    "SPGI":  "SPGI",     # S&P Global

    # Energy
    "XOM":   "XOM",      # Exxon Mobil
    "CVX":   "CVX",      # Chevron
    "COP":   "COP",      # ConocoPhillips
    "EOG":   "EOG",      # EOG Resources
    "SLB":   "SLB",      # Schlumberger

    # Industrials
    "GE":    "GE",       # GE
    "CAT":   "CAT",      # Caterpillar
    "BA":    "BA",       # Boeing
    "RTX":   "RTX",      # RTX
    "UNP":   "UNP",      # Union Pacific
    "HON":   "HON",      # Honeywell
    "DE":    "DE",       # Deere
    "LMT":   "LMT",      # Lockheed Martin
    "UPS":   "UPS",      # UPS
    "FDX":   "FDX",      # FedEx
    "ETN":   "ETN",      # Eaton

    # Materials
    "LIN":   "LIN",      # Linde
    "FCX":   "FCX",      # Freeport-McMoRan
    "NEM":   "NEM",      # Newmont
    "SHW":   "SHW",      # Sherwin-Williams

    # Real Estate
    "PLD":   "PLD",      # Prologis
    "AMT":   "AMT",      # American Tower
    "EQIX":  "EQIX",     # Equinix

    # Utilities
    "NEE":   "NEE",      # NextEra
    "DUK":   "DUK",      # Duke Energy
    "SO":    "SO",       # Southern Company

    # Others
    "ACN":   "ACN",      # Accenture
    "F":     "F",        # Ford
    "GM":    "GM",       # GM
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
}

# ============================================================================
# Strategy configuration
# ============================================================================
CONFIG = {
    # Position counts
    "N_SP500_POSITIONS": 4,         # Number of S&P 500 stocks to hold
    "N_IBEX_POSITIONS": 2,          # Number of IBEX stocks to hold
<<<<<<< HEAD
    
    # Capital weights (must sum to 1.0)
    "WEIGHT_SP500": 0.67,           # 67% of capital in US stocks
    "WEIGHT_IBEX": 0.33,            # 33% of capital in Spanish stocks
    
    # Momentum calculation
    "LOOKBACK_MONTHS": 12,          # Total lookback window
    "SKIP_MONTHS": 1,               # Skip the most recent month (short-term reversal)
    
    # Commissions (IBKR Tiered)
    "COMMISSION_IBEX_EUR": 3.0,     # EUR per trade for Madrid (BME) stocks
    "COMMISSION_SP500_USD": 1.0,    # USD per trade for US stocks
    
    # Currency
    "EUR_USD_REFERENCE": 1.1758,    # Reference rate (12 May 2026)
=======

    # Capital weights (must sum to 1.0)
    "WEIGHT_SP500": 0.65,           # 65% of capital in US stocks
    "WEIGHT_IBEX": 0.30,            # 30% of capital in Spanish stocks
    "CASH_RESERVE": 0.05,           # 5% cash reserve for flexibility and commissions

    # Momentum calculation
    "LOOKBACK_MONTHS": 12,          # Total lookback window
    "SKIP_MONTHS": 1,               # Skip the most recent month

    # Order sizing
    # IBKR supports fractional shares for most US stocks and many European ones.
    # With small capital (e.g. 2,000 EUR split into 6 positions ~ 333 EUR each),
    # fractional shares are essential because expensive stocks like BKNG (~5,000 USD)
    # or AVGO (~2,000 USD) would not fit in a single whole share.
    # Set this to False to force whole-share orders (useful for brokers that don't
    # support fractions or for stocks where fractions aren't allowed).
    "ALLOW_FRACTIONAL_SHARES": True,

    # Currency
    "EUR_USD_REFERENCE": 1.1758,    # Reference rate (12 May 2026)

    # NOTE on commissions:
    # IBKR commissions vary significantly between accounts (Tiered vs Fixed),
    # account size, monthly volume, and market venue. Rather than estimating
    # commissions in the script, you should record the ACTUAL commissions you
    # paid per trade directly in data/history.json after executing orders.
    # This keeps the historical record accurate without forcing a single model.
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
}
