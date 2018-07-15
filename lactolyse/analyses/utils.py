"""Utilities for lactolyse analyses."""
import numpy as np


class FittedPolynomial:
    """Polynomial of 3rd degree fitted on the given values."""

    def __init__(self, x_values, y_values):
        """Initialize fitted polynomial."""
        self.poly = np.poly1d(np.polyfit(x_values, y_values, 3))

        self.min_x = x_values[0]
        self.max_x = x_values[-1]

        self._deriv = None
        self._deriv_roots = None
        self._second_deriv = None
        self._second_deriv_roots = None

    @property
    def deriv(self):
        """Return first derivative of the polynomial."""
        if self._deriv is None:
            self._deriv = self.poly.deriv()

        return self._deriv

    @property
    def deriv_roots(self):
        """Return real roots of the first derivative of the polynomial.

        Filter out values that are not between the min and the max value
        of the values on which the polynomial was fitted.
        """
        if self._deriv_roots is None:
            self._deriv_roots = np.roots(self.deriv)

            self._deriv_roots = self._deriv_roots[np.logical_and(
                np.isreal(self._deriv_roots),
                self._deriv_roots > self.min_x,
                self._deriv_roots < self.max_x,
            )]

        return self._deriv_roots

    @property
    def second_deriv(self):
        """Return second derivative of the polynomial."""
        if self._second_deriv is None:
            self._second_deriv = self.deriv.deriv()

        return self._second_deriv

    @property
    def second_deriv_roots(self):
        """Return real roots of the second derivative of the polynomial.

        Filter out values that are not between the min and the max value
        of the values on which the polynomial was fitted.
        """
        if self._second_deriv_roots is None:
            self._second_deriv_roots = np.roots(self.second_deriv)

            self._second_deriv_roots = self._second_deriv_roots[np.logical_and(
                np.isreal(self._second_deriv_roots),
                self._second_deriv_roots > self.min_x,
                self._second_deriv_roots < self.max_x,
            )]

        return self._second_deriv_roots
