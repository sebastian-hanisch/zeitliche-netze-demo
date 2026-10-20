"""Verdikte (reine Funktionen: Art und Text) und Formatierung: jede Zahl im Text kommt aus der Rechnung, Grenzfälle und leere Eingaben."""

import math

import ztn_constants as C
import ztn_evaluation as ev


def _an(**kw):
    return ev.analyse(ev.Settings(**kw))


def test_formatting_helpers_use_comma_and_typographic_minus():
    assert ev.de(1.234, 2) == "1,23" and ev.de(-0.5, 1) == "−0,5" and ev.de(-0.0004, 2) == "0,00" and ev.de(float("nan")) == "–" and ev.de(None) == "–"
    assert ev.pct(0.714) == "71" and ev.pct(0.0714, 1) == "7,1"
    assert ev.form_txt(1.0) == "1" and ev.form_txt(3.0) == "3" and ev.form_txt(0.25) == "0,25" and ev.form_txt(0.5) == "0,50"


def test_main_verdict_warns_when_the_aggregate_overestimates_the_reach():
    kind, text = ev.verdict_main(_an())
    assert kind == "warning" and text.startswith("Von einem Startbetrieb erreicht die Nachricht im Mittel 64 % der anderen Betriebe; das Aggregat aller Kontakte (ohne Reihenfolge) hängt zu 94 % zusammen.")
    assert "Das Aggregat überschätzt die Reichweite um 30 Prozentpunkte." in text and "Endgröße 6 % gegen 61 % in der Aggregat-Rechnung (Kanten ohne Reihenfolge, jede mit 2 Kontakten)" in text
    assert "(Fenster 0 bis 1000), 14 % der Tripel" in text


def test_main_verdict_names_the_si_gap_when_only_the_spread_differs():
    kind, text = ev.verdict_main(_an(raum=C.T_COMMUNITIES, c=6, k=3))
    assert kind == "warning" and "Die Reichweite stimmt mit dem Aggregat überein, die SI-Ausbreitung liegt aber 68 Prozentpunkte darunter." in text


def test_main_verdict_is_a_success_when_everything_agrees():
    kind, text = ev.verdict_main(_an(c=6, k=8, form=15, null=C.N_TIME))
    assert kind == "success" and "Aggregat und Kontaktfolge stimmen hier überein." in text


def test_main_verdict_grammar_for_one_contact():
    assert "jede mit 1 Kontakt)" in ev.verdict_main(_an(k=1))[1] and "jede mit 3 Kontakten)" in ev.verdict_main(_an(k=3))[1]


def test_main_verdict_without_contacts():
    an = _an(n=60, k=0)
    assert an.contacts == [] and an.reach == 0.0
    assert ev.verdict_main(an) == ("info", "Das Netz hat keine Kontakte: keine Nachricht kommt an.")


def _reach_rows(reach_by_form):
    rows = []
    for form, vals in reach_by_form.items():
        for k, r in zip((1, 2, 3, 4), vals):
            rows.append({"k": k, "form": form, "reach": r, "static": 0.96, "median": 500.0 - 50 * k, "nets": 5})
    return rows


def test_reach_verdict_names_the_thresholds_per_form_and_never():
    rows = _reach_rows({0.25: (0.15, 0.45, 0.6, 0.9), 1.0: (0.2, 0.67, 0.88, 0.94)})
    kind, text = ev.verdict_reach(rows)
    assert kind == "info" and text.startswith("Bei 1 Kontakt je Kante erreicht ein Startbetrieb im Mittel 20 % der anderen (Form 1), obwohl das Aggregat zu 96 % zusammenhängt.")
    assert text.endswith("Mindestens 90 % des Aggregats werden erreicht: Form 0,25: ab k = 4; Form 1: ab k = 3.")
    assert "Form 0,25: nie" in ev.verdict_reach(_reach_rows({0.25: (0.1, 0.2, 0.3, 0.4)}))[1]
    assert ev.verdict_reach([]) == ("warning", "Keine Läufe.")


def test_threshold_k_and_reach_cell_pick_the_right_rows():
    rows = _reach_rows({1.0: (0.2, 0.67, 0.88, 0.94)})
    assert ev.threshold_k(rows, 1.0) == 3 and ev.threshold_k(rows, 1.0, share=0.99) is None and ev.threshold_k(rows, 1.0, share=0.5) == 2 and ev.threshold_k(rows, 3.0) is None
    assert ev.reach_cell(rows, 2, 1.0)["reach"] == 0.67


def test_transitivity_verdict_reports_the_range_and_the_form_contrast():
    rows = [{"k": 2, "form": 0.25, "nt": 0.18, "reach": 0.6, "nets": 5, "n": 100}, {"k": 6, "form": 0.25, "nt": 0.01, "reach": 0.9, "nets": 5, "n": 100},
            {"k": 2, "form": 1.0, "nt": 0.1, "reach": 0.7, "nets": 5, "n": 100}, {"k": 6, "form": 1.0, "nt": 0.0, "reach": 0.95, "nets": 5, "n": 100}]
    kind, text = ev.verdict_transitivity(rows)
    assert kind == "info" and text.startswith("Zwischen 0,0 % (k = 6, Form 1) und 18,0 % (k = 2, Form 0,25) der Tripel") and text.endswith("Bei k = 2 liegt der Anteil bei Form 0,25 bei 18,0 %, bei Form 1 bei 10,0 %.")
    assert "Bei k = " not in ev.verdict_transitivity(rows[:2])[1]
    assert ev.verdict_transitivity([]) == ("warning", "Keine Läufe.")


def test_null_verdict_compares_the_original_with_both_shuffles():
    rows = [{"form": 0.25, "null": nl, "reach": r, "median": m, "k": 3, "nets": 5} for nl, r, m in ((C.N_ORIGINAL, 0.69, 944.0), (C.N_TIME, 0.88, 786.0), (C.N_EDGE, 0.9, 748.0))]
    kind, text = ev.verdict_nulls(rows)
    assert kind == "info" and text == ("Bei Form 0,25 und k = 3: Reichweite 69 % im Original, 88 % mit gemischten Zeitmarken und 90 % mit gemischten Kanten; Median der Ankunftszeit 944 im Original, 786 bzw. 748 nach dem Mischen.")
    assert ev.verdict_nulls([]) == ("warning", "Keine Läufe.")


def _spread_rows(si):
    return [{"form": f, "si": s, "si_shuffled": 0.2, "t50": 900.0, "aggregate": 0.9, "unreached": 0.5, "k": 4, "beta": 0.3, "nets": 5} for f, s in zip((0.25, 0.5, 1.0, 3.0), si)]


def test_spread_verdict_states_the_aggregate_range_and_monotonicity():
    kind, text = ev.verdict_spread(_spread_rows((0.13, 0.18, 0.2, 0.24)))
    assert kind == "info" and text.startswith("Bei β = 30 % und k = 4 sagt die Aggregat-Rechnung 90 % Endgröße voraus; die SI-Ausbreitung auf der Kontaktfolge erreicht 13 % (Form 0,25) bis 24 % (Form 3).") and text.endswith("steigt mit der Form.")
    assert text.count("90 %") == 1 and "ist in der Form nicht monoton." in ev.verdict_spread(_spread_rows((0.3, 0.18, 0.2, 0.24)))[1]
    rows = _spread_rows((0.13, 0.18, 0.2, 0.24))
    rows[0]["aggregate"] = 0.85
    assert "sagt die Aggregat-Rechnung 85 % bis 90 % Endgröße voraus" in ev.verdict_spread(rows)[1]
    assert ev.verdict_spread([]) == ("warning", "Keine Läufe.")


def test_exact_verdict_reports_the_worst_deviation_in_standard_errors():
    rows = [{"instance": 1, "beta": 0.3, "contacts": 12, "times": 5, "exact": 0.3, "sim": 0.302, "se": 0.001}, {"instance": 2, "beta": 0.3, "contacts": 12, "times": 5, "exact": 0.2, "sim": 0.1985, "se": 0.001}]
    kind, text = ev.verdict_exact(rows)
    assert kind == "info" and text == "Auf 2 Fällen (zufällige Folgen mit 8 Betrieben und 12 Kontakten) weicht die Simulation höchstens um 2,0 Standardfehler von der exakten erwarteten Endgröße ab."
    assert ev.verdict_exact([]) == ("warning", "Keine Rechnung.")
    assert "um 0,0 Standardfehler" in ev.verdict_exact([{**rows[0], "sim": 0.3, "se": 0.0}])[1]


def test_nan_inputs_never_leak_into_the_text():
    an = _an(n=60, k=1)
    assert not math.isnan(an.reach) and "nan" not in ev.verdict_main(an)[1].lower()
