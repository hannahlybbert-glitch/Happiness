# SEXORNT missingness breakdown and its effect on the happiness reference line

General Social Survey, 2004-2024. `GSS_main.csv` collapses every flavor of missing SEXORNT to plain NaN; this re-reads the raw SAS file's reserved codes to tell 'not on that year's ballot' (Inapplicable) apart from genuine non-response among respondents who *were* asked (Don't know / No answer / Skipped on web).

## Breakdown by SEXORNT response category

| Category | N | % of total | N (valid HAPPY) | Mean happy | SD | 95% CI |
|---|---|---|---|---|---|---|
| Answered | 17,739 | 55.4% | 17,668 | 2.068 | 0.659 | (2.059, 2.078) |
| Inapplicable (not on ballot) | 13,804 | 43.1% | 10,771 | 2.125 | 0.646 | (2.112, 2.137) |
| Don't know | 192 | 0.6% | 188 | 2.016 | 0.777 | (1.905, 2.127) |
| No answer | 184 | 0.6% | 184 | 2.092 | 0.675 | (1.995, 2.190) |
| Skipped on web | 82 | 0.3% | 78 | 2.013 | 0.712 | (1.855, 2.171) |

## Declined-to-answer vs. inapplicable vs. answered

"Declined" pools Don't know / No answer / Skipped on web - respondents who *were* asked SEXORNT but didn't give a substantive answer.

| Group | N | Mean happy | SD | 95% CI |
|---|---|---|---|---|
| Answered | 17,668 | 2.068 | 0.659 | (2.059, 2.078) |
| Declined (asked but no answer) | 450 | 2.047 | 0.725 | (1.980, 2.114) |
| Inapplicable (not on ballot) | 10,771 | 2.125 | 0.646 | (2.112, 2.137) |
| Overall | 28,889 | 2.089 | 0.656 | (2.081, 2.097) |

## Category share by survey year (%)

| Year | N | Answered | Inapplicable (not on ballot) | Don't know | No answer | Skipped on web |
|---|---|---|---|---|---|---|
| 2004 | 2,812 | 0.0 | 100.0 | 0.0 | 0.0 | 0.0 |
| 2006 | 4,510 | 0.0 | 100.0 | 0.0 | 0.0 | 0.0 |
| 2008 | 2,023 | 87.0 | 11.7 | 0.3 | 1.0 | 0.0 |
| 2010 | 2,044 | 88.4 | 9.9 | 0.4 | 1.3 | 0.0 |
| 2012 | 1,974 | 86.5 | 12.0 | 0.2 | 1.4 | 0.0 |
| 2014 | 2,538 | 90.8 | 7.4 | 0.2 | 1.5 | 0.0 |
| 2016 | 2,867 | 60.8 | 38.2 | 0.2 | 0.8 | 0.0 |
| 2018 | 2,348 | 58.5 | 40.1 | 0.3 | 1.1 | 0.0 |
| 2021 | 4,032 | 56.1 | 41.7 | 1.3 | 0.0 | 0.9 |
| 2022 | 3,544 | 43.6 | 53.6 | 1.7 | 0.2 | 0.9 |
| 2024 | 3,309 | 97.9 | 0.0 | 1.2 | 0.3 | 0.5 |
