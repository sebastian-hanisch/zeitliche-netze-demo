"""Zeitliche Netze: die Reihenfolge der Kontakte - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Dreizehntes und letztes Stück der Reihe „Netzwerkanalyse“ und fünftes des Ausbreitungs-Arms: dieselben Betriebe und dieselben Kontakte, nur in anderer zeitlicher Reihenfolge. Die Demo zeigt, wie weit eine Nachricht
kommt (zeitrespektierende Wege), wie viel das statische Aggregat überschätzt, was stoßartige Aktivität ändert und was die Nullmodelle zeigen. Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import ztn_constants as C
from ztn_evaluation import (
    Settings,
    analyse,
    de,
    exact_rows,
    form_txt,
    null_rows,
    pct,
    reach_rows,
    spread_rows,
    transitivity_rows,
    verdict_exact,
    verdict_main,
    verdict_nulls,
    verdict_reach,
    verdict_spread,
    verdict_transitivity,
)
from ztn_layout import dunkles_design, kopf_css
from ztn_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from ztn_visualization import build_band, build_curves, build_exact, build_network, build_nulls, build_reach, build_spread, build_transitivity

st.set_page_config(page_title="Zeitliche Netze – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _reach(raum, n, c):
    return reach_rows(raum, n, c)


@st.cache_data(show_spinner=False)
def _transitivity(raum, c):
    return transitivity_rows(raum, c)


@st.cache_data(show_spinner=False)
def _nulls(raum, n, c, k):
    return null_rows(raum, n, c, k)


@st.cache_data(show_spinner=False)
def _spread(raum, n, c, k, beta):
    return spread_rows(raum, n, c, k, beta)


@st.cache_data(show_spinner=False)
def _exact():
    return exact_rows()


def experiment(name, label, key, compute, show, hint):
    """Teure Zusatzansicht erst auf Klick; das Ergebnis bleibt nur für genau diese Einstellungen stehen (Session State)."""
    state_key = f"exp_{name}"
    if st.button(label, key=f"run_{name}", help=hint):
        with st.spinner("Rechne …"):
            result = compute()
        st.session_state[state_key] = (key, result)
    state = st.session_state.get(state_key)
    if state is None:
        st.caption(f"Noch nicht gerechnet. {hint}")
        return
    if state[0] != key:
        st.info("Die Einstellungen haben sich seit der letzten Rechnung geändert. Bitte neu starten.")
        return
    show(state[1])


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in ztn_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🕰️ Zeitliche Netze: die Reihenfolge der Kontakte")
st.markdown(
    """
**Dreizehntes und letztes Stück** der Reihe „Netzwerkanalyse“ und fünftes des **Ausbreitungs-Arms**: in den bisherigen Stücken ist eine Verbindung fest da oder nicht. Hier ist sie nur **zu bestimmten Zeitpunkten** da (ein Telefonat, eine Lieferung, eine Begegnung am Gate), und die **Reihenfolge der Kontakte** entscheidet, wer wen erreichen kann. Eine Nachricht (zum Beispiel eine Störungsmeldung) darf nur über Kontakte mit **streng wachsenden Zeitmarken** weiterlaufen; solche Wege sind **nicht transitiv**: erreicht Betrieb *i* den Betrieb *j* und *j* den Betrieb *k*, muss *i* den Betrieb *k* nicht erreichen.

Die Kernfrage: **Wie weit kommt die Nachricht, und wie viel überschätzt das statische Aggregat?** Der Hook: dasselbe Netz, bei dem das Aggregat aller Kontakte zu 94 % zusammenhängt, lässt eine Nachricht bei **einem** Kontakt je Verbindung nur etwa jeden fünften Betrieb erreichen; bei der SI-Ausbreitung sagt die Aggregat-Rechnung (jede Verbindung „überträgt“ mit der Wahrscheinlichkeit aus ihren Kontakten) ein Vielfaches der Endgröße voraus, die die Kontaktfolge schafft. **Stoßartige** Aktivität (Kontakte einer Verbindung drängen sich zusammen) wirkt nur im Übergangsbereich und über die Zuordnung von Verbindung und Zeit, wie die Nullmodelle zeigen. Anders als [`time-dependent-demo`](https://sebastianhanisch-time-dependent-demo.streamlit.app/) (Kantenkosten hängen von der Uhrzeit ab), [`raptor-demo`](https://sebastianhanisch-raptor-demo.streamlit.app/) (Fahrplan), [`zeitfluss-demo`](https://sebastianhanisch-zeitfluss-demo.streamlit.app/) (Fluss über die Zeit) und [`kaskaden-demo`](https://sebastianhanisch-kaskaden-demo.streamlit.app/) (SIR auf dem festen Netz) ist hier die **Kontaktfolge selbst** das Objekt. Alle Ergebnisse sind **Modellbefunde** über zufällige Netze, keine echten Kontaktdaten.

Weiter unten: fünf Experimente (**🔬**), der Abschnitt **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Ausbreitung über Kontakte", expanded=True):
    st.markdown(
        """
1. **Aggregat:** ein Netz aus Stück 1 (*n* Betriebe, mittlerer Grad *c*): wer überhaupt Kontakt haben kann.
2. **Kontaktfolge:** jede Verbindung hat genau *K* Kontakte im Fenster 0 bis 1000. Die *K* + 1 Zwischenzeiten sind Weibull-verteilt mit der **Form κ** und werden auf das Fenster gestreckt: κ = 1 ist Poisson-artig, κ < 1 **stoßartig**, κ > 1 regelmäßig.
3. **Zeitrespektierender Weg:** die Nachricht geht über einen Kontakt von *u* nach *v*, wenn *u* sie **vor** der Zeitmarke hatte; zwei Kontakte derselben Zeitmarke verketten sich nicht. Die **früheste Ankunft** aller Betriebe ergibt ein Durchlauf über die nach Zeit sortierten Kontakte.
4. **SI:** ein angesteckter Betrieb steckt beim Kontakt mit der Wahrscheinlichkeit β an (Information, keine Epidemie).
5. **Nullmodelle:** *Zeitmarken gemischt* (Zeiten zufällig auf die Kontakte verteilt) und *Kanten gemischt* (Verbindungen zufällig auf die Zeitmarken verteilt) behalten Zahl und Aggregat der Kontakte, aber nicht die Zuordnung von Verbindung und Zeit.
        """
    )
    st.markdown(
        """
| Begriff | Bedeutung hier |
|---|---|
| **Kontakt** | Tripel (Zeitmarke, Betrieb, Betrieb): zu dieser Zeit sprechen die zwei Betriebe miteinander |
| **Reichweite** | mittlerer Anteil der anderen Betriebe, die ein Startbetrieb zeitrespektierend erreicht (Mittel über alle Startbetriebe) |
| **Aggregat** | alle Verbindungen mit mindestens einem Kontakt, ohne Zeit: der Anteil erreichbarer Paare ist das, was die statische Sicht für möglich hält |
| **Nicht transitiv** | Anteil der Tripel (*i*, *j*, *k*) mit *i* erreicht *j*, *j* erreicht *k*, aber *i* erreicht *k* nicht |
| **Stoßartigkeit *B*** | (σ − μ) / (σ + μ) der Zwischenzeiten einer Verbindung: −1 regelmäßig, 0 Poisson-artig, nahe 1 sehr stoßartig |
| **Aggregat-Rechnung** | jede Verbindung „überträgt“ mit *p* = 1 − (1 − β)<sup>*K*</sup>, ohne Reihenfolge der Kontakte (Perkolation auf dem Aggregat) |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um einen Lauf zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Aggregat**")
    raum = st.selectbox("Netztyp", C.ALL_TYPES, key="raum_select", help="Welches Netz aus Stück 1 das Aggregat bildet: wer überhaupt Kontakt haben kann.")
    n = st.slider("Betriebe n", *bounds("n_slider"), key="n_slider", help="Zahl der Betriebe im Netz.")
    c = st.slider("Nachbarn je Betrieb c", *bounds("c_slider"), key="c_slider", help="Was c bedeutet, hängt vom Netztyp ab (siehe darunter).")
    st.caption(C.C_MEANING[raum])
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Bestimmt das Netz, die Zeitmarken und die Auswahl der Startbetriebe.")
    st.button("🎲 Neuer Lauf", width="stretch", on_click=randomize_seed)
    st.markdown("**Kontakte**")
    k = st.slider("Kontakte je Verbindung K", *bounds("k_slider"), key="k_slider", help="Jede Verbindung hat genau so viele Kontakte im Fenster 0 bis 1000.")
    form = st.slider("Form κ der Zwischenzeiten (in Hundertsteln)", *bounds("form_slider"), key="form_slider", help="100 = Poisson-artig (κ = 1), darunter stoßartig (Kontakte einer Verbindung drängen sich zusammen), darüber regelmäßig.")
    null = st.selectbox("Nullmodell", C.NULLS, key="null_select", help="Original oder eine gemischte Fassung derselben Kontakte.")
    st.caption(C.NULL_HELP[null])
    st.markdown("**Ausbreitung**")
    beta = st.slider("Übertragung β je Kontakt (%)", *bounds("beta_slider"), key="beta_slider", help="Wahrscheinlichkeit, dass ein Kontakt zwischen einem angesteckten und einem noch nicht angesteckten Betrieb überträgt.")

sync_query_params({"raum_select": raum, "n_slider": int(n), "c_slider": int(c), "k_slider": int(k), "form_slider": int(form), "beta_slider": int(beta), "null_select": null, "seed_input": int(seed)})

settings = Settings(raum, int(n), int(c), int(k), int(form), int(beta), null, int(seed))
with st.spinner("Rechne die Kontaktfolge …"):
    an = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Wie weit kommt die Nachricht?")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Reichweite", f"{pct(an.reach)} %", help="Mittlerer Anteil der anderen Betriebe, den ein Startbetrieb zeitrespektierend erreicht (Mittel über alle Startbetriebe).")
m2.metric("Aggregat", f"{pct(an.static)} %", help="Anteil erreichbarer Paare im Aggregat aller Kontakte, ohne Zeit.")
m3.metric("Ankunft (Median)", de(an.median, 0), help=f"Median der Ankunftszeit aller erreichten Paare (Fenster 0 bis {C.T_WINDOW}).")
m4.metric("Nicht transitiv", f"{pct(an.nt, 1)} %", help="Anteil der Tripel „i erreicht j, j erreicht k“, bei denen i das k nicht erreicht.")
m5.metric("SI-Endgröße", f"{pct(an.si_final)} %", help=f"Mittlere Endgröße der SI-Ausbreitung über {C.SI_SOURCES} Startbetriebe; die Aggregat-Rechnung nimmt jede Verbindung als unabhängig übertragend mit p = 1 − (1 − β)^K.")
st.caption(f"**Stoßartigkeit** der gezeigten Folge: B = {de(an.burst, 2)} (−1 regelmäßig, 0 Poisson-artig, nahe 1 stoßartig); {len(an.contacts)} Kontakte auf {an.m} Verbindungen. **SI-Endgröße in der Aggregat-Rechnung:** {pct(an.agg_final)} %.")
t = st.select_slider("Zeit t", options=an.grid, value=an.grid[len(an.grid) // 2], key="t_" + "_".join(str(v) for v in (raum, n, c, k, form, beta, null, seed)), help="Zeigt, welche Betriebe die Nachricht bis zu diesem Zeitpunkt erreicht hat.")
st.markdown(f"**Das Netz zur Zeit t = {t}** (Farbe: Ankunftszeit der Nachricht vom Startbetrieb ★; grau: noch nicht erreicht; Ring: angesteckt; orange Linien: Kontakte der letzten 20 Zeiteinheiten)")
if an.m > 3000:
    st.caption("Das Netz hat zu viele Kanten für die Zeichnung; sie werden weggelassen.")
st.plotly_chart(build_network(an, t), width="stretch", key="net_chart")
st.markdown("**Anteil erreichter und angesteckter Betriebe über die Zeit** (Mittel über Startbetriebe; gestrichelt: was das Aggregat für möglich hält)")
st.plotly_chart(build_curves(an, t), width="stretch", key="curves_chart")
st.markdown("**Kontakte von 30 Verbindungen** (eine Zeile je Verbindung)")
st.plotly_chart(build_band(an, t), width="stretch", key="band_chart")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie weit kommt die Nachricht, und wie viel überschätzt das Aggregat?")
kind, text = verdict_main(an)
getattr(st, kind)(text)
st.caption("Ein einzelnes Netz ist ein Beispiel; die Experimente rechnen über feste Netze.")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

n_e, c_e, k_e, beta_e = settings.n, settings.c, settings.k, settings.p
st.subheader("🔬 Experiment 1: Reichweite über die Zahl der Kontakte")
st.caption(f"Netztyp „{raum}“ mit n = {n_e}, c = {c_e}; Kontakte je Verbindung k = {', '.join(str(x) for x in C.E1_KS)}, Form κ = {', '.join(form_txt(f) for f in C.E1_FORMS)}. Mittel über {C.LIVE_NETS} feste Netze und {C.SI_SOURCES} Startbetriebe; gestrichelt: der Anteil im Aggregat.")


def show_reach(rows):
    st.markdown("**Erreichter Anteil**")
    st.plotly_chart(build_reach(rows, "reach"), width="stretch", key="reach_chart")
    st.markdown("**Median der Ankunftszeit**")
    st.plotly_chart(build_reach(rows, "median"), width="stretch", key="median_chart")
    kind_, text_ = verdict_reach(rows)
    getattr(st, kind_)(text_)


experiment("reach", "Reichweite messen", (raum, n_e, c_e), lambda: _reach(raum, n_e, c_e), show_reach, "Rechnet 7 Kontaktzahlen bei 4 Formen mit je 5 Netzen, einige Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 2: Nicht-Transitivität")
st.caption(f"Netze mit {C.E2_N} Betrieben (alle Betriebe als Startbetrieb), c = {c_e}, Kontakte je Verbindung k = {', '.join(str(x) for x in C.E2_KS)}, Form κ = {', '.join(form_txt(f) for f in C.E2_FORMS)}: Anteil der Tripel „i erreicht j, j erreicht k“, bei denen i das k nicht erreicht. Mittel über {C.LIVE_NETS} feste Netze.")


def show_transitivity(rows):
    st.plotly_chart(build_transitivity(rows), width="stretch", key="trans_chart")
    kind_, text_ = verdict_transitivity(rows)
    getattr(st, kind_)(text_)


experiment("trans", "Tripel zählen", (raum, c_e), lambda: _transitivity(raum, c_e), show_transitivity, "Rechnet 8 Zellen mit je 5 Netzen und allen Startbetrieben, wenige Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 3: Nullmodelle")
st.caption(f"Netztyp „{raum}“ mit n = {n_e}, c = {c_e}, k = {k_e}: Original, Zeitmarken gemischt, Kanten gemischt, bei Form κ = {', '.join(form_txt(f) for f in C.E3_FORMS)}. Mittel über {C.LIVE_NETS} feste Netze und {C.SI_SOURCES} Startbetriebe.")


def show_nulls(rows):
    st.markdown("**Erreichter Anteil**")
    st.plotly_chart(build_nulls(rows, "reach"), width="stretch", key="null_reach_chart")
    st.markdown("**Median der Ankunftszeit**")
    st.plotly_chart(build_nulls(rows, "median"), width="stretch", key="null_median_chart")
    kind_, text_ = verdict_nulls(rows)
    getattr(st, kind_)(text_)


experiment("nulls", "Nullmodelle messen", (raum, n_e, c_e, k_e), lambda: _nulls(raum, n_e, c_e, k_e), show_nulls, "Rechnet 2 Formen mit 3 Nullmodellen und je 5 Netzen, einige Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 4: SI gegen Aggregat-Rechnung")
st.caption(f"Netztyp „{raum}“ mit n = {n_e}, c = {c_e}, k = {k_e}, β = {settings.beta} %: SI-Endgröße auf der Kontaktfolge, mit gemischten Zeitmarken und die Aggregat-Rechnung (Perkolation mit p = 1 − (1 − β)^k, ohne Reihenfolge), bei Form κ = {', '.join(form_txt(f) for f in C.E4_FORMS)}. Mittel über {C.LIVE_NETS} feste Netze und {C.SI_SOURCES} Startbetriebe.")


def show_spread(rows):
    st.plotly_chart(build_spread(rows), width="stretch", key="spread_chart")
    kind_, text_ = verdict_spread(rows)
    getattr(st, kind_)(text_)


experiment("spread", "Ausbreitung messen", (raum, n_e, c_e, k_e, settings.beta), lambda: _spread(raum, n_e, c_e, k_e, beta_e), show_spread, "Rechnet 4 Formen mit je 5 Netzen und 20 Startbetrieben, einige Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 5: Exakt auf kleinen Folgen")
st.caption(f"{C.EXACT_INSTANCES} zufällige Folgen mit {C.EXACT_N} Betrieben und {C.EXACT_CONTACTS} Kontakten (Zeitmarken 0 bis 5, Gleichstände möglich), β = {', '.join(pct(b) for b in C.EXACT_BETAS)} %: die exakte erwartete SI-Endgröße über alle Mengen Angesteckter gegen die Simulation mit {C.EXACT_SIM_RUNS} Läufen.")


def show_exact(rows):
    st.plotly_chart(build_exact(rows), width="stretch", key="exact_chart")
    kind_, text_ = verdict_exact(rows)
    getattr(st, kind_)(text_)


experiment("exact", "Exakt rechnen", "fest", _exact, show_exact, f"Rechnet {C.EXACT_INSTANCES * len(C.EXACT_BETAS)} Fälle exakt und je {C.EXACT_SIM_RUNS} Läufe, wenige Sekunden.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Ein Erzeuger der Zeitmarken** | Die Zwischenzeiten sind Weibull-verteilt und auf das Fenster gestreckt, mit genau *K* Kontakten je Verbindung. Echte Kontaktfolgen haben Tagesrhythmen, Gewichte und Abhängigkeiten zwischen Verbindungen; ein stationärer Prozess ändert die Kontaktzahl und ist damit nicht vergleichbar. | – |
| **Streng wachsende Zeitmarken, keine Übertragungsdauer** | Ein Kontakt trägt die Nachricht sofort, aber nicht weiter innerhalb derselben Zeitmarke. Mit Dauer oder Verkettung in einer Zeitmarke wächst die Reichweite. | – |
| **Gleiche Kontaktzahl für alle Verbindungen** | Verbindungen haben im Modell gleich viele Kontakte; in der Wirklichkeit streut die Zahl stark (starke und schwache Bindungen). | Stück 3 (strukturelle Löcher, schwache Bindungen) |
| **SI mit gleicher Übertragung** | Kein Genesen, gleiches β je Kontakt, keine Schwelle. Andere Ansteckungsregeln und Gegenmaßnahmen ändern die Endgröße. | Stück 6 (komplexe Ansteckung), 7 (Eindämmung), `kaskaden-demo` (SIR) |
| **Zufällige Aggregate, keine echten Daten** | Die Netze sind synthetisch; die Demo zeigt Verhalten im Modell, keine Kontaktdaten. | – |
| **Aggregat-Rechnung als Gegenstück** | Die Perkolation mit p = 1 − (1 − β)^K ignoriert die Reihenfolge; sie ist kein Fehler der Rechnung, sondern genau die Annahme, die die Demo prüft. | – |
| **Stichproben** | Mittel über fünf feste Netze und 20 Startbetriebe in der App (zwölf Netze in der README); die Streuung ist nicht ausgewiesen. Experiment 2 rechnet mit 100 Betrieben. | – |
| **Modellbefund** | Alle Befunde gelten für diese Netze und Einstellungen. Ob echte Kontaktfolgen sich so verhalten, ist eine eigene empirische Frage. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Kontaktfolge und Weg.** Eine Kontaktfolge ist eine Menge $C$ von Tripeln $(u, v, t)$. Ein zeitrespektierender Weg von $s$ nach $v$ ist eine Folge von Kontakten $(v_{i-1}, v_i, t_i)$ mit $v_0 = s$, $v_\ell = v$ und

$$t_1 < t_2 < \dots < t_\ell$$

**Früheste Ankunft.** Mit $a_s(s) = -1$ und $a_s(v) = \infty$ sonst ist die früheste Ankunft

$$a_s(v) = \min \{\, t : (u, v, t) \in C,\ a_s(u) < t \,\}$$

und wird in einem Durchlauf über die nach Zeit sortierten Kontakte berechnet: für jeden Kontakt $(u, v, t)$ setzt man $a(v) = t$, wenn $a(u) < t < a(v)$ (und ebenso mit vertauschten Enden).

**Reichweite.** Mit $s \to v$ für $a_s(v) < \infty$ ist die Reichweite

$$\rho = \frac{1}{n(n-1)} \sum_{s \neq v} \mathbf{1}[\, s \to v \,]$$

**Nicht-Transitivität.** Der Anteil der Tripel, bei denen die Erreichbarkeit nicht weiterläuft, ist

$$\nu = \frac{|\{(i,j,k) : i \to j,\ j \to k,\ k \neq i,\ i \not\to k\}|}{|\{(i,j,k) : i \to j,\ j \to k,\ k \neq i\}|}$$

**Erzeuger.** Mit gleichverteilten Zahlen $u_{e,j}$ sind die Zwischenzeiten $g_{e,j} = (-\ln(1 - u_{e,j}))^{1/\kappa}$ (Weibull mit Form $\kappa$), und die $K$ Zeitmarken der Kante $e$ sind

$$t_{e,i} = \left\lfloor T \, \frac{\sum_{j \le i} g_{e,j}}{\sum_{j \le K+1} g_{e,j}} \right\rfloor, \qquad i = 1, \dots, K$$

**Stoßartigkeit.** Mit Mittel $\mu$ und Standardabweichung $\sigma$ der Zwischenzeiten einer Kante ist

$$B = \frac{\sigma - \mu}{\sigma + \mu}$$

**SI und Aggregat-Rechnung.** Jeder Kontakt überträgt unabhängig mit Wahrscheinlichkeit $\beta$, wenn genau ein Ende vor der Zeitmarke angesteckt war. Die Aggregat-Rechnung ersetzt die $K$ Kontakte einer Verbindung durch eine einzige Übertragung mit

$$p = 1 - (1 - \beta)^K$$

und rechnet die Größe der Komponente des Startbetriebs (Bond-Perkolation), ohne die Reihenfolge der Kontakte.

**Exakte SI-Rechnung.** Die Verteilung $\pi_t(S)$ über die Menge $S$ der Angesteckten wird Zeitmarke für Zeitmarke fortgeschrieben; mit den Kontakten $c_1, \dots, c_r$ der Zeitmarke, die zu Beginn genau ein angestecktes Ende haben, geht $S$ mit Wahrscheinlichkeit $\beta^{|J|}(1-\beta)^{r-|J|}$ in $S \cup \{\text{Ziele von } J\}$ über (für jede Teilmenge $J$ der Kontakte). Die erwartete Endgröße ist $\sum_S \pi(S)\,|S|\,/\,n$.

**Literatur.**
- Holme, P., Saramäki, J. (2012): *Temporal networks.* Physics Reports 519, 97–125.
- Kempe, D., Kleinberg, J., Kumar, A. (2002): *Connectivity and inference problems for temporal networks* (zeitrespektierende Wege; Journalangabe nicht geprüft).
- Pan, R. K., Saramäki, J. (2011): *Path lengths, correlations, and centrality in temporal networks.* Physical Review E 84, 016105.
- Karsai, M. u. a. (2011): *Small but slow world: How network topology and burstiness slow down spreading.* Physical Review E 83, 025102(R).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
