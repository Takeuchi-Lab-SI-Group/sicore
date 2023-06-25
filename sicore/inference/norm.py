from abc import ABC, abstractmethod
import numpy as np
from typing import Callable, List, Tuple, Type
from ..utils import is_int_or_float
from ..intervals import intersection, not_, union_all, _interval_to_intervals
from ..cdf_mpmath import tn_cdf_mpmath
from .base import *

from scipy import sparse
from scipy.stats import norm

import random

INF = np.inf
NINF = -np.inf


class InferenceNorm(ABC):
    """Base inference class for a test statistic which follows normal distribution under null.

    Args:
        data (np.ndarray, tf.Tensor, torch.Tensor):
            Observation data in 1-D array. When given as a tensor,
            activate the corresponding option.
        var (float, np.ndarray, tf.Tensor, torch.Tensor, sparse.csr_array):
            Value of known variance covariance. Assuming that
            the shape of the input is a scalar or 1-D array or 2-D array,
            the variance-covariance matrix Cov is interpreted as follows.
            When the input is a scalar, Cov = input * Identity.
            When the input is a 1-D array, Cov = diag(input).
            When the input is a 2-D array, Cov = input.
            Also, activate the option, when given as a sparse array.
        eta (np.ndarray, tf.Tensor, torch.Tensor):
            Contrast vector in 1-D array. When given as a tensor,
            activate the corresponding option.
        use_sparse (boolean, optional):
            Whether to use sparse array or not. Defaults to False.
        use_tf (boolean, optional):
            Whether to use tensorflow or not. Defaults to False.
        use_torch (boolean, optional):
            Whether to use pytorch or not. Defaults to False.
    """

    def __init__(
        self,
        data: np.ndarray,
        var: float | np.ndarray | sparse.csr_array,
        eta: np.ndarray,
        use_sparse: bool = False,
        use_tf: bool = False,
        use_torch: bool = False,
    ):
        if use_sparse and (use_tf or use_torch):
            raise Exception(
                "Sparse matrix cannot be used with the deep learning framework at the same time."
            )
        if use_tf and use_torch:
            raise Exception("Only one of tensorflow and pytorch is available.")

        self.data = data  # unnecessary
        self.length = len(data)  # unnecessary
        self.eta = eta  # unnecessary

        if use_tf:
            try:
                import tensorflow as tf
            except ModuleNotFoundError:
                raise Exception(
                    "The option use_tf is activated, but tensorflow was not found."
                )

            assert isinstance(data, tf.Tensor)
            assert isinstance(eta, tf.Tensor)

            self.stat = tf.tensordot(eta, data, axes=1)
            if is_int_or_float(var):
                self.sigma_eta = var * eta
            elif len(var.shape) == 1:
                vars = tf.constant(var, dtype=data.dtype)
                self.sigma_eta = vars * eta
            elif len(var.shape) == 2:
                cov = tf.constant(var, dtype=data.dtype)
                self.sigma_eta = tf.tensordot(cov, eta, axes=1)
            self.eta_sigma_eta = tf.tensordot(eta, self.sigma_eta, axes=1)

        elif use_torch:
            try:
                import torch
            except ModuleNotFoundError:
                raise Exception(
                    "The option use_torch is activated, but pytorch was not found."
                )

            assert isinstance(data, torch.Tensor)
            assert isinstance(eta, torch.Tensor)

            self.stat = torch.dot(eta, data)
            if is_int_or_float(var):
                self.sigma_eta = var * eta
            elif len(var.shape) == 1:
                vars = torch.tensor(var, dtype=data.dtype)
                self.sigma_eta = vars * eta
            elif len(var.shape) == 2:
                cov = torch.tensor(var, dtype=data.dtype)
                self.sigma_eta = torch.mv(cov, eta)
            self.eta_sigma_eta = torch.dot(eta, self.sigma_eta)

        else:
            data, eta = np.array(data), np.array(eta)
            self.stat = eta @ data
            if is_int_or_float(var):
                self.sigma_eta = var * eta
            elif len(var.shape) == 1:
                vars = np.array(var)
                self.sigma_eta = vars * eta
            elif len(var.shape) == 2:
                cov = sparse.csr_array(var) if use_sparse else np.array(var)
                self.sigma_eta = cov @ eta
            self.eta_sigma_eta = eta @ self.sigma_eta

    @abstractmethod
    def inference(self, *args, **kwargs):
        """Perform statistical inference."""
        pass


class NaiveInferenceNorm(InferenceNorm):
    """Naive inference for a test statistic which follows normal distribution under null.

    Args:
        data (np.ndarray, List[float], tf.Tensor, torch.Tensor):
            Observation data in 1-D array. When given as a tensor,
            activate the corresponding option.
        var (float, np.ndarray, tf.Tensor, torch.Tensor, sparse.csr_array):
            Value of known variance covariance. Assuming that
            the shape of the input is a scalar or 1-D array or 2-D array,
            the variance-covariance matrix Cov is interpreted as follows.
            When the input is a scalar, Cov = input * Identity.
            When the input is a 1-D array, Cov = diag(input).
            When the input is a 2-D array, Cov = input.
            Also, activate the option, when given as a sparse array.
        eta (np.ndarray, List[float], tf.Tensor, torch.Tensor):
            Contrast vector in 1-D array. When given as a tensor,
            activate the corresponding option.
        use_sparse (boolean, optional):
            Whether to use sparse array or not. Defaults to False.
        use_tf (boolean, optional):
            Whether to use tensorflow or not. Defaults to False.
        use_torch (boolean, optional):
            Whether to use pytorch or not. Defaults to False.
    """

    def inference(self, alternative: str = "two-sided", popmean: float = 0):
        """Perform naive statistical inference.

        Args:
            alternative (str, optional):
                'two-sided' for two-tailed test,
                'less' for right-tailed test,
                'greater' for left-tailed test.
                Defaults to 'two-sided'.
            popmean (float, optional):
                Population mean of the test statistic under null hypothesis.
                Defaults to 0.

        Returns:
            float: p-value
        """
        stat = standardize(self.stat, popmean, self.eta_sigma_eta)
        F = norm.cdf(stat)
        return calc_pvalue(F, alternative=alternative)


class SelectiveInferenceNorm(InferenceNorm):
    """Selective inference for a test statistic which follows normal distribution under null.

    Args:
        data (np.ndarray, List[float], tf.Tensor, torch.Tensor):
            Observation data in 1-D array. When given as a tensor,
            activate the corresponding option.
        var (float, np.ndarray, tf.Tensor, torch.Tensor, sparse.csr_array):
            Value of known variance covariance. Assuming that
            the shape of the input is a scalar or 1-D array or 2-D array,
            the variance-covariance matrix Cov is interpreted as follows.
            When the input is a scalar, Cov = input * Identity.
            When the input is a 1-D array, Cov = diag(input).
            When the input is a 2-D array, Cov = input.
            Also, activate the option, when given as a sparse array.
        eta (np.ndarray, List[float], tf.Tensor, torch.Tensor):
            Contrast vector in 1-D array. When given as a tensor,
            activate the corresponding option.
        use_sparse (boolean, optional):
            Whether to use sparse array or not. Defaults to False.
        use_tf (boolean, optional):
            Whether to use tensorflow or not. Defaults to False.
        use_torch (boolean, optional):
            Whether to use pytorch or not. Defaults to False.
    """

    def __init__(
        self,
        data: np.ndarray,
        var: float | np.ndarray | sparse.csr_array,
        eta: np.ndarray,
        use_sparse: bool = False,
        use_tf: bool = False,
        use_torch: bool = False,
    ):
        super().__init__(data, var, eta, use_sparse, use_tf, use_torch)
        self.c = self.sigma_eta / self.eta_sigma_eta  # `b` vector in para si.
        self.z = data - self.stat * self.c  # `a` vecotr in para si.

    def inference(
        self,
        algorithm: Callable[
            [np.ndarray, np.ndarray, float], Tuple[List[List[float]], Any]
        ],
        model_selector: Callable[[Any], bool],
        significance_level: float = 0.05,
        parametric_mode: str = "p_value",
        over_conditioning: bool = False,
        alternative: str = "abs",
        threshold: float = 1e-3,
        popmean: float = 0,
        line_search: bool = True,
        max_tail: float = 1e3,
        choose_method: str = "near_stat",
        retain_selected_model: bool = False,
        retain_mappings: bool = False,
        tol: float = 1e-10,
        step: float = 1e-10,
        dps: int | str = "auto",
        max_dps: int = 5000,
        out_log: str = "test_log.log",
        max_iter: int = 1e6,
        callback: None = None,
    ) -> Type[SelectiveInferenceResult]:
        """Perform Selective Inference.

        Args:
            algorithm (Callable[[np.ndarray, np.ndarray, float], Tuple[List[List[float]], Any]]):
                Callable function which takes two vectors (`a`, `b`)
                and a scalar `z` that can satisfy `data = a + b * z`
                as arguments, and returns the selected model (any) and
                the truncation intervals (array-like). A closure function might be
                helpful to implement this.
            model_selector (Callable[[Any], bool]):
                Callable function which takes a selected model (any) as single argument, and
                returns True if the model is used for the testing, and False otherwise.
            significance_level (float, optional):
                Significance level for the testing. Defaults to 0.05.
            parametric_mode (str, optional):
                Specifies the method used to perform parametric selective inference. This option is
                ignored when the over_conditioning option is activated.
                'p_value' for calculation of p-value with guaranteed accuracy specified by the threshold option.
                'reject_or_not' for only determining whether the null hypothesis is rejected.
                'all_search' for all searches of the interval specified by the max_tail option.
            over_conditioning (bool, optional):
                Over conditioning Inference. Defaults to False.
            alternative (str, optional):
                'two-sided' for two-tailed test,
                'less' for right-tailed test,
                'greater' for left-tailed test,
                'abs' for two-tailed test for
                the distribution of absolute values
                following the null distribution.
                Defaults to 'abs'.
            threshold (float, optional):
                Guaranteed accuracy when calculating p-value. Defaults to 1e-3.
            popmean (float, optional):
                Mean of the null distribution. Defaults to 0.
            line_search (bool, optional):
                Wheter to perform a line search or a random search. Defaults to True.
            max_tail (float, optional):
                Maximum tail value to be parametrically searched when
                the parametric_mode option is set to all_search. Defaults to 1e3.
            choose_method (str, optional):
                How to determine the search direction when parametric_mode
                is other than all_search. 'near_stat', 'high_pdf', and 'random'
                can be specified. Defaults to 'near_stat'.
            retain_selected_model (bool, optional):
                Whether retain selected model as returns or not. Defaults to False.
            retain_mappings (bool, optional):
                Whether retain mappings as returns or not. Defaults to False.
            tol (float, optional):
                Tolerance error parameter for intervals. Defaults to 1e-10.
            step (float, optional):
                Step width for parametric search. Defaults to 1e-10.
            dps (int | str, optional):
                dps value for mpmath. Set 'auto' to select dps
                automatically. Defaults to 'auto'.
            max_dps (int, optional):
                Maximum dps value for mpmath. This option is valid
                when `dps` is set to 'auto'. Defaults to 5000.
            out_log (str, optional):
                Name for log file of mpmath. Defaults to 'test_log.log'.
            max_iter (int, optional):
                Maximum number of times to perform parametric search.
                If this value is exceeded, the loop is considered
                to be infinite. Defaults to 1e6.

        Raises:
            Exception:
                The parametric_mode option is not p_value, reject_or_not, or all_search,
                and the over_conditioning option is set False.

        Returns:
            Type[SelectiveInferenceResult]
        """

        lim = max(30, 10 + abs(standardize(self.stat, popmean, self.eta_sigma_eta)))
        self.restrict = [[-lim, lim]]

        if over_conditioning:
            result = self._over_conditioned_inference(
                algorithm,
                significance_level,
                alternative,
                popmean,
                retain_selected_model,
                tol,
                dps,
                max_dps,
                out_log,
            )
            return result

        elif parametric_mode == "p_value" or parametric_mode == "reject_or_not":
            result = self._parametric_inference(
                algorithm,
                model_selector,
                significance_level,
                parametric_mode,
                alternative,
                threshold,
                popmean,
                choose_method,
                retain_selected_model,
                retain_mappings,
                tol,
                step,
                dps,
                max_dps,
                out_log,
                max_iter,
                callback,
            )

        elif parametric_mode == "all_search":
            result = self._all_search_parametric_inference(
                algorithm,
                model_selector,
                significance_level,
                alternative,
                popmean,
                line_search,
                max_tail,
                retain_selected_model,
                retain_mappings,
                tol,
                step,
                dps,
                max_dps,
                out_log,
            )

        else:
            raise Exception(
                "Please activate either parametric_mode or over_conditioning option."
            )

        return result

    def _evaluate_pvalue(self, truncated_intervals, searched_intervals, alternative):
        unsearched_intervals = not_(searched_intervals)

        if alternative == "abs":
            mask_intervals = [[-abs(float(self.stat)), abs(float(self.stat))]]
            absolute = True
        else:
            mask_intervals = [[NINF, float(self.stat)]]
            absolute = False

        inf_intervals = union_all(
            truncated_intervals
            + intersection(unsearched_intervals, not_(mask_intervals)),
            tol=self.tol,
        )
        sup_intervals = union_all(
            truncated_intervals + intersection(unsearched_intervals, mask_intervals),
            tol=self.tol,
        )

        norm_inf_intervals = standardize(
            inf_intervals, self.popmean, self.eta_sigma_eta
        )
        norm_sup_intervals = standardize(
            sup_intervals, self.popmean, self.eta_sigma_eta
        )

        flatten = np.ravel(norm_inf_intervals)
        nonfinites = flatten[np.isfinite(flatten)]
        if len(nonfinites) != 0:
            if np.abs(nonfinites).max() > self.restrict[0][1]:
                norm_inf_intervals = intersection(norm_inf_intervals, self.restrict)
        flatten = np.ravel(norm_sup_intervals)
        nonfinites = flatten[np.isfinite(flatten)]
        if len(nonfinites) != 0:
            if np.abs(nonfinites).max() > self.restrict[0][1]:
                norm_sup_intervals = intersection(norm_sup_intervals, self.restrict)

        # norm_inf_intervals = intersection(norm_inf_intervals, self.restrict)
        # norm_sup_intervals = intersection(norm_sup_intervals, self.restrict)

        stat_std = standardize(self.stat, self.popmean, self.eta_sigma_eta)

        inf_F = tn_cdf_mpmath(
            stat_std,
            norm_inf_intervals,
            absolute=absolute,
            dps=self.dps,
            max_dps=self.max_dps,
            out_log=self.out_log,
        )
        sup_F = tn_cdf_mpmath(
            stat_std,
            norm_sup_intervals,
            absolute=absolute,
            dps=self.dps,
            max_dps=self.max_dps,
            out_log=self.out_log,
        )
        inf_p, sup_p = calc_prange(inf_F, sup_F, alternative)

        return inf_p, sup_p

    def _determine_next_search_data(self, choose_method, searched_intervals):
        unsearched_intervals = standardize(
            not_(searched_intervals), self.popmean, self.eta_sigma_eta
        ).tolist()
        candidates = list()
        mode = 0

        if choose_method == "sup_pdf":
            for interval in unsearched_intervals:
                if np.isinf(interval[0]):
                    l = min(mode - 2, interval[1] - 2)
                else:
                    l = interval[0]
                if np.isinf(interval[1]):
                    u = max(mode + 2, interval[0] + 2)
                else:
                    u = interval[1]
                if u - l > 2 * self.step:
                    candidates += list(
                        np.linspace(
                            l + self.step,
                            u - self.step,
                            int(1000 / len(unsearched_intervals)),
                        )
                    )

        if choose_method == "near_stat" or choose_method == "high_pdf":
            unsearched_lower_stat = intersection(
                unsearched_intervals,
                [[NINF, standardize(self.stat, self.popmean, self.eta_sigma_eta)]],
            )
            unsearched_upper_stat = intersection(
                unsearched_intervals,
                [[standardize(self.stat, self.popmean, self.eta_sigma_eta), INF]],
            )
            if len(unsearched_lower_stat) != 0:
                candidates.append(unsearched_lower_stat[-1][-1] - self.step)
            if len(unsearched_upper_stat) != 0:
                candidates.append(unsearched_upper_stat[0][0] + self.step)

        if choose_method == "near_stat":

            def method(z):
                return -np.abs(
                    z - standardize(self.stat, self.popmean, self.eta_sigma_eta)
                )

        if choose_method == "high_pdf" or choose_method == "sup_pdf":

            def method(z):
                return norm.logpdf(z)

        candidates = np.array(candidates)
        return (
            np.sqrt(self.eta_sigma_eta) * candidates[np.argmax(method(candidates))]
            + self.popmean
        )

    def _next_search_data(self, line_search):
        intervals = not_(self.searched_intervals)
        if len(intervals) == 0:
            return None
        if line_search:
            param = intervals[0][0] + self.step
        else:
            s, e = random.choice(intervals)
            param = (e + s) / 2
        return param

    def _execute_callback(self, callback, progress):
        self.search_history.append(callback(progress))

    def _parametric_inference(
        self,
        algorithm,
        model_selector,
        significance_level,
        parametric_mode,
        alternative,
        threshold,
        popmean,
        choose_method,
        retain_selected_model,
        retain_mappings,
        tol,
        step,
        dps,
        max_dps,
        out_log,
        max_iter,
        callback,
    ):
        self.popmean = popmean
        self.tol = tol
        self.step = step
        self.dps = dps
        self.max_dps = max_dps
        self.out_log = out_log
        self.searched_intervals = list()

        self.search_history = list()
        self.search_checker = SearchChecker(max_iter)

        mappings = dict() if retain_mappings else None
        truncated_intervals = list()

        search_count = 0
        detect_count = 0

        z = self.stat
        while True:
            search_count += 1

            model, interval = algorithm(self.z, self.c, z)
            interval = np.asarray(interval)
            intervals = _interval_to_intervals(interval)

            if retain_mappings:
                for interval in intervals:
                    interval = tuple(interval)
                    if interval in mappings:
                        raise Exception(
                            "An interval appeared a second time. Usually, numerical error "
                            "causes this exception. Consider increasing the tol parameter "
                            "or decreasing max_tail parameter to avoid it."
                        )
                    mappings[interval] = model

            if model_selector(model):
                selected_model = model if retain_selected_model else None
                truncated_intervals += intervals
                detect_count += 1

            self.searched_intervals = union_all(
                self.searched_intervals + intervals, tol=self.tol
            )
            self.search_checker.verify_progress(self.searched_intervals)

            inf_p, sup_p = self._evaluate_pvalue(
                truncated_intervals, self.searched_intervals, alternative
            )

            if parametric_mode == "p_value":
                if np.abs(sup_p - inf_p) < threshold:
                    break
            if parametric_mode == "reject_or_not":
                if sup_p <= significance_level:
                    reject_or_not = True
                    break
                if inf_p > significance_level:
                    reject_or_not = False
                    break

            z = self._determine_next_search_data(choose_method, self.searched_intervals)

        stat_std = standardize(self.stat, popmean, self.eta_sigma_eta)
        truncated_intervals = union_all(truncated_intervals, tol=self.tol)
        norm_intervals = standardize(
            truncated_intervals, popmean, self.eta_sigma_eta
        ).tolist()
        norm_intervals = intersection(norm_intervals, self.restrict)
        absolute = True if alternative == "abs" else False
        F = tn_cdf_mpmath(
            stat_std,
            norm_intervals,
            absolute=absolute,
            dps=self.dps,
            max_dps=self.max_dps,
            out_log=self.out_log,
        )
        p_value = calc_pvalue(F, alternative)
        if parametric_mode == "p_value":
            reject_or_not = p_value <= significance_level

        return SelectiveInferenceResult(
            stat_std,
            significance_level,
            p_value,
            inf_p,
            sup_p,
            reject_or_not,
            norm_intervals,
            search_count,
            detect_count,
            selected_model,
            mappings,
        )

    def _all_search_parametric_inference(
        self,
        algorithm,
        model_selector,
        significance_level,
        alternative,
        popmean,
        line_search,
        max_tail,
        retain_selected_model,
        retain_mappings,
        tol,
        step,
        dps,
        max_dps,
        out_log,
    ):
        self.popmean = popmean
        self.tol = tol
        self.step = step
        self.dps = dps
        self.max_dps = max_dps
        self.out_log = out_log
        self.searched_intervals = union_all(
            [[NINF, -float(max_tail)], [float(max_tail), INF]], tol=self.tol
        )

        mappings = dict() if retain_mappings else None
        result_intervals = list()

        search_count = 0
        detect_count = 0

        z = self._next_search_data(line_search)
        while True:
            search_count += 1
            if search_count > 3e4:
                raise Exception(
                    "The number of searches exceeds 100,000 times, suggesting an infinite loop."
                )

            model, interval = algorithm(self.z, self.c, z)
            interval = np.asarray(interval)
            intervals = _interval_to_intervals(interval)

            if retain_mappings:
                for interval in intervals:
                    interval = tuple(interval)
                    if interval in mappings:
                        raise Exception(
                            "An interval appeared a second time. Usually, numerical error "
                            "causes this exception. Consider increasing the tol parameter "
                            "or decreasing max_tail parameter to avoid it."
                        )
                    mappings[interval] = model

            if model_selector(model):
                selected_model = model if retain_selected_model else None
                result_intervals += intervals
                detect_count += 1

            self.searched_intervals = union_all(
                self.searched_intervals + intervals, tol=self.tol
            )

            prev_z = z
            z = self._next_search_data(line_search)

            if z is None:
                break

            if np.abs(prev_z - z) < self.step * 0.5:
                raise InfiniteLoopError

        stat_std = standardize(self.stat, popmean, self.eta_sigma_eta)
        truncated_intervals = union_all(result_intervals, tol=self.tol)
        norm_intervals = standardize(
            truncated_intervals, popmean, self.eta_sigma_eta
        ).tolist()
        norm_intervals = intersection(norm_intervals, self.restrict)
        absolute = True if alternative == "abs" else False
        F = tn_cdf_mpmath(
            stat_std,
            norm_intervals,
            absolute=absolute,
            dps=self.dps,
            max_dps=self.max_dps,
            out_log=self.out_log,
        )
        p_value = calc_pvalue(F, alternative)

        inf_p, sup_p = self._evaluate_pvalue(
            truncated_intervals, [[-float(max_tail), float(max_tail)]], alternative
        )

        return SelectiveInferenceResult(
            stat_std,
            significance_level,
            p_value,
            inf_p,
            sup_p,
            (p_value <= significance_level),
            norm_intervals,
            search_count,
            detect_count,
            selected_model,
            mappings,
        )

    def _over_conditioned_inference(
        self,
        algorithm,
        significance_level,
        alternative,
        popmean,
        retain_selected_model,
        tol,
        dps,
        max_dps,
        out_log,
    ):
        self.popmean = popmean
        self.tol = tol
        self.dps = dps
        self.max_dps = max_dps
        self.out_log = out_log

        model, interval = algorithm(self.z, self.c, self.stat)
        interval = np.asarray(interval)
        intervals = _interval_to_intervals(interval)

        stat_std = standardize(self.stat, popmean, self.eta_sigma_eta)
        norm_intervals = standardize(intervals, popmean, self.eta_sigma_eta).tolist()
        norm_intervals = intersection(norm_intervals, self.restrict)
        absolute = True if alternative == "abs" else False
        F = tn_cdf_mpmath(
            stat_std,
            norm_intervals,
            absolute=absolute,
            dps=self.dps,
            max_dps=self.max_dps,
            out_log=self.out_log,
        )
        p_value = calc_pvalue(F, alternative)

        inf_p, sup_p = self._evaluate_pvalue(intervals, intervals, alternative)

        return SelectiveInferenceResult(
            stat_std,
            significance_level,
            p_value,
            inf_p,
            sup_p,
            (p_value <= significance_level),
            norm_intervals,
            1,
            1,
            None,
            model if retain_selected_model else None,
        )
