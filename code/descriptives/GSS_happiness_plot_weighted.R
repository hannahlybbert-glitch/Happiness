# Author: Hannah Lybbert, assisted by Claude
# Created: 2026-08-04; Updated: 2026-08-04
# Purpose: Design-based, survey-weighted version of GSS_happiness_plot.py. Same
#   2004-2024 GSS subgroup buckets (issue #5) and same underlying HAPPY variable,
#   but subgroup means/CIs come from the `survey` package using WTSSNRPS (NORC's
#   recommended post-stratification, nonresponse-adjusted weight for 2004-2024) plus
#   VPSU/VSTRAT for design-based (clustered, stratified) standard errors - not just
#   weight-adjusted point estimates with naive SEs.
#
#   VSTRAT codes are already globally unique across survey years in this file (ranges
#   don't overlap year to year), so no YEAR interaction is needed when specifying strata.
#
# Requires: data/ProcessGSS/GSS_main.csv containing WTSSNRPS, VPSU, VSTRAT
#   (re-run code/ProcessGSS/1_clean_filter_GSS_raw.py if those columns are missing).
# Packages: install.packages(c("dplyr", "survey", "ggplot2", "here"))
#
# Outputs (output/descriptives/GSS/):
#   GSS_happiness_plot_weighted.png
#   GSS_happiness_table_weighted.md

suppressPackageStartupMessages({
  library(dplyr)
  library(survey)
  library(ggplot2)
  library(here)
})

# GSS's VSTRAT/VPSU are a collapsed (2-PSU-per-stratum) design meant for exactly this
# kind of variance estimation, but if any stratum still resolves to a single PSU,
# "adjust" centers that PSU's contribution at the stratum mean instead of erroring out.
options(survey.lonely.psu = "adjust")

UCHICAGO_MAROON <- "#800000"
CATEGORY_STRIP_COLOR <- "#767676"

INPUT_FILE <- here::here("data", "ProcessGSS", "GSS_main.csv")
OUTPUT_PLOT <- here::here("output", "descriptives", "GSS", "GSS_happiness_plot_weighted.png")
OUTPUT_TABLE <- here::here("output", "descriptives", "GSS", "GSS_happiness_table_weighted.md")

# ============================================================================
# RECODING (mirrors label_* functions in GSS_happiness_plot.py)
# ============================================================================

clean_numeric <- function(x, exclude = numeric(0)) {
  x <- suppressWarnings(as.numeric(x))
  x[x %in% exclude] <- NA
  x
}

map_values <- function(code, mapping) {
  # mapping: named numeric vector, e.g. c(`1` = "White", `2` = "Black")
  unname(mapping[as.character(code)])
}

label_happy <- function(x) {
  code <- clean_numeric(x)
  map_values(code, c(`1` = "3", `2` = "2", `3` = "1")) |> as.numeric()
}

label_age <- function(x) {
  code <- clean_numeric(x)
  cut(code, breaks = c(0, 34, 64, Inf), labels = c("18-34", "35-64", "65+"))
}
AGE_LEVELS <- c("18-34", "35-64", "65+")

label_sex <- function(x) {
  code <- clean_numeric(x)
  map_values(code, c(`1` = "Man", `2` = "Woman"))
}
SEX_LEVELS <- c("Man", "Woman")

label_race <- function(x) {
  # Uses RACECEN1 only, per issue #5 - matches GSS_happiness_plot.py's label_race().
  code <- clean_numeric(x)
  mapping <- c(`1` = "White", `2` = "Black", `16` = "Hispanic",
               `4` = "Asian", `5` = "Asian", `6` = "Asian", `7` = "Asian",
               `8` = "Asian", `9` = "Asian", `10` = "Asian")
  map_values(code, mapping)
}
RACE_LEVELS <- c("White", "Black", "Hispanic", "Asian")

label_education <- function(x) {
  code <- clean_numeric(x)
  mapping <- c(`0` = "Less than HS", `1` = "HS+some college", `2` = "HS+some college",
               `3` = "Bachelors+Graduate", `4` = "Bachelors+Graduate")
  map_values(code, mapping)
}
EDUCATION_LEVELS <- c("Less than HS", "HS+some college", "Bachelors+Graduate")

label_employment <- function(x) {
  code <- clean_numeric(x)
  mapping <- c(`1` = "Employed", `2` = "Employed", `3` = "Employed", `4` = "Unemployed",
               `5` = "Not in Labor Force", `6` = "Not in Labor Force",
               `7` = "Not in Labor Force", `8` = "Not in Labor Force")
  map_values(code, mapping)
}
EMPLOYMENT_LEVELS <- c("Employed", "Unemployed", "Not in Labor Force")

label_marital <- function(x) {
  code <- clean_numeric(x)
  mapping <- c(`1` = "Married", `2` = "Widowed", `3` = "Separated/Divorced",
               `4` = "Separated/Divorced", `5` = "Never Married")
  map_values(code, mapping)
}
MARITAL_LEVELS <- c("Married", "Widowed", "Separated/Divorced", "Never Married")

label_childs <- function(x) {
  code <- clean_numeric(x)
  ifelse(is.na(code), NA_character_, ifelse(code == 0, "No Children", "Children"))
}
CHILDS_LEVELS <- c("No Children", "Children")

label_attend <- function(x) {
  code <- clean_numeric(x)
  mapping <- c(`0` = "Never", `1` = "Sometimes", `2` = "Sometimes", `3` = "Sometimes",
               `4` = "Sometimes", `5` = "Sometimes", `6` = "Sometimes",
               `7` = "Weekly or more", `8` = "Weekly or more")
  map_values(code, mapping)
}
ATTEND_LEVELS <- c("Never", "Sometimes", "Weekly or more")

label_party <- function(x) {
  code <- clean_numeric(x)
  mapping <- c(`0` = "Democrat", `1` = "Democrat", `2` = "Democrat", `3` = "Independent",
               `4` = "Republican", `5` = "Republican", `6` = "Republican")
  map_values(code, mapping)
}
PARTY_LEVELS <- c("Democrat", "Independent", "Republican")

label_urban <- function(x) {
  code <- clean_numeric(x)
  mapping <- c(`1` = "Big city", `2` = "Big city",
               `3` = "Suburb", `4` = "Suburb", `5` = "Suburb", `6` = "Suburb",
               `7` = "Small/rural town", `8` = "Small/rural town",
               `9` = "Small/rural town", `10` = "Small/rural town")
  map_values(code, mapping)
}
URBAN_LEVELS <- c("Big city", "Suburb", "Small/rural town")

label_health <- function(x) {
  code <- clean_numeric(x)
  mapping <- c(`1` = "Good", `2` = "Good", `3` = "Fair", `4` = "Poor")
  map_values(code, mapping)
}
HEALTH_LEVELS <- c("Good", "Fair", "Poor")

label_socfrend <- function(x) {
  code <- clean_numeric(x)
  mapping <- c(`1` = "Weekly or more", `2` = "Weekly or more", `3` = "Weekly or more",
               `4` = "Sometimes", `5` = "Sometimes", `6` = "Sometimes", `7` = "Never")
  map_values(code, mapping)
}
SOCFREND_LEVELS <- c("Weekly or more", "Sometimes", "Never")

label_dwelown <- function(x) {
  code <- clean_numeric(x)
  mapping <- c(`1` = "Own", `2` = "Rent")
  map_values(code, mapping)
}
DWELOWN_LEVELS <- c("Own", "Rent")

# (category display name, group column name, level order) - grp columns added to df below
SUBGROUP_SPECS <- list(
  list(category = "Age", col = "grp_age", levels = AGE_LEVELS),
  list(category = "Gender", col = "grp_sex", levels = SEX_LEVELS),
  list(category = "Race", col = "grp_race", levels = RACE_LEVELS),
  list(category = "Education", col = "grp_education", levels = EDUCATION_LEVELS),
  list(category = "Income", col = "grp_income", levels = c("Low", "Mid", "High")),
  list(category = "Employment", col = "grp_employment", levels = EMPLOYMENT_LEVELS),
  list(category = "Marital Status", col = "grp_marital", levels = MARITAL_LEVELS),
  list(category = "Children Ever Born", col = "grp_childs", levels = CHILDS_LEVELS),
  list(category = "Religious Attendance", col = "grp_attend", levels = ATTEND_LEVELS),
  list(category = "Party", col = "grp_party", levels = PARTY_LEVELS),
  list(category = "Urban vs Rural", col = "grp_urban", levels = URBAN_LEVELS),
  list(category = "Health", col = "grp_health", levels = HEALTH_LEVELS),
  list(category = "Socializing with Friends", col = "grp_socfrend", levels = SOCFREND_LEVELS),
  list(category = "Own or Rent", col = "grp_dwelown", levels = DWELOWN_LEVELS)
)

# ============================================================================
# LOAD + RECODE
# ============================================================================

df <- read.csv(INPUT_FILE, stringsAsFactors = FALSE)

df <- df |>
  mutate(
    happy = label_happy(HAPPY),
    grp_age = label_age(AGE),
    grp_sex = label_sex(SEX),
    grp_race = label_race(RACECEN1),
    grp_education = label_education(DEGREE),
    grp_employment = label_employment(WRKSTAT),
    grp_marital = label_marital(MARITAL),
    grp_childs = label_childs(CHILDS),
    grp_attend = label_attend(ATTEND),
    grp_party = label_party(PARTYID),
    grp_urban = label_urban(XNORCSIZ),
    grp_health = label_health(HEALTH),
    grp_socfrend = label_socfrend(SOCFREND),
    grp_dwelown = label_dwelown(DWELOWN)
  )

# Income terciles: simple weight-only quantile cutpoints (not design-based - these are
# just bucket boundaries, not an estimate that needs a CI). The happiness mean *within*
# each resulting bucket is still computed with the full design below.
weighted_quantile <- function(x, w, probs) {
  keep <- !is.na(x) & !is.na(w)
  x <- x[keep]; w <- w[keep]
  ord <- order(x)
  x <- x[ord]; w <- w[ord]
  cum_w <- cumsum(w) / sum(w)
  vapply(probs, function(p) x[which(cum_w >= p)[1]], numeric(1))
}
income_cuts <- weighted_quantile(df$REALINC, df$WTSSNRPS, c(1 / 3, 2 / 3))
cat(sprintf("Income tercile cutpoints (weighted, REALINC): %.2f, %.2f\n",
            income_cuts[1], income_cuts[2]))
df$grp_income <- cut(df$REALINC, breaks = c(-Inf, income_cuts, Inf),
                      labels = c("Low", "Mid", "High"), right = TRUE)

# ============================================================================
# SURVEY DESIGN
# ============================================================================

design <- svydesign(ids = ~VPSU, strata = ~VSTRAT, weights = ~WTSSNRPS,
                     nest = TRUE, data = df)

# ============================================================================
# SUMMARIZE
# ============================================================================

summarize_subgroup <- function(design, df, category, col, level_order) {
  keep <- !is.na(df$happy) & !is.na(df[[col]]) & df[[col]] %in% level_order
  sub_design <- subset(design, keep)

  form <- as.formula(paste0("~", col))
  res <- svyby(~happy, form, sub_design, svymean, na.rm = TRUE)

  n_tab <- table(factor(df[[col]][keep], levels = level_order))

  out <- data.frame(
    category = category,
    subgroup = as.character(res[[col]]),
    n = as.integer(n_tab[as.character(res[[col]])]),
    mean = as.numeric(coef(res)),
    se = as.numeric(SE(res)),
    stringsAsFactors = FALSE
  )
  out$ci_lo <- out$mean - 1.96 * out$se
  out$ci_hi <- out$mean + 1.96 * out$se

  # Reorder to match level_order (svyby sorts alphabetically by default)
  out <- out[match(level_order, out$subgroup), ]
  out <- out[!is.na(out$subgroup), ]
  out
}

results <- do.call(rbind, lapply(SUBGROUP_SPECS, function(spec) {
  summarize_subgroup(design, df, spec$category, spec$col, spec$levels)
}))
rownames(results) <- NULL

overall_design <- subset(design, !is.na(happy))
overall_est <- svymean(~happy, overall_design, na.rm = TRUE)
overall_mean <- as.numeric(coef(overall_est))
overall_se <- as.numeric(SE(overall_est))
overall_n <- sum(!is.na(df$happy))
overall_ci_lo <- overall_mean - 1.96 * overall_se
overall_ci_hi <- overall_mean + 1.96 * overall_se

cat(sprintf("\nWeighted overall average happiness score: %.3f (95%% CI: %.3f, %.3f), n=%d\n",
            overall_mean, overall_ci_lo, overall_ci_hi, overall_n))

# ============================================================================
# PLOT
# ============================================================================

category_order <- unique(results$category)
results$category_f <- factor(results$category, levels = rev(category_order))

# Build a single "row key" per subgroup so ordering within + across categories is
# preserved top-to-bottom exactly as in SUBGROUP_SPECS.
results$row_key <- paste(results$category, results$subgroup, sep = " | ")
row_order <- unlist(lapply(SUBGROUP_SPECS, function(spec) paste(spec$category, spec$levels, sep = " | ")))
row_order <- intersect(row_order, results$row_key)
results$row_f <- factor(results$row_key, levels = rev(row_order))

y_labels <- setNames(sprintf("%s (n=%s)", results$subgroup, formatC(results$n, big.mark = ",")),
                      results$row_key)

theme_weighted <- function(base_size = 11) {
  theme_bw(base_size = base_size) +
    theme(
      panel.grid.minor = element_blank(),
      panel.grid.major.y = element_blank(),
      panel.grid.major.x = element_blank(),
      panel.border = element_blank(),
      axis.line.x = element_line(color = "black", linewidth = 0.4),
      axis.ticks.y = element_blank(),
      axis.text.y = element_text(size = 10.5, lineheight = 0.85),
      axis.text.x = element_text(size = 11),
      axis.title.x = element_text(size = 13, margin = margin(t = 8)),
      plot.title = element_text(size = 18, hjust = 0.5),
      plot.subtitle = element_text(size = 10, color = "gray40", hjust = 0.5),
      legend.position = "none",
      panel.spacing.y = unit(4, "pt"),
      strip.background = element_rect(fill = CATEGORY_STRIP_COLOR, color = NA),
      strip.text.y.left = element_text(size = 11, face = "bold", color = "white",
                                        angle = 0, hjust = 0.5, lineheight = 1.1),
      strip.placement = "outside",
      plot.margin = margin(10, 15, 10, 5, "pt")
    )
}

p <- ggplot(results, aes(x = mean, y = row_f)) +
  geom_vline(xintercept = overall_mean, linetype = "dashed", linewidth = 0.7, color = "dimgray") +
  geom_errorbarh(aes(xmin = ci_lo, xmax = ci_hi), height = 0, linewidth = 1.1, color = UCHICAGO_MAROON) +
  geom_point(size = 2.2, color = UCHICAGO_MAROON) +
  facet_grid(category_f ~ ., scales = "free_y", space = "free_y", switch = "y") +
  scale_y_discrete(labels = y_labels) +
  labs(
    title = "Happiness across U.S. subgroups (survey-weighted)",
    subtitle = paste0("General Social Survey, 2004-2024; WTSSNRPS-weighted subgroup means with ",
                       "design-based 95% CIs (VPSU/VSTRAT)"),
    x = "Weighted Average Happiness Score (1=Not too happy, 2=Pretty happy, 3=Very happy)",
    y = NULL
  ) +
  theme_weighted()

n_rows <- nrow(results)
plot_height <- max(6, 0.32 * n_rows + 1.5)
ggsave(OUTPUT_PLOT, p, width = 11, height = plot_height, dpi = 300)
cat(sprintf("Wrote plot with %d subgroup rows to %s\n", n_rows, OUTPUT_PLOT))

# ============================================================================
# TABLE
# ============================================================================

md_lines <- c(
  "# Happiness across U.S. subgroups (survey-weighted)",
  "",
  "General Social Survey, 2004-2024; WTSSNRPS-weighted subgroup means with design-based 95% CIs (VPSU/VSTRAT)",
  "",
  sprintf("Income tercile cutpoints (weighted, REALINC): Low < %.2f <= Mid < %.2f <= High",
          income_cuts[1], income_cuts[2]),
  "",
  "| Category | Subgroup | N | Weighted Mean | SE | 95% CI |",
  "|---|---|---|---|---|---|",
  sprintf("| Overall | Overall | %s | %.3f | %.3f | (%.3f, %.3f) |",
          formatC(overall_n, big.mark = ","), overall_mean, overall_se, overall_ci_lo, overall_ci_hi)
)

last_category <- NULL
for (i in seq_len(nrow(results))) {
  row <- results[i, ]
  category_cell <- if (!identical(row$category, last_category)) row$category else ""
  md_lines <- c(md_lines, sprintf("| %s | %s | %s | %.3f | %.3f | (%.3f, %.3f) |",
                                   category_cell, row$subgroup, formatC(row$n, big.mark = ","),
                                   row$mean, row$se, row$ci_lo, row$ci_hi))
  last_category <- row$category
}

dir.create(dirname(OUTPUT_TABLE), recursive = TRUE, showWarnings = FALSE)
writeLines(md_lines, OUTPUT_TABLE)
cat(sprintf("Wrote table to %s\n", OUTPUT_TABLE))
