"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, fährt jeden Slider an seine Grenzen,
prüft Permalink, Netztypen, Nullmodelle, den Zeit-Regler und alle fünf Experimente; es darf kein Python-Fehler auftreten."""

import os

import pytest
from streamlit.testing.v1 import AppTest

import ztn_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
EXPERIMENTS = ("reach", "trans", "nulls", "spread", "exact")
METRICS = ["Reichweite", "Aggregat", "Ankunft (Median)", "Nicht transitiv", "SI-Endgröße"]
SLIDERS = ["n_slider", "c_slider", "k_slider", "form_slider", "beta_slider"]


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _metric(at, label):
    return next(m.value for m in at.metric if m.label == label)


def test_app_loads_without_exception():
    at = _fresh_app()
    assert [m.label for m in at.metric] == METRICS
    assert [_metric(at, k) for k in METRICS] == ["64 %", "94 %", "669", "13,5 %", "6 %"]
    assert not at.error and not at.success
    assert any(w.value.startswith("Von einem Startbetrieb erreicht die Nachricht im Mittel 64 % der anderen Betriebe;") for w in at.warning)
    assert any("**SI-Endgröße in der Aggregat-Rechnung:** 61 %." in c.value for c in at.caption)


def test_every_preset_click_does_not_raise():
    for name in C.PRESETS:
        at = _fresh_app()
        at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
        assert not at.exception, (name, [str(e) for e in at.exception])


def test_the_presets_show_their_numbers():
    at = _fresh_app()
    at.sidebar.button(key="preset_Ein Kontakt je Kante: nur jeder Fünfte erreichbar").click().run(timeout=TIMEOUT)
    assert [_metric(at, k) for k in ("Reichweite", "Aggregat", "Nicht transitiv")] == ["20 %", "94 %", "45,0 %"]
    at.sidebar.button(key="preset_Zeitmarken gemischt: viel schneller").click().run(timeout=TIMEOUT)
    assert _metric(at, "Ankunft (Median)") == "11" and any("Aggregat und Kontaktfolge stimmen hier überein." in s.value for s in at.success)
    at.sidebar.button(key="preset_Verbünde").click().run(timeout=TIMEOUT)
    assert at.selectbox(key="raum_select").value == C.T_COMMUNITIES and _metric(at, "Reichweite") == "99 %" and _metric(at, "SI-Endgröße") == "27 %"


def test_the_sidebar_has_exactly_these_sliders_in_this_order():
    at = _fresh_app()
    assert [s.key for s in at.sidebar.slider] == SLIDERS and [s.disabled for s in at.sidebar.slider] == [False] * 5


@pytest.mark.parametrize("key", SLIDERS)
@pytest.mark.parametrize("edge", ["min", "max"])
def test_every_slider_at_its_min_and_max_does_not_raise(key, edge):
    at = _fresh_app()
    slider = at.sidebar.slider(key=key)
    slider.set_value(int(slider.min if edge == "min" else slider.max)).run(timeout=TIMEOUT)
    assert not at.exception, (key, edge, [str(e) for e in at.exception])


def test_all_sliders_at_their_minimum_and_all_at_their_maximum_do_not_raise():
    for edge in ("min", "max"):
        at = _fresh_app()
        for slider in at.sidebar.slider:
            slider.set_value(int(slider.min if edge == "min" else slider.max))
        at.run(timeout=TIMEOUT)
        assert not at.exception, (edge, [str(e) for e in at.exception])


@pytest.mark.parametrize("typ", C.ALL_TYPES)
def test_every_network_type_renders(typ):
    at = _fresh_app()
    at.selectbox(key="raum_select").set_value(typ).run(timeout=TIMEOUT)
    assert not at.exception, (typ, [str(e) for e in at.exception])


@pytest.mark.parametrize("null", C.NULLS)
def test_every_null_model_renders(null):
    at = _fresh_app()
    at.selectbox(key="null_select").set_value(null).run(timeout=TIMEOUT)
    assert not at.exception, (null, [str(e) for e in at.exception])


def test_the_time_slider_moves_through_the_grid_and_resets_with_the_settings():
    at = _fresh_app()
    slider = at.select_slider[0]
    assert slider.label == "Zeit t" and len(slider.options) == 51 and slider.value == 500 and int(slider.options[-1]) == C.T_WINDOW
    slider.set_value(1000).run(timeout=TIMEOUT)
    assert not at.exception and at.select_slider[0].value == 1000
    at.sidebar.slider(key="k_slider").set_value(3).run(timeout=TIMEOUT)
    assert not at.exception and at.select_slider[0].value == 500                                      # neue Einstellungen: neuer Regler, zurück auf die Mitte


def test_a_new_run_changes_the_seed_and_the_result():
    at = _fresh_app()
    before = at.number_input(key="seed_input").value
    at.button[[b.label for b in at.button].index("🎲 Neuer Lauf")].click().run(timeout=TIMEOUT)
    assert not at.exception and at.number_input(key="seed_input").value != before


def test_permalink_values_are_clamped_and_unknown_choices_ignored():
    at = AppTest.from_file(APP_PATH)
    at.query_params["n"] = "5"
    at.query_params["kontakte"] = "99"
    at.query_params["form"] = "9999"
    at.query_params["nullmodell"] = "gibt es nicht"
    at.query_params["raum"] = "gibt es nicht"
    at.run(timeout=TIMEOUT)
    assert not at.exception
    assert at.slider(key="n_slider").value == C.N_MIN and at.slider(key="k_slider").value == C.K_MAX and at.slider(key="form_slider").value == C.FORM_MAX
    assert at.selectbox(key="null_select").value == C.N_ORIGINAL and at.selectbox(key="raum_select").value == C.T_RANDOM


def test_permalink_selects_type_and_null_model_and_the_address_mirrors_the_settings():
    at = AppTest.from_file(APP_PATH)
    at.query_params["raum"] = C.T_COMMUNITIES
    at.query_params["nullmodell"] = C.N_TIME
    at.query_params["kontakte"] = "5"
    at.run(timeout=TIMEOUT)
    assert not at.exception and at.selectbox(key="raum_select").value == C.T_COMMUNITIES and at.selectbox(key="null_select").value == C.N_TIME and at.slider(key="k_slider").value == 5
    assert dict(at.query_params) == {"raum": C.T_COMMUNITIES, "n": "200", "c": "4", "kontakte": "5", "form": "100", "beta": "30", "nullmodell": C.N_TIME, "seed": "35"}


def test_every_experiment_runs_and_is_invalidated_by_a_setting_change():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    at.sidebar.slider(key="n_slider").set_value(C.N_MIN).run(timeout=TIMEOUT)         # kleines Netz: schnell
    for name in EXPERIMENTS:
        at.button(key=f"run_{name}").click().run(timeout=TIMEOUT)
        assert not at.exception, (name, [str(e) for e in at.exception])
    texts = " ".join(x.value for x in list(at.info) + list(at.warning) + list(at.success))
    for fragment in ("Mindestens 90 % des Aggregats werden erreicht:", "der Tripel „i erreicht j, j erreicht k“ haben kein i → k", "mit gemischten Zeitmarken und", "sagt die Aggregat-Rechnung", "Auf 8 Fällen (zufällige Folgen mit 8 Betrieben und 12 Kontakten)"):
        assert fragment in texts, fragment
    at.sidebar.slider(key="n_slider").set_value(C.N_MIN + 10).run(timeout=TIMEOUT)
    assert not at.exception
    assert sum("neu starten" in i.value for i in at.info) == 3                                    # Experiment 1, 3 und 4 hängen an n; 2 und 5 nicht
