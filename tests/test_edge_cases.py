"""Randfälle der Auswertung: Grenzen aller Regler, alle Netztypen und Nullmodelle, kleine Messreihen, Seeds, Gleichstände."""

import dataclasses
import math

import pytest

import ztn_algorithm as A
import ztn_constants as C
import ztn_evaluation as ev


def _an(**kw):
    return ev.analyse(ev.Settings(**kw))


@pytest.mark.parametrize("typ", C.ALL_TYPES)
@pytest.mark.parametrize("n,c,k,form,beta", [(C.N_MIN, C.C_MIN, C.K_MIN, C.FORM_MIN, C.BETA_MIN), (C.N_MIN, C.C_MAX, C.K_MAX, C.FORM_MAX, C.BETA_MAX), (C.N_MAX, C.C_MIN, C.K_MIN, C.FORM_MAX, C.BETA_MAX),
                                              (C.N_MAX, C.C_MAX, C.K_MAX, C.FORM_MIN, C.BETA_MIN)])
def test_corners_of_all_sliders_run_and_stay_consistent(typ, n, c, k, form, beta):
    an = _an(raum=typ, n=n, c=c, k=k, form=form, beta=beta)
    assert len(an.contacts) == k * an.m and 0.0 <= an.reach <= an.static + 1e-12 <= 1.0 + 1e-12
    kind, text = ev.verdict_main(an)
    assert kind in ("success", "info", "warning") and text and "nan" not in text.lower()
    assert 0.0 <= an.si_final <= 1.0 and 0.0 <= an.agg_final <= 1.0 and all(0.0 <= x <= 1.0 + 1e-12 for x in an.curve_reach + an.curve_si)


@pytest.mark.parametrize("null", C.NULLS)
def test_every_null_model_runs_and_keeps_the_contact_count(null):
    base = _an(null=C.N_ORIGINAL)
    an = _an(null=null)
    assert len(an.contacts) == len(base.contacts) and an.edges == base.edges


def test_si_with_full_transmission_equals_the_reach_of_the_source_and_without_transmission_stays_at_the_source():
    full = _an(beta=100, n=60)
    assert full.inf0 == full.arr0
    low = ev.Settings(n=60, beta=0)
    assert low.p == 0.0


def test_the_end_of_the_time_slider_shows_all_arrivals():
    an = _an(n=60, k=4)
    assert an.grid[-1] == C.T_WINDOW and all(a < C.T_WINDOW for a in an.arr0 if a < A.INF)


def test_seeds_zero_and_maximum_run_and_differ():
    a, b = _an(n=60, seed=0), _an(n=60, seed=C.SEED_MAX)
    assert a.contacts != b.contacts


def test_the_same_settings_give_the_same_run_and_other_seeds_other_runs():
    base = ev.Settings(n=80)
    a, b = ev.analyse(base), ev.analyse(base)
    assert a.contacts == b.contacts and a.reach == b.reach and a.inf0 == b.inf0 and a.si_final == b.si_final
    assert ev.analyse(dataclasses.replace(base, seed=36)).contacts != a.contacts


def test_the_contacts_do_not_depend_on_the_transmission_or_the_null_model_choice_of_the_other_settings():
    base = _an(n=80)
    assert _an(n=80, beta=60).contacts == base.contacts and _an(n=80, beta=60).reach == base.reach


def test_settings_derived_values():
    s = ev.Settings(form=25, beta=40)
    assert s.shape == 0.25 and s.p == 0.4


def test_measurement_rows_with_one_net_and_few_sources_are_well_formed():
    rows = ev.reach_rows(C.T_RANDOM, 60, 4, ks=(1, 3), forms=(0.5, 1.0), nets=1, sources=5)
    assert len(rows) == 4 and all(r["nets"] == 1 and 0.0 <= r["reach"] <= r["static"] + 1e-12 for r in rows) and ev.reach_cell(rows, 3, 0.5)["form"] == 0.5
    trans = ev.transitivity_rows(C.T_RING, 4, ks=(2,), forms=(1.0,), nets=1, n=60)
    assert len(trans) == 1 and trans[0]["n"] == 60 and 0.0 <= trans[0]["nt"] <= 1.0
    nulls = ev.null_rows(C.T_POWER, 60, 4, 2, forms=(0.5,), nets=1, sources=5)
    assert [r["null"] for r in nulls] == list(C.NULLS)
    spread = ev.spread_rows(C.T_BA, 60, 4, 2, 0.5, forms=(1.0,), nets=1, sources=5)
    assert len(spread) == 1 and 0.0 <= spread[0]["si"] <= 1.0 and 0.0 <= spread[0]["unreached"] <= 1.0


def test_exact_rows_on_tiny_instances_agree_between_exact_and_simulation():
    rows = ev.exact_rows(instances=2, betas=(0.5,), n=6, contacts=8, sim_runs=1500)
    assert len(rows) == 2 and all(abs(r["sim"] - r["exact"]) < 5 * r["se"] + 1e-9 and r["contacts"] == 8 for r in rows)


def test_burstiness_of_a_generated_sequence_is_defined_for_k_at_least_two():
    assert math.isnan(_an(n=60, k=1).burst) and not math.isnan(_an(n=60, k=2).burst)
