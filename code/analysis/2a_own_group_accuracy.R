# Author: Hannah Lybbert, assisted by Claude
# Created: 2026-09-08
# Purpose: Analysis 2a - does a respondent's OWN demographic group relate to how
#   accurately they predict average happiness across groups?
#
#   Step 1. Build the "actual" GSS average happiness for every subgroup slider, using
#           the identical bin definitions as code/descriptives/betas_plot/
#           run_betas_regression.R (WTSSNRPS-weighted mean of recoded HAPPY, 1-3 with
#           3 = very happy, GSS 2004-2024, pairwise deletion per dimension).
#   Step 2. Reshape the cleaned survey to long: one row per respondent x subgroup
#           slider (14 dimensions, 44 subgroups; the pet-death / work-promotion
#           attention-check sliders are excluded). Attach predicted, actual,
#           abs_error, signed_error, and is_own_group (1 if that subgroup is the
#           respondent's own crosswalked category on that dimension, 0 if it maps but
#           differs, NA if their self-report does not map cleanly - e.g. "Other" race).
#   Step 3. Pooled regression on the long data, SEs clustered by respondent (CR1
#           sandwich, hand-rolled in base R matrix algebra - same approach as
#           run_betas_regression.R):
#              abs_error_ij = b0 + b1 * X_i + subgroup_FE_j + e_ij
#           X_i = respondent demographic dummies; subgroup FE net out that some groups
#           are inherently harder to predict.
#   Step 4. Bivariate version for interpretability: each respondent's mean absolute
#           error across all 44 predictions, then group means (+/- 95% CI) by the
#           respondent's own category, one comparison per demographic dimension.
#   Step 5. Dot-and-CI plot, one block of rows per respondent demographic dimension.
#
# Inputs:
#   data/Qualtrics_Responses/cleaned_qualtrics_responses.csv
#   data/Qualtrics_Responses/demographic_gss_crosswalk.csv
#   data/ProcessGSS/GSS_main.csv
# Outputs (all under output/analysis/):
#   prediction_errors_long.csv          - the long respondent x subgroup dataset
#   gss_actual_by_subgroup.csv          - the GSS "actual" target per subgroup
#   accuracy_regression_2a.csv          - pooled regression coefficients + cluster SEs
#   accuracy_regression_2a.txt          - readable regression summary
#   accuracy_by_respondent_group.csv    - bivariate group means + 95% CI
#   accuracy_by_respondent_group.png    - dot-and-CI plot
#
# Packages: base R only, plus `here` (the `happiness` conda env has no ggplot2 /
#   sandwich / dplyr). Run from the repo root or anywhere inside it.

suppressPackageStartupMessages(library(here))

GSS_FILE   <- here::here("data", "ProcessGSS", "GSS_main.csv")
RESP_FILE  <- here::here("data", "Qualtrics_Responses", "cleaned_qualtrics_responses.csv")
XWALK_FILE <- here::here("data", "Qualtrics_Responses", "demographic_gss_crosswalk.csv")
OUT_DIR    <- here::here("output", "analysis")
dir.create(OUT_DIR, recursive = TRUE, showWarnings = FALSE)

MAROON <- "#800000"

# ============================================================================
# Helpers (same idea as run_betas_regression.R)
# ============================================================================

clean_numeric <- function(x, exclude = numeric(0)) {
  x <- suppressWarnings(as.numeric(x))
  x[x %in% exclude] <- NA
  x
}

map_values <- function(code, mapping) unname(mapping[as.character(code)])

weighted_mean_na <- function(x, w) {
  keep <- !is.na(x) & !is.na(w)
  if (!any(keep)) return(NA_real_)
  sum(x[keep] * w[keep]) / sum(w[keep])
}

weighted_quantile <- function(x, w, probs) {
  keep <- !is.na(x) & !is.na(w)
  x <- x[keep]; w <- w[keep]
  ord <- order(x)
  x <- x[ord]; w <- w[ord]
  cum_w <- cumsum(w) / sum(w)
  vapply(probs, function(p) x[which(cum_w >= p)[1]], numeric(1))
}

# ============================================================================
# BRIDGE TABLE: survey slider column  <->  GSS bin
#
# `gss_level` values are exactly the factor labels produced by the recode blocks
# in run_betas_regression.R. `dimension` names match demographic_gss_crosswalk.csv.
# Order within a dimension = display order for the plot (own-group-friendly:
# roughly the run_betas baseline first).
# ============================================================================

bridge <- read.csv(text = "
dimension,subgroup,subgroup_label,gss_col,gss_level
Gender,female,Female,sex_f,Woman
Gender,male,Male,sex_f,Man
Age,age_35_64,35-64,age_f,35-64
Age,age_18_34,18-34,age_f,18-34
Age,age_65_plus,65+,age_f,65+
Race,white,White,race_f,White
Race,black,Black,race_f,Black
Race,hispanic,Hispanic,race_f,Hispanic
Race,asian,Asian,race_f,Asian
Education,HS_and_college,HS and/or some college,educ_f,HS+some college
Education,less_HS,Less than high school,educ_f,Less than HS
Education,bachelors_plus,Bachelor's or more,educ_f,Bachelors+Graduate
Income,middle_income,Middle income,income_f,Mid
Income,low_income,Low income,income_f,Low
Income,high_income,High income,income_f,High
Marital Status,married,Married,marital_f,Married
Marital Status,widowed,Widowed,marital_f,Widowed
Marital Status,divorced,Separated/Divorced,marital_f,Separated/Divorced
Marital Status,single,Never married,marital_f,Never Married
Children Ever Born,no_children,No children,childs_f,No Children
Children Ever Born,children,Has had children,childs_f,Children
Religious Attendance,sometimes_attend,Sometimes attend,attend_f,Sometimes
Religious Attendance,never_attend,Never attend,attend_f,Never
Religious Attendance,weekly_attend,Weekly or more,attend_f,Weekly or more
Party,independent,Independent,party_f,Independent
Party,democrat,Democrat,party_f,Democrat
Party,republican,Republican,party_f,Republican
Urban vs Rural,suburb,Suburb,urban_f,Suburb
Urban vs Rural,city,Big or medium city,urban_f,Big city
Urban vs Rural,small_rural,Small or rural town,urban_f,Small/rural town
Health,good_health,Good health,health_f,Good
Health,excellent_health,Excellent health,health_f,Excellent
Health,fair_health,Fair health,health_f,Fair
Health,poor_health,Poor health,health_f,Poor
Socializing with Friends,sometimes_socialize,Sometimes socialize,socfrend_f,Sometimes
Socializing with Friends,never_socialize,Never socialize,socfrend_f,Never
Socializing with Friends,weekly_socialize,Weekly or more,socfrend_f,Weekly or more
Sexual Orientation,heterosexual,Heterosexual/straight,sexornt_f,Heterosexual/Straight
Sexual Orientation,homosexual,Gay/lesbian/homosexual,sexornt_f,Gay/Lesbian/Homosexual
Sexual Orientation,bisexual,Bisexual,sexornt_f,Bisexual
Region,south,South,region_f,South
Region,northeast,Northeast,region_f,Northeast
Region,midwest,Midwest,region_f,Midwest
Region,west,West,region_f,West
", header = TRUE, stringsAsFactors = FALSE, strip.white = TRUE)

DIMENSION_ORDER <- unique(bridge$dimension)
bridge$dimension <- factor(bridge$dimension, levels = DIMENSION_ORDER)
bridge <- bridge[order(bridge$dimension), ]
bridge$dimension <- as.character(bridge$dimension)

# ============================================================================
# STEP 1: GSS "actual" average happiness per subgroup
# ============================================================================

gss <- read.csv(GSS_FILE, stringsAsFactors = FALSE)

# HAPPY 1/2/3 -> 3/2/1 so higher = happier (same as run_betas_regression.R).
gss$happy <- as.numeric(map_values(clean_numeric(gss$HAPPY), c(`1` = "3", `2` = "2", `3` = "1")))
w <- gss$WTSSNRPS

gss$sex_f <- map_values(clean_numeric(gss$SEX), c(`1` = "Man", `2` = "Woman"))

gss$age_f <- as.character(cut(clean_numeric(gss$AGE), breaks = c(0, 34, 64, Inf),
                              labels = c("18-34", "35-64", "65+")))

race_map <- c(`1` = "White", `2` = "Black", `16` = "Hispanic",
              `4` = "Asian", `5` = "Asian", `6` = "Asian", `7` = "Asian",
              `8` = "Asian", `9` = "Asian", `10` = "Asian")
gss$race_f <- map_values(clean_numeric(gss$RACECEN1), race_map)

educ_map <- c(`0` = "Less than HS", `1` = "HS+some college", `2` = "HS+some college",
              `3` = "Bachelors+Graduate", `4` = "Bachelors+Graduate")
gss$educ_f <- map_values(clean_numeric(gss$DEGREE), educ_map)

income_cuts <- weighted_quantile(gss$REALINC, gss$WTSSNRPS, c(1/3, 2/3))
cat(sprintf("GSS REALINC weighted tercile cutpoints: %.1f, %.1f\n", income_cuts[1], income_cuts[2]))
gss$income_f <- as.character(cut(clean_numeric(gss$REALINC),
                                 breaks = c(-Inf, income_cuts, Inf),
                                 labels = c("Low", "Mid", "High")))

marital_map <- c(`1` = "Married", `2` = "Widowed", `3` = "Separated/Divorced",
                 `4` = "Separated/Divorced", `5` = "Never Married")
gss$marital_f <- map_values(clean_numeric(gss$MARITAL), marital_map)

childs_code <- clean_numeric(gss$CHILDS)
gss$childs_f <- ifelse(is.na(childs_code), NA_character_,
                       ifelse(childs_code == 0, "No Children", "Children"))

attend_map <- c(`0` = "Never", `1` = "Sometimes", `2` = "Sometimes", `3` = "Sometimes",
                `4` = "Sometimes", `5` = "Sometimes", `6` = "Sometimes",
                `7` = "Weekly or more", `8` = "Weekly or more")
gss$attend_f <- map_values(clean_numeric(gss$ATTEND), attend_map)

party_map <- c(`0` = "Democrat", `1` = "Democrat", `2` = "Democrat", `3` = "Independent",
               `4` = "Republican", `5` = "Republican", `6` = "Republican")
gss$party_f <- map_values(clean_numeric(gss$PARTYID), party_map)

urban_map <- c(`1` = "Big city", `2` = "Big city",
               `3` = "Suburb", `4` = "Suburb", `5` = "Suburb", `6` = "Suburb",
               `7` = "Small/rural town", `8` = "Small/rural town",
               `9` = "Small/rural town", `10` = "Small/rural town")
gss$urban_f <- map_values(clean_numeric(gss$XNORCSIZ), urban_map)

gss$health_f <- map_values(clean_numeric(gss$HEALTH),
                           c(`1` = "Excellent", `2` = "Good", `3` = "Fair", `4` = "Poor"))

socfrend_map <- c(`1` = "Weekly or more", `2` = "Weekly or more", `3` = "Weekly or more",
                  `4` = "Sometimes", `5` = "Sometimes", `6` = "Sometimes", `7` = "Never")
gss$socfrend_f <- map_values(clean_numeric(gss$SOCFREND), socfrend_map)

gss$sexornt_f <- map_values(clean_numeric(gss$SEXORNT),
                            c(`3` = "Heterosexual/Straight", `1` = "Gay/Lesbian/Homosexual",
                              `2` = "Bisexual"))

gss$region_f <- map_values(clean_numeric(gss$REGION),
                           c(`1` = "Northeast", `2` = "Midwest", `3` = "South", `4` = "West"))

# Weighted mean happiness for each bridge row's GSS bin (pairwise deletion).
bridge$actual <- NA_real_
bridge$gss_n  <- NA_integer_
for (i in seq_len(nrow(bridge))) {
  col <- bridge$gss_col[i]; lvl <- bridge$gss_level[i]
  sel <- !is.na(gss[[col]]) & gss[[col]] == lvl
  bridge$actual[i] <- weighted_mean_na(gss$happy[sel], w[sel])
  bridge$gss_n[i]  <- sum(sel & !is.na(gss$happy))
}

write.csv(bridge[, c("dimension", "subgroup", "subgroup_label", "gss_col",
                     "gss_level", "actual", "gss_n")],
          file.path(OUT_DIR, "gss_actual_by_subgroup.csv"), row.names = FALSE)

# ============================================================================
# STEP 2: reshape survey to long + is_own_group
# ============================================================================

resp <- read.csv(RESP_FILE, stringsAsFactors = FALSE, check.names = TRUE)
stopifnot(!anyDuplicated(resp$ResponseId))
cat(sprintf("Survey respondents (cleaned): %d\n", nrow(resp)))

xw <- read.csv(XWALK_FILE, stringsAsFactors = FALSE)
xw$slider_var[xw$slider_var == ""] <- NA

# dimension -> self-report column in the cleaned survey (from the crosswalk).
dim_srv <- unique(xw[, c("dimension", "self_report_var")])
stopifnot(all(dim_srv$self_report_var %in% names(resp)))
stopifnot(setequal(dim_srv$dimension, DIMENSION_ORDER))

# Long predictions: one row per respondent x subgroup slider.
long <- do.call(rbind, lapply(seq_len(nrow(bridge)), function(i) {
  sv <- bridge$subgroup[i]
  data.frame(respondent_id  = resp$ResponseId,
             dimension       = bridge$dimension[i],
             subgroup        = sv,
             subgroup_label  = bridge$subgroup_label[i],
             predicted       = suppressWarnings(as.numeric(resp[[sv]])),
             actual          = bridge$actual[i],
             stringsAsFactors = FALSE)
}))
long$abs_error    <- abs(long$predicted - long$actual)
long$signed_error <- long$predicted - long$actual

# Each respondent's own subgroup on each dimension, via the crosswalk.
own <- do.call(rbind, lapply(seq_len(nrow(dim_srv)), function(k) {
  dm  <- dim_srv$dimension[k]
  srv <- dim_srv$self_report_var[k]
  key <- xw[xw$self_report_var == srv, c("self_report_value", "slider_var")]
  names(key) <- c("val", "own_subgroup")
  m <- merge(
    data.frame(respondent_id = resp$ResponseId,
               val = trimws(as.character(resp[[srv]])), stringsAsFactors = FALSE),
    key, by = "val", all.x = TRUE, sort = FALSE
  )
  m$dimension <- dm
  m[, c("respondent_id", "dimension", "own_subgroup")]
}))

unmatched <- own[is.na(own$own_subgroup) & !is.na(own$respondent_id), ]
tab_unmatched <- as.data.frame(table(dimension = unmatched$dimension))
cat("\nRespondents with no clean own-group mapping, by dimension:\n")
print(tab_unmatched[tab_unmatched$Freq > 0, ], row.names = FALSE)

long <- merge(long, own, by = c("respondent_id", "dimension"), all.x = TRUE, sort = FALSE)
long$is_own_group <- ifelse(is.na(long$own_subgroup), NA_integer_,
                            as.integer(long$subgroup == long$own_subgroup))

long <- long[order(long$respondent_id,
                   factor(long$dimension, levels = DIMENSION_ORDER),
                   long$subgroup), ]
write.csv(long[, c("respondent_id", "dimension", "subgroup", "subgroup_label",
                   "predicted", "actual", "abs_error", "signed_error",
                   "own_subgroup", "is_own_group")],
          file.path(OUT_DIR, "prediction_errors_long.csv"), row.names = FALSE)
cat(sprintf("\nLong dataset: %d rows (%d respondents x %d subgroups)\n",
            nrow(long), nrow(resp), nrow(bridge)))

# ============================================================================
# STEP 3: pooled regression, abs_error ~ X_i + subgroup FE, clustered by respondent
# ============================================================================

# Respondent demographic factor per dimension (levels = survey subgroup names;
# unmapped "Other" answers kept as an explicit level so those respondents stay in
# the model). Reference level = the run_betas_regression.R baseline group.
own_wide <- reshape(own, idvar = "respondent_id", timevar = "dimension",
                    direction = "wide")
names(own_wide) <- sub("^own_subgroup\\.", "", names(own_wide))

BASELINE <- c(
  "Gender" = "female", "Age" = "age_35_64", "Race" = "white",
  "Education" = "HS_and_college", "Income" = "middle_income",
  "Marital Status" = "married", "Children Ever Born" = "no_children",
  "Religious Attendance" = "sometimes_attend", "Party" = "independent",
  "Urban vs Rural" = "suburb", "Health" = "good_health",
  "Socializing with Friends" = "sometimes_socialize",
  "Sexual Orientation" = "heterosexual", "Region" = "south"
)
RESP_VAR <- c(
  "Gender" = "resp_gender", "Age" = "resp_age", "Race" = "resp_race",
  "Education" = "resp_educ", "Income" = "resp_income",
  "Marital Status" = "resp_marital", "Children Ever Born" = "resp_children",
  "Religious Attendance" = "resp_attend", "Party" = "resp_party",
  "Urban vs Rural" = "resp_urban", "Health" = "resp_health",
  "Socializing with Friends" = "resp_social",
  "Sexual Orientation" = "resp_sexornt", "Region" = "resp_region"
)

for (dm in DIMENSION_ORDER) {
  v <- own_wide[[dm]]
  v[is.na(v)] <- "Other/unmapped"
  base_lvl <- BASELINE[[dm]]
  lvls <- c(base_lvl, sort(setdiff(unique(v), base_lvl)))
  own_wide[[RESP_VAR[[dm]]]] <- factor(v, levels = lvls)
}

model_df <- merge(long, own_wide[, c("respondent_id", unname(RESP_VAR))],
                  by = "respondent_id", sort = FALSE)
model_df$subgroup <- factor(model_df$subgroup, levels = bridge$subgroup)

rhs <- paste(c("subgroup", unname(RESP_VAR)), collapse = " + ")
form <- as.formula(paste("abs_error ~", rhs))

keep <- stats::complete.cases(model_df[, c("abs_error", "subgroup", unname(RESP_VAR))])
model_df <- model_df[keep, ]
cat(sprintf("\nRegression rows: %d  |  clusters (respondents): %d\n",
            nrow(model_df), length(unique(model_df$respondent_id))))

fit <- lm(form, data = model_df)

# CR1 cluster-robust (sandwich) SEs, clustered by respondent - same hand-rolled
# estimator as run_betas_regression.R, here unweighted (w = 1).
cluster_robust_se <- function(X, u, cluster, K_full) {
  XtX_inv <- solve(t(X) %*% X)
  score <- X * u
  ug <- rowsum(score, cluster)
  meat <- t(ug) %*% ug
  G <- nrow(ug); N <- nrow(X)
  correction <- (G / (G - 1)) * ((N - 1) / (N - K_full))
  vcov <- XtX_inv %*% meat %*% XtX_inv * correction
  list(se = sqrt(diag(vcov)), G = G)
}

beta_all <- coef(fit)
aliased <- is.na(beta_all)
if (any(aliased)) {
  cat("\nlm() dropped these terms as collinear (SE reported as NA):\n  ",
      paste(names(beta_all)[aliased], collapse = "\n   "), "\n", sep = "")
}
X <- model.matrix(fit)[, !aliased, drop = FALSE]
u <- residuals(fit)
cr <- cluster_robust_se(X, u, model_df$respondent_id, K_full = sum(!aliased))

beta <- beta_all
se <- rep(NA_real_, length(beta_all))
names(se) <- names(beta_all)
se[!aliased] <- cr$se[names(beta_all)[!aliased]]

z <- beta / se
reg_out <- data.frame(
  term = names(beta),
  term_type = ifelse(names(beta) == "(Intercept)", "intercept",
              ifelse(grepl("^subgroup", names(beta)), "subgroup_FE",
                     "respondent_characteristic")),
  beta = as.numeric(beta),
  se = as.numeric(se),
  z = as.numeric(z),
  p = as.numeric(2 * pnorm(-abs(z))),
  ci_lo = as.numeric(beta - 1.96 * se),
  ci_hi = as.numeric(beta + 1.96 * se),
  stringsAsFactors = FALSE
)
attr(reg_out, "n_obs") <- nrow(model_df)
write.csv(reg_out, file.path(OUT_DIR, "accuracy_regression_2a.csv"), row.names = FALSE)

sink(file.path(OUT_DIR, "accuracy_regression_2a.txt"))
cat("Analysis 2a - pooled regression\n")
cat("abs_error_ij = b0 + b1*X_i + subgroup_FE_j + e_ij\n")
cat(sprintf("Rows: %d   Clusters (respondents): %d   R^2: %.4f\n\n",
            nrow(model_df), cr$G, summary(fit)$r.squared))
cat("CR1 cluster-robust SEs (clustered by respondent).\n")
cat("Respondent-characteristic terms (subgroup FE omitted from this print):\n\n")
rc <- reg_out[reg_out$term_type == "respondent_characteristic", ]
print(within(rc, {
  beta <- round(beta, 4); se <- round(se, 4); z <- round(z, 2)
  p <- round(p, 4); ci_lo <- round(ci_lo, 4); ci_hi <- round(ci_hi, 4)
}), row.names = FALSE)
cat("\nIntercept:\n")
print(within(reg_out[reg_out$term_type == "intercept", ], {
  beta <- round(beta, 4); se <- round(se, 4)
}), row.names = FALSE)
cat("\n(Full table incl. subgroup fixed effects: accuracy_regression_2a.csv)\n")
sink()

# ============================================================================
# STEP 4: bivariate - respondent-level mean abs error, grouped by own category
# ============================================================================

resp_mae <- aggregate(abs_error ~ respondent_id, data = long, FUN = mean)
names(resp_mae)[2] <- "resp_mae"
cat(sprintf("\nRespondent mean |error|: mean %.3f, sd %.3f, range %.3f-%.3f\n",
            mean(resp_mae$resp_mae), sd(resp_mae$resp_mae),
            min(resp_mae$resp_mae), max(resp_mae$resp_mae)))

biv <- do.call(rbind, lapply(DIMENSION_ORDER, function(dm) {
  o <- own[own$dimension == dm & !is.na(own$own_subgroup), c("respondent_id", "own_subgroup")]
  m <- merge(o, resp_mae, by = "respondent_id")
  grp <- split(m$resp_mae, m$own_subgroup)
  data.frame(
    dimension = dm,
    subgroup = names(grp),
    n_respondents = vapply(grp, length, integer(1)),
    mean_abs_error = vapply(grp, mean, numeric(1)),
    se = vapply(grp, function(x) sd(x) / sqrt(length(x)), numeric(1)),
    stringsAsFactors = FALSE
  )
}))
biv <- merge(biv, bridge[, c("subgroup", "subgroup_label")], by = "subgroup", all.x = TRUE)
biv$ci_lo <- biv$mean_abs_error - 1.96 * biv$se
biv$ci_hi <- biv$mean_abs_error + 1.96 * biv$se

# order rows: dimension order, then bridge subgroup order within dimension
biv$dimension <- factor(biv$dimension, levels = DIMENSION_ORDER)
biv$subgroup  <- factor(biv$subgroup, levels = bridge$subgroup)
biv <- biv[order(biv$dimension, biv$subgroup), ]
biv$dimension <- as.character(biv$dimension)
biv$subgroup  <- as.character(biv$subgroup)

write.csv(biv[, c("dimension", "subgroup", "subgroup_label", "n_respondents",
                  "mean_abs_error", "se", "ci_lo", "ci_hi")],
          file.path(OUT_DIR, "accuracy_by_respondent_group.csv"), row.names = FALSE)

# ============================================================================
# STEP 5: dot-and-CI plot - one block of rows per respondent demographic dimension
# ============================================================================

biv$row_id <- seq_len(nrow(biv))
gap <- 0.8
dim_change <- c(0, cumsum(head(as.integer(factor(biv$dimension, levels = DIMENSION_ORDER)), -1) !=
                          tail(as.integer(factor(biv$dimension, levels = DIMENSION_ORDER)), -1)))
biv$y <- rev(biv$row_id + gap * dim_change)

overall_mae <- mean(resp_mae$resp_mae)
xlim <- range(c(biv$ci_lo, biv$ci_hi, overall_mae))
xlim <- xlim + c(-0.02, 0.02) * diff(xlim)

png(file.path(OUT_DIR, "accuracy_by_respondent_group.png"),
    width = 1150, height = 1500, res = 130)
op <- par(mar = c(5, 15, 3, 2), xaxs = "i")

plot(NA, xlim = xlim, ylim = c(min(biv$y) - 1, max(biv$y) + 1),
     xlab = "Mean absolute error in predicted happiness (1-3 scale)", ylab = "",
     yaxt = "n", bty = "n")
abline(v = overall_mae, col = "grey65", lty = 2)
axis(1)

# per-group rows
segments(biv$ci_lo, biv$y, biv$ci_hi, biv$y, col = MAROON, lwd = 2)
points(biv$mean_abs_error, biv$y, pch = 19, col = MAROON, cex = 1.1)
axis(2, at = biv$y,
     labels = sprintf("%s  (n=%d)", biv$subgroup_label, biv$n_respondents),
     las = 1, tick = FALSE, cex.axis = 0.8, line = -0.5)

# dimension headers + separators
for (dm in DIMENSION_ORDER) {
  yy <- biv$y[biv$dimension == dm]
  mtext(dm, side = 2, at = max(yy) + gap * 0.9, las = 1, adj = 1,
        font = 2, cex = 0.85, line = 13.5)
}
sep_y <- sort(unique(vapply(DIMENSION_ORDER[-1], function(dm)
  max(biv$y[biv$dimension == dm]) + gap * 0.55, numeric(1))))
abline(h = sep_y, col = "grey88", lwd = 0.8)

title(main = "Prediction accuracy by respondent's own demographic group",
      cex.main = 1.05)
mtext(sprintf("Dashed line = overall mean |error| (%.3f). Each point = mean over that group's respondents, all 44 predictions each. Whiskers = 95%% CI.",
              overall_mae),
      side = 1, line = 3.4, cex = 0.7, col = "grey35")
par(op)
dev.off()

cat(sprintf("\nWrote outputs to %s\n", OUT_DIR))
cat("  gss_actual_by_subgroup.csv\n  prediction_errors_long.csv\n",
    "  accuracy_regression_2a.csv / .txt\n  accuracy_by_respondent_group.csv / .png\n", sep = "")
