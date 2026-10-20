"""Kennzahlen, Messreihen und Verdikte der Demo „Zeitliche Netze“. Verdikte sind reine Funktionen (Art, Text); jede Zahl im Text kommt aus der Rechnung.

Modell: ein Aggregat (Netz aus Stück 1), jede Kante mit genau K Kontakten im Fenster [0, T) (Zwischenzeiten Weibull mit Form, auf das Fenster gestreckt), zeitrespektierende Wege mit streng wachsenden Zeitmarken,
SI-Ausbreitung mit Wahrscheinlichkeit β je Kontakt, Nullmodelle durch Mischen. Jede Messreihe mittelt über feste Netze (`SWEEP_SEEDS`) und Startbetriebe; jede Zelle hat ihren eigenen Zufallsstrom."""

import math
import os
from dataclasses import dataclass

# BLAS-Threads: siehe ztn_algorithm.py (muss vor dem ersten Import von numpy stehen).
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np

import ztn_algorithm as A
import ztn_constants as C
from ztn_scenario import make_instance

NAN = float("nan")


def de(x, digits=1) -> str:
    """Dezimalzahl mit Komma (deutsche Texte); eine nicht definierte Zahl erscheint als Gedankenstrich."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    s = f"{x:.{digits}f}"
    if float(s) == 0.0:
        s = s.lstrip("-")                       # „−0,00“ liest sich wie eine Zahl kleiner null
    return s.replace(".", ",").replace("-", "−")


def pct(x, digits=0) -> str:
    return de(100.0 * x, digits)


def form_txt(shape) -> str:
    """Weibull-Form als Zahl mit Komma („0,25“, „1“, „3“)."""
    return de(shape, 0 if shape == int(shape) else 2)


def _rng(*parts):
    return np.random.default_rng([int(p) for p in parts])


def _mean(values):
    v = [x for x in values if not math.isnan(x)]
    return float(np.mean(v)) if v else NAN


def _median(values):
    v = [x for x in values if not math.isnan(x)]
    return float(np.median(v)) if v else NAN


# --- Netz und Kontaktfolge ---------------------------------------------------------------------------------------------------------------------------


def build_net(raum, n, c, seed, layout=False):
    """Aggregat (Netz aus Stück 1): Instanz und Kantenliste."""
    inst = make_instance(raum, n, c, seed, layout=layout)
    return inst, A.edges_of(inst.adj)


def make_contacts(edges, k, shape, rng, null=C.N_ORIGINAL, rng_null=None):
    """Kontaktfolge mit genau k Kontakten je Kante; je nach Nullmodell mit gemischten Zeitmarken bzw. Kanten."""
    cs = A.contact_sequence(edges, C.T_WINDOW, k, shape, rng)
    if null == C.N_TIME:
        return A.shuffle_times(cs, rng_null if rng_null is not None else rng)
    if null == C.N_EDGE:
        return A.shuffle_edges(cs, rng_null if rng_null is not None else rng)
    if null != C.N_ORIGINAL:
        raise ValueError(f"unbekanntes Nullmodell: {null}")
    return cs


# --- Hauptanalyse ------------------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Settings:
    raum: str = C.T_RANDOM
    n: int = C.DEFAULT_N
    c: int = C.DEFAULT_C
    k: int = C.DEFAULT_K
    form: int = C.DEFAULT_FORM          # Weibull-Form in Hundertsteln
    beta: int = C.DEFAULT_BETA          # Übertragungswahrscheinlichkeit je Kontakt in Prozent
    null: str = C.N_ORIGINAL
    seed: int = C.DEFAULT_SEED

    @property
    def shape(self) -> float:
        return self.form / 100.0

    @property
    def p(self) -> float:
        return self.beta / 100.0


@dataclass(frozen=True, eq=False)
class Analysis:
    settings: Settings
    inst: object
    edges: list
    contacts: list          # die gezeigte Folge (nach dem Nullmodell)
    arrival: object         # Ankunftsmatrix, alle Startbetriebe
    source: int             # Startbetrieb der Anzeige
    reach: float            # mittlerer Anteil erreichter Betriebe (alle Startbetriebe)
    median: float           # Median der Ankunftszeiten
    nt: float               # Anteil nicht-transitiver Tripel
    static: float           # Anteil erreichbarer Paare im Aggregat
    burst: float            # Stoßartigkeit B der gezeigten Folge
    si_final: float         # SI: mittlere Endgröße über die Startbetriebe
    si_t50: float
    si_t90: float
    agg_final: float        # Aggregat-Rechnung (Bond-Perkolation mit p = 1 − (1 − β)^k)
    grid: list              # Zeitpunkte der Kurven
    curve_reach: list
    curve_si: list
    arr0: list              # früheste Ankunft vom Startbetrieb der Anzeige
    inf0: list              # Ansteckungszeiten des SI-Laufs vom Startbetrieb der Anzeige

    @property
    def m(self) -> int:
        return len(self.edges)


def analyse(settings: Settings) -> Analysis:
    s = settings
    inst, edges = build_net(s.raum, s.n, s.c, s.seed, layout=True)
    cs = make_contacts(edges, s.k, s.shape, _rng(s.seed, 1), s.null, _rng(s.seed, 2))
    a = A.arrival_matrix(s.n, cs)
    r = A.reach_bool(a)
    sources = _rng(s.seed, 4).permutation(s.n)[: min(C.SI_SOURCES, s.n)].tolist()
    infs = [A.si_infection_times(s.n, cs, src, s.p, _rng(s.seed, 5, i)) for i, src in enumerate(sources)]
    summ = [A.si_summary(x) for x in infs]
    pe = 1.0 - (1.0 - s.p) ** s.k
    agg = [A.aggregate_percolation(s.n, edges, pe, src, _rng(s.seed, 6, i, j)) for i, src in enumerate(sources) for j in range(C.STATIC_ROUNDS)]
    grid = np.linspace(0, C.T_WINDOW, 51).astype(int).tolist()
    return Analysis(s, inst, edges, cs, a, sources[0], A.reach_fraction(a), A.median_arrival(a), A.non_transitive_fraction(r), A.static_reach(s.n, edges), A.burstiness(cs),
                    _mean([x[0] for x in summ]), _median([x[1] for x in summ]), _median([x[2] for x in summ]), _mean(agg), grid, A.fraction_by_time(a, grid),
                    A.fraction_by_time(np.array(infs), grid), a[sources[0]].tolist(), infs[0])


def verdict_main(an: Analysis) -> tuple[str, str]:
    """Verdikt dieses Laufs: wie weit kommt die Nachricht, und wie viel überschätzt das Aggregat?"""
    s = an.settings
    if an.m == 0 or s.k == 0:
        return "info", "Das Netz hat keine Kontakte: keine Nachricht kommt an."
    gap = an.static - an.reach
    head = (f"Von einem Startbetrieb erreicht die Nachricht im Mittel {pct(an.reach)} % der anderen Betriebe; das Aggregat aller Kontakte (ohne Reihenfolge) hängt zu {pct(an.static)} % zusammen. "
            f"Der Median der Ankunftszeit liegt bei t = {de(an.median, 0)} (Fenster 0 bis {C.T_WINDOW}), {pct(an.nt)} % der Tripel „i erreicht j, j erreicht k“ sind nicht transitiv. ")
    tail = (f"SI mit β = {s.beta} % je Kontakt: Endgröße {pct(an.si_final)} % gegen {pct(an.agg_final)} % in der Aggregat-Rechnung (Kanten ohne Reihenfolge, jede mit {s.k} Kontakt{'en' if s.k != 1 else ''}).")
    gap_si = an.agg_final - an.si_final
    if gap >= 0.03:
        return "warning", head + f"Das Aggregat überschätzt die Reichweite um {pct(gap)} Prozentpunkte. " + tail
    if gap_si >= 0.1:
        return "warning", head + f"Die Reichweite stimmt mit dem Aggregat überein, die SI-Ausbreitung liegt aber {pct(gap_si)} Prozentpunkte darunter. " + tail
    return "success", head + "Aggregat und Kontaktfolge stimmen hier überein. " + tail


# --- E1: Reichweite über Kontakte je Kante und Form -----------------------------------------------------------------------------------------


def _net_seeds(nets):
    return C.SWEEP_SEEDS[:nets]


def reach_rows(raum, n, c, ks=C.E1_KS, forms=C.E1_FORMS, nets=C.LIVE_NETS, sources=C.SI_SOURCES) -> list[dict]:
    """Je Kontaktzahl k und Form: mittlere Reichweite (über `nets` feste Netze und `sources` Startbetriebe), Anteil im Aggregat und Median der Ankunftszeit."""
    rows = []
    for fi, shape in enumerate(forms):
        for k in ks:
            reach, static, med = [], [], []
            for seed in _net_seeds(nets):
                _, edges = build_net(raum, n, c, seed)
                cs = A.contact_sequence(edges, C.T_WINDOW, k, shape, _rng(seed, 10, k, fi))
                src = _rng(seed, 11).permutation(n)[: min(sources, n)]
                a = A.arrival_matrix(n, cs, src)
                reach.append(A.reach_fraction(a))
                med.append(A.median_arrival(a))
                static.append(A.static_reach(n, edges))
            rows.append({"k": k, "form": shape, "reach": _mean(reach), "static": _mean(static), "median": _median(med), "nets": len(reach)})
    return rows


def reach_cell(rows, k, form):
    return next(r for r in rows if r["k"] == k and r["form"] == form)


def threshold_k(rows, form, share=0.9):
    """Kleinste Kontaktzahl, ab der die Reichweite mindestens `share` des Aggregats erreicht (None, wenn nie)."""
    for r in sorted((r for r in rows if r["form"] == form), key=lambda r: r["k"]):
        if r["reach"] >= share * r["static"]:
            return r["k"]
    return None


def verdict_reach(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E1: wie viel überschätzt das Aggregat, und wo liegt der Übergang?"""
    if not rows:
        return "warning", "Keine Läufe."
    ks = sorted({r["k"] for r in rows})
    forms = sorted({r["form"] for r in rows})
    k0 = ks[0]
    lo = reach_cell(rows, k0, 1.0) if 1.0 in forms else reach_cell(rows, k0, forms[0])
    parts = []
    for f in forms:
        kk = threshold_k(rows, f)
        parts.append(f"Form {form_txt(f)}: ab k = {kk}" if kk is not None else f"Form {form_txt(f)}: nie")
    return "info", (f"Bei {k0} Kontakt{'en' if k0 != 1 else ''} je Kante erreicht ein Startbetrieb im Mittel {pct(lo['reach'])} % der anderen (Form {form_txt(lo['form'])}), obwohl das Aggregat zu {pct(lo['static'])} % zusammenhängt. "
                    f"Mindestens 90 % des Aggregats werden erreicht: " + "; ".join(parts) + ".")


# --- E2: Nicht-Transitivität -------------------------------------------------------------------------------------------------------------------------


def transitivity_rows(raum, c, ks=C.E2_KS, forms=C.E2_FORMS, nets=C.LIVE_NETS, n=C.E2_N) -> list[dict]:
    """Je Kontaktzahl und Form (Netze mit n Betrieben, alle Betriebe als Start): Anteil nicht-transitiver Tripel und Reichweite."""
    rows = []
    for fi, shape in enumerate(forms):
        for k in ks:
            nt, reach = [], []
            for seed in _net_seeds(nets):
                _, edges = build_net(raum, n, c, seed)
                cs = A.contact_sequence(edges, C.T_WINDOW, k, shape, _rng(seed, 20, k, fi))
                a = A.arrival_matrix(n, cs)
                nt.append(A.non_transitive_fraction(A.reach_bool(a)))
                reach.append(A.reach_fraction(a))
            rows.append({"k": k, "form": shape, "nt": _mean(nt), "reach": _mean(reach), "nets": len(nt), "n": n})
    return rows


def transitivity_cell(rows, k, form):
    return next(r for r in rows if r["k"] == k and r["form"] == form)


def verdict_transitivity(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E2: wie oft ist die Erreichbarkeit nicht transitiv, und was ändert Stoßartigkeit?"""
    if not rows:
        return "warning", "Keine Läufe."
    ks = sorted({r["k"] for r in rows})
    forms = sorted({r["form"] for r in rows})
    hi = max(rows, key=lambda r: (r["nt"] if not math.isnan(r["nt"]) else -1.0))
    lo = min(rows, key=lambda r: (r["nt"] if not math.isnan(r["nt"]) else 2.0))
    text = (f"Zwischen {pct(lo['nt'], 1)} % (k = {lo['k']}, Form {form_txt(lo['form'])}) und {pct(hi['nt'], 1)} % (k = {hi['k']}, Form {form_txt(hi['form'])}) der Tripel „i erreicht j, j erreicht k“ haben kein i → k.")
    if len(forms) > 1:
        a, b = transitivity_cell(rows, ks[0], forms[0]), transitivity_cell(rows, ks[0], forms[-1])
        text += f" Bei k = {ks[0]} liegt der Anteil bei Form {form_txt(forms[0])} bei {pct(a['nt'], 1)} %, bei Form {form_txt(forms[-1])} bei {pct(b['nt'], 1)} %."
    return "info", text


# --- E3: Nullmodelle ----------------------------------------------------------------------------------------------------------------------------------


def null_rows(raum, n, c, k, forms=C.E3_FORMS, nets=C.LIVE_NETS, sources=C.SI_SOURCES) -> list[dict]:
    """Je Form und Nullmodell (Original, Zeitmarken gemischt, Kanten gemischt): Reichweite und Median der Ankunftszeit."""
    rows = []
    for fi, shape in enumerate(forms):
        for ni, null in enumerate(C.NULLS):
            reach, med = [], []
            for seed in _net_seeds(nets):
                _, edges = build_net(raum, n, c, seed)
                cs = make_contacts(edges, k, shape, _rng(seed, 30, k, fi), null, _rng(seed, 31, fi, ni))
                src = _rng(seed, 32).permutation(n)[: min(sources, n)]
                a = A.arrival_matrix(n, cs, src)
                reach.append(A.reach_fraction(a))
                med.append(A.median_arrival(a))
            rows.append({"form": shape, "null": null, "reach": _mean(reach), "median": _median(med), "k": k, "nets": len(reach)})
    return rows


def null_cell(rows, form, null):
    return next(r for r in rows if r["form"] == form and r["null"] == null)


def verdict_nulls(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E3: wie viel der Stoßartigkeit steckt in der Zuordnung von Kante und Zeit?"""
    if not rows:
        return "warning", "Keine Läufe."
    forms = sorted({r["form"] for r in rows})
    f = forms[0]
    o, t, e = null_cell(rows, f, C.N_ORIGINAL), null_cell(rows, f, C.N_TIME), null_cell(rows, f, C.N_EDGE)
    return "info", (f"Bei Form {form_txt(f)} und k = {o['k']}: Reichweite {pct(o['reach'])} % im Original, {pct(t['reach'])} % mit gemischten Zeitmarken und {pct(e['reach'])} % mit gemischten Kanten; "
                    f"Median der Ankunftszeit {de(o['median'], 0)} im Original, {de(t['median'], 0)} bzw. {de(e['median'], 0)} nach dem Mischen.")


# --- E4: SI gegen Aggregat ------------------------------------------------------------------------------------------------------------------------------


def spread_rows(raum, n, c, k, beta, forms=C.E4_FORMS, nets=C.LIVE_NETS, sources=C.SI_SOURCES) -> list[dict]:
    """Je Form: SI-Endgröße auf der Kontaktfolge und mit gemischten Zeitmarken, T50 (Median), und die Aggregat-Rechnung (Bond-Perkolation mit p = 1 − (1 − β)^k, ohne Reihenfolge)."""
    pe = 1.0 - (1.0 - beta) ** k
    rows = []
    for fi, shape in enumerate(forms):
        fin, fin_sh, t50, agg = [], [], [], []
        for seed in _net_seeds(nets):
            _, edges = build_net(raum, n, c, seed)
            cs = A.contact_sequence(edges, C.T_WINDOW, k, shape, _rng(seed, 40, k, fi))
            sh = A.shuffle_times(cs, _rng(seed, 41, fi))
            src = _rng(seed, 42).permutation(n)[: min(sources, n)].tolist()
            for i, s in enumerate(src):
                f1, a50, _ = A.si_summary(A.si_infection_times(n, cs, s, beta, _rng(seed, 43, fi, i)))
                f2 = A.si_summary(A.si_infection_times(n, sh, s, beta, _rng(seed, 44, fi, i)))[0]
                fin.append(f1)
                fin_sh.append(f2)
                t50.append(a50)
                agg.append(A.aggregate_percolation(n, edges, pe, s, _rng(seed, 45, fi, i)))
        rows.append({"form": shape, "si": _mean(fin), "si_shuffled": _mean(fin_sh), "t50": _median(t50), "aggregate": _mean(agg), "unreached": float(np.mean([math.isnan(x) for x in t50])), "k": k, "beta": beta, "nets": len(_net_seeds(nets))})
    return rows


def spread_cell(rows, form):
    return next(r for r in rows if r["form"] == form)


def verdict_spread(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E4: wie viel überschätzt die Aggregat-Rechnung die SI-Endgröße, und wie hängt sie an der Form?"""
    if not rows:
        return "warning", "Keine Läufe."
    forms = sorted({r["form"] for r in rows})
    lo, hi = spread_cell(rows, forms[0]), spread_cell(rows, forms[-1])
    mono = all(spread_cell(rows, a)["si"] <= spread_cell(rows, b)["si"] + 1e-9 for a, b in zip(forms, forms[1:]))
    aggs = [r["aggregate"] for r in rows]
    agg_txt = f"{pct(min(aggs))} %" if pct(min(aggs)) == pct(max(aggs)) else f"{pct(min(aggs))} % bis {pct(max(aggs))} %"
    return "info", (f"Bei β = {pct(lo['beta'])} % und k = {lo['k']} sagt die Aggregat-Rechnung {agg_txt} Endgröße voraus; die SI-Ausbreitung auf der Kontaktfolge erreicht "
                    f"{pct(lo['si'])} % (Form {form_txt(lo['form'])}) bis {pct(hi['si'])} % (Form {form_txt(hi['form'])}). Die Endgröße " + ("steigt mit der Form." if mono else "ist in der Form nicht monoton."))


# --- E5: exakt auf kleinen Folgen ----------------------------------------------------------------------------------------------------------------------


def exact_rows(instances=C.EXACT_INSTANCES, betas=C.EXACT_BETAS, n=C.EXACT_N, contacts=C.EXACT_CONTACTS, sim_runs=C.EXACT_SIM_RUNS) -> list[dict]:
    """Zufällige kleine Kontaktfolgen (n Betriebe, `contacts` Kontakte, Zeitmarken 0 bis 5, Gleichstände möglich): exakte erwartete SI-Endgröße gegen die Simulation (Mittel und Standardfehler über `sim_runs` Läufe)."""
    rows = []
    for inst in range(instances):
        rng = _rng(50, inst)
        cs = []
        while len(cs) < contacts:
            u, v = sorted(rng.choice(n, size=2, replace=False).tolist())
            cs.append((int(rng.integers(6)), u, v))
        cs.sort()
        for bi, beta in enumerate(betas):
            exact = A.si_exact(n, cs, 0, beta)
            runs = np.array([A.si_summary(A.si_infection_times(n, cs, 0, beta, _rng(51, inst, bi, i)))[0] for i in range(sim_runs)])
            rows.append({"instance": inst + 1, "beta": beta, "contacts": len(cs), "times": len({c[0] for c in cs}), "exact": exact, "sim": float(runs.mean()), "se": float(runs.std() / math.sqrt(sim_runs))})
    return rows


def verdict_exact(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E5: stimmt die Simulation mit der exakten Erwartung überein?"""
    if not rows:
        return "warning", "Keine Rechnung."
    worst = max(abs(r["sim"] - r["exact"]) / r["se"] if r["se"] > 0 else 0.0 for r in rows)
    return "info", (f"Auf {len(rows)} Fällen (zufällige Folgen mit 8 Betrieben und {rows[0]['contacts']} Kontakten) weicht die Simulation höchstens um {de(worst, 1)} Standardfehler von der exakten erwarteten Endgröße ab.")
