# JobPulse — India Data Analyst Job Market Intelligence

[![Live Dashboard](https://img.shields.io/badge/Live-Dashboard-success?logo=streamlit)](https://jobpulse91.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-SQLite-orange?logo=sqlite)]
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)]

JobPulse is an end-to-end data analytics project that analyzes public Data Analyst job postings in India to understand skill demand, geographic hiring patterns, experience requirements, salary availability, and relationships between commonly requested skills.

The project combines a Python data pipeline, data cleaning and validation, rule-based skill extraction, SQLite-based analytical storage, SQL and Python analytics, and an interactive Streamlit dashboard.

Live Dashboard: https://jobpulse91.streamlit.app/




## Overview

The Data Analyst job market requires a combination of analytical, programming, business intelligence, database, cloud, and data engineering skills.

JobPulse was built to analyze these requirements using real public job-posting data rather than relying only on a static dataset.

The project collects job postings, cleans and validates the source data, extracts structured information from job descriptions, stores the processed information in a relational database, performs analytical queries, and presents the results through an interactive dashboard.

The project is designed around practical questions such as:

- Which skills are most frequently requested for Data Analyst roles?
- Which programming and business intelligence tools appear most often?
- Which skills commonly occur together?
- Which locations have the highest concentration of collected opportunities?
- What experience requirements are explicitly mentioned?
- How frequently is salary information available?
- How can job-market demand be tracked across different collection periods?
- Which skills may be useful for candidates based on observed market demand?


## Live Dashboard

JobPulse is deployed using Streamlit Community Cloud.

Live Dashboard:

https://jobpulse91.streamlit.app/

The dashboard currently contains seven analytical sections:

1. Market Overview
2. Skill Intelligence
3. Skill Relationships
4. Geography
5. Trends
6. Skill Gap Analyzer
7. Job Explorer


## Project Objectives

The main objectives of JobPulse are:

- Collect real public Data Analyst job-posting data.
- Build a reproducible data-cleaning pipeline.
- Extract commonly requested technical and analytical skills.
- Measure skill demand and penetration.
- Analyze the geographic distribution of job postings.
- Extract experience requirements from job descriptions.
- Analyze salary information where available.
- Identify commonly occurring skill combinations.
- Store structured information in an analytical database.
- Build a historical snapshot framework.
- Present the results through an interactive dashboard.
- Create a foundation for automated recurring market analysis.


## Architecture

```text
                         Adzuna API
                             |
                             v
                    Job Data Collection
                    Python + Requests
                             |
                             v
                       Raw Job Data
                             |
                             v
                    Data Cleaning Layer
                         pandas
                             |
              +--------------+--------------+
              |                             |
              v                             v
       Skill Extraction              Experience Extraction
       Regex + Taxonomy              Rule-based Extraction
              |                             |
              +--------------+--------------+
                             |
                             v
                    Geography Analysis
                             |
                             v
                       SQLite Database
                             |
              +--------------+--------------+
              |                             |
              v                             v
       SQL / Python Analytics       Historical Snapshots
              |                             |
              +--------------+--------------+
                             |
                             v
                    Streamlit Dashboard
                         + Plotly
                             |
                             v
                  Streamlit Community Cloud
