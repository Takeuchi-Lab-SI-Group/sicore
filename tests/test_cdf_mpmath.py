from numpy.testing import assert_allclose
from sicore.cdf_mpmath import (
    chi_cdf_mpmath,
    chi2_cdf_mpmath,
    f_cdf_mpmath,
    mp,
    t_cdf_mpmath,
    tc_cdf_mpmath,
    tc2_cdf_mpmath,
    tf_cdf_mpmath,
    tn_cdf_mpmath,
    tt_cdf_mpmath,
)

mp.dps = 300

INF = float("inf")
NINF = -INF


def test_t_cdf_mpmath():
    testcase = [
        ((NINF, 2), 0.0),
        ((NINF, 3), 0.0),
        ((-5.0, 2), 0.018874775675311862),
        ((-5.0, 3), 0.007696219036651148),
        ((0.0, 2), 0.5),
        ((0.0, 3), 0.5),
        ((5.0, 2), 0.9811252243246881),
        ((5.0, 3), 0.9923037809633488),
        ((INF, 2), 1.0),
        ((INF, 3), 1.0),
    ]

    for args, expected in testcase:
        assert_allclose(float(t_cdf_mpmath(*args)), expected)


def test_chi_cdf_mpmath():
    testcase = [
        ((0.0, 2), 0.0),
        ((0.0, 3), 0.0),
        ((1.0, 2), 0.3934693402873665),
        ((1.0, 3), 0.19874804309879915),
        ((3.0, 2), 0.9888910034617577),
        ((3.0, 3), 0.9707091134651118),
        ((3.0, 15), 0.1224825483987176),
        ((INF, 2), 1.0),
        ((INF, 3), 1.0),
    ]

    for args, expected in testcase:
        assert_allclose(float(chi_cdf_mpmath(*args)), expected)


def test_chi2_cdf_mpmath():
    testcase = [
        ((0.0, 2), 0.0),
        ((0.0, 3), 0.0),
        ((1.0, 2), 0.3934693402873665),
        ((1.0, 3), 0.19874804309879915),
        ((3.0, 2), 0.7768698398515702),
        ((3.0, 3), 0.6083748237289109),
        ((INF, 2), 1.0),
        ((INF, 3), 1.0),
    ]

    for args, expected in testcase:
        assert_allclose(float(chi2_cdf_mpmath(*args)), expected)


def test_f_cdf_mpmath():
    testcase = [
        ((0.0, 2, 2), 0.0),
        ((0.0, 2, 3), 0.0),
        ((1.0, 2, 2), 0.5),
        ((1.0, 2, 3), 0.53524199845511),
        ((2.0, 2, 2), 0.6666666666666666),
        ((2.0, 2, 3), 0.7194341411251527),
        ((INF, 2, 2), 1.0),
        ((INF, 2, 3), 1.0),
    ]

    for args, expected in testcase:
        assert_allclose(float(f_cdf_mpmath(*args)), expected)


def test_tn_cdf_mpmath():
    testcase = [
        ((NINF, [[NINF, -1.5], [-1.0, -0.8], [-0.3, 0.5], [1.0, INF]]), 0.0),
        ((-1.7, [[NINF, -1.5], [-1.0, -0.8], [-0.3, 0.5], [1.0, INF]]),
         0.07578690102235282),
        ((0.0, [[NINF, -1.5], [-1.0, -0.8], [-0.3, 0.5], [1.0, INF]]),
         0.40459865137689516),
        ((0.3, [[NINF, -1.5], [-1.0, -0.8], [-0.3, 0.5], [1.0, INF]]),
         0.6051158395693588),
        ((INF, [[NINF, -1.5], [-1.0, -0.8], [-0.3, 0.5], [1.0, INF]]), 1.0),
    ]

    for args, expected in testcase:
        assert_allclose(float(tn_cdf_mpmath(*args)), expected)


def test_tn_cdf_mpmath_absolute():
    testcase = [
        ((-4, [[-5, -4], [-2, -1], [1, 3], [4, 5]]), 0.9997859703),
        ((2, [[1, 3], [4, 5]]), 0.8637850356),
        ((-9.8, [[NINF, -19], [-10, -9.5]]), 0.953281348403),
        ((-0.5, [[NINF, INF]]), 0.3829249225480),
        ((5.3, [[-10, -6], [4, 4.6], [5, 11]]), 0.998026968808),
        ((-0.03, [[-7, 1], [2, 3]]), 0.02774046489227),
        ((-2.6, [[-3, -2]]), 0.84526851411),
        ((1.9, [[-5, -2], [1.4, 2], [6, INF]]), 0.6444085725),
        ((3.5, [[3.4, 3.7], [5, 5.6]]), 0.45465432178)
    ]
    for args, expected in testcase:
        assert_allclose(float(tn_cdf_mpmath(*args, absolute=True)), expected)


def test_tt_cdf_mpmath():
    testcase = [
        ((NINF, [[NINF, -1.5], [-1.0, -0.8], [-0.3, 0.5], [1.0, INF]], 2), 0.0),
        ((-1.7, [[NINF, -1.5], [-1.0, -0.8], [-0.3, 0.5], [1.0, INF]], 2),
         0.17506081601590198),
        ((0.0, [[NINF, -1.5], [-1.0, -0.8], [-0.3, 0.5], [1.0, INF]], 2),
         0.4276648740747664),
        ((0.3, [[NINF, -1.5], [-1.0, -0.8], [-0.3, 0.5], [1.0, INF]], 2),
         0.5847685858739919),
        ((INF, [[NINF, -1.5], [-1.0, -0.8], [-0.3, 0.5], [1.0, INF]], 2), 1.0),
    ]

    for args, expected in testcase:
        assert_allclose(float(tt_cdf_mpmath(*args)), expected)


def test_tc_cdf_mpmath():
    testcase = [
        ((2.5, [[1.6, 6.6]], 14), 0.039857837599),
        ((8.4, [[8.3, 24.4], [24.6, 27.1]], 1), 0.571152956027),
        ((6.7, [[6.4, 7.3], [18.9, 22.2], [24.7, 27.9]], 5), 0.842784288742),
        ((2.3, [[0.0, 0.5], [1.0, 1.5], [2.0, INF]], 7), 0.247393505668),
        ((INF, [[0.0, 0.5], [1.0, 1.5], [2.0, INF]], 2), 1.0),
    ]

    for args, expected in testcase:
        assert_allclose(float(tc_cdf_mpmath(*args)), expected)


def test_tc2_cdf_mpmath():
    testcase = [
        ((0.0, [[0.0, 0.5], [1.0, 1.5], [2.0, INF]], 2), 0.0),
        ((0.3, [[0.0, 0.5], [1.0, 1.5], [2.0, INF]], 2), 0.19259373242557318),
        ((1.2, [[0.0, 0.5], [1.0, 1.5], [2.0, INF]], 2), 0.3856495412291721),
        ((INF, [[0.0, 0.5], [1.0, 1.5], [2.0, INF]], 2), 1.0),
    ]

    for args, expected in testcase:
        assert_allclose(float(tc2_cdf_mpmath(*args)), expected)


def test_tf_cdf_mpmath():
    testcase = [
        ((0.0, [[0.0, 0.5], [1.0, 1.5], [2.0, INF]], 2, 3), 0.0),
        ((0.3, [[0.0, 0.5], [1.0, 1.5], [2.0, INF]], 2, 3), 0.3223627738673543),
        ((1.2, [[0.0, 0.5], [1.0, 1.5], [2.0, INF]], 2, 3), 0.5404533787680365),
        ((INF, [[0.0, 0.5], [1.0, 1.5], [2.0, INF]], 2, 3), 1.0),
    ]

    for args, expected in testcase:
        assert_allclose(float(tf_cdf_mpmath(*args)), expected)
