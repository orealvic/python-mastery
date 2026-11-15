# Track: Scientific Computing

**Stack:** NumPy · SciPy · matplotlib · SymPy · Numba · Jupyter · (optional) JAX, Cython

## Milestone 1: Numerical foundations
- **Learn:** floating-point representation and error, vectorization, broadcasting, linear algebra with `numpy.linalg`.
- **Build:** solve a linear system three ways (Gaussian elimination by hand, `np.linalg.solve`, LU from SciPy) and compare their accuracy and speed.
- **Done when:** you can explain condition numbers and show a badly conditioned example failing.

## Milestone 2: Calculus numerically
- **Learn:** finite differences, numerical integration (trapezoid, Simpson, `scipy.integrate.quad`), root finding (bisection, Newton, `scipy.optimize`).
- **Build:** a small library implementing each method, tested against analytical answers.
- **Done when:** you can plot error against step size on a log-log scale and explain the slope.

## Milestone 3: Differential equations
- **Learn:** Euler, RK4, `scipy.integrate.solve_ivp`, stiffness.
- **Build:** simulate a pendulum, a predator–prey model and an orbital system, with animated plots.
- **Done when:** your RK4 matches `solve_ivp`, and energy drift is measured and explained.

## Milestone 4: Symbolic math
- **Learn:** SymPy: symbols, simplification, derivatives, solving equations, `lambdify` to NumPy.
- **Build:** derive equations of motion symbolically, then simulate them numerically.

## Milestone 5: Performance
- **Learn:** profiling numeric code, Numba `@njit`, parallel loops, and when to reach for Cython, JAX or Rust (PyO3).
- **Build:** an N-body or cellular-automaton simulation, optimized step by step.
- **Done when:** you have a benchmark table showing pure Python, then NumPy, then Numba, with a speedup factor at each step.

## Milestone 6: Reproducible research
- **Learn:** project layout for research code, pinned environments, tests for numerical code (tolerances), documenting with notebooks.
- **Done when:** someone else can reproduce your figures from a fresh clone with one command.

## Capstone
Simulate a system from your own field (physics, biology, finance, engineering), validate it against a known result, optimize it, and write up the results.

## Key reading
- *Numerical Python* (Johansson) · *Effective Computation in Physics* (Scopatz & Huff)
- SciPy lecture notes (free) · Numba docs
