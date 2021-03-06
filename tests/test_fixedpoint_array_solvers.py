# -*- coding: utf-8 -*-
"""
Test iterative methods using a chemical process engineering problem
regarding chemical recycle loops with reactions.

"""
import numpy as np
import flexsolve as flx
from matplotlib import pyplot as plt
from numpy import allclose

conversion = 0.8
stoichiometry = np.array([-1, 0.5, 2, 1, 0.1, 0.001, 0, 0])
feed = np.array([20, 10, 0, 0, 0, 0, 30, 15], dtype=float)
recycle = np.zeros_like(feed)

@flx.njitable(cache=True)
def f(x):
    if (x < 0.).any():
        raise Exception('negative values are infeasible')
    recycle = feed.copy()
    recycle[:] = x
    reactor_feed = recycle + feed
    effluent = reactor_feed + (reactor_feed[0] * stoichiometry * conversion)
    product = effluent * 0.1
    return effluent - product

def create_plot(p, line=False):
    xs = np.array(p.xs)
    ys = np.array(p.ys)
    xs = np.abs(xs).sum(0)
    ys = np.abs(ys).sum(0)
    plt.scatter(xs, ys)
    if line:
        plt.plot(xs, ys)

def test_fixedpoint_array_solvers():
    real_solution = np.array([4.39024390e+00, 1.77804878e+02, 3.51219512e+02, 1.75609756e+02,
                              1.75609756e+01, 1.75609756e-01, 2.70000000e+02, 1.35000000e+02])
    original_feed = feed.copy()
    p = flx.Profiler(f)
    solution = flx.wegstein(p, feed, xtol=1e-8)
    assert allclose(feed, original_feed)
    assert allclose(solution, real_solution)
    p.archive('Wegstein')
    solution = flx.aitken(p, feed, xtol=1e-8,maxiter=200)
    assert allclose(feed, original_feed)
    assert allclose(solution, real_solution)
    p.archive('Aitken')
    solution = flx.fixed_point_lstsq(p, feed, xtol=5e-8, maxiter=200)
    assert allclose(feed, original_feed)
    assert allclose(solution, real_solution)
    p.archive('Lstsq')
    solution = flx.fixed_point(p, feed, xtol=5e-8, maxiter=200)
    assert allclose(feed, original_feed)
    assert allclose(solution, real_solution)
    p.archive('Fixed point')
    assert p.sizes() == {'Wegstein': 5, 'Aitken': 5, 'Lstsq': 22, 'Fixed point': 194}
    
    flx.speed_up()
    solution = flx.wegstein(f, feed, xtol=5e-8)
    assert allclose(solution, real_solution)
    solution = flx.aitken(f, feed, xtol=5e-8)
    assert allclose(solution, real_solution)