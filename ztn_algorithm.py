"""Kern: Kontaktfolgen, früheste Ankunft, Reichweite, Nicht-Transitivität, Stoßartigkeit, Nullmodelle, SI-Ausbreitung (Simulation und exakt) und das Aggregat als Gegenstück.

Eine Kontaktfolge ist eine nach (Zeit, Betrieb, Betrieb) sortierte Liste von Tripeln (t, u, v) mit u < v und ganzzahliger Zeitmarke t in [0, T). Ein zeitrespektierender Weg nutzt Kontakte mit
**streng wachsenden** Zeitmarken (ein Kontakt je Schritt, keine Verkettung innerhalb einer Zeitmarke); der Startbetrieb hat die Nachricht „zur Zeit −1“. Zufall nur über `numpy.random.default_rng(Seed)`."""

import math
import os

# BLAS-Threads auf 1 (muss vor dem ersten Import von numpy stehen): die dichten Matrixprodukte sind klein, die Thread-Verwaltung kostet mehr, als sie spart.
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np

INF = 1 << 60                 # „noch nicht erreicht“ in Ankunftsmatrizen
EXACT_LIMIT = 12              # größte Betriebszahl der exakten SI-Rechnung (2^n Mengen)


# --- Aggregat und Kontaktfolge -------------------------------------------------------------------------------------------------------------------------


def edges_of(adj) -> list:
    """Kantenliste (i, j) mit i < j, sortiert, aus Nachbarlisten."""
    return sorted((i, j) for i, nb in enumerate(adj) for j in nb if i < j)


def contact_sequence(edges, T, K, shape, rng) -> list:
    """K Kontakte je Kante: die K + 1 Zwischenzeiten sind Weibull-verteilt mit Form `shape` (1 = Poisson-artig, darunter stoßartig, darüber regelmäßig) und werden auf das Fenster [0, T) gestreckt;
    jede Einstellung hat also genau K Kontakte je Kante. Zeitmarken ganzzahlig (abgerundet), Folge sortiert nach (Zeit, u, v)."""
    if shape <= 0:
        raise ValueError("die Form muss positiv sein")
    if T < 1 or K < 0:
        raise ValueError("Fenster und Zahl der Kontakte müssen positiv sein")
    m = len(edges)
    if m == 0 or K == 0:
        return []
    u = rng.random((m, K + 1))
    g = (-np.log1p(-u)) ** (1.0 / shape)                                  # Weibull(Form) aus gleichverteilten Zahlen, ohne Bibliotheks-Sonderfall
    total = g.sum(axis=1, keepdims=True)
    total[total == 0.0] = 1.0                                              # nur bei lauter Nullen (u = 0): alle Kontakte bei Zeit 0
    t = np.minimum((np.cumsum(g[:, :K], axis=1) / total * T).astype(np.int64), T - 1)
    e = np.asarray(edges, dtype=np.int64)
    tt, uu, vv = t.ravel(), np.repeat(e[:, 0], K), np.repeat(e[:, 1], K)
    order = np.lexsort((vv, uu, tt))
    return list(zip(tt[order].tolist(), uu[order].tolist(), vv[order].tolist()))


def aggregate_edges(contacts) -> list:
    """Kanten des statischen Aggregats einer Kontaktfolge."""
    return sorted({(u, v) for _, u, v in contacts})


def burstiness(contacts) -> float:
    """Stoßartigkeit B = (σ − μ) / (σ + μ) der Zwischenzeiten zwischen aufeinanderfolgenden Kontakten derselben Kante (σ: Standardabweichung, μ: Mittel; alle Kanten zusammen).
    B = −1 regelmäßig, 0 Poisson-artig, nahe 1 sehr stoßartig; nicht definiert (nan) ohne zwei Kontakte einer Kante."""
    last, gaps = {}, []
    for t, u, v in contacts:
        k = (u, v)
        if k in last:
            gaps.append(t - last[k])
        last[k] = t
    if not gaps:
        return math.nan
    g = np.asarray(gaps, dtype=float)
    mu, sd = float(g.mean()), float(g.std())
    return math.nan if sd + mu == 0.0 else (sd - mu) / (sd + mu)


def shuffle_times(contacts, rng) -> list:
    """Nullmodell „Zeitmarken mischen“: die Zeitmarken werden zufällig auf die Kontakte verteilt (Kanten und Zahl der Kontakte je Kante bleiben)."""
    if not contacts:
        return []
    t = np.asarray([c[0] for c in contacts])
    perm = rng.permutation(len(contacts))
    return sorted((int(a), u, v) for a, (_, u, v) in zip(t[perm], contacts))


def shuffle_edges(contacts, rng) -> list:
    """Nullmodell „Kanten mischen“: die Kanten werden zufällig auf die Zeitmarken verteilt (die Zeitmarken bleiben)."""
    if not contacts:
        return []
    perm = rng.permutation(len(contacts))
    return sorted((c[0], contacts[j][1], contacts[j][2]) for c, j in zip(contacts, perm))


# --- Früheste Ankunft und Reichweite ---------------------------------------------------------------------------------------------------------------


def arrival_matrix(n, contacts, sources=None):
    """Früheste Ankunftszeit für jeden Startbetrieb in `sources` (Voreinstellung: alle) und jeden Betrieb in einem Durchlauf über die sortierten Kontakte: Zeile s, Spalte v; INF = nie erreicht,
    der Startbetrieb selbst hat −1. Ein Kontakt (t, u, v) trägt die Nachricht von u nach v, wenn u sie vor t hatte (Ankunft < t) und v sie noch nicht vor t."""
    src = np.arange(n) if sources is None else np.asarray(sources, dtype=np.int64)
    a = np.full((len(src), n), INF, dtype=np.int64)
    a[np.arange(len(src)), src] = -1
    for t, u, v in contacts:
        au, av = a[:, u], a[:, v]
        m1 = (au < t) & (av > t)
        m2 = (av < t) & (au > t)
        if m1.any():
            a[m1, v] = t
        if m2.any():
            a[m2, u] = t
    return a


def earliest_arrival(n, contacts, source) -> list:
    """Früheste Ankunft von einem Startbetrieb (Liste; INF = nie erreicht, Startbetrieb −1)."""
    return arrival_matrix(n, contacts, [source])[0].tolist()


def reach_fraction(a) -> float:
    """Mittlerer Anteil erreichter anderer Betriebe über die Zeilen (Startbetriebe) einer Ankunftsmatrix."""
    n = a.shape[1]
    return float(((a < INF).sum(axis=1) - 1).mean() / (n - 1)) if n > 1 else math.nan


def median_arrival(a) -> float:
    """Median der Ankunftszeiten aller erreichten (Start, Ziel)-Paare mit Ziel ≠ Start; nan, wenn keines erreicht wird."""
    vals = a[(a < INF) & (a >= 0)]
    return float(np.median(vals)) if vals.size else math.nan


def reach_bool(a):
    """Erreichbarkeitsmatrix (Zeile i erreicht Spalte j) aus der vollen Ankunftsmatrix (alle Startbetriebe), Diagonale falsch."""
    r = a < INF
    np.fill_diagonal(r, False)
    return r


def non_transitive_fraction(r) -> float:
    """Anteil der Tripel (i, j, k) mit i erreicht j, j erreicht k und k ≠ i, bei denen i das k **nicht** erreicht; nan ohne solche Tripel."""
    rf = r.astype(np.int64)
    out = rf.sum(axis=1)
    den = int((rf * (out[None, :] - rf.T)).sum())                          # Σ_{i,j} R[i,j] · (Ausgrad j ohne den Rückweg zu i)
    if den == 0:
        return math.nan
    two = rf @ rf                                                          # Zahl der j mit i → j → k
    np.fill_diagonal(two, 0)                                               # k = i gehört nicht dazu
    return (den - int((rf * two).sum())) / den


def static_reach(n, edges) -> float:
    """Anteil erreichbarer geordneter Paare im statischen Aggregat (Zusammenhangskomponenten)."""
    if n < 2:
        return math.nan
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    sizes = {}
    for x in range(n):
        sizes[find(x)] = sizes.get(find(x), 0) + 1
    return sum(s * (s - 1) for s in sizes.values()) / (n * (n - 1))


def fraction_by_time(times, grid) -> list:
    """Anteil der anderen Betriebe, die bis zu jedem Zeitpunkt der `grid` erreicht bzw. angesteckt sind (Mittel über die Zeilen der Matrix `times`: Ankunfts- oder Ansteckungszeiten, Start −1)."""
    n = times.shape[1]
    flat = np.sort(times[(times >= 0) & (times < INF)])
    rows = times.shape[0]
    return [float(np.searchsorted(flat, t, side="right") / (rows * (n - 1))) for t in grid]


# --- SI-Ausbreitung ----------------------------------------------------------------------------------------------------------------------------------


def si_infection_times(n, contacts, source, beta, rng) -> list:
    """SI auf der Kontaktfolge: jeder Kontakt überträgt unabhängig mit Wahrscheinlichkeit `beta` (eine Zufallszahl je Kontakt, in Folgenreihenfolge), wenn genau ein Ende schon vor der Zeitmarke
    angesteckt war. Rückgabe: Ansteckungszeit je Betrieb (INF = nie, Start −1)."""
    coin = rng.random(len(contacts)).tolist()
    inf = [INF] * n
    inf[source] = -1
    for (t, u, v), c in zip(contacts, coin):
        if c < beta:
            if inf[u] < t and inf[v] == INF:
                inf[v] = t
            elif inf[v] < t and inf[u] == INF:
                inf[u] = t
    return inf


def si_summary(inf) -> tuple:
    """(Endgröße als Anteil aller Betriebe, T50, T90): Zeitpunkte, zu denen die Hälfte bzw. 90 % der Betriebe angesteckt sind (nan, wenn nie erreicht)."""
    n = len(inf)
    ts = sorted(x for x in inf if x < INF)
    out = []
    for q in (0.5, 0.9):
        idx = math.ceil(q * n) - 1
        out.append(float(ts[idx]) if len(ts) > idx else math.nan)
    return len(ts) / n, out[0], out[1]


def si_exact(n, contacts, source, beta) -> float:
    """Exakte erwartete Endgröße (Anteil aller Betriebe) der SI-Ausbreitung: Verteilung über alle Mengen Angesteckter, Zeitmarke für Zeitmarke. In einer Zeitmarke zählen nur Kontakte, deren eines
    Ende zu Beginn der Zeitmarke angesteckt war und das andere nicht; ihre Zufallsentscheidungen sind unabhängig."""
    if n > EXACT_LIMIT:
        raise ValueError(f"die exakte SI-Rechnung kennt höchstens {EXACT_LIMIT} Betriebe")
    dist = {1 << source: 1.0}
    i = 0
    while i < len(contacts):
        j = i
        while j < len(contacts) and contacts[j][0] == contacts[i][0]:
            j += 1
        batch = contacts[i:j]
        new = {}
        for state, p in dist.items():
            cand = []
            for _, u, v in batch:
                su, sv = (state >> u) & 1, (state >> v) & 1
                if su != sv:
                    cand.append(v if su else u)                            # der angesteckte Betrieb wäre der andere
            if not cand:
                new[state] = new.get(state, 0.0) + p
                continue
            for mask in range(1 << len(cand)):
                prob, nxt = p, state
                for b, target in enumerate(cand):
                    if (mask >> b) & 1:
                        prob *= beta
                        nxt |= 1 << target
                    else:
                        prob *= 1.0 - beta
                if prob > 0.0:
                    new[nxt] = new.get(nxt, 0.0) + prob
        dist = new
        i = j
    return sum(p * bin(s).count("1") for s, p in dist.items()) / n


def aggregate_percolation(n, edges, p, source, rng) -> float:
    """Die Aggregat-Rechnung: jede Kante „überträgt“ unabhängig mit Wahrscheinlichkeit p (Bond-Perkolation, ohne Reihenfolge); Anteil aller Betriebe in der Komponente des Startbetriebs."""
    keep = rng.random(len(edges)) < p
    adj = [[] for _ in range(n)]
    for (u, v), k in zip(edges, keep.tolist()):
        if k:
            adj[u].append(v)
            adj[v].append(u)
    seen = {source}
    stack = [source]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) / n
