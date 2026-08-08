"""Material models used by the PAPER_A reproduction route.

The official Q1-Q2 route uses the PAPER_A three-term SiC Sellmeier relation
with a fixed carrier effective mass.  The silicon double-oscillator model is
kept separate because Q3 must retain absorption whereas Q2 works in a weak-
absorption SiC band.
"""
from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator


M0 = 9.1093837015e-31
E_CHARGE = 1.602176634e-19
EPS0 = 8.8541878128e-12
C0 = 299792458.0
SIC_EFFECTIVE_MASS_RATIO = 0.28
SI_EFFECTIVE_MASS_RATIO = 0.26

SIC_SELLMEIER = {
    "A": 1.0,
    "B": np.array([0.20075, 5.54861, 35.65066], dtype=float),
    "C_um2": np.array([-12.07224, 0.02641, 1268.24708], dtype=float),
}

SI_PAPER_A_LATTICE = {
    "epsilon_inf": 11.68,
    "A": np.array([0.29972, 11.34965], dtype=float),
    "lambda_um": np.array([10.6683, 16.2026], dtype=float),
    "gamma_um": np.array([0.092613, 0.23572], dtype=float),
}


def sic_sellmeier_epsilon(
    wavenumber_cm: np.ndarray | float,
    coefficients: dict[str, np.ndarray | float] | None = None,
) -> np.ndarray:
    """Return PAPER_A SiC lattice permittivity in the Sellmeier form."""
    coeff = SIC_SELLMEIER if coefficients is None else coefficients
    sigma = np.asarray(wavenumber_cm, dtype=float)
    wavelength2 = (1.0e4 / sigma) ** 2
    b = np.asarray(coeff["B"], dtype=float)
    c = np.asarray(coeff["C_um2"], dtype=float)
    return float(coeff["A"]) + np.sum(
        b[:, None] * wavelength2.reshape(1, -1)
        / (wavelength2.reshape(1, -1) - c[:, None]),
        axis=0,
    ).reshape(sigma.shape)


def sic_weak_absorption_index(
    wavenumber_cm: np.ndarray | float,
    carrier_density_cm3: float = 0.0,
    effective_mass_ratio: float = SIC_EFFECTIVE_MASS_RATIO,
) -> np.ndarray:
    """Return the real PAPER_A SiC index used over 2500--3300 cm^-1.

    The Drude correction is evaluated in SI units and only its weak-absorption
    real part is retained, matching the formal Q1-Q2 approximation.
    """
    sigma = np.asarray(wavenumber_cm, dtype=float)
    wavelength_m = (1.0e4 / sigma) * 1.0e-6
    density_m3 = float(carrier_density_cm3) * 1.0e6
    drude = (
        density_m3
        * E_CHARGE**2
        * wavelength_m**2
        / (4.0 * np.pi**2 * C0**2 * EPS0 * effective_mass_ratio * M0)
    )
    epsilon = sic_sellmeier_epsilon(sigma) - drude
    return np.sqrt(np.maximum(epsilon, 1.0e-12))


def si_complex_index_paper_a(
    wavenumber_cm: np.ndarray | float,
    carrier_density_cm3: float,
    collision_rate_s: float,
    effective_mass_ratio: float = SI_EFFECTIVE_MASS_RATIO,
) -> np.ndarray:
    """Return PAPER_A's two-oscillator--Drude Si index for exp(-ikz).

    The square-root branch is chosen with non-positive imaginary part so that
    the round-trip factor exp(-ikz) attenuates rather than grows.
    """
    sigma = np.asarray(wavenumber_cm, dtype=float)
    wavelength_um = 1.0e4 / sigma
    lattice = np.full(sigma.shape, SI_PAPER_A_LATTICE["epsilon_inf"], dtype=complex)
    for strength, resonance, damping in zip(
        SI_PAPER_A_LATTICE["A"],
        SI_PAPER_A_LATTICE["lambda_um"],
        SI_PAPER_A_LATTICE["gamma_um"],
    ):
        lattice += strength * wavelength_um**2 / (
            wavelength_um**2 - resonance**2 + 1j * damping * wavelength_um
        )
    omega = 2.0 * np.pi * C0 / (wavelength_um * 1.0e-6)
    density_m3 = float(carrier_density_cm3) * 1.0e6
    plasma2 = density_m3 * E_CHARGE**2 / (EPS0 * effective_mass_ratio * M0)
    drude = -plasma2 / (omega**2 - 1j * float(collision_rate_s) * omega)
    root = np.sqrt(lattice + drude + 0j)
    return np.where(np.imag(root) > 0.0, np.conjugate(root), root)


def sic_background_index(wavenumber_cm: np.ndarray | float) -> np.ndarray:
    """Compatibility alias for the registered SiC Sellmeier background."""
    return np.sqrt(sic_sellmeier_epsilon(wavenumber_cm) + 0j)


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
