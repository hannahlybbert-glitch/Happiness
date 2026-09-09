# Health: predicted vs. actual happiness, by predictor subgroup

Happiness scale: 1 = Not too happy, 2 = Pretty happy, 3 = Very happy.

- **True (GSS) averages**: WTSSNRPS-weighted GSS 2004-2024, design-based 95% CIs.
- **Predicted averages**: unweighted mean of survey respondents' single guesses at the subgroup's average happiness, split by the predictor's own Health subgroup (via demographic_gss_crosswalk.csv). SE = sd / sqrt(n); 95% CI = mean +/- 1.96 SE.
- Overall GSS weighted average happiness: 2.114 (n=28,889).
- Rows are ordered happiest to least happy by the true GSS average.

## True GSS averages

| Subgroup | N (GSS) | True mean | SE | 95% CI |
|---|---|---|---|---|
| Excellent | 5,127 | 2.364 | 0.012 | (2.341, 2.387) |
| Good | 11,514 | 2.114 | 0.008 | (2.098, 2.130) |
| Fair | 4,947 | 1.881 | 0.011 | (1.859, 1.903) |
| Poor | 1,171 | 1.675 | 0.027 | (1.621, 1.728) |

## Predicted averages by predictor subgroup

`Pred - true` is the predictor subgroup's average guess minus that subgroup's true GSS average (positive = over-estimated happiness).

| Subgroup | Predictor subgroup | N (predictors) | Predicted mean | SE | 95% CI | Pred - true |
|---|---|---|---|---|---|---|
| Excellent | Excellent (own group) | 303 | 2.438 | 0.008 | (2.421, 2.454) | +0.074 |
| Excellent | Good | 1,108 | 2.409 | 0.004 | (2.401, 2.418) | +0.046 |
| Excellent | Fair | 457 | 2.401 | 0.007 | (2.387, 2.414) | +0.037 |
| Excellent | Poor | 83 | 2.404 | 0.013 | (2.378, 2.430) | +0.040 |
| Good | Excellent | 303 | 2.336 | 0.008 | (2.320, 2.352) | +0.222 |
| Good | Good (own group) | 1,108 | 2.311 | 0.004 | (2.303, 2.319) | +0.197 |
| Good | Fair | 457 | 2.292 | 0.006 | (2.281, 2.304) | +0.178 |
| Good | Poor | 83 | 2.289 | 0.013 | (2.263, 2.314) | +0.175 |
| Fair | Excellent | 303 | 2.155 | 0.009 | (2.138, 2.173) | +0.275 |
| Fair | Good | 1,108 | 2.140 | 0.004 | (2.132, 2.148) | +0.259 |
| Fair | Fair (own group) | 457 | 2.124 | 0.006 | (2.113, 2.135) | +0.243 |
| Fair | Poor | 83 | 2.094 | 0.014 | (2.067, 2.121) | +0.213 |
| Poor | Excellent | 303 | 1.867 | 0.010 | (1.847, 1.886) | +0.192 |
| Poor | Good | 1,108 | 1.863 | 0.005 | (1.854, 1.872) | +0.188 |
| Poor | Fair | 457 | 1.861 | 0.008 | (1.845, 1.876) | +0.186 |
| Poor | Poor (own group) | 83 | 1.819 | 0.020 | (1.779, 1.858) | +0.144 |
