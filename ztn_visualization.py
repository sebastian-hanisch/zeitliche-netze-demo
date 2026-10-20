"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import numpy as np
import plotly.graph_objects as go
from plotly.colors import sample_colorscale

import ztn_algorithm as A
import ztn_constants as C
from ztn_evaluation import form_txt, pct

MAX_EDGES = 3000          # größere Netze werden ohne Kanten gezeichnet
BAND_EDGES = 30           # so viele Kanten zeigt das Kontaktband
ACTIVE_WINDOW = 20        # Kontakte der letzten so vielen Zeiteinheiten gelten als „gerade aktiv“
UNREACHED = "rgba(160,160,160,0.55)"


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340, bottom=10):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=bottom), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_network(an, t):
    """Aggregat zur Zeit t: Farbe = früheste Ankunft der Nachricht vom Startbetrieb (Viridis, nur Betriebe mit Ankunft bis t), grau = noch nicht erreicht; Ring = angesteckt (SI-Lauf); dicke Linien = Kontakte der
    letzten `ACTIVE_WINDOW` Zeiteinheiten; Stern = Startbetrieb."""
    pos = an.inst.pos
    n = an.settings.n
    fig = go.Figure()
    if an.m <= MAX_EDGES:
        xs, ys = [], []
        for i, j in an.edges:
            xs += [pos[i][0], pos[j][0], None]
            ys += [pos[i][1], pos[j][1], None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_EDGE, width=0.6), hoverinfo="skip", showlegend=False))
        active = {(u, v) for ct, u, v in an.contacts if t - ACTIVE_WINDOW < ct <= t}
        if active:
            ax, ay = [], []
            for i, j in sorted(active):
                ax += [pos[i][0], pos[j][0], None]
                ay += [pos[i][1], pos[j][1], None]
            fig.add_trace(go.Scatter(x=ax, y=ay, mode="lines", line=dict(color=C.COLOR_B, width=2.2), hoverinfo="skip", showlegend=False))
    arr = an.arr0
    reached = [i for i in range(n) if 0 <= arr[i] <= t]
    colors = [UNREACHED] * n
    if reached:
        cols = sample_colorscale("Viridis", [min(1.0, arr[i] / C.T_WINDOW) for i in reached])
        for i, col in zip(reached, cols):
            colors[i] = col
    size = 6 if n > 120 else 9
    hover = [f"Betrieb {i}: " + ("Startbetrieb" if arr[i] == -1 else f"Nachricht angekommen bei t = {arr[i]}" if arr[i] < A.INF else "nie erreicht") for i in range(n)]
    fig.add_trace(go.Scatter(x=[p[0] for p in pos], y=[p[1] for p in pos], mode="markers", showlegend=False, marker=dict(size=size, color=colors, line=dict(color="rgba(40,40,40,0.35)", width=0.4)),
                             hovertext=hover, hoverinfo="text"))
    inf = [i for i in range(n) if 0 <= an.inf0[i] <= t]
    if inf:
        fig.add_trace(go.Scatter(x=[pos[i][0] for i in inf], y=[pos[i][1] for i in inf], mode="markers", showlegend=False, hoverinfo="skip",
                                 marker=dict(size=size + 5, color="rgba(0,0,0,0)", line=dict(color=C.COLOR_B, width=1.6))))
    s = an.source
    fig.add_trace(go.Scatter(x=[pos[s][0]], y=[pos[s][1]], mode="markers", showlegend=False, hovertext=[f"Startbetrieb {s}"], hoverinfo="text", marker=dict(symbol="star", size=size + 8, color="#d1a43b", line=dict(color="black", width=1))))
    fig.update_xaxes(visible=False, autorange=True)
    fig.update_yaxes(visible=False, autorange=True, scaleanchor="x", scaleratio=1)
    fig.update_layout(height=470, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_curves(an, t):
    """Anteil erreichter bzw. angesteckter Betriebe über die Zeit (Mittel über Startbetriebe), dazu das Aggregat als Waagerechte; senkrechte Linie = gewählte Zeit."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=an.grid, y=[100.0 * x for x in an.curve_reach], mode="lines", name="Nachricht erreicht (zeitrespektierend)", line=dict(color=C.COLOR_A, width=3), hovertemplate="t = %{x}: %{y:.1f} %<extra></extra>"))
    fig.add_trace(go.Scatter(x=an.grid, y=[100.0 * x for x in an.curve_si], mode="lines", name="SI angesteckt", line=dict(color=C.COLOR_B, width=3, dash="dot"), hovertemplate="t = %{x}: %{y:.1f} %<extra></extra>"))
    fig.add_hline(y=100.0 * an.static, line=dict(color="rgba(120,120,120,0.9)", dash="dash", width=1.5), annotation_text="Aggregat", annotation_position="top left")
    fig.add_vline(x=t, line=dict(color="rgba(120,120,120,0.9)", width=1.5, dash="dot"))
    fig.update_xaxes(title_text="Zeit t", range=[0, C.T_WINDOW])
    fig.update_yaxes(title_text="Anteil der Betriebe", range=[0, 102], ticksuffix=" %")
    return _base(fig, height=320, bottom=60)


def build_band(an, t):
    """Kontakte von höchstens `BAND_EDGES` zufällig gewählten Kanten über die Zeit (eine Zeile je Kante): drängen sich die Punkte einer Zeile zusammen, ist die Folge stoßartig."""
    pick = sorted(np.random.default_rng([an.settings.seed, 7]).permutation(an.m)[: min(BAND_EDGES, an.m)].tolist())
    row = {an.edges[e]: k for k, e in enumerate(pick)}
    xs, ys = [], []
    for ct, u, v in an.contacts:
        k = row.get((u, v))
        if k is not None:
            xs.append(ct)
            ys.append(k)
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="markers", marker=dict(size=7, color=C.COLOR_LINE, symbol="line-ns-open", line=dict(width=1.5, color=C.COLOR_LINE)), hovertemplate="t = %{x}<extra></extra>", showlegend=False))
    fig.add_vline(x=t, line=dict(color="rgba(120,120,120,0.9)", width=1.5, dash="dot"))
    fig.update_xaxes(title_text="Zeit t", range=[0, C.T_WINDOW])
    fig.update_yaxes(title_text=f"{len(pick)} Kanten", showticklabels=False, range=[-1, len(pick)])
    return _base(fig, height=300, bottom=30)


def _forms(rows):
    return sorted({r["form"] for r in rows})


def build_reach(rows, key="reach"):
    """Reichweite (bzw. Median der Ankunftszeit mit key „median“) über die Kontaktzahl je Kante, eine Linie je Form; gestrichelt das Aggregat."""
    fig = go.Figure()
    scale = 100.0 if key == "reach" else 1.0
    for f in _forms(rows):
        mine = sorted((r for r in rows if r["form"] == f), key=lambda r: r["k"])
        fig.add_trace(go.Scatter(x=[r["k"] for r in mine], y=[scale * r[key] for r in mine], mode="lines+markers", name=f"Form {form_txt(f)}", line=dict(color=C.SHAPE_COLORS.get(f, C.COLOR_LINE), width=3),
                                 hovertemplate="k = %{x}: %{y:.1f}<extra></extra>"))
    if key == "reach":
        base = float(np.mean([r["static"] for r in rows]))
        fig.add_hline(y=100.0 * base, line=dict(color="rgba(120,120,120,0.9)", dash="dash", width=1.5), annotation_text="Aggregat", annotation_position="bottom right")
        fig.update_yaxes(title_text="Erreichter Anteil", range=[0, 102], ticksuffix=" %")
    else:
        fig.update_yaxes(title_text="Median der Ankunftszeit", rangemode="tozero")
    ks = sorted({r["k"] for r in rows})
    fig.update_xaxes(title_text="Kontakte je Kante k", tickvals=ks)
    return _base(fig, height=340, bottom=90)


def build_transitivity(rows):
    """Anteil nicht-transitiver Tripel über die Kontaktzahl je Kante, eine Linie je Form."""
    fig = go.Figure()
    for f in _forms(rows):
        mine = sorted((r for r in rows if r["form"] == f), key=lambda r: r["k"])
        fig.add_trace(go.Scatter(x=[r["k"] for r in mine], y=[100.0 * r["nt"] for r in mine], mode="lines+markers", name=f"Form {form_txt(f)}", line=dict(color=C.SHAPE_COLORS.get(f, C.COLOR_LINE), width=3),
                                 hovertemplate="k = %{x}: %{y:.1f} %<extra></extra>"))
    fig.update_xaxes(title_text="Kontakte je Kante k", tickvals=sorted({r["k"] for r in rows}))
    fig.update_yaxes(title_text="Nicht-transitive Tripel", rangemode="tozero", ticksuffix=" %")
    return _base(fig, height=320, bottom=80)


def build_nulls(rows, key="reach"):
    """Reichweite (bzw. Median der Ankunftszeit) je Form und Nullmodell als gruppierte Balken."""
    fig = go.Figure()
    scale = 100.0 if key == "reach" else 1.0
    forms = _forms(rows)
    for null in C.NULLS:
        mine = [next(r for r in rows if r["form"] == f and r["null"] == null) for f in forms]
        fig.add_trace(go.Bar(x=[f"Form {form_txt(f)}" for f in forms], y=[scale * r[key] for r in mine], name=null, marker_color=C.NULL_COLORS[null],
                             text=[(f"{pct(r[key])} %" if key == "reach" else f"{r[key]:.0f}") for r in mine], textposition="outside"))
    fig.update_layout(barmode="group")
    if key == "reach":
        fig.update_yaxes(title_text="Erreichter Anteil", range=[0, 112], ticksuffix=" %")
    else:
        fig.update_yaxes(title_text="Median der Ankunftszeit", rangemode="tozero")
    return _base(fig, height=340, bottom=90)


def build_spread(rows):
    """SI-Endgröße auf der Kontaktfolge, mit gemischten Zeitmarken und die Aggregat-Rechnung je Form."""
    fig = go.Figure()
    forms = _forms(rows)
    for key, name, color in (("si", "SI auf der Kontaktfolge", C.COLOR_A), ("si_shuffled", "SI, Zeitmarken gemischt", C.COLOR_B), ("aggregate", "Aggregat-Rechnung (ohne Reihenfolge)", "#9d9d9d")):
        fig.add_trace(go.Bar(x=[f"Form {form_txt(f)}" for f in forms], y=[100.0 * next(r for r in rows if r["form"] == f)[key] for f in forms], name=name, marker_color=color,
                             text=[f"{pct(next(r for r in rows if r['form'] == f)[key])} %" for f in forms], textposition="outside"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Endgröße", range=[0, 112], ticksuffix=" %")
    return _base(fig, height=340, bottom=90)


def build_exact(rows):
    """Simulation gegen exakte erwartete Endgröße (mit Standardfehler); die Punkte liegen auf der Diagonalen."""
    fig = go.Figure()
    hi = max(max(r["exact"], r["sim"]) for r in rows) * 1.1
    fig.add_trace(go.Scatter(x=[0, hi], y=[0, hi], mode="lines", line=dict(color="rgba(120,120,120,0.9)", dash="dash", width=1.5), name="Simulation = exakt", hoverinfo="skip"))
    for beta, color in zip(sorted({r["beta"] for r in rows}), (C.COLOR_A, C.COLOR_B, C.COLOR_C)):
        mine = [r for r in rows if r["beta"] == beta]
        fig.add_trace(go.Scatter(x=[100.0 * r["exact"] for r in mine], y=[100.0 * r["sim"] for r in mine], mode="markers", name=f"β = {pct(beta)} %", marker=dict(size=11, color=color, line=dict(width=1.5, color="white")),
                                 error_y=dict(type="data", array=[100.0 * 4.5 * r["se"] for r in mine], visible=True), hovertemplate="exakt %{x:.2f} %, Simulation %{y:.2f} %<extra></extra>"))
    fig.update_xaxes(title_text="Exakte erwartete Endgröße (%)", range=[0, 100.0 * hi])
    fig.update_yaxes(title_text="Simulation (%, Balken: ±4,5 Standardfehler)", range=[0, 100.0 * hi])
    return _base(fig, height=340, bottom=90)
