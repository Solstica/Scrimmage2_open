"""Complex Fresnel forward operator for a single epitaxial film."""
from __future__ import annotations

import math
import numpy as np


def _signed_fresnel(
    n_i: np.ndarray | complex | float,
    n_j: np.ndarray | complex | float,
    theta_i: np.ndarray | float,
    theta_j: np.ndarray | float,
    polarization: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Signed PAPER_A Fresnel amplitude coefficients."""
    ni = np.asarray(n_i, dtype=complex)
    nj = np.asarray(n_j, dtype=complex)
    ci = np.cos(theta_i)
    cj = np.cos(theta_j)
    if polarization == "s":
        denominator = ni * ci + nj * cj
        return (ni * ci - nj * cj) / denominator, 2.0 * ni * ci / denominator
    if polarization == "p":
        denominator = nj * ci + ni * cj
        return (nj * ci - ni * cj) / denominator, 2.0 * ni * ci / denominator
    raise ValueError("polarization must be 's' or 'p'")


def fresnel_coefficients_real_angle(
    n_i: np.ndarray | complex | float,
    n_j: np.ndarray | complex | float,
    theta_i: np.ndarray | float,
    polarization: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """PAPER_A Fresnel coefficients using a real Snell refraction angle."""
    ni = np.asarray(n_i, dtype=complex)
    nj = np.asarray(n_j, dtype=complex)
    argument = np.real(ni) * np.sin(theta_i) / np.maximum(np.real(nj), 1.0e-12)
    theta_j = np.arcsin(np.clip(argument, -1.0, 1.0))
    reflection, transmission = _signed_fresnel(ni, nj, theta_i, theta_j, polarization)
    return reflection, transmission, theta_j


def _paper_a_components(
    wavenumber_cm: np.ndarray,
    angle_deg: float,
    thickness_um: float,
    film_index: np.ndarray,
    substrate_index: np.ndarray | float,
    air_index: float = 1.0003,
) -> dict[str, dict[str, np.ndarray]]:
    sigma = np.asarray(wavenumber_cm, dtype=float)
    n1 = np.full(sigma.shape, complex(air_index), dtype=complex)
    n2 = np.broadcast_to(np.asarray(film_index, dtype=complex), sigma.shape)
    n3 = np.broadcast_to(np.asarray(substrate_index, dtype=complex), sigma.shape)
    theta1 = np.full(sigma.shape, np.deg2rad(angle_deg), dtype=float)
    output: dict[str, dict[str, np.ndarray]] = {}
    for polarization in ("s", "p"):
        r12, t12, theta2 = fresnel_coefficients_real_angle(n1, n2, theta1, polarization)
        r23, _, _ = fresnel_coefficients_real_angle(n2, n3, theta2, polarization)
        r21, t21, _ = fresnel_coefficients_real_angle(n2, n1, theta2, polarization)
        phase = 4.0 * np.pi * 1.0e-4 * sigma * float(thickness_um) * n2 * np.cos(theta2)
        propagation = np.exp(-1j * phase)
        output[polarization] = {
            "surface": r12,
            "first_internal": t12 * r23 * t21 * propagation,
            "loop": r21 * r23 * propagation,
            "propagation": propagation,
            "theta_film": theta2,
        }
    return output


def double_beam_reflectance_paper_a(
    wavenumber_cm: np.ndarray,
    angle_deg: float,
    thickness_um: float,
    film_index: np.ndarray,
    substrate_index: np.ndarray | float,
    air_index: float = 1.0003,
) -> np.ndarray:
    """PAPER_A signed-Fresnel double-beam unpolarized reflectance."""
    parts = _paper_a_components(
        wavenumber_cm, angle_deg, thickness_um, film_index, substrate_index, air_index
    )
    fields = [parts[p]["surface"] + parts[p]["first_internal"] for p in ("s", "p")]
    return 0.5 * (np.abs(fields[0]) ** 2 + np.abs(fields[1]) ** 2)


def airy_reflectance_paper_a(
    wavenumber_cm: np.ndarray,
    angle_deg: float,
    thickness_um: float,
    film_index: np.ndarray,
    substrate_index: np.ndarray | float,
    air_index: float = 1.0003,
) -> np.ndarray:
    """PAPER_A Airy infinite-beam unpolarized reflectance."""
    parts = _paper_a_components(
        wavenumber_cm, angle_deg, thickness_um, film_index, substrate_index, air_index
    )
    fields = [
        parts[p]["surface"] + parts[p]["first_internal"] / (1.0 - parts[p]["loop"])
        for p in ("s", "p")
    ]
    return 0.5 * (np.abs(fields[0]) ** 2 + np.abs(fields[1]) ** 2)


def third_beam_ratio_paper_a(
    wavenumber_cm: np.ndarray,
    angle_deg: float,
    thickness_um: float,
    film_index: np.ndarray,
    substrate_index: np.ndarray | float,
    air_index: float = 1.0003,
) -> np.ndarray:
    """Return PAPER_A's third-beam to surface-beam intensity ratio."""
    parts = _paper_a_components(
        wavenumber_cm, angle_deg, thickness_um, film_index, substrate_index, air_index
    )
    numerator = sum(np.abs(parts[p]["first_internal"] * parts[p]["loop"]) ** 2 for p in ("s", "p"))
    denominator = sum(np.abs(parts[p]["surface"]) ** 2 for p in ("s", "p"))
    return numerator / np.maximum(denominator, 1.0e-30)


def passive_sqrt(value: np.ndarray | complex) -> np.ndarray:
    """Return the passive square-root branch (Im>=0, then Re>=0)."""
    root = np.sqrt(np.asarray(value, dtype=complex) + 0j)
    flip = (np.imag(root) < 0) | ((np.abs(np.imag(root)) < 1e-14) & (np.real(root) < 0))
    return np.where(flip, -root, root)


def _admittance(n: np.ndarray | complex, q: np.ndarray, pol: str) -> np.ndarray:
    return q if pol == "s" else np.asarray(n, dtype=complex) ** 2 / q


def layer_amplitudes(
    wavenumber_cm: np.ndarray,
    angle_deg: float,
    thickness_um: float,
    film_index: np.ndarray,
    substrate_permittivity: np.ndarray,
) -> dict[str, dict[str, np.ndarray]]:
    sigma = np.asarray(wavenumber_cm, dtype=float)
    n0 = 1.0 + 0j
    n1 = np.asarray(film_index, dtype=complex)
    n2 = passive_sqrt(substrate_permittivity)
    s2 = np.sin(np.deg2rad(angle_deg)) ** 2
    q0 = passive_sqrt(n0**2 - s2)
    q1 = passive_sqrt(n1**2 - s2)
    q2 = passive_sqrt(n2**2 - s2)
    beta = 2.0 * np.pi * sigma * (thickness_um * 1.0e-4) * q1
    round_trip_phase = np.exp(2j * beta)
    output: dict[str, dict[str, np.ndarray]] = {}
    for pol in ("s", "p"):
        y0, y1, y2 = (_admittance(n0, q0, pol), _admittance(n1, q1, pol), _admittance(n2, q2, pol))
        r01 = (y0 - y1) / (y0 + y1)
        r10 = (y1 - y0) / (y1 + y0)
        r12 = (y1 - y2) / (y1 + y2)
        t01 = 2.0 * y0 / (y0 + y1)
        t10 = 2.0 * y1 / (y1 + y0)
        first_internal = t01 * t10 * r12 * round_trip_phase
        loop = r10 * r12 * round_trip_phase
        output[pol] = {"surface": r01, "first_internal": first_internal, "loop": loop}
    return output


def reflected_amplitude(component: dict[str, np.ndarray], order: int | float) -> np.ndarray:
    surface, first, loop = component["surface"], component["first_internal"], component["loop"]
    if math.isinf(order):
        return surface + first / (1.0 - loop)
    count = int(order)
    if count < 1:
        raise ValueError("order counts retained internal beams and must be >=1")
    if count == 1:
        return surface + first
    near_one = np.abs(1.0 - loop) < 1e-12
    series = np.where(near_one, count + 0j, (1.0 - loop**count) / (1.0 - loop))
    return surface + first * series


def unpolarized_reflectance(
    wavenumber_cm: np.ndarray,
    angle_deg: float,
    thickness_um: float,
    film_index: np.ndarray,
    substrate_permittivity: np.ndarray,
    order: int | float,
) -> np.ndarray:
    parts = layer_amplitudes(wavenumber_cm, angle_deg, thickness_um, film_index, substrate_permittivity)
    rs = reflected_amplitude(parts["s"], order)
    rp = reflected_amplitude(parts["p"], order)
    return 0.5 * (np.abs(rs) ** 2 + np.abs(rp) ** 2)


def loop_metrics(parts: dict[str, dict[str, np.ndarray]]) -> dict[str, float]:
    loops = np.concatenate([np.abs(parts[pol]["loop"]) for pol in ("s", "p")])
    intensity = loops**2
    return {
        "loop_amplitude_max": float(np.max(loops)),
        "loop_amplitude_median": float(np.median(loops)),
        "rho_intensity_max": float(np.max(intensity)),
        "rho_intensity_median": float(np.median(intensity)),
    }
