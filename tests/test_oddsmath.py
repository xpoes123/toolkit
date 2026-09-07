"""Behavior lock for djtoolkit.oddsmath — the canonical odds math before any
live app (SharpLab, sharp-nba, nba-modeling) depends on it. Values verified
equivalent to SharpLab's shared/odds_utils.py (the source it was ported from)."""
import math
import pytest
from djtoolkit import oddsmath as om


def test_american_to_prob():
    assert abs(om.american_to_prob(-110) - 110 / 210) < 1e-12
    assert om.american_to_prob(100) == 0.5
    assert om.american_to_prob(150) == 100 / 250
    with pytest.raises(ValueError):
        om.american_to_prob(0)


def test_prob_to_american():
    assert om.prob_to_american(0.5) == -100          # >=0.5 branch
    assert om.prob_to_american(0.4) == 150
    for bad in (0, 1, -0.1, 1.5):
        with pytest.raises(ValueError):
            om.prob_to_american(bad)


@pytest.mark.parametrize("odds", [-350, -110, 145, 500])   # skip even money: ±100 both = 50%
def test_american_prob_roundtrip(odds):
    assert om.prob_to_american(om.american_to_prob(odds)) == odds


def test_decimal_conversions():
    assert om.american_to_decimal(100) == 2.0
    assert abs(om.american_to_decimal(-110) - (100 / 110 + 1)) < 1e-12
    assert om.decimal_to_american(2.0) == 100
    assert om.decimal_to_american(2.5) == 150
    with pytest.raises(ValueError):
        om.american_to_decimal(0)
    with pytest.raises(ValueError):
        om.decimal_to_american(1.0)


def test_profit():
    assert abs(om.profit(-110) - 100 / 110) < 1e-12
    assert om.profit(150) == 1.5
    assert om.profit(100) == 1.0
    # profit(a) == american_to_decimal(a) - 1
    for a in (-250, -110, 120, 300):
        assert abs(om.profit(a) - (om.american_to_decimal(a) - 1)) < 1e-12


def test_devig_sums_to_one_and_orders():
    h, a = om.devig_two_way(-150, 130)
    assert abs(h + a - 1.0) < 1e-12 and h > a          # favorite has higher fair prob
    assert om.devig_two_way(-110, -110) == (0.5, 0.5)


def test_kelly():
    assert abs(om.kelly_fraction(0.6, 100) - 0.2) < 1e-12   # 2p-1 at even money
    assert om.kelly_fraction(0.4, 100) == 0.0               # no edge -> 0
    assert abs(om.kelly_fraction(0.6, 100, fraction=0.5) - 0.1) < 1e-12
    with pytest.raises(ValueError):
        om.kelly_fraction(1.0, 100)


def test_compute_clv():
    assert om.compute_clv(-110, -120) > 0                   # closed shorter -> +CLV
    assert om.compute_clv(-120, -110) < 0
    # spread: home bettor laid FEWER points than close (bet -2.5, closed -3.5)
    # -> got the better number -> extra positive adjustment
    base = om.compute_clv(-110, -110)
    better = om.compute_clv(-110, -110, market="spread", bet_line=-2.5,
                            close_line=-3.5, is_home=True)
    worse = om.compute_clv(-110, -110, market="spread", bet_line=-3.5,
                           close_line=-2.5, is_home=True)
    assert better > base > worse


@pytest.mark.parametrize("raw,label", [
    ("-110", "american"), ("+150", "american"), ("52%", "percent"),
    ("52", "cents"), ("52c", "cents"), ("1.91", "decimal"), ("0.52", "prob"),
])
def test_parse_odds_input_labels(raw, label):
    assert om.parse_odds_input(raw)[1] == label


def test_odds_breakdown_native_precision():
    b = om.odds_breakdown("0.52")
    assert b["fmt"] == "prob" and abs(b["prob"] - 0.52) < 1e-12
    assert abs(b["decimal"] - 1 / 0.52) < 1e-12


def test_demo_selfcheck_runs():
    om._demo()   # the module's own assertions must still hold
