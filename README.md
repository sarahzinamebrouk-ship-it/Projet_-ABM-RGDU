# Projet\_-ABM-RGD

\# Projet\_-ABM-RGDU

\# An agent-based model of the French RGDU reform



This repository contains a Python agent-based model designed to study the employment effects of the 2026 reform of employer social security contribution reductions in France (RGDU).



The model compares the new RGDU scheme with the previous contribution reduction system and a no-exemption scenario. It is a simulation model designed to explore employment and labour-market mechanisms, not a forecasting model.



\## Before you begin



Install Python 3.10 or later and Visual Studio Code with the Microsoft Python extension.



Open the project folder that directly contains `run.py`, `parameters.py`, `model`, `equations` and `markets`.



The model requires NumPy and Matplotlib. Other components use the Python standard library.



\## Installation on Windows



Open a new VS Code terminal in the project folder and run:



```powershell

py --version

py -m venv .venv

.venv\\Scripts\\python.exe -m pip install numpy matplotlib

```



These commands use the project's Python directly. Activating the virtual environment is optional, so PowerShell's script policy cannot block the setup.



Run the model and generate the results:



```powershell

.venv\\Scripts\\python.exe run.py

```



Run the validation checks:



```powershell

.venv\\Scripts\\python.exe tests\\validation.py

```



\## Installation on macOS or Linux



```bash

python3 --version

python3 -m venv .venv

.venv/bin/python -m pip install numpy matplotlib

.venv/bin/python run.py

```



Run the validation checks:



```bash

.venv/bin/python tests/validation.py

```



\## Model architecture



```text

parameters.py                 baseline calibration and assumptions

run.py                        launches simulations and policy experiments

plot\_outputs.py               creates figures from simulation results

excel\_outputs.py              exports results to an Excel workbook



model/

&#x20;   entities.py               firm agents and their characteristics

&#x20;   model.py                  creates firms and initializes simulations

&#x20;   scheduler.py              orders mechanisms within each quarter

&#x20;   collector.py              records employment and labour-market outcomes



equations/                    one economic or behavioural equation per file

markets/                      labour-market matching and hiring allocation

tests/                        checks equations, mechanisms and model outcomes

outputs/                      generated CSV files, Excel workbook and figures

```



The central coding convention is:



> One equation or autonomous behavioural mechanism, one Python file; one market interaction protocol, one market module.



\## What happens during one quarter?



`model/scheduler.py` makes the sequence explicit:



1\. unemployment durations are updated;

2\. transitions between unemployment and inactivity are simulated;

3\. workers leave employment and enter unemployment;

4\. firms update their demand expectations;

5\. firms adjust their desired employment and may lay off excess workers;

6\. vacancies are calculated;

7\. firms choose their recruitment effort;

8\. the labour market matches unemployed workers and vacancies;

9\. hires are allocated between firms;

10\. recruitment scores and labour-market outcomes are updated;

11\. the collector records the results of the quarter.



The model represents six economic sectors through 36 representative firm profiles (six profiles per sector).



Firms are represented by firm-level employment counts, while unemployed workers are represented as individual agents. The model uses a 1/100 scale: one simulated employee represents 100 actual employees.



The simulation covers 60 quarters, corresponding to 15 years.



\## Policy scenarios



The model compares three policy scenarios:



\- \*\*No exemption:\*\* no reduction in employer social security contributions.

\- \*\*Previous scheme:\*\* the contribution reduction system preceding the RGDU.

\- \*\*RGDU 2026:\*\* the new contribution reduction system.



The model also examines general reductions in employer contributions, recruitment learning, demand shocks, and sensitivity to selected behavioural parameters.



The baseline policy comparison uses 200 simulations per scenario. Common random seeds are used across policy scenarios to make comparisons more consistent.



\## Generated outputs



The `outputs` folder contains:



\- `final\_table.csv`: summary of the main employment, unemployment, cost and sensitivity results.

\- `assumptions\_and\_sources.csv`: model assumptions, their justifications and robustness-testing information.

\- `simulation\_results.xlsx`: Excel workbook containing the final results and assumptions.

\- `rgdu\_employment\_effect.png`: employment effects of the RGDU compared with the previous scheme.

\- `demand\_shock.png`: employment dynamics under a severe demand shock.

\- `recruitment\_learning.png`: evolution of firms' intensive recruitment effort.

\- `learning\_sensitivity.png`: sensitivity of employment effects to learning parameters.



All these outputs are generated by running `run.py`.



\## How to modify the model



\### Change an existing equation



To change the RGDU contribution reduction formula, edit `equations/rgdu\_relief\_rate.py`.



To change the previous contribution reduction formula, edit `equations/legacy\_relief.py`.



To modify the employment response to labour-cost changes, edit `equations/employment\_elasticity.py` or `equations/desired\_employment\_change.py`.



Rerun the validation checks and the model after making changes.



\### Add a parameter



Add its baseline value to `parameters.py`, then pass it explicitly to the equation or mechanism that uses it.



\### Add a new state variable



1\. add it to the relevant class in `model/entities.py`;

2\. initialize it in `model/model.py`;

3\. update it through an equation or market mechanism;

4\. record it in `model/collector.py` if it should appear in the simulation outputs.



\### Add a new mechanism



1\. write the equation in a new file under `equations/`, or the interaction protocol in a new file under `markets/`;

2\. import it in `model/scheduler.py`;

3\. call it at the appropriate point in the quarterly sequence;

4\. add a validation check in `tests/validation.py`;

5\. compare the baseline results with the modified model.



\## Run the validation checks



The project includes a validation script in `tests/validation.py`.



The script first checks the implementation of the model's equations and mechanisms. These checks cover contribution reduction formulas, employment elasticities, stochastic rounding, recruitment learning, labour-market matching, worker allocation and population conservation.



It then compares selected simulation outcomes with external reference values from Insee and Dares. These comparisons include unemployment, long-term unemployment, vacancy rates, job-finding rates and employment dynamics after demand shocks.



The script reports the number of successful checks and stops the execution if a code check fails.



To run the checks:



Windows:



```powershell

.venv\\Scripts\\python.exe tests\\validation.py

```



macOS or Linux:



```bash

.venv/bin/python tests/validation.py

```



\## Possible extensions



The model could be extended by introducing additional sectors, more heterogeneous firm profiles, alternative employment elasticities, different recruitment strategies, or additional macroeconomic mechanisms.



The baseline remains a simplified representation of the French labour market. Firms are represented through 36 profiles rather than a fully heterogeneous population of individual firms, and employed workers are represented through firm-level employment counts rather than individual agents.



These simplifications make it possible to focus on the employment mechanisms associated with changes in employer social security contribution reductions.

