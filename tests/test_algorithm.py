"""Einheiten des Kerns an Mini-Instanzen mit von Hand gerechneten Werten (DEMO-PLAYBOOK §1b)."""

import math

import numpy as np
import pytest

import ztn_algorithm as A

INF = A.INF

# --- Kontaktfolge -------------------------------------------------------------------------------------------------------------------------------


def test_contact_sequence_has_exactly_k_sorted_integer_contacts_per_edge(rng):
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
    for shape in (0.2, 1.0, 4.0):
        cs = A.contact_sequence(edges, 100, 6, shape, rng)
        assert len(cs) == 30 and cs == sorted(cs)
        assert all(isinstance(t, int) and 0 <= t < 100 for t, _, _ in cs)
        for e in edges:
            assert sum(1 for _, u, v in cs if (u, v) == e) == 6


def test_contact_sequence_is_deterministic_and_shape_one_gives_uniform_times():
    edges = [(i, i + 1) for i in range(400)]
    a = A.contact_sequence(edges, 1000, 1, 1.0, np.random.default_rng(3))
    assert a == A.contact_sequence(edges, 1000, 1, 1.0, np.random.default_rng(3)) and a != A.contact_sequence(edges, 1000, 1, 1.0, np.random.default_rng(4))
    t = np.array([c[0] for c in a])
    assert t.mean() == pytest.approx(500, abs=4.5 * 288.7 / 20) and t.min() < 30 and t.max() > 970    # K = 1, Form 1: gleichverteilte Zeitmarke (σ = T / √12)


def test_small_shape_clusters_the_contacts_of_an_edge_and_burstiness_orders_the_shapes():
    edges = [(i, i + 1) for i in range(300)]
    b = {s: A.burstiness(A.contact_sequence(edges, 10000, 6, s, np.random.default_rng(5))) for s in (0.2, 0.5, 1.0, 4.0)}
    assert b[0.2] > b[0.5] > b[1.0] > b[4.0] and b[4.0] < -0.2 and b[0.2] > 0.1


def test_contact_sequence_edge_cases_and_errors(rng):
    assert A.contact_sequence([], 10, 3, 1.0, rng) == [] and A.contact_sequence([(0, 1)], 10, 0, 1.0, rng) == []
    assert A.contact_sequence([(0, 1)], 1, 3, 1.0, rng) == [(0, 0, 1)] * 3                      # Fenster der Länge 1: alle bei Zeit 0
    for args, msg in (((10, 3, 0.0), "Form"), ((10, 3, -1.0), "Form"), ((0, 3, 1.0), "Fenster"), ((10, -1, 1.0), "Fenster")):
        with pytest.raises(ValueError, match=msg):
            A.contact_sequence([(0, 1)], *args, rng)


def test_the_last_contact_of_an_edge_stays_inside_the_window():
    """Ist die letzte Zwischenzeit null, läge der letzte Kontakt genau bei T: er wird auf T − 1 zurückgesetzt."""

    class Fake:
        def random(self, shape):
            a = np.full(shape, 0.5)
            a[:, -1] = 0.0
            return a

    assert A.contact_sequence([(0, 1)], 10, 2, 1.0, Fake()) == [(5, 0, 1), (9, 0, 1)]


def test_edges_of_and_aggregate_edges():
    assert A.edges_of(((1, 2), (0,), (0, 3), (2,))) == [(0, 1), (0, 2), (2, 3)]
    assert A.aggregate_edges([(1, 0, 1), (2, 0, 1), (3, 1, 2)]) == [(0, 1), (1, 2)]


# --- Früheste Ankunft -----------------------------------------------------------------------------------------------------------------------------


def test_earliest_arrival_on_the_triangle_by_hand(triangle):
    assert A.earliest_arrival(3, triangle, 0) == [-1, 1, 2]
    assert A.earliest_arrival(3, triangle, 1) == [1, -1, 2]
    assert A.earliest_arrival(3, triangle, 2) == [3, 2, -1]                          # 2 erreicht 0 nur über den dritten Kontakt (der erste Kontakt kommt nach dem zweiten zu spät)


def test_non_transitivity_on_the_reversed_path(reversed_path):
    a = A.arrival_matrix(3, reversed_path)
    assert a.tolist() == [[-1, 2, INF], [2, -1, 1], [2, 1, -1]]
    r = A.reach_bool(a)
    assert r[0, 1] and r[1, 2] and not r[0, 2]                                         # 0 → 1 und 1 → 2, aber nicht 0 → 2
    assert A.non_transitive_fraction(r) == pytest.approx(0.25)                          # von 4 Tripeln fehlt genau eines


def test_equal_timestamps_do_not_chain_and_waiting_is_allowed():
    assert A.earliest_arrival(3, [(1, 0, 1), (1, 1, 2)], 0) == [-1, 1, INF]            # streng: derselbe Zeitpunkt reicht nicht
    assert A.earliest_arrival(3, [(1, 0, 1), (5, 1, 2)], 0) == [-1, 1, 5]              # Warten ist erlaubt
    assert A.earliest_arrival(2, [(0, 0, 1)], 0) == [-1, 0]                              # ein Kontakt bei Zeit 0 genügt (Start „zur Zeit −1“)


def test_a_path_is_reachable_in_one_direction_only():
    path = [(1, 0, 1), (2, 1, 2), (3, 2, 3)]
    assert A.earliest_arrival(4, path, 0) == [-1, 1, 2, 3] and A.earliest_arrival(4, path, 3) == [INF, INF, 3, -1]


def test_arrival_matrix_rows_equal_single_source_runs_and_no_contacts_reach_nobody():
    cs = [(1, 0, 3), (2, 1, 3), (2, 0, 1), (4, 2, 3), (6, 1, 2)]
    full = A.arrival_matrix(4, cs)
    for s in range(4):
        assert full[s].tolist() == A.earliest_arrival(4, cs, s)
    assert A.arrival_matrix(4, cs, [2, 0]).tolist() == full[[2, 0]].tolist()
    assert A.arrival_matrix(3, []).tolist() == [[-1, INF, INF], [INF, -1, INF], [INF, INF, -1]]


def test_reach_fraction_median_arrival_and_fraction_by_time_on_the_triangle(triangle):
    a = A.arrival_matrix(3, triangle)
    assert A.reach_fraction(a) == 1.0 and A.median_arrival(a) == 2.0                    # Werte 1, 2 | 1, 2 | 3, 2 → Median 2
    assert A.fraction_by_time(a, [0, 1, 2, 3]) == pytest.approx([0.0, 2 / 6, 5 / 6, 1.0])
    none = A.arrival_matrix(3, [])
    assert A.reach_fraction(none) == 0.0 and math.isnan(A.median_arrival(none))
    assert math.isnan(A.reach_fraction(A.arrival_matrix(1, [])))


def test_non_transitive_fraction_is_nan_without_triples_and_zero_for_complete_reach(triangle):
    assert math.isnan(A.non_transitive_fraction(A.reach_bool(A.arrival_matrix(3, []))))
    assert A.non_transitive_fraction(A.reach_bool(A.arrival_matrix(3, triangle))) == 0.0


def test_static_reach_counts_ordered_pairs_in_components():
    assert A.static_reach(5, [(0, 1), (1, 2), (3, 4)]) == pytest.approx(8 / 20) and A.static_reach(3, []) == 0.0 and A.static_reach(3, [(0, 1), (1, 2)]) == 1.0
    assert math.isnan(A.static_reach(1, []))


# --- Stoßartigkeit und Nullmodelle ----------------------------------------------------------------------------------------------------------


def test_burstiness_by_hand():
    assert A.burstiness([(0, 0, 1), (1, 0, 1), (3, 0, 1)]) == pytest.approx(-0.5)      # Zwischenzeiten 1 und 2: μ = 1,5, σ = 0,5
    assert A.burstiness([(0, 0, 1), (2, 0, 1), (4, 0, 1), (6, 0, 1)]) == -1.0           # regelmäßig
    assert math.isnan(A.burstiness([(0, 0, 1), (1, 1, 2)])) and math.isnan(A.burstiness([]))
    assert math.isnan(A.burstiness([(5, 0, 1), (5, 0, 1)]))                              # lauter gleiche Zeitmarken: σ + μ = 0
    assert A.burstiness([(0, 0, 1), (0, 0, 1), (2, 0, 1)]) == 0.0                         # Zwischenzeiten 0 und 2: μ = σ = 1, B = 0 (nicht „nicht definiert“)


def test_shuffle_times_keeps_edges_and_the_multiset_of_times(rng):
    cs = A.contact_sequence([(0, 1), (1, 2), (2, 3), (0, 3)], 50, 5, 0.4, rng)
    sh = A.shuffle_times(cs, np.random.default_rng(9))
    assert sorted(c[0] for c in sh) == sorted(c[0] for c in cs) and sorted((u, v) for _, u, v in sh) == sorted((u, v) for _, u, v in cs) and sh == sorted(sh) and sh != cs
    assert A.shuffle_times([], rng) == []


def test_shuffle_edges_keeps_the_times_and_the_multiset_of_edges(rng):
    cs = A.contact_sequence([(0, 1), (1, 2), (2, 3), (0, 3)], 50, 5, 0.4, rng)
    sh = A.shuffle_edges(cs, np.random.default_rng(9))
    assert [c[0] for c in sh] == [c[0] for c in cs] and sorted((u, v) for _, u, v in sh) == sorted((u, v) for _, u, v in cs) and sh != cs
    assert A.shuffle_edges([], rng) == []


# --- SI ---------------------------------------------------------------------------------------------------------------------------------------------------


def test_si_with_beta_one_equals_the_earliest_arrival_and_beta_zero_infects_only_the_source(rng):
    cs = [(1, 0, 3), (2, 1, 3), (2, 0, 1), (4, 2, 3), (6, 1, 2), (6, 0, 2)]
    for s in range(4):
        assert A.si_infection_times(4, cs, s, 1.0, rng) == A.earliest_arrival(4, cs, s)
        assert A.si_infection_times(4, cs, s, 0.0, rng).count(INF) == 3


def test_si_infection_is_strict_in_time():
    assert A.si_infection_times(3, [(1, 0, 1), (1, 1, 2)], 0, 1.0, np.random.default_rng(1)) == [-1, 1, INF]


def test_si_summary_by_hand():
    final, t50, t90 = A.si_summary([-1, 0, 2, INF])
    assert final == 0.75 and t50 == 0.0 and math.isnan(t90)
    assert A.si_summary([-1, 3, 5, 7]) == (1.0, 3.0, 7.0)
    final, t50, t90 = A.si_summary([-1, INF, INF, INF])
    assert final == 0.25 and math.isnan(t50) and math.isnan(t90)


def test_si_exact_by_hand():
    assert A.si_exact(2, [(1, 0, 1)], 0, 0.5) == pytest.approx(0.75)                     # 1 + 0,5 Betriebe von 2
    assert A.si_exact(3, [(1, 0, 1), (2, 1, 2)], 0, 0.5) == pytest.approx((1 + 0.5 + 0.25) / 3)
    assert A.si_exact(3, [(1, 0, 1), (1, 1, 2)], 0, 1.0) == pytest.approx(2 / 3)         # gleiche Zeitmarke: keine Kette
    assert A.si_exact(3, [(1, 0, 1), (1, 0, 2)], 0, 0.5) == pytest.approx((1 + 0.5 + 0.5) / 3)   # zwei Kontakte derselben Zeitmarke wirken unabhängig
    assert A.si_exact(3, [], 0, 0.5) == pytest.approx(1 / 3) and A.si_exact(3, [(1, 1, 2)], 0, 0.9) == pytest.approx(1 / 3)
    with pytest.raises(ValueError):
        A.si_exact(A.EXACT_LIMIT + 1, [], 0, 0.5)


def test_aggregate_percolation_limits(rng):
    edges = [(0, 1), (1, 2), (3, 4)]
    assert A.aggregate_percolation(5, edges, 1.0, 0, rng) == 3 / 5 and A.aggregate_percolation(5, edges, 0.0, 0, rng) == 1 / 5
    assert A.aggregate_percolation(5, edges, 1.0, 4, rng) == 2 / 5
