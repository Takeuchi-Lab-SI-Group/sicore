"""
Core package for selective inference.
"""
from . import intervals
from .intervals import polytope_to_interval, poly_lt_zero
from .utils import OneVec, construct_projection_matrix
from .cdf_mpmath import tc_cdf_mpmath as tc_cdf
from .cdf_mpmath import tc2_cdf_mpmath as tc2_cdf
from .cdf_mpmath import tf_cdf_mpmath as tf_cdf
from .cdf_mpmath import tn_cdf_mpmath as tn_cdf
from .cdf_mpmath import tt_cdf_mpmath as tt_cdf
from .evaluation import (
    false_negative_rate,
    false_positive_rate,
    power,
    true_negative_rate,
    true_positive_rate,
    type1_error_rate,
    type2_error_rate,
)
from .figures import (
    FprFigure,
    PowerFigure,
    pvalues_hist,
    pvalues_qqplot,
    search_history_visualizer,
    pvalue_bounds_plot,
)
from .inference.base import (
    SelectiveInferenceResult,
    InfiniteLoopError,
)
from .inference.norm import (
    NaiveInferenceNorm,
    SelectiveInferenceNorm,
)
from .inference.chi import NaiveInferenceChi, SelectiveInferenceChi

__all__ = [
    "NaiveInferenceNorm",
    "SelectiveInferenceNorm",
    "NaiveInferenceChi",
    "SelectiveInferenceChi",
    "SelectiveInferenceResult",
    "InfiniteLoopError",
    "tn_cdf",
    "tt_cdf",
    "tc_cdf",
    "tc2_cdf",
    "tf_cdf",
    "false_positive_rate",
    "false_negative_rate",
    "true_negative_rate",
    "true_positive_rate",
    "type1_error_rate",
    "type2_error_rate",
    "power",
    "pvalues_hist",
    "pvalues_qqplot",
    "FprFigure",
    "PowerFigure",
    "search_history_visualizer",
    "pvalue_bounds_plot",
    "intervals",
    "polytope_to_interval",
    "poly_lt_zero",
    "construct_projection_matrix",
    "OneVec",
]
