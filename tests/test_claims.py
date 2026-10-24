"""Jede Zahl aus der README wird hier über dieselben Auswertungsfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Messreihen: die zwölf festen Netze `SWEEP_SEEDS` je Zelle (Mittel bzw. Median, siehe die Funktionen in `ztn_evaluation.py`); Zufallsnetz mit 200 Betrieben und mittlerem Grad 4, Fenster 0 bis 1000, 20 Startbetriebe
je Netz (Experiment 2: 100 Betriebe, alle als Start). Alle Läufe sind deterministisch (feste Seeds, Zufall nur über `numpy.random.default_rng`); Anteile stehen auf vier, Zeiten auf eine Nachkommastelle,
die Bänder fangen die Rundung."""

import math
from functools import lru_cache

import numpy as np
import pytest

import ztn_algorithm as A
import ztn_constants as C
import ztn_evaluation as ev

N, CC = 200, 4
NETS = len(C.SWEEP_SEEDS)
K_NULL, K_SPREAD, BETA, BURST_K = 3, 4, 0.3, 6
EXPECT = {'E1': [{'k': 1, 'form': 0.25, 'reach': 0.1545, 'static': 0.9612, 'median': 993.0, 'nets': 12},
        {'k': 2, 'form': 0.25, 'reach': 0.464, 'static': 0.9612, 'median': 984.5, 'nets': 12},
        {'k': 3, 'form': 0.25, 'reach': 0.6606, 'static': 0.9612, 'median': 953.5, 'nets': 12},
        {'k': 4, 'form': 0.25, 'reach': 0.8007, 'static': 0.9612, 'median': 870.5, 'nets': 12},
        {'k': 6, 'form': 0.25, 'reach': 0.8923, 'static': 0.9612, 'median': 616.5, 'nets': 12},
        {'k': 8, 'form': 0.25, 'reach': 0.9168, 'static': 0.9612, 'median': 446.5, 'nets': 12},
        {'k': 12, 'form': 0.25, 'reach': 0.9457, 'static': 0.9612, 'median': 227.0, 'nets': 12},
        {'k': 1, 'form': 0.5, 'reach': 0.1798, 'static': 0.9612, 'median': 933.2, 'nets': 12},
        {'k': 2, 'form': 0.5, 'reach': 0.5514, 'static': 0.9612, 'median': 866.0, 'nets': 12},
        {'k': 3, 'form': 0.5, 'reach': 0.7791, 'static': 0.9612, 'median': 749.0, 'nets': 12},
        {'k': 4, 'form': 0.5, 'reach': 0.8726, 'static': 0.9612, 'median': 577.0, 'nets': 12},
        {'k': 6, 'form': 0.5, 'reach': 0.9354, 'static': 0.9612, 'median': 361.0, 'nets': 12},
        {'k': 8, 'form': 0.5, 'reach': 0.9451, 'static': 0.9612, 'median': 271.0, 'nets': 12},
        {'k': 12, 'form': 0.5, 'reach': 0.9508, 'static': 0.9612, 'median': 159.5, 'nets': 12},
        {'k': 1, 'form': 1.0, 'reach': 0.1895, 'static': 0.9612, 'median': 789.5, 'nets': 12},
        {'k': 2, 'form': 1.0, 'reach': 0.6682, 'static': 0.9612, 'median': 711.0, 'nets': 12},
        {'k': 3, 'form': 1.0, 'reach': 0.8802, 'static': 0.9612, 'median': 564.5, 'nets': 12},
        {'k': 4, 'form': 1.0, 'reach': 0.9406, 'static': 0.9612, 'median': 443.5, 'nets': 12},
        {'k': 6, 'form': 1.0, 'reach': 0.9504, 'static': 0.9612, 'median': 317.0, 'nets': 12},
        {'k': 8, 'form': 1.0, 'reach': 0.9518, 'static': 0.9612, 'median': 232.5, 'nets': 12},
        {'k': 12, 'form': 1.0, 'reach': 0.9518, 'static': 0.9612, 'median': 158.5, 'nets': 12},
        {'k': 1, 'form': 3.0, 'reach': 0.181, 'static': 0.9612, 'median': 613.0, 'nets': 12},
        {'k': 2, 'form': 3.0, 'reach': 0.7877, 'static': 0.9612, 'median': 621.0, 'nets': 12},
        {'k': 3, 'form': 3.0, 'reach': 0.9392, 'static': 0.9612, 'median': 496.0, 'nets': 12},
        {'k': 4, 'form': 3.0, 'reach': 0.9512, 'static': 0.9612, 'median': 398.5, 'nets': 12},
        {'k': 6, 'form': 3.0, 'reach': 0.9516, 'static': 0.9612, 'median': 286.0, 'nets': 12},
        {'k': 8, 'form': 3.0, 'reach': 0.9518, 'static': 0.9612, 'median': 219.0, 'nets': 12},
        {'k': 12, 'form': 3.0, 'reach': 0.9518, 'static': 0.9612, 'median': 147.0, 'nets': 12}],
 'E2': [{'k': 2, 'form': 0.25, 'nt': 0.1825, 'reach': 0.6047, 'nets': 12},
        {'k': 3, 'form': 0.25, 'nt': 0.0992, 'reach': 0.7598, 'nets': 12},
        {'k': 4, 'form': 0.25, 'nt': 0.0532, 'reach': 0.8587, 'nets': 12},
        {'k': 6, 'form': 0.25, 'nt': 0.0155, 'reach': 0.9343, 'nets': 12},
        {'k': 2, 'form': 1.0, 'nt': 0.1055, 'reach': 0.745, 'nets': 12},
        {'k': 3, 'form': 1.0, 'nt': 0.0247, 'reach': 0.9137, 'nets': 12},
        {'k': 4, 'form': 1.0, 'nt': 0.0065, 'reach': 0.9544, 'nets': 12},
        {'k': 6, 'form': 1.0, 'nt': 0.0002, 'reach': 0.9668, 'nets': 12}],
 'E3': [{'form': 0.25, 'null': 'Original', 'reach': 0.6941, 'median': 944.0, 'k': 3, 'nets': 12},
        {'form': 0.25, 'null': 'Zeitmarken gemischt', 'reach': 0.8795, 'median': 785.5, 'k': 3, 'nets': 12},
        {'form': 0.25, 'null': 'Kanten gemischt', 'reach': 0.8968, 'median': 747.5, 'k': 3, 'nets': 12},
        {'form': 1.0, 'null': 'Original', 'reach': 0.8928, 'median': 558.0, 'k': 3, 'nets': 12},
        {'form': 1.0, 'null': 'Zeitmarken gemischt', 'reach': 0.9012, 'median': 542.5, 'k': 3, 'nets': 12},
        {'form': 1.0, 'null': 'Kanten gemischt', 'reach': 0.8813, 'median': 557.0, 'k': 3, 'nets': 12}],
 'E4': [{'form': 0.25, 'si': 0.1349, 'si_shuffled': 0.1867, 't50': None, 'aggregate': 0.9028, 'unreached': 1.0, 'k': 4, 'beta': 0.3, 'nets': 12},
        {'form': 0.5, 'si': 0.1814, 'si_shuffled': 0.1946, 't50': 996.0, 'aggregate': 0.906, 'unreached': 0.975, 'k': 4, 'beta': 0.3, 'nets': 12},
        {'form': 1.0, 'si': 0.1971, 'si_shuffled': 0.1979, 't50': 932.0, 'aggregate': 0.8794, 'unreached': 0.9625, 'k': 4, 'beta': 0.3, 'nets': 12},
        {'form': 3.0, 'si': 0.2421, 'si_shuffled': 0.2054, 't50': 836.5, 'aggregate': 0.8943, 'unreached': 0.9, 'k': 4, 'beta': 0.3, 'nets': 12}],
 'E5': [{'instance': 1, 'beta': 0.3, 'contacts': 12, 'times': 5, 'exact': 0.31448, 'sim': 0.314, 'se': 0.00196},
        {'instance': 1, 'beta': 0.6, 'contacts': 12, 'times': 5, 'exact': 0.46796, 'sim': 0.46766, 'se': 0.00179},
        {'instance': 2, 'beta': 0.3, 'contacts': 12, 'times': 5, 'exact': 0.2, 'sim': 0.1975, 'se': 0.00128},
        {'instance': 2, 'beta': 0.6, 'contacts': 12, 'times': 5, 'exact': 0.275, 'sim': 0.27331, 'se': 0.00137},
        {'instance': 3, 'beta': 0.3, 'contacts': 12, 'times': 6, 'exact': 0.21125, 'sim': 0.21334, 'se': 0.00159},
        {'instance': 3, 'beta': 0.6, 'contacts': 12, 'times': 6, 'exact': 0.32, 'sim': 0.31844, 'se': 0.00197},
        {'instance': 4, 'beta': 0.3, 'contacts': 12, 'times': 5, 'exact': 0.2525, 'sim': 0.25284, 'se': 0.0014},
        {'instance': 4, 'beta': 0.6, 'contacts': 12, 'times': 5, 'exact': 0.335, 'sim': 0.33619, 'se': 0.001}],
 'TYPES': [{'typ': 'Zufallsnetz', 'k': 1, 'reach': 0.1835, 'static': 0.9612, 'median': 789.0},
           {'typ': 'Zufallsnetz', 'k': 2, 'reach': 0.6719, 'static': 0.9612, 'median': 718.5},
           {'typ': 'Zufallsnetz', 'k': 4, 'reach': 0.9351, 'static': 0.9612, 'median': 441.5},
           {'typ': 'Potenzgesetz-Netz', 'k': 1, 'reach': 0.3464, 'static': 0.9708, 'median': 738.5},
           {'typ': 'Potenzgesetz-Netz', 'k': 2, 'reach': 0.7354, 'static': 0.9708, 'median': 605.5},
           {'typ': 'Potenzgesetz-Netz', 'k': 4, 'reach': 0.946, 'static': 0.9708, 'median': 385.5},
           {'typ': 'Skalenfreies Netz (BA)', 'k': 1, 'reach': 0.3718, 'static': 1.0, 'median': 759.0},
           {'typ': 'Skalenfreies Netz (BA)', 'k': 2, 'reach': 0.826, 'static': 1.0, 'median': 627.5},
           {'typ': 'Skalenfreies Netz (BA)', 'k': 4, 'reach': 0.9961, 'static': 1.0, 'median': 374.5},
           {'typ': 'Verbünde', 'k': 1, 'reach': 0.1611, 'static': 0.9653, 'median': 768.5},
           {'typ': 'Verbünde', 'k': 2, 'reach': 0.5968, 'static': 0.9653, 'median': 710.5},
           {'typ': 'Verbünde', 'k': 4, 'reach': 0.9469, 'static': 0.9653, 'median': 465.0},
           {'typ': 'Ring mit Abkürzungen', 'k': 1, 'reach': 0.0628, 'static': 1.0, 'median': 647.2},
           {'typ': 'Ring mit Abkürzungen', 'k': 2, 'reach': 0.1661, 'static': 1.0, 'median': 680.5},
           {'typ': 'Ring mit Abkürzungen', 'k': 4, 'reach': 0.5173, 'static': 1.0, 'median': 711.5}],
 'BURST': [{'form': 0.25, 'burst': 0.301}, {'form': 0.5, 'burst': 0.163}, {'form': 1.0, 'burst': -0.077}, {'form': 3.0, 'burst': -0.494}],
 'presets': {'Zwei Kontakte je Kante: das Aggregat täuscht (Voreinstellung)': {'m': 400,
                                                                               'contacts': 800,
                                                                               'reach': 0.6384,
                                                                               'static': 0.9408,
                                                                               'median': 669.0,
                                                                               'nt': 0.1355,
                                                                               'burst': -0.163,
                                                                               'si': 0.0633,
                                                                               't50': None,
                                                                               'agg': 0.6118,
                                                                               'kind': 'warning',
                                                                               'verdict': 'Von einem Startbetrieb erreicht die Nachricht im Mittel 64 % der anderen '
                                                                                          'Betriebe; das Aggregat aller Kontakte (ohne Reihenfolge) hängt zu 94 % '
                                                                                          'zusammen. Der Median der Ankunftszeit liegt bei t = 669 (Fenster 0 bis 1000), '
                                                                                          '14 % der Tripel „i erreicht j, j erreicht k“ sind nicht transitiv. Das '
                                                                                          'Aggregat überschätzt die Reichweite um 30 Prozentpunkte. SI mit β = 30 % je '
                                                                                          'Kontakt: Endgröße 6 % gegen 61 % in der Aggregat-Rechnung (Kanten ohne '
                                                                                          'Reihenfolge, jede mit 2 Kontakten).'},
             'Ein Kontakt je Kante: nur jeder Fünfte erreichbar': {'m': 400,
                                                                   'contacts': 400,
                                                                   'reach': 0.1982,
                                                                   'static': 0.9408,
                                                                   'median': 814.0,
                                                                   'nt': 0.4496,
                                                                   'burst': None,
                                                                   'si': 0.0137,
                                                                   't50': None,
                                                                   'agg': 0.1143,
                                                                   'kind': 'warning',
                                                                   'verdict': 'Von einem Startbetrieb erreicht die Nachricht im Mittel 20 % der anderen Betriebe; das '
                                                                              'Aggregat aller Kontakte (ohne Reihenfolge) hängt zu 94 % zusammen. Der Median der '
                                                                              'Ankunftszeit liegt bei t = 814 (Fenster 0 bis 1000), 45 % der Tripel „i erreicht j, j '
                                                                              'erreicht k“ sind nicht transitiv. Das Aggregat überschätzt die Reichweite um 74 '
                                                                              'Prozentpunkte. SI mit β = 30 % je Kontakt: Endgröße 1 % gegen 11 % in der '
                                                                              'Aggregat-Rechnung (Kanten ohne Reihenfolge, jede mit 1 Kontakt).'},
             'Sechs Kontakte je Kante: fast alle erreicht': {'m': 400,
                                                             'contacts': 2400,
                                                             'reach': 0.9364,
                                                             'static': 0.9408,
                                                             'median': 298.0,
                                                             'nt': 0.0028,
                                                             'burst': -0.064,
                                                             'si': 0.4037,
                                                             't50': 815.5,
                                                             'agg': 0.9206,
                                                             'kind': 'warning',
                                                             'verdict': 'Von einem Startbetrieb erreicht die Nachricht im Mittel 94 % der anderen Betriebe; das Aggregat '
                                                                        'aller Kontakte (ohne Reihenfolge) hängt zu 94 % zusammen. Der Median der Ankunftszeit liegt bei '
                                                                        't = 298 (Fenster 0 bis 1000), 0 % der Tripel „i erreicht j, j erreicht k“ sind nicht transitiv. '
                                                                        'Die Reichweite stimmt mit dem Aggregat überein, die SI-Ausbreitung liegt aber 52 Prozentpunkte '
                                                                        'darunter. SI mit β = 30 % je Kontakt: Endgröße 40 % gegen 92 % in der Aggregat-Rechnung (Kanten '
                                                                        'ohne Reihenfolge, jede mit 6 Kontakten).'},
             'Stoßartig: erreichbar, aber langsam': {'m': 600,
                                                     'contacts': 4800,
                                                     'reach': 0.9785,
                                                     'static': 0.99,
                                                     'median': 198.0,
                                                     'nt': 0.0032,
                                                     'burst': 0.415,
                                                     'si': 0.8047,
                                                     't50': 996.0,
                                                     'agg': 0.994,
                                                     'kind': 'warning',
                                                     'verdict': 'Von einem Startbetrieb erreicht die Nachricht im Mittel 98 % der anderen Betriebe; das Aggregat aller '
                                                                'Kontakte (ohne Reihenfolge) hängt zu 99 % zusammen. Der Median der Ankunftszeit liegt bei t = 198 '
                                                                '(Fenster 0 bis 1000), 0 % der Tripel „i erreicht j, j erreicht k“ sind nicht transitiv. Die Reichweite '
                                                                'stimmt mit dem Aggregat überein, die SI-Ausbreitung liegt aber 19 Prozentpunkte darunter. SI mit β = 30 '
                                                                '% je Kontakt: Endgröße 80 % gegen 99 % in der Aggregat-Rechnung (Kanten ohne Reihenfolge, jede mit 8 '
                                                                'Kontakten).'},
             'Zeitmarken gemischt: viel schneller': {'m': 600,
                                                             'contacts': 4800,
                                                             'reach': 0.9899,
                                                             'static': 0.99,
                                                             'median': 11.0,
                                                             'nt': 0.0001,
                                                             'burst': 0.235,
                                                             'si': 0.9705,
                                                             't50': 498.0,
                                                             'agg': 0.994,
                                                             'kind': 'success',
                                                             'verdict': 'Von einem Startbetrieb erreicht die Nachricht im Mittel 99 % der anderen Betriebe; das Aggregat '
                                                                        'aller Kontakte (ohne Reihenfolge) hängt zu 99 % zusammen. Der Median der Ankunftszeit liegt bei '
                                                                        't = 11 (Fenster 0 bis 1000), 0 % der Tripel „i erreicht j, j erreicht k“ sind nicht transitiv. '
                                                                        'Aggregat und Kontaktfolge stimmen hier überein. SI mit β = 30 % je Kontakt: Endgröße 97 % gegen '
                                                                        '99 % in der Aggregat-Rechnung (Kanten ohne Reihenfolge, jede mit 8 Kontakten).'},
             'Verbünde': {'m': 600,
                          'contacts': 1800,
                          'reach': 0.9906,
                          'static': 1.0,
                          'median': 385.0,
                          'nt': 0.0048,
                          'burst': -0.125,
                          'si': 0.2737,
                          't50': 928.5,
                          'agg': 0.9512,
                          'kind': 'warning',
                          'verdict': 'Von einem Startbetrieb erreicht die Nachricht im Mittel 99 % der anderen Betriebe; das Aggregat aller Kontakte (ohne Reihenfolge) '
                                     'hängt zu 100 % zusammen. Der Median der Ankunftszeit liegt bei t = 385 (Fenster 0 bis 1000), 0 % der Tripel „i erreicht j, j '
                                     'erreicht k“ sind nicht transitiv. Die Reichweite stimmt mit dem Aggregat überein, die SI-Ausbreitung liegt aber 68 Prozentpunkte '
                                     'darunter. SI mit β = 30 % je Kontakt: Endgröße 27 % gegen 95 % in der Aggregat-Rechnung (Kanten ohne Reihenfolge, jede mit 3 '
                                     'Kontakten).'}},
 'V_E1': 'Bei 1 Kontakt je Kante erreicht ein Startbetrieb im Mittel 19 % der anderen (Form 1), obwohl das Aggregat zu 96 % zusammenhängt. Mindestens 90 % des Aggregats '
         'werden erreicht: Form 0,25: ab k = 6; Form 0,50: ab k = 4; Form 1: ab k = 3; Form 3: ab k = 3.',
 'V_E2': 'Zwischen 0,0 % (k = 6, Form 1) und 18,2 % (k = 2, Form 0,25) der Tripel „i erreicht j, j erreicht k“ haben kein i → k. Bei k = 2 liegt der Anteil bei Form '
         '0,25 bei 18,2 %, bei Form 1 bei 10,6 %.',
 'V_E3': 'Bei Form 0,25 und k = 3: Reichweite 69 % im Original, 88 % mit gemischten Zeitmarken und 90 % mit gemischten Kanten; Median der Ankunftszeit 944 im Original, '
         '786 bzw. 748 nach dem Mischen.',
 'V_E4': 'Bei β = 30 % und k = 4 sagt die Aggregat-Rechnung 88 % bis 91 % Endgröße voraus; die SI-Ausbreitung auf der Kontaktfolge erreicht 13 % (Form 0,25) bis 24 % '
         '(Form 3). Die Endgröße steigt mit der Form.',
 'V_E5': 'Auf 8 Fällen (zufällige Folgen mit 8 Betrieben und 12 Kontakten) weicht die Simulation höchstens um 2,0 Standardfehler von der exakten erwarteten Endgröße ab.'}


@lru_cache(maxsize=None)
def _e1():
    return ev.reach_rows(C.T_RANDOM, N, CC, nets=NETS)


@lru_cache(maxsize=None)
def _e2():
    return ev.transitivity_rows(C.T_RANDOM, CC, nets=NETS)


@lru_cache(maxsize=None)
def _e3():
    return ev.null_rows(C.T_RANDOM, N, CC, K_NULL, nets=NETS)


@lru_cache(maxsize=None)
def _e4():
    return ev.spread_rows(C.T_RANDOM, N, CC, K_SPREAD, BETA, nets=NETS)


@lru_cache(maxsize=None)
def _e5():
    return ev.exact_rows()


@lru_cache(maxsize=None)
def _types():
    out = []
    for typ in C.ALL_TYPES:
        out += [{**x, "typ": typ} for x in ev.reach_rows(typ, N, CC, ks=(1, 2, 4), forms=(1.0,), nets=NETS)]
    return out


def _band(x, digits):
    return pytest.approx(x, abs=0.6 * 10.0**-digits)


def _nan_or(x, digits):
    return pytest.approx(math.nan, nan_ok=True) if x is None else _band(x, digits)


def _r(k, form):
    return ev.reach_cell(_e1(), k, form)


# --- E1: Reichweite über die Kontaktzahl -------------------------------------------------------------------------------------------------------------


def test_reach_table():
    rows = _e1()
    assert len(rows) == len(EXPECT["E1"]) == len(C.E1_KS) * len(C.E1_FORMS)
    for got, exp in zip(rows, EXPECT["E1"]):
        assert (got["k"], got["form"], got["nets"]) == (exp["k"], exp["form"], exp["nets"]), exp
        assert got["reach"] == _band(exp["reach"], 4) and got["static"] == _band(exp["static"], 4) and got["median"] == _band(exp["median"], 1), exp
    assert ev.verdict_reach(rows)[1] == EXPECT["V_E1"]


def test_the_aggregate_overestimates_massively_at_one_contact_per_edge_and_the_reach_never_exceeds_it():
    assert all(r["static"] > 0.95 for r in _e1()) and all(r["reach"] <= r["static"] + 1e-12 for r in _e1())
    assert all(_r(1, f)["reach"] < 0.2 for f in C.E1_FORMS) and _r(1, 1.0)["static"] - _r(1, 1.0)["reach"] > 0.75                       # H1: ein Kontakt je Kante
    spread = [_r(1, f)["reach"] for f in C.E1_FORMS]
    assert max(spread) - min(spread) < 0.05                                                                                         # bei k = 1 hängt die Reichweite nicht von der Form ab


def test_the_reach_grows_and_the_median_arrival_falls_with_the_number_of_contacts():
    for f in C.E1_FORMS:
        reach = [_r(k, f)["reach"] for k in C.E1_KS]
        med = [_r(k, f)["median"] for k in C.E1_KS]
        assert all(a < b for a, b in zip(reach, reach[1:4])) and reach[-1] > 0.9 and all(a >= b for a, b in zip(med[1:], med[2:])), f                                        # ab k = 2: bei k = 1 zählen nur die wenigen früh erreichten Paare


def test_burstiness_lowers_the_reach_in_the_transition_region_and_moves_the_threshold_in_k():
    for k in (2, 3, 4, 6):
        assert _r(k, 0.25)["reach"] < _r(k, 1.0)["reach"] < _r(k, 3.0)["reach"] + 1e-9, k                                           # H4: stoßartiger, weniger erreicht
    assert _r(2, 3.0)["reach"] - _r(2, 0.25)["reach"] > 0.25
    thr = {f: ev.threshold_k(_e1(), f) for f in C.E1_FORMS}
    assert thr[0.25] >= thr[0.5] >= thr[1.0] >= thr[3.0] and thr[0.25] > thr[3.0] and all(v is not None for v in thr.values())     # der Kipppunkt in k wandert mit der Stoßartigkeit
    assert _r(12, 0.25)["reach"] > 0.94                                                                                           # bei vielen Kontakten verschwindet der Unterschied fast
    assert _r(12, 0.25)["median"] > _r(12, 1.0)["median"] > _r(12, 3.0)["median"]                                                  # stoßartig bleibt langsamer, auch bei zwölf Kontakten


# --- E2: Nicht-Transitivität ---------------------------------------------------------------------------------------------------------------------------


def test_transitivity_table():
    rows = _e2()
    assert len(rows) == len(EXPECT["E2"]) == len(C.E2_KS) * len(C.E2_FORMS)
    for got, exp in zip(rows, EXPECT["E2"]):
        assert (got["k"], got["form"], got["nets"]) == (exp["k"], exp["form"], exp["nets"]), exp
        assert got["nt"] == _band(exp["nt"], 4) and got["reach"] == _band(exp["reach"], 4), exp
    assert ev.verdict_transitivity(rows)[1] == EXPECT["V_E2"]


def test_paths_are_not_transitive_and_burstiness_raises_the_share():
    rows = _e2()
    for f in C.E2_FORMS:
        nt = [ev.transitivity_cell(rows, k, f)["nt"] for k in C.E2_KS]
        assert nt == sorted(nt, reverse=True)                                                                                       # mit mehr Kontakten wird die Erreichbarkeit transitiver
    assert ev.transitivity_cell(rows, 2, 0.25)["nt"] > 0.15 and ev.transitivity_cell(rows, 2, 1.0)["nt"] > 0.1 and all(ev.transitivity_cell(rows, k, 0.25)["nt"] > ev.transitivity_cell(rows, k, 1.0)["nt"] for k in C.E2_KS)   # H2


# --- E3: Nullmodelle -------------------------------------------------------------------------------------------------------------------------------------


def test_null_model_table():
    rows = _e3()
    assert len(rows) == len(EXPECT["E3"]) == len(C.E3_FORMS) * len(C.NULLS)
    for got, exp in zip(rows, EXPECT["E3"]):
        assert (got["form"], got["null"], got["k"], got["nets"]) == (exp["form"], exp["null"], exp["k"], exp["nets"]), exp
        assert got["reach"] == _band(exp["reach"], 4) and got["median"] == _band(exp["median"], 1), exp
    assert ev.verdict_nulls(rows)[1] == EXPECT["V_E3"]


def test_shuffling_restores_the_reach_of_bursty_sequences_and_changes_nothing_for_poisson_like_ones():
    o, t, e = (ev.null_cell(_e3(), 0.25, n) for n in C.NULLS)
    assert t["reach"] - o["reach"] > 0.15 and e["reach"] - o["reach"] > 0.15 and t["median"] < o["median"] and e["median"] < o["median"]       # H5
    o1, t1, e1 = (ev.null_cell(_e3(), 1.0, n) for n in C.NULLS)
    assert abs(t1["reach"] - o1["reach"]) < 0.03 and abs(e1["reach"] - o1["reach"]) < 0.03


# --- E4: SI gegen Aggregat -----------------------------------------------------------------------------------------------------------------------------------


def test_spread_table():
    rows = _e4()
    assert len(rows) == len(EXPECT["E4"]) == len(C.E4_FORMS)
    for got, exp in zip(rows, EXPECT["E4"]):
        assert (got["form"], got["k"], got["beta"], got["nets"]) == (exp["form"], exp["k"], exp["beta"], exp["nets"]), exp
        assert got["si"] == _band(exp["si"], 4) and got["si_shuffled"] == _band(exp["si_shuffled"], 4) and got["aggregate"] == _band(exp["aggregate"], 4) and got["unreached"] == _band(exp["unreached"], 4), exp
        assert got["t50"] == _nan_or(exp["t50"], 1), exp
    assert ev.verdict_spread(rows)[1] == EXPECT["V_E4"]


def test_the_aggregate_calculation_overestimates_the_si_final_size_several_fold():
    rows = _e4()
    assert all(r["aggregate"] > 0.85 and r["si"] < 0.3 and r["aggregate"] > 3 * r["si"] for r in rows)                             # H1 (SI)
    si = [ev.spread_cell(rows, f)["si"] for f in C.E4_FORMS]
    assert si == sorted(si)                                                                                                         # H6: bei diesem Netz steigt die Endgröße mit der Form
    shuffled = [ev.spread_cell(rows, f)["si_shuffled"] for f in C.E4_FORMS]
    assert max(shuffled) - min(shuffled) < 0.05 < max(si) - min(si) + 0.05                                                          # nach dem Mischen fast keine Abhängigkeit von der Form


# --- E5: exakt -----------------------------------------------------------------------------------------------------------------------------------------------


def test_exact_table_and_simulation_agree():
    rows = _e5()
    assert len(rows) == len(EXPECT["E5"]) == C.EXACT_INSTANCES * len(C.EXACT_BETAS)
    for got, exp in zip(rows, EXPECT["E5"]):
        assert (got["instance"], got["beta"], got["contacts"], got["times"]) == (exp["instance"], exp["beta"], exp["contacts"], exp["times"]), exp
        assert got["exact"] == _band(exp["exact"], 6) and got["sim"] == _band(exp["sim"], 5) and got["se"] == _band(exp["se"], 5), exp
        assert abs(got["sim"] - got["exact"]) <= 4.5 * got["se"]                                                                    # H7
    assert ev.verdict_exact(rows)[1] == EXPECT["V_E5"]


# --- Netztypen und Stoßartigkeit ---------------------------------------------------------------------------------------------------------------------


def test_network_type_table():
    rows = _types()
    assert len(rows) == len(EXPECT["TYPES"])
    for got, exp in zip(rows, EXPECT["TYPES"]):
        assert (got["typ"], got["k"]) == (exp["typ"], exp["k"]), exp
        assert got["reach"] == _band(exp["reach"], 4) and got["static"] == _band(exp["static"], 4) and got["median"] == _band(exp["median"], 1), exp


def test_the_ring_overestimates_most_and_the_scale_free_net_least():
    by = {(r["typ"], r["k"]): r for r in _types()}
    gap = {t: by[(t, 4)]["static"] - by[(t, 4)]["reach"] for t in C.ALL_TYPES}
    assert gap[C.T_RING] > 0.4 and gap[C.T_BA] < 0.01 and gap[C.T_RING] == max(gap.values()) and gap[C.T_BA] == min(gap.values())
    assert all(by[(t, 1)]["reach"] < 0.4 < by[(t, 1)]["static"] for t in C.ALL_TYPES)


def test_burstiness_coefficient_by_form():
    rows = []
    for fi, shape in enumerate(C.E1_FORMS):
        vals = []
        for seed in C.SWEEP_SEEDS:
            _, edges = ev.build_net(C.T_RANDOM, N, CC, seed)
            vals.append(A.burstiness(A.contact_sequence(edges, C.T_WINDOW, BURST_K, shape, ev._rng(seed, 60, fi))))
        rows.append(float(np.mean(vals)))
    assert len(rows) == len(EXPECT["BURST"])
    for got, exp in zip(rows, EXPECT["BURST"]):
        assert got == _band(exp["burst"], 3)
    assert rows == sorted(rows, reverse=True) and rows[0] > 0.2 and rows[-1] < -0.4


# --- Presets ---------------------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_preset_numbers(name):
    an = ev.analyse(ev.Settings(**C.PRESETS[name]))
    exp = EXPECT["presets"][name]
    assert (an.m, len(an.contacts)) == (exp["m"], exp["contacts"])
    for got, key, digits in ((an.reach, "reach", 4), (an.static, "static", 4), (an.median, "median", 1), (an.nt, "nt", 4), (an.si_final, "si", 4), (an.agg_final, "agg", 4)):
        assert got == _band(exp[key], digits), (name, key)
    assert an.burst == _nan_or(exp["burst"], 3) and an.si_t50 == _nan_or(exp["t50"], 1)
    assert ev.verdict_main(an) == (exp["kind"], exp["verdict"])
