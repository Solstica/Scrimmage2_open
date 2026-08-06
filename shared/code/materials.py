"""Optical-constant functions used by the normalized implementation.

The SiC Sellmeier coefficients are transcribed as a model component from the
two reviewed national-first papers and are independently exercised by tests.
The Si background table follows the 293 K values commonly attributed to Li.
No fitted number from either paper or the user's former package is imported.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator


def sic_background_index(wavenumber_cm: np.ndarray | float) -> np.ndarray:
    sigma = np.asarray(wavenumber_cm, dtype=float)
    wavelength_um = 1.0e4 / sigma
    l2 = wavelength_um**2
    eps = (
        1.0
        + 0.20075 * l2 / (l2 + 12.07224)
        + 5.54861 * l2 / (l2 - 0.02641)
        + 35.65066 * l2 / (l2 - 1268.24708)
    )
    return np.sqrt(eps + 0j)


_SI_LAMBDA_UM = np.array([
    1.20,1.22,1.24,1.26,1.28,1.30,1.32,1.34,1.36,1.38,1.40,1.45,1.50,
    1.55,1.60,1.65,1.70,1.80,1.90,2.00,2.25,2.50,2.75,3.00,4.00,5.00,
    6.00,7.00,8.00,9.00,10.0,11.0,12.0,13.0,14.0
], dtype=float)
_SI_N_293K = np.array([
    3.5167,3.5133,3.5102,3.5072,3.5043,3.5016,3.4990,3.4965,3.4941,
    3.4918,3.4896,3.4845,3.4799,3.4757,3.4719,3.4684,3.4653,3.4597,
    3.4550,3.4510,3.4431,3.4375,3.4334,3.4302,3.4229,3.4195,3.4177,
    3.4165,3.4158,3.4153,3.4150,3.4147,3.4145,3.4144,3.4142
], dtype=float)
_SI_INTERPOLATOR = PchipInterpolator(_SI_LAMBDA_UM, _SI_N_293K, extrapolate=True)


def si_background_index(wavenumber_cm: np.ndarray | float) -> np.ndarray:
    sigma = np.asarray(wavenumber_cm, dtype=float)
    return _SI_INTERPOLATOR(1.0e4 / sigma).astype(complex)


def background_index(material: str, wavenumber_cm: np.ndarray | float) -> np.ndarray:
    if material.lower() == "sic":
        return sic_background_index(wavenumber_cm)
    if material.lower() == "si":
        return si_background_index(wavenumber_cm)
    raise ValueError(f"Unsupported material: {material}")


def drude_substrate_permittivity(
    material: str,
    wavenumber_cm: np.ndarray,
    plasma_wavenumber_cm: float,
    damping_wavenumber_cm: float,
    index_scale: float = 1.0,
) -> np.ndarray:
    sigma = np.asarray(wavenumber_cm, dtype=float)
    n_background = index_scale * background_index(material, sigma)
    # The +i*gamma convention yields Im(epsilon)>0 and a decaying propagation
    # factor under exp(+i*k*z), matching optics.py.
    free_carrier = plasma_wavenumber_cm**2 / (
        sigma * (sigma + 1j * damping_wavenumber_cm)
    )
    return n_background**2 - free_carrier
