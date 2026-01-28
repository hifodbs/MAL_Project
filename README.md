# Solar Energy Forecasting Project
This is the repository for the coding project for the course of Data-Driven Systems Engeneering / Machine Learning Operations, Master in Computer Engeenering / Master of Science in Data Science and Artificial Intelligence (a. y. 2025/2026, UniTS).
The project has been developed by Alessandro Longato, Matteo Pillinini and Giovanni Leonardi.

## Overview
The scope of this project is the design and development of an end-to-end data-driven system for short-
term solar power generation forecasting. The system covers the full lifecycle of a machine learning
application, including data ingestion, preprocessing, model training, validation, deployment, monitoring,
and incremental updates. The solution is designed to simulate real-world operational conditions through
synthetic sensors. The project further incorporates a slightly simpler ILSTM model proposed in this
paper (https://www.sciencedirect.com/science/article/pii/S0045790621001592) as a proof of concept for advanced forecasting techniques.

## How to run
1. Clone the repository and navigate to the project directory:
```sh
git clone https://github.com/hifodbs/MAL_Project
cd MAL_Project
```
2. Create and activate a virtual environment (recommended):

Linux/MacOS:
```sh
python3 -m venv venv
source venv/bin/activate
```
Windows:
```sh
python -m venv venv
venv\Scripts\activate
```
3. Install the dependencies:
```sh
pip install -r requirements.txt
```
4. To start the project, run the **`main.py`** automation script. This will initialize the Flask backend, wait for it to come online, and then launch the Streamlit dashboard.
The script will automatically handle directory navigation for the separate backend and frontend services. Press **`Ctrl+C`** in the terminal to stop both servers.

Linux/MacOS:
```sh
python3 main.py
```
Windows:
```sh
python main.py
```
