"""
Universe definitions for the momentum strategy.

The strategy operates on TWO COMPLETE universes that are scanned dynamically
each quarter to find the stocks with the strongest momentum:

  1. IBEX_35: all 35 components of the Spanish IBEX 35 index
  2. US_LARGE_CAP: ~155 large/mid cap US stocks across NYSE and NASDAQ
     - Includes S&P 500 large caps
     - Plus large NYSE/NASDAQ companies that are NOT in the S&P 500
       (e.g., Sandisk, Bloom Energy, Lumentum, NU, ARM, etc.)
     - Plus mid caps that have shown strong momentum recently
       (e.g., Astera Labs, Argan, IES Holdings, Vertiv, Sterling Construction,
        Powell, MP Materials, Rocket Lab, etc.)

There is NO static pre-selection of "best stocks". Each rebalance computes
12-1 momentum on every stock in these universes and picks the top performers.

WHY US_LARGE_CAP INSTEAD OF S&P 500 ONLY?
The S&P 500 imposes strict inclusion criteria (US-domiciled, profitable for the
last four quarters, market cap thresholds, etc.). Many high-quality US stocks
listed on NYSE or NASDAQ are NOT in the S&P 500 because of those rules:
  - Foreign-domiciled (e.g., NU - Brazilian fintech, ARM - UK chip design)
  - Recently IPO'd and not yet profitable for four quarters
  - Below the index's stringent market cap criteria but still genuinely large
  - Small-mid caps with explosive momentum signals (e.g., AAOI, IESC, VRT)

By widening the US universe beyond the S&P 500 we capture good US stocks the
S&P inclusion committee hasn't accepted yet — which is often where the
strongest momentum lives in the early-growth phase of a sector cycle.

SIZE OF THE US UNIVERSE
~155 stocks: still computationally cheap (data download stays under 1 second
on Yahoo Finance for live `rebalance.py`, and the backtest now reads from a
local CSV `data/monthly-historic-prices.csv`).

These lists should be reviewed periodically:
  - IBEX 35: index composition is reviewed twice a year (June, December) by BME.
    Update this file after each review.
  - US_LARGE_CAP: review yearly. Add new entrants (recent IPOs, rising stars)
    and remove stocks that have permanently lost relevance.

LAST UPDATED: May 2026
  - IBEX 35: based on BME composition effective from September 2024
  - US_LARGE_CAP: based on market cap and momentum rankings as of Q2 2026,
    plus selected non-S&P 500 stocks on NYSE/NASDAQ

Yahoo Finance ticker conventions:
  - IBEX stocks: suffix ".MC" (Madrid)
  - US stocks: no suffix (NYSE/NASDAQ); some use "-" for class shares
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
# US LARGE CAP — Broad US universe (NYSE + NASDAQ)
# Includes S&P 500 large caps PLUS large non-S&P 500 listings PLUS recent
# momentum mid-caps. Source: market cap and momentum rankings as of Q2 2026.
# ============================================================================
US_LARGE_CAP = {
    # ----- Technology - mega caps -----
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
    "INTC":  "INTC",     # Intel
    "AMAT":  "AMAT",     # Applied Materials
    "MRVL":  "MRVL",     # Marvell Technology

    # ----- Technology - non-S&P 500 / foreign / newer -----
    "ARM":   "ARM",      # Arm Holdings (UK-domiciled, NASDAQ)
    "SNDK":  "SNDK",     # Sandisk Corporation (re-listed NASDAQ, not in S&P)
    "LITE":  "LITE",     # Lumentum Holdings (optical components, NASDAQ)
    "AAOI":  "AAOI",     # Applied Optoelectronics (NASDAQ)
    "ASML":  "ASML",     # ASML (Dutch, NASDAQ ADR — not in S&P 500)
    "TSM":   "TSM",      # Taiwan Semiconductor (Taiwanese ADR, not in S&P 500)
    "ALAB":  "ALAB",     # Astera Labs (recent IPO 2024)

    # ----- Technology - momentum mid caps -----
    "AEIS":  "AEIS",     # Advanced Energy Industries
    "AMKR":  "AMKR",     # Amkor Technology
    "CIEN":  "CIEN",     # Ciena Corp
    "COHR":  "COHR",     # Coherent
    "FLEX":  "FLEX",     # Flex
    "GLW":   "GLW",      # Corning
    "MKSI":  "MKSI",     # MKS Instruments
    "MTSI":  "MTSI",     # MACOM Technology
    "ON":    "ON",       # ON Semiconductor
    "ONTO":  "ONTO",     # Onto Innovation
    "SANM":  "SANM",     # Sanmina
    "SITM":  "SITM",     # Sitime
    "SMTC":  "SMTC",     # Semtech
    "TER":   "TER",      # Teradyne
    "TTMI":  "TTMI",     # TTM Technologies
    "VIAV":  "VIAV",     # Viavi Solutions
    "VICR":  "VICR",     # Vicor
    "VRT":   "VRT",      # Vertiv Holdings (AI infrastructure)
    "WDC":   "WDC",      # Western Digital

    # ----- Communications & Media -----
    "GOOGL": "GOOGL",    # Alphabet Class A
    "META":  "META",     # Meta
    "NFLX":  "NFLX",     # Netflix
    "TMUS":  "TMUS",     # T-Mobile
    "DIS":   "DIS",      # Disney
    "CMCSA": "CMCSA",    # Comcast
    "VZ":    "VZ",       # Verizon
    "T":     "T",        # AT&T
    "GSAT":  "GSAT",     # Globalstar (satellite communications)
    "SATS":  "SATS",     # EchoStar
    "ASTS":  "ASTS",     # AST SpaceMobile

    # ----- Consumer Discretionary -----
    "AMZN":  "AMZN",     # Amazon
    "TSLA":  "TSLA",     # Tesla
    "HD":    "HD",       # Home Depot
    "MCD":   "MCD",      # McDonald's
    "NKE":   "NKE",      # Nike
    "LOW":   "LOW",      # Lowe's
    "SBUX":  "SBUX",     # Starbucks
    "TJX":   "TJX",      # TJX
    "BKNG":  "BKNG",     # Booking Holdings
    "MELI":  "MELI",     # MercadoLibre (Argentinian, NASDAQ)
    "PDD":   "PDD",      # PDD Holdings / Temu (Chinese ADR)
    "BABA":  "BABA",     # Alibaba (Chinese ADR)

    # ----- Consumer Staples -----
    "WMT":   "WMT",      # Walmart
    "PG":    "PG",       # Procter & Gamble
    "KO":    "KO",       # Coca-Cola
    "PEP":   "PEP",      # PepsiCo
    "COST":  "COST",     # Costco
    "MDLZ":  "MDLZ",     # Mondelez
    "CL":    "CL",       # Colgate-Palmolive
    "PM":    "PM",       # Philip Morris

    # ----- Healthcare -----
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
    "NVO":   "NVO",      # Novo Nordisk (Danish ADR)
    "AZN":   "AZN",      # AstraZeneca (UK ADR)
    "ARWR":  "ARWR",     # Arrowhead Pharma (RNA therapeutics)
    "CYTK":  "CYTK",     # Cytokinetics
    "RVMD":  "RVMD",     # Revolution Medicines

    # ----- Financials -----
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
    "NU":    "NU",       # Nu Holdings (Brazilian fintech)
    "HOOD":  "HOOD",     # Robinhood
    "DOCN":  "DOCN",     # DigitalOcean (cloud)

    # ----- Energy -----
    "XOM":   "XOM",      # Exxon Mobil
    "CVX":   "CVX",      # Chevron
    "COP":   "COP",      # ConocoPhillips
    "EOG":   "EOG",      # EOG Resources
    "SLB":   "SLB",      # Schlumberger
    "BE":    "BE",       # Bloom Energy (fuel cells)
    "ENPH":  "ENPH",     # Enphase Energy (solar)

    # ----- Industrials -----
    "GE":    "GE",       # GE Aerospace
    "CAT":   "CAT",      # Caterpillar
    "BA":    "BA",       # Boeing
    "RTX":   "RTX",      # RTX Corp
    "UNP":   "UNP",      # Union Pacific
    "HON":   "HON",      # Honeywell
    "DE":    "DE",       # Deere
    "LMT":   "LMT",      # Lockheed Martin
    "UPS":   "UPS",      # UPS
    "FDX":   "FDX",      # FedEx
    "ETN":   "ETN",      # Eaton
    "AGX":   "AGX",      # Argan (power infrastructure)
    "FIX":   "FIX",      # Comfort Systems USA (HVAC)
    "IESC":  "IESC",     # IES Holdings (infrastructure)
    "MOD":   "MOD",      # Modine Manufacturing (thermal management)
    "MTZ":   "MTZ",      # MasTec (infrastructure)
    "POWL":  "POWL",     # Powell Industries (electrical)
    "STRL":  "STRL",     # Sterling Construction (infrastructure)
    "RKLB":  "RKLB",     # Rocket Lab (space)
    "HUT":   "HUT",      # Hut 8 (bitcoin mining)

    # ----- Materials -----
    "LIN":   "LIN",      # Linde
    "FCX":   "FCX",      # Freeport-McMoRan
    "NEM":   "NEM",      # Newmont
    "SHW":   "SHW",      # Sherwin-Williams
    "ALB":   "ALB",      # Albemarle (lithium)
    "MP":    "MP",       # MP Materials (rare earths)

    # ----- Real Estate -----
    "PLD":   "PLD",      # Prologis
    "AMT":   "AMT",      # American Tower
    "EQIX":  "EQIX",     # Equinix

    # ----- Utilities -----
    "NEE":   "NEE",      # NextEra
    "DUK":   "DUK",      # Duke Energy
    "SO":    "SO",       # Southern Company

    # ----- Other notable large caps -----
    "ACN":   "ACN",      # Accenture
    "F":     "F",        # Ford
    "GM":    "GM",       # GM
}

# Backwards compatibility alias.
# Older code (and the backtest module) may still reference SP500_LARGE_CAP.
# New code should use US_LARGE_CAP.
SP500_LARGE_CAP = US_LARGE_CAP

# ============================================================================
# Strategy configuration
# ============================================================================
CONFIG = {
    # Position counts
    "N_SP500_POSITIONS": 4,         # Number of US stocks to hold (legacy name)
    "N_IBEX_POSITIONS": 2,          # Number of IBEX stocks to hold

    # Capital weights (must sum to at most 1.0; remainder is cash reserve)
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
    "ALLOW_FRACTIONAL_SHARES": True,

    # Currency
    "EUR_USD_REFERENCE": 1.1758,    # Reference rate (12 May 2026)

    # NOTE on commissions:
    # IBKR commissions vary significantly between accounts (Tiered vs Fixed),
    # account size, monthly volume, and market venue. Rather than estimating
    # commissions in the script, you should record the ACTUAL commissions you
    # paid per trade directly in data/history.json after executing orders.
    # This keeps the historical record accurate without forcing a single model.
}
