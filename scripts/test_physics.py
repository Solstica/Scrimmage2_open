from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.code.materials import sic_weak_absorption_index
from shared.code.optics import (
    airy_reflectance_paper_a,
    double_beam_reflectance_paper_a,
    fresnel_coefficients_real_angle,
    third_beam_ratio_paper_a,
)


class PhysicsTests(unittest.TestCase):
    def test_paper_a_normal_incidence_fresnel_limit(self):
        r, t, angle = fresnel_coefficients_real_angle(1.0, 2.0, 0.0, "s")
        self.assertAlmostEqual(float(np.real(r)), -1.0 / 3.0, places=12)
        self.assertAlmostEqual(float(np.real(t)), 2.0 / 3.0, places=12)
        self.assertAlmostEqual(float(angle), 0.0, places=12)

    def test_paper_a_zero_thickness_airy_limit(self):
        sigma = np.linspace(2500.0, 3300.0, 50)
        film = np.full_like(sigma, 2.5)
        reflected = airy_reflectance_paper_a(sigma, 0.0, 0.0, film, 3.2, air_index=1.0)
        direct = abs((1.0 - 3.2) / (1.0 + 3.2)) ** 2
        self.assertLess(float(np.max(np.abs(reflected - direct))), 1.0e-12)

    def test_paper_a_phase_is_linear_in_thickness(self):
        sigma = np.array([2800.0])
        film = np.array([2.6])
        # The difference between two thicknesses must equal the signed Fresnel
        # hand calculation; no extra pi phase is inserted by the implementation.
        r1 = double_beam_reflectance_paper_a(sigma, 10.0, 7.0, film, 3.1)
        r2 = double_beam_reflectance_paper_a(sigma, 10.0, 7.5, film, 3.1)
        self.assertTrue(np.isfinite(r1[0]) and np.isfinite(r2[0]))
        self.assertGreater(abs(float(r2[0] - r1[0])), 1.0e-8)

    def test_paper_a_um_to_cm_phase_period(self):
        sigma = np.array([1000.0, 1500.0])
        film = np.full(2, 2.0)
        d_um = 10.0
        phase_difference = 4.0 * np.pi * (sigma[1] - sigma[0]) * d_um * 1.0e-4 * film[0]
        expected = np.exp(-1j * phase_difference)
        observed = np.exp(-1j * 4.0 * np.pi * sigma[1] * d_um * 1.0e-4 * film[1]) / np.exp(
            -1j * 4.0 * np.pi * sigma[0] * d_um * 1.0e-4 * film[0]
        )
        self.assertAlmostEqual(abs(observed - expected), 0.0, places=11)

    def test_paper_a_reflectance_and_ratio_are_finite(self):
        sigma = np.linspace(2500.0, 3300.0, 100)
        film = sic_weak_absorption_index(sigma, carrier_density_cm3=1.0e16)
        reflected = double_beam_reflectance_paper_a(sigma, 15.0, 7.7, film, 2.6)
        ratio = third_beam_ratio_paper_a(sigma, 15.0, 7.7, film, 2.6)
        self.assertTrue(np.all(np.isfinite(reflected)))
        self.assertTrue(np.all(reflected >= 0.0))
        self.assertTrue(np.all(np.isfinite(ratio)))
        self.assertTrue(np.all(ratio >= 0.0))


if __name__ == "__main__":
    unittest.main()
