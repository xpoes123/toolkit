"""Odds/probability conversion math shared across SharpLab, nba-modeling, nsba,
and sharp-nba — each reimplemented american_to_prob/devig independently.
This is the canonical version; ported from SharpLab's shared/odds_utils.py
(the most complete of the three), minus vendor-specific fetchers (Kalshi/
Polymarket network calls stay in the app that needs them — this module is
pure math, no I/O, no deps beyond stdlib).
"""

from __future__ import annotations


def prob_to_american(prob: float) -> int:
    """Convert implied probability (0-1) to American odds."""
    if prob <= 0 or prob >= 1:
        raise ValueError(f"Probability must be between 0 and 1, got {prob}")
    if prob >= 0.5:
        return round(-prob / (1 - prob) * 100)
    return round((1 - prob) / prob * 100)


def american_to_prob(odds: int) -> float:
    """Convert American odds to implied probability."""
    if odds == 0:
        raise ValueError("American odds cannot be zero")
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)


def american_to_decimal(odds: int) -> float:
    if odds == 0:
        raise ValueError("American odds cannot be zero")
    return (odds / 100) + 1 if odds > 0 else (100 / abs(odds)) + 1


def decimal_to_american(decimal: float) -> int:
    if decimal <= 1.0:
        raise ValueError(f"Decimal odds must be > 1.0, got {decimal}")
    return round((decimal - 1) * 100) if decimal >= 2.0 else round(-100 / (decimal - 1))


def devig_two_way(ml_home: int, ml_away: int) -> tuple[float, float]:
    """Normalize a two-sided American moneyline into fair (home, away) win
    probabilities summing to 1 (removes the bookmaker's vig)."""
    hp = american_to_prob(ml_home)
    ap = american_to_prob(ml_away)
    total = hp + ap
    if total <= 0:
        return 0.5, 0.5
    return hp / total, ap / total


def fmt_prob(odds: int) -> str:
    """Format American odds as an implied-probability percentage, e.g. -110 -> '52.4%'."""
    return f"{american_to_prob(odds) * 100:.1f}%"


def fmt_odds(odds: int, fmt: str = "american") -> str:
    if fmt == "decimal":
        return f"{american_to_decimal(odds):.2f}"
    if fmt == "probability":
        return fmt_prob(odds)
    return f"+{odds}" if odds > 0 else str(odds)


def kelly_fraction(prob: float, american_odds: int, fraction: float = 1.0) -> float:
    """Fraction of bankroll to stake per the Kelly criterion, given your true
    win probability and the American odds offered. `fraction` scales it down
    (e.g. 0.5 = half-Kelly) — full Kelly is high-variance for anything but a
    precisely known edge. Returns 0 if there's no positive edge."""
    if not (0 < prob < 1):
        raise ValueError(f"Probability must be between 0 and 1, got {prob}")
    b = american_to_decimal(american_odds) - 1  # net odds (profit per unit staked)
    edge = prob * b - (1 - prob)
    if edge <= 0:
        return 0.0
    return fraction * edge / b


# Approximate win-probability change per half-point of NBA line movement —
# standard industry approximation, used to number-adjust CLV.
_PP_PER_HALF_POINT_SPREAD = 2.0
_PP_PER_HALF_POINT_TOTAL = 1.0


def compute_clv(
    bet_odds: int,
    close_odds: int,
    *,
    market: str = "",
    bet_line: float | None = None,
    close_line: float | None = None,
    is_home: bool | None = None,
    is_over: bool | None = None,
) -> float:
    """Closing-line value in percentage points. Moneyline/no line info: pure
    juice-based CLV. Spread/total with a line: adds a per-half-point
    adjustment when the number moved between bet time and close."""
    bet_prob = american_to_prob(bet_odds)
    close_prob = american_to_prob(close_odds)
    juice_clv = (close_prob - bet_prob) * 100

    if bet_line is None or close_line is None:
        return juice_clv

    if market == "spread" and is_home is not None:
        close_for_bettor = close_line if is_home else -close_line
        diff = bet_line - close_for_bettor  # positive = bettor got the better number
        return juice_clv + (diff / 0.5) * _PP_PER_HALF_POINT_SPREAD

    if market == "total" and is_over is not None:
        diff = (close_line - bet_line) if is_over else (bet_line - close_line)
        return juice_clv + (diff / 0.5) * _PP_PER_HALF_POINT_TOTAL

    return juice_clv


def parse_odds_input(raw: str) -> tuple[int, str]:
    """Parse odds in any format a human might type and return (american, label).

    Supported: American (-110, +150, 150), decimal (1.91), cents (52, 52c,
    52 cents — Kalshi/Polymarket style), prob (0.52), percent (52%)."""
    raw = raw.strip()

    if raw.endswith("%"):
        prob = float(raw[:-1]) / 100
        if not (0 < prob < 1):
            raise ValueError(f"Probability must be between 0% and 100% exclusive, got {raw!r}")
        return prob_to_american(prob), "percent"

    low = raw.lower()
    for suf in ("cents", "¢", "c"):
        if low.endswith(suf):
            num = low[: -len(suf)].strip()
            if num and num.replace(".", "", 1).isdigit() and 0 < float(num) < 100:
                return prob_to_american(float(num) / 100), "cents"
            break

    if "." in raw:
        val = float(raw)
        return (prob_to_american(val), "prob") if val < 1.0 else (decimal_to_american(val), "decimal")

    val = int(raw.lstrip("+"))
    if val == 0:
        raise ValueError("American odds cannot be zero")
    if not raw.startswith("-") and not raw.startswith("+") and 1 <= val <= 99:
        return prob_to_american(val / 100), "cents"
    return val, "american"


def odds_breakdown(raw: str) -> dict:
    """Parse any odds input into {fmt, prob, decimal, american}, deriving
    prob/decimal from the input's native precision so a decimal/prob/cents
    input doesn't pick up rounding artifacts from round-tripping through
    (integer) American odds."""
    american, fmt = parse_odds_input(raw)
    r = raw.strip().lower()
    if fmt == "decimal":
        decimal = float(r)
        prob = 1.0 / decimal
    elif fmt == "prob":
        prob = float(r)
        decimal = 1.0 / prob
    elif fmt == "percent":
        prob = float(r.rstrip("%")) / 100
        decimal = 1.0 / prob
    elif fmt == "cents":
        digits = r.replace("cents", "").replace("¢", "").rstrip("c").strip()
        prob = float(digits) / 100
        decimal = 1.0 / prob
    else:
        prob = american_to_prob(american)
        decimal = american_to_decimal(american)
    return {"fmt": fmt, "prob": prob, "decimal": decimal, "american": american}


def _demo() -> None:
    assert american_to_prob(-110) == abs(-110) / (abs(-110) + 100)
    assert round(american_to_prob(100), 4) == 0.5
    assert prob_to_american(0.5) == -100 or prob_to_american(0.5) == 100
    h, a = devig_two_way(-150, 130)
    assert abs(h + a - 1.0) < 1e-9 and h > a
    assert american_to_decimal(100) == 2.0
    assert decimal_to_american(2.0) == 100
    assert parse_odds_input("-110") == (-110, "american")
    assert parse_odds_input("52%")[1] == "percent"
    assert parse_odds_input("52")[1] == "cents"  # unsigned 1-99 => Kalshi cents
    assert parse_odds_input("1.91")[1] == "decimal"
    b = odds_breakdown("0.52")
    assert b["fmt"] == "prob" and abs(b["prob"] - 0.52) < 1e-9
    # true prob 60%, offered even money (+100) -> positive edge, full Kelly = 2p-1 = 0.2
    assert abs(kelly_fraction(0.6, 100) - 0.2) < 1e-9
    assert kelly_fraction(0.4, 100) == 0.0  # no edge -> stake nothing
    clv = compute_clv(-110, -120)
    assert clv > 0  # closed shorter than you bet -> positive CLV
    print("oddsmath self-check OK")


if __name__ == "__main__":
    _demo()
