"""Aggregat und Kontaktfolge: gültige Netze, Determinismus (auch über Prozesse), Kantenlisten, Zusammenhang von Einstellung und Folge."""

import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import ztn_algorithm as A
import ztn_constants as C
import ztn_evaluation as ev
import ztn_scenario as S

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("typ", C.ALL_TYPES)
@pytest.mark.parametrize("n,c", [(C.N_MIN, C.C_MIN), (C.N_MIN, C.C_MAX), (C.DEFAULT_N, C.DEFAULT_C), (C.N_MAX, C.C_MAX)])
def test_every_corner_gives_a_valid_aggregate(typ, n, c):
    inst, edges = ev.build_net(typ, n, c, 35, layout=True)
    assert inst.n == n and len(inst.pos) == n
    for x, y in inst.pos:
        assert math.isfinite(x) and math.isfinite(y) and -1e-9 <= x <= 1 + 1e-9 and -1e-9 <= y <= 1 + 1e-9
    for a, nb in enumerate(inst.adj):
        assert list(nb) == sorted(set(nb)) and a not in nb
        for b in nb:
            assert a in inst.adj[b]
    assert edges == sorted(edges) and all(i < j for i, j in edges) and len(edges) == sum(len(nb) for nb in inst.adj) // 2


def test_the_community_network_has_six_groups_and_the_others_none():
    for typ in C.ALL_TYPES:
        inst, _ = ev.build_net(typ, 120, 6, 5)
        if typ == C.T_COMMUNITIES:
            assert sorted(set(inst.groups)) == list(range(C.BLOCKS))
        else:
            assert inst.groups is None


def test_aggregates_are_deterministic_per_seed_and_differ_between_seeds():
    a = ev.build_net(C.T_COMMUNITIES, 80, 6, 5)[1]
    assert a == ev.build_net(C.T_COMMUNITIES, 80, 6, 5)[1] and ev.build_net(C.T_COMMUNITIES, 80, 6, 6)[1] != a


def test_layout_false_skips_the_force_layout_and_unknown_type_raises():
    inst = S.make_instance(C.T_RANDOM, 60, 4, 1, layout=False)
    assert set(inst.pos) == {(0.5, 0.5)}
    for bad in ("gibt es nicht", "Gitter"):
        with pytest.raises(ValueError):
            S.make_instance(bad, 60, 4, 1)


def test_the_contact_sequence_of_an_analysis_has_k_contacts_per_edge_and_the_aggregate_is_the_edge_set():
    an = ev.analyse(ev.Settings(n=100, k=3))
    assert len(an.contacts) == 3 * an.m and A.aggregate_edges(an.contacts) == an.edges
    assert an.static == pytest.approx(A.static_reach(100, an.edges))


def test_the_null_models_keep_the_multiset_of_times_or_edges_of_the_same_base_sequence():
    base = ev.analyse(ev.Settings(n=100, form=25))
    t = ev.analyse(ev.Settings(n=100, form=25, null=C.N_TIME))
    e = ev.analyse(ev.Settings(n=100, form=25, null=C.N_EDGE))
    assert sorted(c[0] for c in t.contacts) == sorted(c[0] for c in base.contacts) and sorted((u, v) for _, u, v in t.contacts) == sorted((u, v) for _, u, v in base.contacts)
    assert [c[0] for c in e.contacts] == [c[0] for c in base.contacts] and sorted((u, v) for _, u, v in e.contacts) == sorted((u, v) for _, u, v in base.contacts)
    assert t.contacts != base.contacts and e.contacts != base.contacts


def test_make_contacts_rejects_an_unknown_null_model():
    with pytest.raises(ValueError):
        ev.make_contacts([(0, 1)], 2, 1.0, np.random.default_rng(1), "gibt es nicht")


def test_the_run_is_independent_of_the_hash_seed_of_the_process():
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import hashlib, ztn_constants as C, ztn_evaluation as E;"
            "h = hashlib.sha256();"
            "[h.update(repr((lambda a: (a.contacts, a.arrival.tolist(), a.inf0, a.si_final, a.agg_final))(E.analyse(E.Settings(sp, 60, 4, 3, f, 40, nl, 7)))).encode()) for sp in C.ALL_TYPES for f in (25, 100) for nl in C.NULLS];"
            "print(h.hexdigest())")
    outs = []
    for hashseed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hashseed)
        outs.append(subprocess.run([sys.executable, "-I", "-X", "utf8", "-c", code, str(ROOT)], capture_output=True, text=True, env=env, check=True).stdout.strip())
    assert outs[0] == outs[1] and len(outs[0]) == 64
