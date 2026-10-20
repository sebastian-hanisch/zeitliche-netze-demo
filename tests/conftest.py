"""Gemeinsame Fixtures und Hilfen (DEMO-PLAYBOOK §1b): Mini-Instanzen, an denen jede Einheit von Hand geprüft wird."""

import os
import sys
from pathlib import Path

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):    # vor dem Import von numpy (siehe ztn_algorithm.py)
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402
import pytest  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def random_contacts(rng, n, count, tmax):
    """Zufällige Kontaktfolge (t, u, v) mit u < v, Zeitmarken in 0 .. tmax - 1 (Gleichstände und Mehrfachkontakte derselben Kante kommen vor), sortiert."""
    out = []
    for _ in range(count):
        u, v = sorted(rng.choice(n, size=2, replace=False).tolist())
        out.append((int(rng.integers(tmax)), u, v))
    return sorted(out)


@pytest.fixture
def rng():
    return np.random.default_rng(7)


@pytest.fixture
def triangle():
    """Kontakte (1, 0–1), (2, 1–2), (3, 0–2): 0 erreicht 2 früh (über 1), 2 erreicht 0 nur über den dritten Kontakt."""
    return [(1, 0, 1), (2, 1, 2), (3, 0, 2)]


@pytest.fixture
def reversed_path():
    """Kontakte (1, 1–2), (2, 0–1): 0 erreicht 1, 1 erreicht 2, aber 0 erreicht 2 nicht (der Kontakt 1–2 liegt vor 0–1): Nicht-Transitivität."""
    return [(1, 1, 2), (2, 0, 1)]
