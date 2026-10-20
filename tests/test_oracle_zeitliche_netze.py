"""Orakel-Tests (ORACLE-PLAYBOOK): der Kern wird gegen unabhängige Rechenwege geprüft, nicht gegen sich selbst.

* Früheste Ankunft: gegen die Breitensuche auf dem **zeitexpandierten Graphen** und gegen die **Aufzählung aller zeitrespektierenden Wege** (300 bzw. 200 Zufallsfolgen mit Gleichständen und Mehrfachkontakten),
  dazu die Zeitumkehr (i erreicht j in der Folge genau dann, wenn j das i in der zeitlich umgekehrten Folge erreicht).
* Aggregat: gegen `networkx`.
* Nicht-Transitivität: gegen die Dreifachschleife.
* SI: die exakte Rechnung gegen die Aufzählung aller Münzwürfe (Gewicht β^k (1 − β)^(m − k)), die Simulation gegen die exakte Erwartung im Band über den Standardfehler.
* Eigenschaften: Monotonie (ein zusätzlicher Kontakt verschlechtert keine Ankunft), Ansteckung nie vor der frühesten Ankunft, zeitlich nie mehr erreicht als im Aggregat.
"""

import itertools
import math

import networkx as nx
import numpy as np
import pytest

import ztn_algorithm as A
from conftest import random_contacts

INF = A.INF


def _cases(count, seed, max_n=8, max_contacts=14):
    rng = np.random.default_rng(seed)
    for _ in range(count):
        n = int(rng.integers(2, max_n + 1))
        tmax = int(rng.integers(1, 9))
        yield rng, n, random_contacts(rng, n, int(rng.integers(0, max_contacts + 1)), tmax), tmax


def _expanded_graph_arrival(n, contacts, tmax, source):
    """Zeitexpandierter Graph: Knoten (v, τ) = „v hat die Nachricht am Ende von τ“; Warten (v, τ) → (v, τ + 1), Kontakt (t, u, v): (u, t − 1) → (v, t) und (v, t − 1) → (u, t). Früheste Ankunft = kleinstes erreichbares τ."""
    adj = {}
    for v in range(n):
        for tau in range(-1, tmax):
            if tau + 1 < tmax:
                adj.setdefault((v, tau), []).append((v, tau + 1))
    for t, u, v in contacts:
        adj.setdefault((u, t - 1), []).append((v, t))
        adj.setdefault((v, t - 1), []).append((u, t))
    seen = {(source, -1)}
    stack = [(source, -1)]
    while stack:
        x = stack.pop()
        for y in adj.get(x, []):
            if y not in seen:
                seen.add(y)
                stack.append(y)
    best = [INF] * n
    for v, tau in seen:
        best[v] = min(best[v], tau)
    return best


def _enumerated_arrival(n, contacts, source):
    """Aufzählung aller zeitrespektierenden Wege (streng wachsende Zeitmarken) durch Tiefensuche über die Kontakte."""
    best = [INF] * n
    best[source] = -1

    def dfs(node, last):
        for t, u, v in contacts:
            if t > last and node in (u, v):
                other = v if node == u else u
                best[other] = min(best[other], t)
                dfs(other, t)

    dfs(source, -1)
    return best


def test_earliest_arrival_equals_breadth_first_search_on_the_time_expanded_graph():
    checked = 0
    for rng, n, cs, tmax in _cases(300, 11):
        a = A.arrival_matrix(n, cs)
        for s in range(n):
            assert a[s].tolist() == _expanded_graph_arrival(n, cs, tmax, s), (n, cs, s)
        checked += 1
    assert checked == 300


def test_earliest_arrival_equals_the_enumeration_of_all_time_respecting_paths():
    for rng, n, cs, tmax in _cases(200, 12, max_n=6, max_contacts=9):
        a = A.arrival_matrix(n, cs)
        for s in range(n):
            assert a[s].tolist() == _enumerated_arrival(n, cs, s), (n, cs, s)


def test_time_reversal_transposes_the_reachability():
    for rng, n, cs, tmax in _cases(150, 13):
        r = A.reach_bool(A.arrival_matrix(n, cs))
        rev = sorted((tmax - 1 - t, u, v) for t, u, v in cs)
        assert (A.reach_bool(A.arrival_matrix(n, rev)) == r.T).all()


def test_aggregate_equals_networkx():
    for rng, n, cs, tmax in _cases(100, 14, max_n=12, max_contacts=20):
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from((u, v) for _, u, v in cs)
        assert sorted(tuple(sorted(e)) for e in g.edges()) == A.aggregate_edges(cs)
        expected = sum(len(c) * (len(c) - 1) for c in nx.connected_components(g)) / (n * (n - 1))
        assert A.static_reach(n, A.aggregate_edges(cs)) == pytest.approx(expected, abs=1e-12)


def test_non_transitive_fraction_equals_the_triple_loop():
    checked = 0
    for rng, n, cs, tmax in _cases(100, 15, max_n=9, max_contacts=16):
        r = A.reach_bool(A.arrival_matrix(n, cs))
        den = num = 0
        for i, j, k in itertools.permutations(range(n), 3):
            if r[i, j] and r[j, k]:
                den += 1
                num += int(not r[i, k])
        got = A.non_transitive_fraction(r)
        if den == 0:
            assert math.isnan(got)
        else:
            assert got == pytest.approx(num / den, abs=1e-12)
            checked += 1
    assert checked >= 60


def _si_enumerated(n, cs, source, beta):
    """Erwartete Endgröße als Summe über alle 2^m Münzwürfe; die Ansteckung folgt der Regel „eine Zeitmarke lang nur Kontakte von zu Beginn Angesteckten“, unabhängig von `si_exact` geschrieben."""
    m = len(cs)
    total = 0.0
    for coins in itertools.product((0, 1), repeat=m):
        k = sum(coins)
        w = beta**k * (1 - beta) ** (m - k)
        infected = {source}
        for t in sorted({c[0] for c in cs}):
            before = set(infected)
            for (tt, u, v), c in zip(cs, coins):
                if tt == t and c:
                    if u in before and v not in before:
                        infected.add(v)
                    elif v in before and u not in before:
                        infected.add(u)
        total += w * len(infected)
    return total / n


def test_si_exact_equals_the_enumeration_of_all_coin_flips():
    for rng, n, cs, tmax in _cases(80, 16, max_n=6, max_contacts=9):
        beta = float(rng.choice([0.2, 0.5, 0.9]))
        source = int(rng.integers(n))
        assert A.si_exact(n, cs, source, beta) == pytest.approx(_si_enumerated(n, cs, source, beta), abs=1e-12)


def test_si_simulation_matches_the_exact_expectation_within_the_band():
    cs = [(1, 0, 1), (1, 1, 2), (2, 2, 3), (3, 0, 3), (3, 1, 3), (4, 3, 4), (5, 0, 4), (6, 2, 4)]
    for beta in (0.3, 0.7):
        exact = A.si_exact(5, cs, 0, beta)
        runs = np.array([A.si_summary(A.si_infection_times(5, cs, 0, beta, np.random.default_rng([i, int(beta * 10)])))[0] for i in range(4000)])
        assert runs.mean() == pytest.approx(exact, abs=4.5 * runs.std() / len(runs) ** 0.5), beta


def test_an_added_contact_never_delays_an_arrival_and_never_adds_a_missing_start():
    for rng, n, cs, tmax in _cases(150, 17):
        extra = random_contacts(rng, n, 1, tmax)[0]
        bigger = sorted(cs + [extra])
        assert (A.arrival_matrix(n, bigger) <= A.arrival_matrix(n, cs)).all()


def test_infection_never_precedes_the_earliest_arrival_and_beta_one_equals_it():
    for rng, n, cs, tmax in _cases(100, 18):
        s = int(rng.integers(n))
        arr = A.earliest_arrival(n, cs, s)
        inf = A.si_infection_times(n, cs, s, float(rng.choice([0.3, 0.8])), rng)
        assert all(i >= a for i, a in zip(inf, arr))
        assert A.si_infection_times(n, cs, s, 1.0, rng) == arr


def test_temporal_reach_never_exceeds_the_static_aggregate():
    for rng, n, cs, tmax in _cases(100, 19, max_n=10, max_contacts=18):
        a = A.arrival_matrix(n, cs)
        assert A.reach_fraction(a) <= A.static_reach(n, A.aggregate_edges(cs)) + 1e-12


def test_burstiness_equals_the_loop_version():
    rng = np.random.default_rng(20)
    for _ in range(40):
        n = 6
        cs = random_contacts(rng, n, 25, 50)
        by_edge = {}
        for t, u, v in cs:
            by_edge.setdefault((u, v), []).append(t)
        gaps = [b - a for ts in by_edge.values() for a, b in zip(ts, ts[1:])]
        if not gaps:
            continue
        mu, sd = sum(gaps) / len(gaps), (sum((g - sum(gaps) / len(gaps)) ** 2 for g in gaps) / len(gaps)) ** 0.5
        got = A.burstiness(cs)
        assert (math.isnan(got) if sd + mu == 0 else got == pytest.approx((sd - mu) / (sd + mu), abs=1e-12))


def test_generated_sequences_have_k_contacts_per_edge_in_the_window_and_the_aggregate_is_the_edge_set():
    rng = np.random.default_rng(21)
    for shape in (0.15, 0.5, 1.0, 5.0):
        edges = sorted({tuple(sorted(rng.choice(30, size=2, replace=False).tolist())) for _ in range(60)})
        cs = A.contact_sequence(edges, 200, 4, shape, rng)
        assert A.aggregate_edges(cs) == edges and len(cs) == 4 * len(edges) and all(0 <= t < 200 for t, _, _ in cs)
