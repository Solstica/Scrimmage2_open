from __future__ import annotations

import math
import unittest

import numpy as np

from shared.code.materials import drude_substrate_permittivity, sic_background_index
from shared.code.optics import layer_amplitudes, passive_sqrt, reflected_amplitude, unpolarized_reflectance


class PhysicsTests(unittest.TestCase):
    def test_passive_root(self):
        roots = passive_sqrt(np.array([4 + 1j, 4 - 1j]))
        self.assertTrue(np.all(np.imag(roots) >= 0))

    def test_um_to_cm_phase_period(self):
        sigma = np.array([1000.0, 1500.0])
        n1 = np.full(2, 2.0 + 0j)
        eps2 = np.full(2, 9.0 + 0j)
        parts = layer_amplitudes(sigma, 0.0, 10.0, n1, eps2)
        loop_ratio = parts["s"]["loop"][1] / parts["s"]["loop"][0]
        expected = np.exp(4j * np.pi * (1500.0 - 1000.0) * 10.0e-4 * 2.0)
        self.assertAlmostEqual(abs(loop_ratio - expected), 0.0, places=11)

    def test_neumann_convergence(self):
        sigma = np.linspace(1200.0, 3000.0, 300)
        n1 = sic_background_index(sigma)
        eps2 = drude_substrate_permittivity("sic", sigma, 1200.0, 500.0)
        parts = layer_amplitudes(sigma, 10.0, 7.4, n1, eps2)
        finite = reflected_amplitude(parts["s"], 20)
        airy = reflected_amplitude(parts["s"], math.inf)
        self.assertLess(float(np.max(np.abs(finite - airy))), 1e-10)

    def test_no_artificial_halfwave_offset(self):
        sigma = np.linspace(1200.0, 3000.0, 100)
        n1 = np.full(100, 2.6 + 0j)
        eps2 = np.full(100, 3.2**2 + 0j)
        r = unpolarized_reflectance(sigma, 0.0, 0.0, n1, eps2, math.inf)
        direct = abs((1.0 - 3.2) / (1.0 + 3.2)) ** 2
        self.assertLess(float(np.max(np.abs(r - direct))), 1e-12)


if __name__ == "__main__":
    unittest.main()
