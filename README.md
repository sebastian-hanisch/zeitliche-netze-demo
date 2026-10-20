# Zeitliche Netze: die Reihenfolge der Kontakte – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-zeitliche-netze-demo.streamlit.app/)** -->

Dreizehntes und letztes Stück der **Netzwerkanalyse-Reihe** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ und fünftes des **Ausbreitungs-Arms** (Stücke 5 bis 8 und 13): in den bisherigen Stücken ist eine Verbindung fest da oder nicht; hier ist sie nur **zu bestimmten Zeitpunkten** da, und die **Reihenfolge der Kontakte** entscheidet, wer wen erreichen kann. Das Aggregat der Verbindungen kommt aus den Netzen von Stück 1 ([k-core-demo](https://github.com/sebastian-hanisch/k-core-demo)); die Ausbreitung (SI mit Wahrscheinlichkeit je Kontakt) ist das Gegenstück zur Ausbreitung auf festen Netzen in der [Kaskaden-Demo](https://sebastianhanisch-kaskaden-demo.streamlit.app/). Abgrenzung: [time-dependent-demo](https://sebastianhanisch-time-dependent-demo.streamlit.app/) (Kantenkosten hängen von der Uhrzeit ab), [raptor-demo](https://sebastianhanisch-raptor-demo.streamlit.app/) (Fahrplan) und [zeitfluss-demo](https://sebastianhanisch-zeitfluss-demo.streamlit.app/) (Fluss über die Zeit) rechnen mit Kantenkosten oder Fahrplänen; hier ist die **Kontaktfolge selbst** das Objekt und die Frage die Erreichbarkeit unter der Reihenfolge.

Zwischen Betrieben in einem Gewerbegebiet finden Kontakte statt (Telefonat, Lieferung, Begegnung am Gate). Eine Nachricht, zum Beispiel eine Störungsmeldung, darf nur über Kontakte mit **streng wachsenden Zeitmarken** weiterlaufen. Die Demo zeigt, **wie weit sie kommt, wie viel das statische Aggregat überschätzt, was stoßartige Aktivität ändert und was die Nullmodelle zeigen**. Alles sind Modellbefunde über zufällige Netze, keine echten Kontaktdaten.

## Kernfrage

**Wie weit kommt die Nachricht, und wie viel überschätzt das Aggregat?** Der Hook: in einem Zufallsnetz mit 200 Betrieben und mittlerem Grad 4 hängt das Aggregat aller Kontakte zu 96,1 % zusammen; hat jede Verbindung nur **einen** Kontakt im Fenster, erreicht ein Startbetrieb im Mittel nur 18,9 % der anderen (Mittel über 12 Netze und 20 Startbetriebe), bei zwei Kontakten 66,8 %, bei drei 88,0 %. Bei SI-Ausbreitung mit 30 % je Kontakt und vier Kontakten je Verbindung sagt die Aggregat-Rechnung (Perkolation, ohne Reihenfolge) 87,9 % Endgröße voraus, die Kontaktfolge schafft 19,7 %. **Stoßartige** Aktivität senkt die Reichweite im Übergangsbereich und verschiebt die nötige Kontaktzahl, aber es gibt **keinen scharfen Kipppunkt** in der Stoßartigkeit; die Nullmodelle (Zeitmarken oder Kanten mischen) zeigen, dass die Wirkung an der Zuordnung von Verbindung und Zeit hängt.

## Befunde und Korrekturen gegenüber dem Plan

- **Das statische Aggregat überschätzt die Reichweite massiv** (bestätigt): bei einem Kontakt je Verbindung erreicht ein Startbetrieb 15,4 bis 18,9 % der anderen (je nach Form der Zwischenzeiten; das Aggregat 96,1 %), bei zwei Kontakten 46,4 bis 78,8 %. Die Reichweite wächst mit der Kontaktzahl und liegt bei Poisson-artiger Folge (Form 1) ab k = 3 bei mindestens 90 % des Aggregats.
- **Die SI-Ausbreitung zeigt den Unterschied noch deutlicher** (bestätigt): bei β = 30 % und vier Kontakten je Verbindung erreicht die Ausbreitung auf der Kontaktfolge 13,5 % (Form 0,25) bis 24,2 % (Form 3) der Betriebe, die Aggregat-Rechnung sagt 87,9 % bis 90,6 % voraus; den Zeitpunkt, zu dem die Hälfte angesteckt ist, erreichen 0 % (Form 0,25) bis 10 % (Form 3) der Läufe im Fenster.
- **Zeitrespektierende Wege sind nicht transitiv** (bestätigt, Holme und Saramäki): zwischen 0,02 % (k = 6, Form 1) und 18,2 % (k = 2, Form 0,25) der Tripel „i erreicht j, j erreicht k“ haben kein i → k (100 Betriebe, alle als Start); der Anteil fällt mit der Kontaktzahl und ist bei stoßartiger Folge in jeder Zelle höher.
- **Bei welcher Stoßartigkeit kippt die Reichweite?** (Plan-Frage, **korrigiert**): es gibt keinen scharfen Kipppunkt in der Form. Bei zwei Kontakten je Verbindung sinkt die Reichweite stetig von 78,8 % (Form 3, regelmäßig) über 66,8 % (Form 1) und 55,1 % (Form 0,5) auf 46,4 % (Form 0,25). Was wandert, ist die **nötige Kontaktzahl**: mindestens 90 % des Aggregats werden bei Form 3 und 1 ab k = 3, bei Form 0,5 ab k = 4 und bei Form 0,25 ab k = 6 erreicht. Bei zwölf Kontakten liegen alle Formen über 95 %, der Median der Ankunftszeit ist bei stoßartiger Folge aber weiter länger (227 gegen 147). Zur Einordnung: die Stoßartigkeit *B* der Folgen (k = 6) beträgt 0,30 (Form 0,25), 0,16 (0,5), −0,08 (1) und −0,49 (3).
- **Mischen der Zeitmarken oder Kanten stellt die Reichweite wieder her** (bestätigt, Karsai u. a.): bei Form 0,25 und k = 3 steigt die Reichweite von 69,4 % im Original auf 87,9 % (Zeitmarken gemischt) bzw. 89,7 % (Kanten gemischt), der Median der Ankunftszeit sinkt von 944 auf 786 bzw. 748; bei Form 1 ändert das Mischen die Reichweite um höchstens 1,2 Prozentpunkte. Die Wirkung steckt also in der **Zuordnung von Verbindung und Zeit**, nicht in der Zahl der Kontakte (die ist in allen Varianten gleich). Im Preset „Stoßartig“ (Grad 6, acht Kontakte, Form 0,15) fällt der Median der Ankunftszeit nach dem Mischen der Zeitmarken von 198 auf 11.
- **Die SI-Endgröße steigt mit der Form, und das Mischen entfernt die Abhängigkeit:** bei Grad 4, k = 4: 13,5 / 18,1 / 19,7 / 24,2 % bei Form 0,25 / 0,5 / 1 / 3, nach dem Mischen der Zeitmarken 18,7 / 19,5 / 19,8 / 20,5 %. (Korrektur gegenüber dem Einzelplan: dort stand diese Hypothese versehentlich als widerlegt; gemessen fällt die Endgröße mit der Stoßartigkeit, in der Vormessung bei Grad 4 und 6.)
- **Welcher Netztyp überschätzt das Aggregat am stärksten?** Bei vier Kontakten je Verbindung (Form 1) erreicht eine Nachricht im Ring mit Abkürzungen nur 51,7 % (Aggregat 100 %; Vermutung, nicht gemessen: die Nachricht muss den Ring in Zeitreihenfolge durchlaufen), im skalenfreien Netz 99,6 % (Aggregat 100 %; Vermutung, nicht gemessen: Hubs verkürzen die Wege); bei einem Kontakt liegen alle fünf Typen zwischen 6,3 und 37,2 %.
- **Exakt nachgerechnet auf kleinen Folgen:** auf 8 zufälligen Folgen mit 8 Betrieben und 12 Kontakten (Zeitmarken 0 bis 5, Gleichstände möglich) stimmt die Simulation mit der exakten erwarteten Endgröße (über alle Mengen Angesteckter) auf höchstens 2,0 Standardfehler überein.
- **Wortbedeutung und Abgrenzung:** der Suchlauf im Portfolio (README-Suche nach Burstiness, zeitrespektierend, temporal network) fand keine andere Demo zu zeitlichen Netzen; „Zeit“ steckt in `time-dependent-demo`, `raptor-demo` und `zeitfluss-demo` in Kantenkosten, Fahrplänen und Flüssen.

## Modell

Aggregat: ein Netz aus Stück 1 (Zufallsnetz, Potenzgesetz-Netz, skalenfrei (BA), Verbünde, Ring mit Abkürzungen) mit *n* Betrieben und mittlerem Grad *c*. **Kontaktfolge:** jede Verbindung hat genau *K* Kontakte im Fenster [0, *T*) mit *T* = 1000 und ganzzahligen Zeitmarken; die *K* + 1 Zwischenzeiten sind Weibull-verteilt mit Form κ (κ = 1 Poisson-artig, darunter stoßartig, darüber regelmäßig, erzeugt als (−ln(1 − *u*))<sup>1/κ</sup> aus gleichverteilten Zahlen) und werden auf das Fenster gestreckt, so dass jede Einstellung dieselbe Zahl von Kontakten hat. **Zeitrespektierender Weg:** Kontakte mit **streng wachsenden** Zeitmarken (zwei Kontakte derselben Zeitmarke verketten sich nicht, ein Kontakt bei Zeit 0 genügt dem Startbetrieb, der die Nachricht „zur Zeit −1“ hat). **Früheste Ankunft** in einem Durchlauf über die sortierten Kontakte: *a*(*v*) = *t*, wenn *a*(*u*) < *t* < *a*(*v*). **SI:** jeder Kontakt überträgt unabhängig mit Wahrscheinlichkeit β, wenn genau ein Ende vor der Zeitmarke angesteckt war. **Aggregat-Rechnung:** jede Verbindung „überträgt“ mit *p* = 1 − (1 − β)<sup>*K*</sup> (Bond-Perkolation, ohne Reihenfolge). **Nullmodelle:** Zeitmarken zufällig auf die Kontakte verteilen, oder Kanten zufällig auf die Zeitmarken verteilen. **Maße:** Reichweite (mittlerer Anteil erreichter anderer Betriebe über alle Startbetriebe), Median der Ankunftszeit aller erreichten Paare, Anteil nicht-transitiver Tripel, Stoßartigkeit *B* = (σ − μ) / (σ + μ) der Zwischenzeiten, SI-Endgröße, *T*50 und *T*90.

## Methodik

| Baustein | Inhalt |
|---|---|
| **Aggregat** | Generatoren aus `k-core-demo` (Stück 1) als Kopie: Zufallsnetz, Potenzgesetz-Netz, skalenfrei (BA), Verbünde, Ring mit Abkürzungen |
| **Hauptansicht** | Netz zur Zeit *t* (Farbe: Ankunftszeit der Nachricht vom Startbetrieb, Ring: angesteckt, orange: gerade aktive Kontakte), Regler „Zeit“, Anteil erreichter und angesteckter Betriebe über die Zeit gegen das Aggregat, Kontaktband von 30 Verbindungen, Kennzahlen |
| **Experiment 1** | Reichweite und Median der Ankunftszeit über *k* = 1, 2, 3, 4, 6, 8, 12 Kontakte je Verbindung und Form κ = 0,25, 0,5, 1, 3 (Mittel über die festen Netze, 20 Startbetriebe) |
| **Experiment 2** | Anteil nicht-transitiver Tripel über *k* = 2, 3, 4, 6 und Form 0,25 und 1 (Netze mit 100 Betrieben, alle Betriebe als Start) |
| **Experiment 3** | Original, Zeitmarken gemischt, Kanten gemischt: Reichweite und Median der Ankunftszeit bei Form 0,25 und 1 |
| **Experiment 4** | SI-Endgröße auf der Kontaktfolge, mit gemischten Zeitmarken und die Aggregat-Rechnung über die Form (β = 30 %, *k* = 4) |
| **Experiment 5** | vier zufällige Folgen mit 8 Betrieben und 12 Kontakten: exakte erwartete SI-Endgröße (alle Mengen Angesteckter) gegen die Simulation mit 4000 Läufen, β = 30 % und 60 % |

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`. Messreihen: die zwölf festen Netze `SWEEP_SEEDS` je Zelle, Zufallsnetz mit 200 Betrieben und mittlerem Grad 4, Fenster 0 bis 1000, 20 Startbetriebe je Netz (Experiment 2: 100 Betriebe, alle als Start); Anteile im Mittel, Zeiten im Median. Die App rechnet dieselben Experimente mit fünf Netzen.

| Frage | Befund |
|---|---|
| **Stimmen die Bausteine?** | früheste Ankunft gegen die Breitensuche auf dem **zeitexpandierten Graphen** (300 Zufallsfolgen) und gegen die **Aufzählung aller zeitrespektierenden Wege** (200 Folgen), Zeitumkehr (*i* erreicht *j* genau dann, wenn *j* das *i* in der umgekehrten Folge erreicht), Aggregat gegen `networkx`, Nicht-Transitivität gegen die Dreifachschleife, exakte SI-Rechnung gegen die Aufzählung aller Münzwürfe, Simulation gegen die exakte Erwartung im Band, Monotonie (ein zusätzlicher Kontakt verschlechtert keine Ankunft), Ansteckung nie vor der frühesten Ankunft (`tests/test_oracle_zeitliche_netze.py`) |
| **Wie viel überschätzt das Aggregat?** | Tabellen zu Experiment 1 |
| **Wie oft ist die Erreichbarkeit nicht transitiv?** | Tabelle zu Experiment 2 |
| **Was zeigen die Nullmodelle?** | Tabelle zu Experiment 3 |
| **SI gegen Aggregat-Rechnung?** | Tabelle zu Experiment 4 |
| **Stimmt die Simulation mit der exakten SI-Rechnung?** | Tabelle zu Experiment 5 |
| **Welcher Netztyp?** | Tabelle „Netztypen“ |
| **Standardlauf (Zwei Kontakte je Kante)** | 400 Verbindungen, 800 Kontakte; Reichweite 63,8 % (Aggregat 94,1 %), Median der Ankunft 669, 13,6 % nicht transitiv, Stoßartigkeit *B* −0,16; SI-Endgröße 6,3 % gegen 61,2 % in der Aggregat-Rechnung |
| **Preset Ein Kontakt je Kante: nur jeder Fünfte erreichbar** | 400 Verbindungen, 400 Kontakte; Reichweite 19,8 % (Aggregat 94,1 %), Median der Ankunft 814, 45,0 % nicht transitiv, Stoßartigkeit *B* –; SI-Endgröße 1,4 % gegen 11,4 % in der Aggregat-Rechnung |
| **Preset Sechs Kontakte je Kante: fast alle erreicht** | 400 Verbindungen, 2400 Kontakte; Reichweite 93,6 % (Aggregat 94,1 %), Median der Ankunft 298, 0,3 % nicht transitiv, Stoßartigkeit *B* −0,06; SI-Endgröße 40,4 % gegen 92,1 % in der Aggregat-Rechnung |
| **Preset Stoßartig: erreichbar, aber langsam** | 600 Verbindungen, 4800 Kontakte; Reichweite 97,9 % (Aggregat 99,0 %), Median der Ankunft 198, 0,3 % nicht transitiv, Stoßartigkeit *B* 0,41; SI-Endgröße 80,5 % gegen 99,4 % in der Aggregat-Rechnung |
| **Preset Zeitmarken gemischt: das Tempo kehrt zurück** | 600 Verbindungen, 4800 Kontakte; Reichweite 99,0 % (Aggregat 99,0 %), Median der Ankunft 11, 0,0 % nicht transitiv, Stoßartigkeit *B* 0,23; SI-Endgröße 97,0 % gegen 99,4 % in der Aggregat-Rechnung |
| **Preset Verbünde** | 600 Verbindungen, 1800 Kontakte; Reichweite 99,1 % (Aggregat 100,0 %), Median der Ankunft 385, 0,5 % nicht transitiv, Stoßartigkeit *B* −0,12; SI-Endgröße 27,4 % gegen 95,1 % in der Aggregat-Rechnung |

**Experiment 1: Reichweite** (Anteil der anderen Betriebe, %, Mittel; Aggregat: 96,1 %):

| Form κ | k = 1 | k = 2 | k = 3 | k = 4 | k = 6 | k = 8 | k = 12 |
|---|---|---|---|---|---|---|---|
| 0,25 | 15,4 | 46,4 | 66,1 | 80,1 | 89,2 | 91,7 | 94,6 |
| 0,50 | 18,0 | 55,1 | 77,9 | 87,3 | 93,5 | 94,5 | 95,1 |
| 1 | 18,9 | 66,8 | 88,0 | 94,1 | 95,0 | 95,2 | 95,2 |
| 3 | 18,1 | 78,8 | 93,9 | 95,1 | 95,2 | 95,2 | 95,2 |

**Experiment 1: Median der Ankunftszeit** (Fenster 0 bis 1000; nur erreichte Paare, bei kleinem *k* also die früh erreichten):

| Form κ | k = 1 | k = 2 | k = 3 | k = 4 | k = 6 | k = 8 | k = 12 |
|---|---|---|---|---|---|---|---|
| 0,25 | 993,0 | 984,5 | 953,5 | 870,5 | 616,5 | 446,5 | 227,0 |
| 0,50 | 933,2 | 866,0 | 749,0 | 577,0 | 361,0 | 271,0 | 159,5 |
| 1 | 789,5 | 711,0 | 564,5 | 443,5 | 317,0 | 232,5 | 158,5 |
| 3 | 613,0 | 621,0 | 496,0 | 398,5 | 286,0 | 219,0 | 147,0 |

**Experiment 2: nicht-transitive Tripel** (%, Mittel; in Klammern die Reichweite, %):

| Form κ | k = 2 | k = 3 | k = 4 | k = 6 |
|---|---|---|---|---|
| 0,25 | 18,25 (60,5) | 9,92 (76,0) | 5,32 (85,9) | 1,55 (93,4) |
| 1 | 10,55 (74,5) | 2,47 (91,4) | 0,65 (95,4) | 0,02 (96,7) |

**Experiment 3: Nullmodelle** (*k* = 3; Reichweite in %, Median der Ankunftszeit in Klammern):

| Form κ | Original | Zeitmarken gemischt | Kanten gemischt |
|---|---|---|---|
| 0,25 | 69,4 (944) | 87,9 (786) | 89,7 (748) |
| 1 | 89,3 (558) | 90,1 (542) | 88,1 (557) |

**Experiment 4: SI gegen Aggregat-Rechnung** (β = 30 %, *k* = 4; Endgröße in %, Mittel über Netze und Startbetriebe; *T*50: Median der Zeit bis zur Hälfte, nur wo erreicht):

| Form κ | SI auf der Kontaktfolge | SI, Zeitmarken gemischt | Aggregat-Rechnung | *T*50 | Läufe ohne Hälfte (%) |
|---|---|---|---|---|---|
| 0,25 | 13,5 | 18,7 | 90,3 | – | 100,0 |
| 0,50 | 18,1 | 19,5 | 90,6 | 996,0 | 97,5 |
| 1 | 19,7 | 19,8 | 87,9 | 932,0 | 96,2 |
| 3 | 24,2 | 20,5 | 89,4 | 836,5 | 90,0 |

**Experiment 5: exakt gegen Simulation** (erwartete SI-Endgröße, Anteil aller 8 Betriebe, Start bei Betrieb 0; Simulation mit 4000 Läufen und Standardfehler):

| Folge | β (%) | Kontakte | Zeitmarken | exakt | Simulation (± Standardfehler) |
|---|---|---|---|---|---|
| 1 | 30 | 12 | 5 | 0,31448 | 0,31400 (0,00196) |
| 1 | 60 | 12 | 5 | 0,46796 | 0,46766 (0,00179) |
| 2 | 30 | 12 | 5 | 0,20000 | 0,19750 (0,00128) |
| 2 | 60 | 12 | 5 | 0,27500 | 0,27331 (0,00137) |
| 3 | 30 | 12 | 6 | 0,21125 | 0,21334 (0,00159) |
| 3 | 60 | 12 | 6 | 0,32000 | 0,31844 (0,00197) |
| 4 | 30 | 12 | 5 | 0,25250 | 0,25284 (0,00140) |
| 4 | 60 | 12 | 5 | 0,33500 | 0,33619 (0,00100) |

**Netztypen** (Form 1, 12 feste Netze, 200 Betriebe, mittlerer Grad 4; Reichweite in %, Aggregat in %, Median der Ankunftszeit):

| Netztyp | k | Reichweite | Aggregat | Median der Ankunft |
|---|---|---|---|---|
| Zufallsnetz | 1 | 18,4 | 96,1 | 789,0 |
| Zufallsnetz | 2 | 67,2 | 96,1 | 718,5 |
| Zufallsnetz | 4 | 93,5 | 96,1 | 441,5 |
| Potenzgesetz-Netz | 1 | 34,6 | 97,1 | 738,5 |
| Potenzgesetz-Netz | 2 | 73,5 | 97,1 | 605,5 |
| Potenzgesetz-Netz | 4 | 94,6 | 97,1 | 385,5 |
| Skalenfreies Netz (BA) | 1 | 37,2 | 100,0 | 759,0 |
| Skalenfreies Netz (BA) | 2 | 82,6 | 100,0 | 627,5 |
| Skalenfreies Netz (BA) | 4 | 99,6 | 100,0 | 374,5 |
| Verbünde | 1 | 16,1 | 96,5 | 768,5 |
| Verbünde | 2 | 59,7 | 96,5 | 710,5 |
| Verbünde | 4 | 94,7 | 96,5 | 465,0 |
| Ring mit Abkürzungen | 1 | 6,3 | 100,0 | 647,2 |
| Ring mit Abkürzungen | 2 | 16,6 | 100,0 | 680,5 |
| Ring mit Abkürzungen | 4 | 51,7 | 100,0 | 711,5 |

### Hypothesen des Einzelplans

|  | Hypothese | Ergebnis |
|---|---|---|
| H1 | Das statische Aggregat überschätzt Reichweite und SI-Endgröße | ✅ 96,1 % im Aggregat gegen 18,9 % / 66,8 % bei k = 1 / 2; SI 13,5 bis 24,2 % gegen 87,9 bis 90,6 % |
| H2 | Zeitrespektierende Wege sind nicht transitiv | ✅ 0,02 bis 18,2 % der Tripel je nach *k* und Form |
| H3 | Die früheste Ankunft in einem Durchlauf stimmt mit dem zeitexpandierten Graphen und der Aufzählung aller Wege überein | ✅ Orakel auf 300 bzw. 200 Zufallsfolgen mit Gleichständen und Mehrfachkontakten, dazu die Zeitumkehr |
| H4 | Stoßartigkeit senkt die Reichweite im Übergangsbereich und verschiebt den Kipppunkt in *k*; kein scharfer Kipppunkt in der Form | ⚠ Reichweite bei k = 2: 78,8 % (Form 3) bis 46,4 % (Form 0,25); 90 % des Aggregats ab k = 3 bzw. 6; stetig, kein Sprung |
| H5 | Die Verlangsamung hängt an der Zuordnung von Verbindung und Zeit (Nullmodelle) | ✅ bei Form 0,25: 69,4 % gegen 87,9 % / 89,7 %; bei Form 1 keine Wirkung |
| H6 | Die SI-Endgröße fällt mit der Stoßartigkeit | ✅ 24,2 % (Form 3) bis 13,5 % (Form 0,25); nach dem Mischen 18,7 bis 20,5 % |
| H7 | Die SI-Simulation stimmt mit der exakten Verteilung auf kleinen Folgen überein | ✅ 8 Fälle, höchstens 2,0 Standardfehler |
| H8 | Der Erzeuger mit festem *K* je Kante ist fair gegenüber stationären Prozessen | ⚠ der stationäre Erzeuger ändert bei starker Stoßartigkeit die Kontaktzahl je Kante (Vormessung: 2,96 statt 4 bei Form 0,2) und wurde deshalb verworfen; die Befunde gelten für den Erzeuger mit festem *K* |

## Ehrliche Grenzen

- **Ein Erzeuger der Zeitmarken:** gestreckte Weibull-Zwischenzeiten mit genau *K* Kontakten je Verbindung; echte Kontaktfolgen haben Tagesrhythmen, Gewichte und Abhängigkeiten zwischen Verbindungen. Die Form κ ist der einzige Regler der Stoßartigkeit (*B* wird gemessen, ist kein Regler); die Aussagen gelten für diesen Erzeuger.
- **Streng wachsende Zeitmarken, keine Übertragungsdauer:** ein Kontakt trägt die Nachricht sofort, aber nicht weiter innerhalb derselben Zeitmarke; mit Dauer oder Verkettung in einer Zeitmarke wächst die Reichweite. Die Zeitauflösung (Fenster 1000 gegen 10 000) änderte in der Vormessung die Reichweite um höchstens 0,05.
- **Gleiche Kontaktzahl für alle Verbindungen, SI mit gleicher Übertragung:** kein Genesen, keine Schwelle, gleiches β je Kontakt; die Aggregat-Rechnung ignoriert die Reihenfolge und ist damit genau die Annahme, die die Demo prüft.
- **Stichproben:** zwölf feste Netze in der README (fünf in der App), 20 Startbetriebe, ein Netztyp in den Tabellen von Experiment 1 bis 4 (die Netztypen-Tabelle zeigt alle fünf bei drei Kontaktzahlen); die Streuung ist nicht ausgewiesen. Experiment 2 rechnet mit 100 Betrieben, Experiment 5 mit 8 Betrieben (exakte Rechnung bis 12 Betriebe).
- **Modellbefund:** die Demo zeigt Verhalten im Modell, keine echten Kontaktdaten und keine Vorhersage über reale Ausbreitungen.
- **Literatur (aus dem Plan der Reihe, hier nicht neu nachgeschlagen):** Holme und Saramäki, Physics Reports 519 (2012), S. 97–125; Kempe, Kleinberg und Kumar (2002, Journalangabe ungeprüft); Pan und Saramäki, Phys. Rev. E 84, 016105 (2011); Karsai u. a., Phys. Rev. E 83, 025102(R) (2011). Zahlen aus diesen Arbeiten werden nicht übernommen.

## Verifikation

- **Kern:** Handwerte auf Mini-Instanzen (`tests/conftest.py`, `tests/test_algorithm.py`): das Dreieck (früheste Ankunft von allen drei Betrieben), der umgekehrte Pfad (Nicht-Transitivität, Anteil ¼), gleiche Zeitmarke verkettet nicht, Warten erlaubt, Pfad nur in einer Richtung, Stoßartigkeit von Hand, Nullmodelle, SI mit β = 0 und β = 1, exakte SI-Rechnung von Hand, Aggregat-Perkolation, Grenzen und Fehler.
- **Orakel:** `tests/test_oracle_zeitliche_netze.py` – siehe die Tabelle oben.
- **Netze und Läufe:** gültig in allen Ecken der Regler, deterministisch je Seed (auch über Prozesse mit verschiedenem Hash-Seed), Nullmodelle erhalten Zeitmarken bzw. Kanten (`tests/test_scenario.py`).
- **Verdikte:** jede Schwelle und jede Zahl im Text an von Hand gesetzten Werten (`tests/test_verdicts.py`), Randfälle (Regler-Ecken für alle Netztypen, alle Nullmodelle, keine Kontakte, kleine Messreihen) in `tests/test_edge_cases.py`.
- **Befunde:** jede Zahl dieser README in `tests/test_claims.py`.
- **Mutationsprüfung des Kerns** (`ztn_algorithm.py`, 125 Stellen, ohne die langsamen Aussagen-Tests in der Suite der Überlebenden): 7 Stellen sind durch wortgleiche Zeilen in Nachbar-Demos gesichert, 103 Mutanten gefangen (4 davon erst nach Ergänzung von Tests: die Meldung bei ungültigem Fenster oder ungültiger Kontaktzahl, die Begrenzung des letzten Kontakts auf das Fenster, die Stoßartigkeit genau null), 12 als äquivalent festgehalten (der Platzhalterwert für „nie erreicht“ in drei Konstanten, vier Vergleiche, die nur bei exakter Gleichheit mit einer Zufallszahl oder einer Zeitmarke abweichen und dort dasselbe ergeben, ein Wächter bei null Kontakten, die Kantenordnung, zwei Wächter bei einem einzigen Betrieb, ein Vergleich mit null in der exakten Rechnung), 3 Zeitüberschreitungen (erkannt durch Hängen, im Werkzeug bleiben sie „offen“). Zustand in `tests/mutation_state.json`.
- **Presets:** vollständig, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung, jedes Preset zeigt, wofür es benannt ist.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum, jeder Netztyp und jedes Nullmodell, Zeit-Regler, neuer Lauf, Permalink, alle fünf Experimente) und Footer-Test.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers hebt die Markierung auf (`tests/test_layout.py`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `ztn_algorithm.py` | Kern: Kontaktfolge, früheste Ankunft, Reichweite, Nicht-Transitivität, Stoßartigkeit, Nullmodelle, SI (Simulation und exakt), Aggregat-Perkolation |
| `ztn_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `ztn_evaluation.py` | Analyse, Verdikt-Logik, Messreihen über feste Netze |
| `ztn_layout.py` | Fester Kopf (Stylesheet) |
| `ztn_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `ztn_scenario.py` | Netze: Generatoren (Kopie aus `k-core-demo`), Anordnung |
| `ztn_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest, networkx (nur für die Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen und Handwerte, Orakel, Netze, Verdikte, Randfälle, Presets, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe, Befunde |

## Bewusst nicht umgesetzt

- **Kontakte mit Dauer, Übertragungszeit, Genesen (SIR) und Schwellen:** eigene Fragen; die Ausbreitung auf festen Netzen zeigen `kaskaden-demo` und die Stücke 5 bis 8.
- **Stationäre Erneuerungsprozesse und echte Kontaktdaten:** der Erzeuger mit festem *K* hält die Vergleiche fair; echte Daten sind nicht Teil der Demo.
- **Zeitliche Zentralität und Erreichbarkeit über Kantengewichte:** nicht untersucht.
- **Netze über 300 Betriebe live:** die Ankunftsmatrix ist dicht (Betriebe × Betriebe).

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
