 JobPulse — India Data Analyst Job Market Intelligence

<p align="center">
  <strong>Real-world job market analytics for Data Analyst roles in India</strong>
</p>

<p align="center">
  <a href="https://jobpulse91.streamlit.app/">Live Dashboard</a>
 
</p>

---

 Overview

**JobPulse** is an end-to-end data analytics project designed to analyze the demand for Data Analyst roles in India using real public job-posting data.

The project collects job postings, cleans and validates the data, extracts technical and analytical skills, stores structured information in SQLite, performs SQL/Python-based market analysis, and presents the results through an interactive Streamlit dashboard.

The objective is to answer practical questions such as:

- Which skills are most frequently requested for Data Analyst roles?
- Which BI, programming, database, cloud, and data-engineering skills appear most often?
- Which Indian cities have the highest concentration of Data Analyst opportunities?
- What experience requirements are visible in job descriptions?
- Which skills commonly appear together?
- What salary signals are available in the collected postings?
- What skills might a candidate need based on selected target skills?
- How can the job market be monitored over time?

> **Current status:** The dashboard is live and the core analytics pipeline is operational. Historical trend analysis is intentionally limited until multiple independent collection snapshots are available.

---
 Live Demo

 Interactive Dashboard

**[Open JobPulse Live Dashboard](https://jobpulse91.streamlit.app/)**

The deployed application currently provides seven analytical views:

1. Market Overview
2. Skill Intelligence
3. Skill Relationships
4. Geography
5. Trends
6. Skill Gap Analyzer
7. Job Explorer

---

 Project Objectives

JobPulse was built around five primary objectives.

### 1. Understand skill demand

Identify which technical and analytical skills are most frequently requested in Data Analyst job postings.

### 2. Analyze geographic demand

Determine where Data Analyst opportunities are concentrated across Indian cities and locations.

### 3. Understand job requirements

Extract experience requirements, salary information, job titles, and other available job attributes.

### 4. Analyze skill relationships

Identify combinations of skills that frequently occur within the same job postings.

### 5. Build a reusable market-intelligence system

Create a pipeline that can be rerun periodically so the project can eventually track changes in job demand over time.

---

 Architecture

```text
                    ┌──────────────────────┐
                    │   Adzuna Job API     │
                    │  Public Job Listings │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Collection       │
                    │  Python + Requests   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Raw Job Dataset    │
                    │       CSV/JSON       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Data Cleaning      │
                    │       pandas         │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌────────────────────────────────┐
              │       Feature Extraction       │
              │                                │
              │  • Skills                      │
              │  • Experience                  │
              │  • Geography                   │
              └────────────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     SQLite DB        │
                    │ Structured Analytics │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
      ┌───────────────────┐        ┌────────────────────┐
      │ SQL / Python      │        │ Historical         │
      │ Analytics         │        │ Snapshots          │
      └─────────┬─────────┘        └─────────┬──────────┘
                │                            │
                └─────────────┬──────────────┘
                              ▼
                    ┌──────────────────────┐
                    │ Streamlit Dashboard  │
                    │      + Plotly        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Streamlit Cloud    │
                    │    Live Dashboard     │
                    └──────────────────────┘
