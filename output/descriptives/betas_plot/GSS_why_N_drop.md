# Why does the complete-case regression sample drop so many respondents?

General Social Survey, 2004-2024; diagnostics for run_betas_regression.R's complete-case sample.

Respondents with valid HAPPY: 28,889. Complete-case sample (0 of 14 categories missing): 10,439 (36.1%). Lost to missingness on at least 1 category: 18,450.

## Marginal missingness per category

`n_unmapped_valid_code` = a valid GSS answer that doesn't fall into any of our current bucket labels (e.g. RACECEN1 = American Indian/Alaska Native) - a labeling gap, not nonresponse. `n_true_nonresponse` = the raw value itself is blank/skipped/refused.

| Category | N Missing | % Missing | True Nonresponse | Unmapped Valid Code |
|---|---|---|---|---|
| Own or Rent | 10,064 | 34.8 | 9,748 | 316 |
| Socializing with Friends | 9,659 | 33.4 | 9,659 | 0 |
| Health | 6,130 | 21.2 | 6,130 | 0 |
| Income | 3,267 | 11.3 | 3,267 | 0 |
| Race | 1,000 | 3.5 | 265 | 735 |
| Party | 960 | 3.3 | 247 | 713 |
| Age | 690 | 2.4 | 690 | 0 |
| Religious Attendance | 211 | 0.7 | 211 | 0 |
| Gender | 129 | 0.4 | 129 | 0 |
| Children Ever Born | 119 | 0.4 | 119 | 0 |
| Marital Status | 50 | 0.2 | 50 | 0 |
| Employment | 39 | 0.1 | 39 | 0 |
| Education | 33 | 0.1 | 33 | 0 |
| Urban vs Rural | 0 | 0.0 | 0 | 0 |

## How many categories is each respondent missing?

Shows whether loss is spread thin (most people missing 0 or 1) or concentrated (many people missing several categories at once).

| Categories Missing | N Respondents | % of Sample |
|---|---|---|
| 0 | 10,439 | 36.1 |
| 1 | 7,251 | 25.1 |
| 2 | 9,144 | 31.7 |
| 3 | 1,656 | 5.7 |
| 4 | 252 | 0.9 |
| 5 | 87 | 0.3 |
| 6 | 32 | 0.1 |
| 7 | 17 | 0.1 |
| 8 | 9 | 0.0 |
| 9 | 2 | 0.0 |

## Among respondents missing exactly one category, which one

These are the people a single question is solely responsible for excluding from the complete-case regression.

| Category | N Respondents | % of Single-Category Losses |
|---|---|---|
| Health | 5,059 | 69.8 |
| Income | 1,098 | 15.1 |
| Race | 342 | 4.7 |
| Party | 305 | 4.2 |
| Age | 194 | 2.7 |
| Own or Rent | 167 | 2.3 |
| Socializing with Friends | 22 | 0.3 |
| Religious Attendance | 19 | 0.3 |
| Children Ever Born | 18 | 0.2 |
| Marital Status | 10 | 0.1 |
| Education | 6 | 0.1 |
| Employment | 6 | 0.1 |
| Gender | 5 | 0.1 |

## Most common missingness patterns (2+ categories missing together)

| Pattern | N Respondents | % of Any-Missing |
|---|---|---|
| Own or Rent, Socializing with Friends | 7,845 | 42.5 |
| Health | 5,059 | 27.4 |
| Income | 1,098 | 6.0 |
| Income, Own or Rent, Socializing with Friends | 836 | 4.5 |
| Health, Income | 571 | 3.1 |
| Race | 342 | 1.9 |
| Party | 305 | 1.7 |
| Own or Rent, Race, Socializing with Friends | 259 | 1.4 |
| Own or Rent, Party, Socializing with Friends | 259 | 1.4 |
| Age | 194 | 1.1 |

## Missingness by survey year, top 3 categories (Own or Rent, Socializing with Friends, Health)

| Year | N | % Missing Own or Rent | % Missing Socializing with Friends | % Missing Health |
|---|---|---|---|---|
| 2004 | 1,337 | 34.6 | 32.5 | 33.1 |
| 2006 | 2,986 | 34.8 | 33.5 | 33.2 |
| 2008 | 2,015 | 35.5 | 34.5 | 33.3 |
| 2010 | 2,039 | 31.5 | 30.3 | 37.5 |
| 2012 | 1,964 | 34.9 | 34.0 | 33.9 |
| 2014 | 2,530 | 35.1 | 33.9 | 32.6 |
| 2016 | 2,859 | 35.3 | 34.1 | 34.2 |
| 2018 | 2,344 | 34.9 | 33.6 | 33.1 |
| 2021 | 4,014 | 35.2 | 33.0 | 0.2 |
| 2022 | 3,520 | 35.1 | 33.2 | 0.1 |
| 2024 | 3,281 | 35.2 | 34.4 | 0.3 |
