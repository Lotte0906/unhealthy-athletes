# Research Design

## 1. Research Objective

The primary objective of this project is to investigate the relationship between elite athletic participation and longevity, using Olympic athletes as the study population.

The ultimate research question is:

**How does the longevity of Olympic athletes compare with that of comparable individuals in the general population?**

Before addressing this question, the project investigates survival patterns and factors associated with longevity within the Olympic athlete population.

## 2. Research Approach

The research follows an incremental approach, progressing from descriptive statistics towards increasingly advanced statistical methods.

Each research question combines mathematical theory, practical implementation, statistical analysis, and interpretation.

Preliminary analyses will be conducted using the existing biographical dataset. Analyses will subsequently be repeated using improved datasets to evaluate the reliability and robustness of the findings.

All preliminary results should be interpreted in the context of known data-quality limitations.

## 3. Research Roadmap

| ID | Research topic | Difficulty | Status |
|---|---|---|---|
| RQ1 | Lifespan distributions | Introductory | In progress |
| RQ2 | Survival differences by sex | Intermediate | Planned |
| RQ3 | Medal status and longevity | Intermediate | Planned |
| RQ4 | Differences between sports | Intermediate | Planned |
| RQ5 | Generational differences | Intermediate–Advanced | Planned |
| RQ6 | Age at first Olympic participation | Intermediate–Advanced | Planned |
| RQ7 | Repeated Olympic participation | Advanced | Planned |
| RQ8 | Multivariable survival modelling | Advanced | Planned |
| RQ9 | Data quality and robustness | Advanced | Planned |
| RQ10 | General-population comparison | Advanced | Planned |

### Status Definitions

- **Planned:** Research question identified but work has not started.
- **In progress:** Mathematical theory, methodology, or analysis is currently being developed.
- **Preliminary:** Initial analysis completed using the available dataset.
- **Under review:** Results are being reassessed following methodological or data-quality improvements.
- **Completed:** Analysis, validation, interpretation, and documentation completed within the defined scope.

## 4. Research Workflow

For each research question, the following steps will be considered:

- [ ] Formulate the research question and define the target population.
- [ ] Study the relevant mathematical theory.
- [ ] Investigate statistical assumptions and limitations.
- [ ] Formulate hypotheses where appropriate.
- [ ] Define the required data and inclusion criteria.
- [ ] Select and justify the statistical methodology.
- [ ] Implement the analysis in Python.
- [ ] Evaluate results and statistical uncertainty.
- [ ] Investigate potential biases and robustness.
- [ ] Document findings and conclusions.
- [ ] Review and update the GitHub repository.

The depth of each step depends on the complexity of the research question.

## 5. Research Questions

### RQ1 — Lifespan Distributions

**Status:** In progress

**Research question:**

What are the observed lifespan characteristics of Olympic athletes, and what can the available data tell us about their underlying lifetime distribution?

**Objective:**

Investigate the distribution of observed ages at death and establish the statistical foundations required for subsequent survival analyses.

**Mathematical theory:**

- [ ] Populations and samples
- [ ] Random variables and realizations
- [ ] Parameters, statistics, estimators, and estimates
- [ ] Probability mass and density functions
- [ ] Cumulative distribution functions
- [ ] Empirical cumulative distribution functions
- [ ] Mean, median, mode, and quantiles
- [ ] Variance, standard deviation, and interquartile range
- [ ] Raw and central moments
- [ ] Skewness and kurtosis
- [ ] Bias and consistency of estimators
- [ ] Sampling distributions and standard errors
- [ ] Law of large numbers
- [ ] Central limit theorem
- [ ] Histograms and kernel density estimation
- [ ] Introduction to censoring and truncation

**Potential methodology:**

Descriptive statistics, histograms, empirical distribution functions, boxplots, and density estimation.

**Required data:**

- Athlete identifier
- Date of birth
- Date of death, where applicable
- Vital status
- Reference date

**Hypotheses:** Not required for the initial descriptive analysis.

**Methodological decisions:** To be determined.

**Key limitations:** Incomplete lifetime observations, missing biographical information, selection bias, and potential identity-matching errors.

**Results and conclusions:** Pending.

**Implementation and notebook:** Pending.

---

### RQ2 — Survival Differences by Sex

**Status:** Planned

**Research question:**

How does survival differ between male and female Olympic athletes?

**Objective:**

Introduce survival analysis and investigate differences between demographic groups while accounting for incomplete lifetime observations.

**Mathematical theory:**

- [ ] Lifetime random variables
- [ ] Survival functions
- [ ] Hazard functions
- [ ] Cumulative hazard functions
- [ ] Right censoring
- [ ] Left truncation and delayed entry
- [ ] Risk sets
- [ ] Kaplan–Meier estimator
- [ ] Greenwood's formula
- [ ] Confidence intervals for survival estimates
- [ ] Log-rank test

**Potential methodology:**

Kaplan–Meier survival curves and log-rank tests, accounting for delayed entry and relevant cohort differences.

**Required data:**

RQ1 variables, sex, and age at first Olympic participation.

**Hypotheses:** To be determined.

**Methodological decisions:** To be determined.

**Key limitations:** Historical differences in Olympic participation, birth-cohort effects, selection bias, and unequal follow-up.

**Results and conclusions:** Pending.

**Implementation and notebook:** Pending.

---

### RQ3 — Medal Status and Longevity

**Status:** Planned

**Research question:**

Is Olympic medal achievement associated with differences in athlete longevity?

**Objective:**

Investigate whether sporting achievement is associated with survival and develop a deeper understanding of statistical inference.

**Mathematical theory:**

- [ ] Null and alternative hypotheses
- [ ] Test statistics and rejection regions
- [ ] P-values
- [ ] Type I and Type II errors
- [ ] Statistical significance
- [ ] Effect sizes
- [ ] Confidence intervals
- [ ] Statistical power
- [ ] Confounding variables
- [ ] Immortal time bias

**Potential methodology:**

Survival comparisons using medal status defined at an appropriate baseline, or methods that account for changes in medal status over time.

**Required data:**

RQ2 variables, medal status, medal achievement dates or years, and Olympic participation history.

**Hypotheses:** To be determined.

**Methodological decisions:** To be determined.

**Key limitations:** Confounding by sport, sex, birth cohort, and career duration; immortal time bias when using lifetime medal status.

**Results and conclusions:** Pending.

**Implementation and notebook:** Pending.

---

### RQ4 — Differences Between Sports

**Status:** Planned

**Research question:**

Does longevity differ between Olympic athletes competing in different sports?

**Objective:**

Investigate whether survival patterns vary across sporting disciplines and broader sport categories.

**Mathematical theory:**

- [ ] Multiple-group comparisons
- [ ] Categorical variables
- [ ] Global hypothesis tests
- [ ] Pairwise comparisons
- [ ] Multiple testing
- [ ] Family-wise error rate
- [ ] Bonferroni and Holm corrections
- [ ] False discovery rate
- [ ] Benjamini–Hochberg procedure

**Potential methodology:**

Sport-specific survival curves, multi-group log-rank tests, and adjusted pairwise comparisons.

Potential secondary analyses include team versus individual sports and Summer versus Winter Olympic sports.

**Required data:**

RQ2 variables, sport, event, Olympic season, and sport classifications.

**Hypotheses:** To be determined.

**Methodological decisions:** To be determined.

**Key limitations:** Unequal group sizes, athletes participating in multiple sports, historical changes in sporting disciplines, confounding, and multiple comparisons.

**Results and conclusions:** Pending.

**Implementation and notebook:** Pending.

---

### RQ5 — Generational Differences

**Status:** Planned

**Research question:**

How has longevity among Olympic athletes changed across generations?

**Objective:**

Investigate historical differences in athlete survival while accounting for differences in observation periods and demographic composition.

**Mathematical theory:**

- [ ] Cohort analysis
- [ ] Birth-cohort and participation-cohort definitions
- [ ] Age, period, and cohort effects
- [ ] Age-period-cohort identification problem
- [ ] Truncation and observation windows
- [ ] Standardization
- [ ] Weighted estimates
- [ ] Restricted mean survival time

**Potential methodology:**

Cohort-specific survival analysis, standardized comparisons, and survival comparisons over common follow-up periods.

**Required data:**

RQ2 variables, birth year, Olympic participation years, and reference date.

**Hypotheses:** To be determined.

**Methodological decisions:** To be determined.

**Key limitations:** Unequal follow-up periods, historical changes in mortality and Olympic participation, and differences in biographical data availability.

**Results and conclusions:** Pending.

**Implementation and notebook:** Pending.

---

### RQ6 — Age at First Olympic Participation

**Status:** Planned

**Research question:**

Is age at first Olympic participation associated with subsequent survival?

**Objective:**

Investigate the relationship between age at Olympic debut and survival following Olympic participation.

**Mathematical theory:**

- [ ] Covariance
- [ ] Pearson correlation
- [ ] Spearman rank correlation
- [ ] Regression foundations
- [ ] Conditional expectations
- [ ] Least squares estimation
- [ ] Likelihood functions
- [ ] Maximum likelihood estimation
- [ ] Log-likelihood functions
- [ ] Nonlinear relationships
- [ ] Introduction to survival regression

**Potential methodology:**

Exploratory correlation and regression exercises, followed by survival regression that appropriately accounts for censoring and the chosen time scale.

**Required data:**

RQ2 variables, first Olympic participation date or year, and age at first participation.

**Hypotheses:** To be determined.

**Methodological decisions:** To be determined.

**Key limitations:** Mathematical dependence between age at entry, attained age, and remaining lifetime; confounding by sport and birth cohort; censoring.

**Results and conclusions:** Pending.

**Implementation and notebook:** Pending.

---

### RQ7 — Repeated Olympic Participation

**Status:** Planned

**Research question:**

Is repeated Olympic participation associated with athlete longevity?

**Objective:**

Investigate the relationship between Olympic career history and survival while accounting for the changing nature of participation over time.

**Mathematical theory:**

- [ ] Time-dependent variables
- [ ] Time-dependent risk sets
- [ ] Immortal time bias
- [ ] Landmark analysis
- [ ] Time-dependent survival regression
- [ ] Start-stop data representation
- [ ] Time-dependent Cox regression

**Potential methodology:**

Landmark analysis and survival models incorporating Olympic participation as a time-dependent covariate.

**Required data:**

RQ2 variables and complete Olympic participation histories.

**Hypotheses:** To be determined.

**Methodological decisions:** To be determined.

**Key limitations:** Athletes must survive long enough to participate repeatedly; career duration may reflect underlying health, sporting ability, and selection processes.

**Results and conclusions:** Pending.

**Implementation and notebook:** Pending.

---

### RQ8 — Multivariable Survival Modelling

**Status:** Planned

**Research question:**

Which athlete characteristics are associated with survival after accounting for other relevant variables?

**Objective:**

Develop a multivariable statistical model to investigate associations between demographic and sporting characteristics and athlete survival.

**Mathematical theory:**

- [ ] Multivariable regression
- [ ] Cox proportional hazards model
- [ ] Baseline hazard functions
- [ ] Hazard ratios
- [ ] Partial likelihood
- [ ] Numerical optimization
- [ ] Score functions and information matrices
- [ ] Wald, score, and likelihood-ratio tests
- [ ] Proportional hazards assumption
- [ ] Schoenfeld residuals
- [ ] Interaction effects
- [ ] Multicollinearity
- [ ] Model selection
- [ ] Model validation
- [ ] Concordance index

**Potential methodology:**

Multivariable Cox regression, model diagnostics, interaction analysis, and alternative survival models where appropriate.

**Required data:**

Relevant variables established in RQ1–RQ7.

**Hypotheses:** To be determined.

**Methodological decisions:** To be determined.

**Key limitations:** Residual confounding, model misspecification, missing data, measurement error, and limited causal interpretability.

**Results and conclusions:** Pending.

**Implementation and notebook:** Pending.

---

### RQ9 — Data Quality and Robustness

**Status:** Planned

**Research question:**

How sensitive are the statistical findings to data-quality limitations and methodological decisions?

**Objective:**

Quantify the impact of data-quality improvements and investigate whether the findings remain stable under different assumptions.

**Mathematical theory:**

- [ ] Missing completely at random (MCAR)
- [ ] Missing at random (MAR)
- [ ] Missing not at random (MNAR)
- [ ] Complete-case analysis
- [ ] Imputation methods
- [ ] Multiple imputation
- [ ] Measurement error
- [ ] Misclassification bias
- [ ] Bootstrap resampling
- [ ] Bootstrap confidence intervals
- [ ] Sensitivity analysis
- [ ] Simulation methods

**Potential methodology:**

Compare original and improved datasets, repeat statistical analyses under alternative inclusion criteria, and investigate the impact of missing or incorrectly matched observations.

**Required data:**

Original and improved biographical datasets, matching information, data-quality indicators, and previous statistical results.

**Hypotheses:** To be determined.

**Methodological decisions:** To be determined.

**Key limitations:** Unknown true identities for some athletes, unverifiable missing-data assumptions, and uncertainty regarding the magnitude of data errors.

**Results and conclusions:** Pending.

**Implementation and notebook:** Pending.

---

### RQ10 — Comparison with the General Population

**Status:** Planned

**Research question:**

How does the longevity of Olympic athletes compare with that of comparable individuals in the general population?

**Objective:**

Address the primary research objective using suitable reference populations and statistical methods that account for demographic differences and selection into the Olympic athlete population.

**Mathematical theory:**

- [ ] Population mortality rates
- [ ] Life tables
- [ ] Age-specific mortality probabilities
- [ ] Life expectancy
- [ ] Person-time and mortality rates
- [ ] Expected number of deaths
- [ ] Observed-to-expected comparisons
- [ ] Standardized mortality ratios
- [ ] Direct and indirect standardization
- [ ] Expected survival
- [ ] Poisson-based confidence intervals
- [ ] Selection effects and the healthy athlete effect
- [ ] Association versus causation

**Potential methodology:**

Life-table-based comparisons, standardized mortality ratios, and comparisons between observed and expected survival.

**Required data:**

Validated athlete-level biographical data, Olympic participation history, and suitable general-population mortality data stratified by relevant demographic characteristics.

**Hypotheses:** To be determined.

**Methodological decisions:** To be determined.

**Key limitations:** Selection into elite sport, comparability of reference populations, socioeconomic confounding, historical changes in mortality, and incomplete reference data.

**Results and conclusions:** Pending.

**Implementation and notebook:** Pending.

## 6. General Methodological Considerations

The following issues should be considered throughout the research:

- Right censoring and incomplete lifetime observations
- Left truncation and survival until Olympic participation
- Selection and survivorship bias
- Missing biographical information
- Incorrect identity matching
- Historical and demographic differences
- Confounding variables
- Immortal time bias
- Multiple comparisons
- Statistical uncertainty
- Association versus causation
- Reproducibility

The relevance and treatment of each issue will depend on the individual research question.

## 7. Research Design Maintenance

This document is updated throughout the project as mathematical theory is studied, methodological decisions are made, and analyses are completed.

Research questions and hypotheses formulated before analysis should be distinguished from those developed in response to exploratory findings.

Changes to research questions, inclusion criteria, statistical methods, or hypotheses should be documented together with their reasoning.

Earlier results should be preserved where practical to support comparisons between different methodologies and dataset versions.

The research roadmap is a guide rather than a strictly sequential plan. Mathematical topics and research questions may be revisited as the project develops.

## 8. References

Mathematical, statistical, methodological, and scientific references will be added throughout the project.