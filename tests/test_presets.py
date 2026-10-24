"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt, wofür es benannt ist."""

import pytest

import ztn_algorithm as A
import ztn_constants as C
import ztn_evaluation as ev
import ztn_presets as P


def _settings(name):
    return ev.Settings(**C.PRESETS[name])


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, p in C.PRESETS.items():
        assert p["raum"] in C.ALL_TYPES and C.N_MIN <= p["n"] <= C.N_MAX and C.C_MIN <= p["c"] <= C.C_MAX and C.K_MIN <= p["k"] <= C.K_MAX and 0 <= p["seed"] <= C.SEED_MAX, name
        assert C.FORM_MIN <= p["form"] <= C.FORM_MAX and C.BETA_MIN <= p["beta"] <= C.BETA_MAX and p["null"] in C.NULLS, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[C.DEFAULT_PRESET_NAME]) == ev.Settings()
    assert next(iter(C.PRESETS)) == C.DEFAULT_PRESET_NAME


def test_setting_specs_cover_every_preset_key_and_defaults_match():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    for key, state_key in P.PRESET_KEYS.items():
        assert P.SETTING_SPECS[state_key].default == C.PRESETS[C.DEFAULT_PRESET_NAME][key], key


def test_every_preset_differs_from_the_default_in_something_besides_the_network_type():
    default = C.PRESETS[C.DEFAULT_PRESET_NAME]
    for name, p in C.PRESETS.items():
        if name != C.DEFAULT_PRESET_NAME:
            assert any(p[k] != default[k] for k in p if k != "raum"), name


def test_each_preset_shows_what_its_name_says():
    an = {name: ev.analyse(_settings(name)) for name in C.PRESETS}
    two = an[C.DEFAULT_PRESET_NAME]
    assert 0.55 < two.reach < 0.75 and two.static > 0.9 and two.static - two.reach > 0.2 and two.si_final < 0.15 < two.agg_final
    one = an["Ein Kontakt je Kante: nur jeder Fünfte erreichbar"]
    assert one.reach < 0.25 and one.static > 0.9 and one.nt > 0.3 and one.settings.k == 1 and one.reach < two.reach
    six = an["Sechs Kontakte je Kante: fast alle erreicht"]
    assert six.reach > 0.9 and six.static - six.reach < 0.03 and six.nt < 0.01 and six.median < two.median
    burst = an["Stoßartig: erreichbar, aber langsam"]
    assert burst.reach > 0.95 and burst.burst > 0.3 and burst.median > 150 and burst.settings.form == 15
    mixed = an["Zeitmarken gemischt: viel schneller"]
    assert mixed.settings.null == C.N_TIME and mixed.median < 30 and mixed.reach > 0.95 and mixed.median < burst.median / 5                               # nur die Zuordnung von Kante und Zeit ist anders
    assert sorted(c[0] for c in mixed.contacts) == sorted(c[0] for c in burst.contacts) and mixed.edges == burst.edges
    comm = an["Verbünde"]
    assert comm.settings.raum == C.T_COMMUNITIES and comm.reach > 0.95 and comm.si_final < 0.4 and comm.agg_final > 0.9


def test_every_preset_runs_and_the_verdict_is_a_known_kind():
    for name in C.PRESETS:
        an = ev.analyse(_settings(name))
        kind, text = ev.verdict_main(an)
        assert kind in ("success", "info", "warning") and text
        assert an.grid[0] == 0 and an.grid[-1] == C.T_WINDOW and len(an.curve_reach) == len(an.curve_si) == len(an.grid)
        assert all(x <= y + 1e-12 for x, y in zip(an.curve_reach, an.curve_reach[1:])) and all(x <= y + 1e-12 for x, y in zip(an.curve_si, an.curve_si[1:]))   # Kurven wachsen
        assert an.reach <= an.static + 1e-12 and an.arr0[an.source] == -1 and an.inf0[an.source] == -1
        assert all(i >= a for i, a in zip(an.inf0, an.arr0))                                                                                                # Ansteckung nie vor der frühesten Ankunft
        assert an.curve_reach[-1] == pytest.approx(an.reach)                                                                                                # am Ende des Fensters ist alles Erreichbare erreicht
        assert A.static_reach(an.settings.n, an.edges) == an.static
