"""Core package for selective inference."""

from .core.base import (
    InfiniteLoopError,
    SelectiveInference,
    SelectiveInferenceResult,
)
from .core.cdf import truncated_cdf
from .core.real_subset import RealSubset
from .main.inference import SelectiveInferenceChi, SelectiveInferenceNorm
from .utils.constructor import OneVector, construct_projection_matrix
from .utils.evaluation import rejection_rate
from .utils.figure import (
    SummaryFigure,
    pvalues_hist,
    pvalues_qqplot,
)
from .utils.intervals import (
    complement,
    difference,
    intersection,
    linear_polynomials_below_zero,
    polynomial_below_zero,
    polytope_below_zero,
    symmetric_difference,
    union,
)
from .utils.non_gaussian import generate_non_gaussian_rv
from .utils.uniformity_test import uniformity_test

__all__ = [
    "SelectiveInference",
    "SelectiveInferenceNorm",
    "SelectiveInferenceChi",
    "SelectiveInferenceResult",
    "InfiniteLoopError",
    "rejection_rate",
    "pvalues_hist",
    "pvalues_qqplot",
    "SummaryFigure",
    "RealSubset",
    "complement",
    "union",
    "intersection",
    "difference",
    "symmetric_difference",
    "polynomial_below_zero",
    "polytope_below_zero",
    "linear_polynomials_below_zero",
    "truncated_cdf",
    "generate_non_gaussian_rv",
    "uniformity_test",
    "OneVector",
    "construct_projection_matrix",
]
