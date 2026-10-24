"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# --- Aggregat (Netze aus Stück 1) ------------------------------------------------------------------------------------------------------------------
T_RANDOM = "Zufallsnetz"
T_POWER = "Potenzgesetz-Netz"
T_BA = "Skalenfreies Netz (BA)"
T_COMMUNITIES = "Verbünde"
T_RING = "Ring mit Abkürzungen"
ALL_TYPES = (T_RANDOM, T_POWER, T_BA, T_COMMUNITIES, T_RING)
BLOCKS = 6

C_MEANING = {
    T_RANDOM: "mittlerer Grad des Zufallsnetzes",
    T_POWER: "mittlerer Grad (Gradfolge mit Potenzgesetz-Exponent 2,5, Konfigurationsmodell)",
    T_BA: "zwei Kanten je neuem Knoten, also m = c / 2 gerundet (jeder Knoten hat mindestens m Nachbarn)",
    T_COMMUNITIES: "mittlerer Grad; 80 % der Kanten bleiben im eigenen Verbund (6 Verbünde, die Gewerbeparks)",
    T_RING: "Nachbarn auf dem Ring (c gerade gerundet), dazu Abkürzungen mit 5 % je Ringkante",
}

N_MIN, N_MAX, DEFAULT_N = 60, 300, 200             # Betriebe
C_MIN, C_MAX, DEFAULT_C = 3, 10, 4                 # mittlerer Grad des Aggregats
K_MIN, K_MAX, DEFAULT_K = 1, 12, 2                 # Kontakte je Kante im Zeitfenster
FORM_MIN, FORM_MAX, DEFAULT_FORM = 15, 500, 100    # Weibull-Form der Zwischenzeiten in Hundertsteln (100 = Poisson-artig)
BETA_MIN, BETA_MAX, DEFAULT_BETA = 5, 100, 30      # Übertragungswahrscheinlichkeit je Kontakt in Prozent
SEED_MAX, DEFAULT_SEED = 999999, 35
T_WINDOW = 1000                                    # Zeitfenster [0, T): ganzzahlige Zeitmarken
SI_SOURCES = 20                                    # Startbetriebe für die Mittel von Reichweite und SI
LIVE_NETS = 5                                      # Netze je Zelle in der App (die README-Zahlen nutzen alle zwölf)
SWEEP_SEEDS = tuple(range(100000, 100012))         # feste Netze für alle Messreihen

# --- Nullmodelle ----------------------------------------------------------------------------------------------------------------------------------------
N_ORIGINAL, N_TIME, N_EDGE = "Original", "Zeitmarken gemischt", "Kanten gemischt"
NULLS = (N_ORIGINAL, N_TIME, N_EDGE)
NULL_HELP = {
    N_ORIGINAL: "Die Kontaktfolge, wie sie erzeugt wurde.",
    N_TIME: "Die Zeitmarken werden zufällig auf die Kontakte verteilt: Aggregat und Zahl der Kontakte bleiben, die Zuordnung von Kante und Zeit geht verloren.",
    N_EDGE: "Die Kanten werden zufällig auf die Zeitmarken verteilt: die Zeitmarken bleiben, welche Kante wann Kontakt hat, geht verloren.",
}

# --- Messreihen ------------------------------------------------------------------------------------------------------------------------------------------
E1_KS = (1, 2, 3, 4, 6, 8, 12)
E1_FORMS = (0.25, 0.5, 1.0, 3.0)
E2_KS = (2, 3, 4, 6)
E2_FORMS = (0.25, 1.0)
E2_N = 100                                         # Betriebe in Experiment 2 (alle Betriebe als Startbetrieb)
E3_FORMS = (0.25, 1.0)
E4_FORMS = (0.25, 0.5, 1.0, 3.0)
EXACT_N = 8                                        # Betriebe in Experiment 5 (exakte Rechnung über alle Mengen Angesteckter)
EXACT_CONTACTS = 12
EXACT_INSTANCES = 4
EXACT_BETAS = (0.3, 0.6)
EXACT_SIM_RUNS = 4000
STATIC_ROUNDS = 5                                  # Stichproben der Aggregat-Perkolation je Startbetrieb

# --- Darstellung ---------------------------------------------------------------------------------------------------------------------------------------
COLOR_EDGE = "rgba(120,120,120,0.30)"
COLOR_A = "#2F6B65"
COLOR_B = "#c4623b"
COLOR_C = "#6b5b95"
COLOR_LINE = "#4c78a8"
NULL_COLORS = {N_ORIGINAL: "#2F6B65", N_TIME: "#c4623b", N_EDGE: "#6b5b95"}
SHAPE_COLORS = {0.25: "#c4623b", 0.5: "#9d755d", 1.0: "#2F6B65", 3.0: "#4c78a8"}

_D = {"raum": T_RANDOM, "n": DEFAULT_N, "c": DEFAULT_C, "k": DEFAULT_K, "form": DEFAULT_FORM, "beta": DEFAULT_BETA, "null": N_ORIGINAL, "seed": DEFAULT_SEED}
PRESETS = {
    "Zwei Kontakte je Kante: das Aggregat täuscht (Voreinstellung)": dict(_D),
    "Ein Kontakt je Kante: nur jeder Fünfte erreichbar": {**_D, "k": 1},
    "Sechs Kontakte je Kante: fast alle erreicht": {**_D, "k": 6},
    "Stoßartig: erreichbar, aber langsam": {**_D, "c": 6, "k": 8, "form": 15},
    "Zeitmarken gemischt: viel schneller": {**_D, "c": 6, "k": 8, "form": 15, "null": N_TIME},
    "Verbünde": {**_D, "raum": T_COMMUNITIES, "c": 6, "k": 3},
}
PRESET_HELP = {
    "Zwei Kontakte je Kante: das Aggregat täuscht (Voreinstellung)": "Jede Verbindung hat im Fenster nur zwei Kontakte: das Aggregat ist fast ganz zusammenhängend, die Nachricht erreicht aber deutlich weniger Betriebe.",
    "Ein Kontakt je Kante: nur jeder Fünfte erreichbar": "Bei einem Kontakt je Verbindung zählt nur die Reihenfolge der Zeitmarken: das Aggregat täuscht am stärksten.",
    "Sechs Kontakte je Kante: fast alle erreicht": "Mit sechs Kontakten je Verbindung kommt die Nachricht fast überall an; bei der Reichweite liegen Aggregat und Kontaktfolge nah beieinander, die SI-Endgröße bleibt aber weit darunter.",
    "Stoßartig: erreichbar, aber langsam": "Die Kontakte einer Verbindung drängen sich zusammen (Form 0,15): fast alle sind erreichbar (97,9 %), und der Median der Ankunftszeit liegt bei Form 0,15 rund ein Drittel über dem Poisson-artigen Fall (198 gegen 147).",
    "Zeitmarken gemischt: viel schneller": "Dieselben Kontakte mit zufällig vertauschten Zeitmarken: die Nachricht kommt viel früher an (Median 11 statt 198); die Stoßartigkeit je Verbindung sinkt (B 0,24 statt 0,41), die ungleichmäßige Verteilung der Zeitmarken über das Fenster bleibt.",
    "Verbünde": "Das Aggregat hat sechs Gewerbeparks mit wenigen Verbindungen dazwischen: die Nachricht muss die Brücken zur richtigen Zeit finden.",
}
DEFAULT_PRESET_NAME = "Zwei Kontakte je Kante: das Aggregat täuscht (Voreinstellung)"
