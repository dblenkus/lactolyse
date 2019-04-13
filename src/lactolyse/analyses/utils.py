"""Utilities for lactolyse analyses."""
import numpy as np


class FittedPolynomial:
    """Polynomial of 3rd degree fitted on the given values."""

    _deriv = None
    _deriv_roots = None
    _second_deriv = None
    _second_deriv_roots = None

    def __init__(self, x_values, y_values):
        """Initialize fitted polynomial."""
        self.x_values = x_values
        self.y_values = y_values

        self.poly = np.poly1d(np.polyfit(x_values, y_values, 3))

        self.error = sum(np.square(self.poly(self.x_values) - self.y_values))

        self.min_x = min(x_values)
        self.max_x = max(x_values)

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

            self._deriv_roots = self._deriv_roots[
                np.logical_and(
                    np.isreal(self._deriv_roots),
                    self._deriv_roots > self.min_x,
                    self._deriv_roots < self.max_x,
                )
            ]

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

            self._second_deriv_roots = self._second_deriv_roots[
                np.logical_and(
                    np.isreal(self._second_deriv_roots),
                    self._second_deriv_roots > self.min_x,
                    self._second_deriv_roots < self.max_x,
                )
            ]

        return self._second_deriv_roots


def fit_polynomial(x_values, y_values, exclude_outliers=0, return_inputs=False):
    """Fit FittedPolynomial to given values and optionally exclude outliers."""
    best_poly = FittedPolynomial(x_values, y_values)

    for _ in range(exclude_outliers):
        best_x, best_y = x_values, y_values

        for i in range(len(x_values)):
            new_x = x_values[:i] + x_values[i + 1 :]
            new_y = y_values[:i] + y_values[i + 1 :]

            new_poly = FittedPolynomial(new_x, new_y)

            if new_poly.error < best_poly.error:
                best_poly = new_poly
                best_x, best_y = new_x, new_y

        x_values, y_values = best_x, best_y

    if return_inputs:
        return best_poly, x_values, y_values
    else:
        return best_poly
