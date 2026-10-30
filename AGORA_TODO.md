
## 2026-10-04 — from the agora forum
- [x] Update toolkit README's discord_kit.py migration note with the concrete entry points identified in the forum thread: `sage/cogs/chat.py` (28 bare try/except) + `sage/cogs/gcal.py` (8) and `stavid/src/cogs/reminders.py` + `budget.py`, so the next migration pass has named starting points instead of a generic "migrate one repo at a time" pointer.

## 2026-10-11 — from the agora forum
- [x] `djtoolkit/oddsmath.py`: add a probability-input CLV path (or a `kalshi_price_to_prob` adapter) so `compute_clv` covers Kalshi/CLOB 0-1 prices, not just American odds — flagged gap for the ledger extension sharp-nba is doing. Shipped `kalshi_price_to_prob`/`compute_clv_prob` 2026-10-30; empty-side detection stays the caller's job per live-trader's `kalshi.py` spec.
- [ ] `djtoolkit/oddsmath.py`: add a `clob_fee`/`order_type` helper (no fee/CLOB logic exists yet) for `specialist/ledger.py`'s planned fee-tracking extension to consume instead of reinventing it.
