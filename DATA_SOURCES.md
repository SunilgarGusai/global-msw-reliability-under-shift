# Data sources and provenance entry points

## Primary outcome source

World Bank, *What a Waste 3.0: Global Snapshot of Solid Waste Management Toward Circularity until 2050* and associated Data360 files.

The acquisition script records the operational endpoints used by the frozen pipeline:

- collection coverage: `https://data360files.worldbank.org/data360-data/data/WB_WAW/WM_COL_COV.csv`
- treatment/disposal: `https://data360files.worldbank.org/data360-data/data/WB_WAW/WM_MSW_TREAT.csv`

## Socioeconomic predictors

World Bank World Development Indicators API: `https://api.worldbank.org/v2`

| Repository variable | WDI code |
|---|---|
| GDP per capita, PPP, constant 2021 international dollars | `NY.GDP.PCAP.PP.KD` |
| Urban population (% of total) | `SP.URB.TOTL.IN.ZS` |
| Population, total | `SP.POP.TOTL` |
| Population density | `EN.POP.DNST` |

## Frozen analytical state

The manuscript-facing point predictions, conformal/OOD predictions, subgroup tables, robustness tables, and V2 decision-audit outputs are committed under `results/`.

The historical Phase-B2 source/output manifest and SHA-256 records are under `provenance/`. Those files document the manuscript-producing local state even if upstream public endpoints later change.

## Redistribution boundary

This repository does not claim ownership of or relicense World Bank source data. Public derived outputs are provided for verification of the article's calculations. Users performing a fresh full rerun should retrieve source data from the official endpoints and comply with their current terms.
