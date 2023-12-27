# Data warehouse using Postgres, DBT and Airflow

Transforming raw data collected from swarm drone cameras in real time by trancking each vehicles in a specified area. 

## Overview

The traffic department wants to utilize the data in order to optimize the traffic flow within that area. our project will be creating data warehouse for hosting the trajectory of each vehicle which collected from swarm drones and static roadside cameras.

## Getting Started

our Extract Load and Transform using dbt and host for analytic engineers to further utilize those data.

1.Airflow :- we will use it to handle dependencies and schedule our tas.

2.DBT(data build tool) :-to handle our transformation of our data in our case we'll use postgres plugin to integrate to our data source .

3.PostgresSQL :- is a powerful open-source object-relational database system.

### 1. Clone the Repository

```bash
git clone https://github.com/DanielZerihunGeda/ETL_PIPELINE.git
cd ETL_PIPELINE
