# Mechanical  Keyboard Analysis Project - Overview

Creator: Matt Salinero

Created: 2021-06-21

Last Updated: 2021-06-21

---
## Project Overview

This project analyzed data on keyset group buys self-scraped from community websites. Relevant data was scraped from [geekhack.org](https://geekhack.org/) using python's beautifulsoup4 library. Ingested raw data was then initially processed for storage using python. This stage of the project included the implementation of an Earley parsing algorithm and custom grammar to parse unstructured topic titles. The scraped data can then be stored in a relational database for analysis.

Prior to full analysis, the selected data on keyset group buys was manually cleaned and further prepared for analysis using SQL. Final analysis was performed using Pandas, Jupyter, and MatPlotLib to generate a [report](mech_report.ipynb).

---
## Project Resources

#### [Project Specification](mech_spec.md)
- markdown file containing more detail about project goals and project execution

#### [SQL files](db_scripts)
- various SQL scripts and statements used to aggregate and analyze data for this project

#### [Full Project Report](mech_report.ipynb)
- full report for project (as a jupyter notebook), includes analysis, visualizations, and the code used to generate the report

#### [Clean Report](https://mattsalinero.github.io/mech_report.html)
- clean version of report for project (as a .html file), includes analysis and visualizations of findings, but code is hidden