# Covid Prediction - Backend

Backend for covid prediction. You can find the frontend [here](https://github.com/mtlv99/covid-app).

Authors:
- Marco León Vargas
- Dwight García Esquivel

# Technologies used
- **Language**: Python 3.10
- **Web Framework**: Django
- **Data Analysis**: pandas
- **Machine Learning**: scikit-learn (sklearn)
- **Data Visualization**: seaborn, matplotlib
- **Database**: MariaDB

## Installation

Download Python version 3.10 before continuing.

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
```

Note: If you are using Windows, you may need to set the execution policy to allow running scripts. Open PowerShell as an administrator and run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the server

```bash
python manage.py runserver
```


### Exit the virtual environment

```bash
deactivate  # On Windows use: .\venv\Scripts\deactivate
```


## Test Examples

### a. User with diabetes

```json
{
    "pregnancies": 3,
    "glucose": 180.0,
    "blood_pressure": 90.0,
    "skin_thickness": 40.0,
    "insulin": 200.0,
    "bmi": 35.2,
    "diabetes_pedigree_function": 0.9,
    "age": 55
}
```

### b. User without diabetes

```json
{
    "pregnancies": 1,
    "glucose": 95.0,
    "blood_pressure": 75.0,
    "skin_thickness": 20.0,
    "insulin": 80.0,
    "bmi": 22.5,
    "diabetes_pedigree_function": 0.3,
    "age": 30
}
```