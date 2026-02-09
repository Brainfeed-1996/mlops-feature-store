from __future__ import annotations

import numpy as np


def psi(a: np.ndarray, b: np.ndarray, bins: int = 10) -> float:
    """Coarse population stability index-like score.

    Notes:
      - bins based on quantiles of a (reference)
      - clipped probabilities
    """

    a = np.asarray(a)
    b = np.asarray(b)
    if a.size == 0 or b.size == 0:
        return 0.0

    qs = np.quantile(a, np.linspace(0, 1, bins + 1))
    qs[0] -= 1e-9
    qs[-1] += 1e-9

    pa, _ = np.histogram(a, bins=qs)
    pb, _ = np.histogram(b, bins=qs)

    pa = pa / max(1, pa.sum())
    pb = pb / max(1, pb.sum())

    pa = np.clip(pa, 1e-6, 1)
    pb = np.clip(pb, 1e-6, 1)
    return float(np.sum((pb - pa) * np.log(pb / pa)))
