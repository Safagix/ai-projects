from __future__ import annotations

import math
import random


def normal_pdf(x: float, mu: float, sigma: float) -> float:
    if sigma <= 0:
        return 0.0
    coeff = 1.0 / (sigma * math.sqrt(2.0 * math.pi))
    exponent = -0.5 * ((x - mu) / sigma) ** 2
    return coeff * math.exp(exponent)


def truncated_gauss(
    mu: float,
    sigma: float,
    lo: float,
    hi: float,
    *,
    rng: random.Random | None = None,
) -> float:
    if lo >= hi:
        return lo
    if sigma <= 0:
        return mu
    r = rng or random
    for _ in range(100):
        v = r.gauss(mu, sigma)
        if lo <= v <= hi:
            return v
    return mu


def skewed_gauss(
    mu: float,
    sigma: float,
    lo: float,
    hi: float,
    *,
    skew: float = 0.0,
    rng: random.Random | None = None,
) -> float:
    r = rng or random
    for _ in range(200):
        base = r.gauss(mu, sigma)
        val = base + skew * (base - mu) ** 2
        if lo <= val <= hi:
            return val
    return truncated_gauss(mu, sigma, lo, hi, rng=r)


def uniform_jitter(value: float, fraction: float, *, rng: random.Random | None = None) -> float:
    r = rng or random
    half = value * fraction
    return r.uniform(value - half, value + half)


def sleep_granular(seconds: float, stop_check: callable, poll_interval: float = 0.05) -> bool:
    remaining = seconds
    while remaining > 0:
        if stop_check():
            return True
        chunk = min(poll_interval, remaining)
        time_module = __import__("time")
        time_module.sleep(chunk)
        remaining -= chunk
    return False


def time_sleep(seconds: float) -> None:
    import time

    time.sleep(seconds)
