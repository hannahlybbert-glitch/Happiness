# Author: Hannah Lybbert, assisted by Claude
# Created: 2026-08-04; Updated: 2026-08-04
# Purpose: Multiple regression of HAPPY on 14 demographic/attitudinal subgroup blocks
#   (dummy-coded, one omitted baseline per block) plus survey-year fixed effects, using
#   the 2004-2024 GSS. WLS (WTSSNRPS) with cluster-robust (CR1 sandwich, clustered by
#   VSTRAT x VPSU) standard errors, computed directly in base R matrix algebra - no
#   extra R packages beyond `here`, avoiding the Matrix/survey Windows/mingw issue that
#   blocked GSS_happiness_plot_weighted.R.
#
# Baselines (confirmed with PI 2026-08-04): 35-64, Woman, White, HS+some college, Mid
#   income, Employed, Married, No Children, Sometimes attendance, Independent, Suburb,
#   Good health, Sometimes socializing, Own. Year fixed effects reference 2004.
#
# Requires: data/ProcessGSS/GSS_main.csv (must include WTSSNRPS, VPSU, VSTRAT).
# Packages: install.packages("here")
#
# Outputs: data/descriptives/betas_plot/GSS_betas.csv (category, subgroup, beta, se,
#   ci_lo, ci_hi, n - one row per non-baseline subgroup level, for
#   GSS_happiness_betas_plot.py to read and plot).

suppressPackageStartupMessages(library(here))

INPUT_FILE <- here::here("data", "ProcessGSS", "GSS_main.csv")
OUTPUT_CSV <- here::here("data", "descriptives", "betas_plot", "GSS_betas.csv")

# ============================================================================
# RECODING (same buckets as GSS_happiness_plot.py / GSS_happiness_plot_weighted.R,
# but returned as factors with the confirmed baseline level listed FIRST, so
# model.matrix()'s default treatment contrasts drop the right reference level.)
# ============================================================================

clean_numeric <- function(x, exclude = numeric(0)) {
  x <- suppressWarnings(as.numeric(x))
  x[x %in% exclude] <- NA
  x
}

map_values <- function(code, mapping) unname(mapping[as.character(code)])

make_factor <- function(labels, level_order) factor(labels, levels = level_order)

weighted_quantile <- function(x, w, probs) {
  keep <- !is.na(x) & !is.na(w)
  x <- x[keep]; w <- w[keep]
  ord <- order(x)
  x <- x[ord]; w <- w[ord]
  cum_w <- cumsum(w) / sum(w)
  vapply(probs, function(p) x[which(cum_w >= p)[1]], numeric(1))
}

df <- read.csv(INPUT_FILE, stringsAsFactors = FALSE)

happy_map <- c(`1` = "3", `2` = "2", `3` = "1")
df$happy <- as.numeric(map_values(clean_numeric(df$HAPPY), happy_map))

age_cut <- cut(clean_numeric(df$AGE), breaks = c(0, 34, 64, Inf), labels = c("18-34", "35-64", "65+"))
df$age_f <- make_factor(as.character(age_cut), c("35-64", "18-34", "65+"))

df$sex_f <- make_factor(map_values(clean_numeric(df$SEX), c(`1` = "Man", `2` = "Woman")),
                         c("Woman", "Man"))

race_map <- c(`1` = "White", `2` = "Black", `16` = "Hispanic",
              `4` = "Asian", `5` = "Asian", `6` = "Asian", `7` = "Asian",
              `8` = "Asian", `9` = "Asian", `10` = "Asian")
df$race_f <- make_factor(map_values(clean_numeric(df$RACECEN1), race_map),
                          c("White", "Black", "Hispanic", "Asian"))

educ_map <- c(`0` = "Less than HS", `1` = "HS+some college", `2` = "HS+some college",
              `3` = "Bachelors+Graduate", `4` = "Bachelors+Graduate")
df$educ_f <- make_factor(map_values(clean_numeric(df$DEGREE), educ_map),
                          c("HS+some college", "Less than HS", "Bachelors+Graduate"))

income_cuts <- weighted_quantile(df$REALINC, df$WTSSNRPS, c(1 / 3, 2 / 3))
cat(sprintf("Income tercile cutpoints (weighted, REALINC): %.2f, %.2f\n", income_cuts[1], income_cuts[2]))
income_cut <- cut(clean_numeric(df$REALINC), breaks = c(-Inf, income_cuts, Inf),
                   labels = c("Low", "Mid", "High"))
df$income_f <- make_factor(as.character(income_cut), c("Mid", "Low", "High"))

emp_map <- c(`1` = "Employed", `2` = "Employed", `3` = "Employed", `4` = "Unemployed",
             `5` = "Not in Labor Force", `6` = "Not in Labor Force",
             `7` = "Not in Labor Force", `8` = "Not in Labor Force")
df$emp_f <- make_factor(map_values(clean_numeric(df$WRKSTAT), emp_map),
                         c("Employed", "Unemployed", "Not in Labor Force"))

marital_map <- c(`1` = "Married", `2` = "Widowed", `3` = "Separated/Divorced",
                  `4` = "Separated/Divorced", `5` = "Never Married")
df$marital_f <- make_factor(map_values(clean_numeric(df$MARITAL), marital_map),
                             c("Married", "Widowed", "Separated/Divorced", "Never Married"))

childs_code <- clean_numeric(df$CHILDS)
childs_lab <- ifelse(is.na(childs_code), NA_character_, ifelse(childs_code == 0, "No Children", "Children"))
df$childs_f <- make_factor(childs_lab, c("No Children", "Children"))

attend_map <- c(`0` = "Never", `1` = "Sometimes", `2` = "Sometimes", `3` = "Sometimes",
                 `4` = "Sometimes", `5` = "Sometimes", `6` = "Sometimes",
                 `7` = "Weekly or more", `8` = "Weekly or more")
df$attend_f <- make_factor(map_values(clean_numeric(df$ATTEND), attend_map),
                            c("Sometimes", "Never", "Weekly or more"))

party_map <- c(`0` = "Democrat", `1` = "Democrat", `2` = "Democrat", `3` = "Independent",
               `4` = "Republican", `5` = "Republican", `6` = "Republican")
df$party_f <- make_factor(map_values(clean_numeric(df$PARTYID), party_map),
                           c("Independent", "Democrat", "Republican"))

urban_map <- c(`1` = "Big city", `2` = "Big city",
               `3` = "Suburb", `4` = "Suburb", `5` = "Suburb", `6` = "Suburb",
               `7` = "Small/rural town", `8` = "Small/rural town",
               `9` = "Small/rural town", `10` = "Small/rural town")
df$urban_f <- make_factor(map_values(clean_numeric(df$XNORCSIZ), urban_map),
                           c("Suburb", "Big city", "Small/rural town"))

health_map <- c(`1` = "Excellent", `2` = "Good", `3` = "Fair", `4` = "Poor")
df$health_f <- make_factor(map_values(clean_numeric(df$HEALTH), health_map),
                            c("Good", "Excellent", "Fair", "Poor"))

socfrend_map <- c(`1` = "Weekly or more", `2` = "Weekly or more", `3` = "Weekly or more",
                   `4` = "Sometimes", `5` = "Sometimes", `6` = "Sometimes", `7` = "Never")
df$socfrend_f <- make_factor(map_values(clean_numeric(df$SOCFREND), socfrend_map),
                              c("Sometimes", "Weekly or more", "Never"))

df$dwelown_f <- make_factor(map_values(clean_numeric(df$DWELOWN), c(`1` = "Own", `2` = "Rent")),
                             c("Own", "Rent"))

df$year_f <- factor(df$YEAR, levels = sort(unique(df$YEAR)))  # reference = 2004, earliest year

# Category display name -> model column, for building the output table afterward
CATEGORY_COLS <- list(
  "Age" = "age_f", "Gender" = "sex_f", "Race" = "race_f", "Education" = "educ_f",
  "Income" = "income_f", "Employment" = "emp_f", "Marital Status" = "marital_f",
  "Children Ever Born" = "childs_f", "Religious Attendance" = "attend_f",
  "Party" = "party_f", "Urban vs Rural" = "urban_f", "Health" = "health_f",
  "Socializing with Friends" = "socfrend_f", "Own or Rent" = "dwelown_f"
)

# ============================================================================
# COMPLETE-CASE SAMPLE
# ============================================================================

model_vars <- c("happy", unlist(CATEGORY_COLS), "year_f", "WTSSNRPS", "VPSU", "VSTRAT")
complete <- stats::complete.cases(df[, model_vars])
df_reg <- df[complete, ]
cat(sprintf("Complete-case regression sample: %d of %d respondents\n", nrow(df_reg), nrow(df)))

# ============================================================================
# WLS REGRESSION
# ============================================================================

form <- as.formula(paste("happy ~", paste(c(unlist(CATEGORY_COLS), "year_f"), collapse = " + ")))
fit <- lm(form, data = df_reg, weights = WTSSNRPS)

X <- model.matrix(fit)
w <- df_reg$WTSSNRPS
u <- residuals(fit)
cluster <- interaction(df_reg$VSTRAT, df_reg$VPSU, drop = TRUE)

# ============================================================================
# CLUSTER-ROBUST (CR1 SANDWICH) STANDARD ERRORS, CLUSTERED BY VSTRAT x VPSU
# ============================================================================

cluster_robust_se <- function(X, w, u, cluster) {
  XtWX_inv <- solve(t(X) %*% (X * w))
  score <- X * (w * u)
  ug <- rowsum(score, cluster)
  meat <- t(ug) %*% ug
  G <- nrow(ug)
  N <- nrow(X)
  K <- ncol(X)
  correction <- (G / (G - 1)) * ((N - 1) / (N - K))
  vcov <- XtWX_inv %*% meat %*% XtWX_inv * correction
  sqrt(diag(vcov))
}

se <- cluster_robust_se(X, w, u, cluster)
names(se) <- colnames(X)
beta <- coef(fit)

cat(sprintf("\nIntercept (baseline combination, predicted happiness): %.3f (SE %.3f)\n",
            beta["(Intercept)"], se["(Intercept)"]))

# ============================================================================
# BUILD OUTPUT TABLE (14 subgroup categories only - year FE kept in the model as
# controls but not reported in the plot)
# ============================================================================

rows <- list()
for (category in names(CATEGORY_COLS)) {
  col <- CATEGORY_COLS[[category]]

  # Baseline row first (beta = 0 by definition, no CI - it's the reference, not an
  # estimated contrast), so Python doesn't need its own hardcoded baseline list.
  baseline_level <- levels(df_reg[[col]])[1]
  rows[[length(rows) + 1]] <- data.frame(
    category = category, subgroup = baseline_level, n = sum(df_reg[[col]] == baseline_level, na.rm = TRUE),
    beta = 0, se = NA, ci_lo = NA, ci_hi = NA, is_baseline = TRUE, stringsAsFactors = FALSE
  )

  term_prefix <- col
  term_names <- grep(paste0("^", term_prefix), names(beta), value = TRUE)
  for (term in term_names) {
    subgroup <- sub(term_prefix, "", term)
    n <- sum(df_reg[[col]] == subgroup, na.rm = TRUE)
    rows[[length(rows) + 1]] <- data.frame(
      category = category, subgroup = subgroup, n = n,
      beta = beta[[term]], se = se[[term]],
      ci_lo = beta[[term]] - 1.96 * se[[term]],
      ci_hi = beta[[term]] + 1.96 * se[[term]],
      is_baseline = FALSE, stringsAsFactors = FALSE
    )
  }
}
results <- do.call(rbind, rows)

dir.create(dirname(OUTPUT_CSV), recursive = TRUE, showWarnings = FALSE)
write.csv(results, OUTPUT_CSV, row.names = FALSE)
cat(sprintf("\nWrote %d subgroup betas to %s\n", nrow(results), OUTPUT_CSV))
