# Disclaimer

## Not financial advice

<<<<<<< HEAD
The content of this repository — including code, documentation, results, and
commentary — is provided for **educational and research purposes only**. It does
=======
The content of this repository - including code, documentation, results, and
commentary - is provided for **educational and research purposes only**. It does
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
not constitute investment advice, financial advice, trading advice, or any other
sort of advice.

The author is not a licensed financial advisor, investment professional, broker,
or fiduciary. Nothing in this repository should be construed as a recommendation
to buy, sell, or hold any security or financial instrument.

## You are responsible for your own decisions

If you choose to apply any part of this strategy with real money:

- You are doing so entirely at your own risk
- You should consult a qualified financial advisor and tax professional in your
  jurisdiction first
- You should understand the risks, including the possibility of losing the
  entire invested capital
- You should never invest money you cannot afford to lose

## Past performance does not predict future results

The backtest results in this repository:

- Were generated against **synthetic price data** calibrated to historical
  annual returns, **not** actual market prices
- Cover a specific 7-year period (2019-2025) that included unique events
  (COVID-19, AI boom, rate cycle) unlikely to repeat in the same way
- Do not include important real-world frictions (slippage, currency risk,
<<<<<<< HEAD
  dividends, survivorship bias) — see [methodology.md](methodology.md)
=======
  dividends, survivorship bias) - see [methodology.md](methodology.md)
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)
- Should be understood as **upper-bound estimates** of what the strategy could
  achieve under favorable conditions

A real-money implementation can be expected to underperform the backtest by
5-15 percentage points of CAGR or more.

## Strategy risks

Specific risks of the momentum 12-1 strategy include:

1. **Momentum crashes**: when markets reverse rapidly, momentum portfolios can
   lose 30-50% in months (e.g., March-April 2009, late 2020)
2. **Concentration**: with only 6 positions, a single bad pick can hurt 15-20%
   of the portfolio
3. **Currency risk**: USD positions add EUR/USD exposure not modeled in the
   backtest
4. **Regime changes**: momentum works well in trending markets, badly in choppy
   ones
5. **Tax drag**: frequent rebalancing creates taxable events that erode
   compounding
6. **Operational risk**: missing a rebalance or making mistakes in IBKR can
   eliminate the edge

## No warranty

The software is provided "as is", without warranty of any kind, express or
implied. The authors make no warranties regarding the accuracy, reliability, or
performance of the code or its outputs.

## Privacy

<<<<<<< HEAD
The repository does not contain personal financial data. The user's actual
portfolio is stored locally in `data/portfolio.json`, which is excluded from
version control via `.gitignore`. Never commit your real portfolio to a public
repository.
=======
This repository tracks an IBKR DEMO (paper trading) account, not a real
money account. All portfolio data in data/portfolio.json and data/history.json
reflects simulated trades with simulated capital. No personal financial data,
real positions, or actual brokerage balances are exposed by this repo.
If you fork this repository to apply the strategy to a real money account, add
data/portfolio.json to your .gitignore before committing anything. See the
note in the project's .gitignore file for the exact line to uncomment. Never
commit real portfolio data to a public repository.
>>>>>>> 9cb58e0 (Updates: minor updates to the docs and comments in the scripts)

## Regulatory note (Spain)

This repository is written from the perspective of a Spanish tax resident with
an Interactive Brokers account and a W-8BEN form active. If you are a tax
resident of another country, the tax modeling in `src/backtest.py` will not
apply to your situation and the entire strategy may need adaptation.

Consult your local tax authority or a professional before applying.
