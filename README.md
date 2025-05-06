# Covid Prediction - Backend

Backend for covid prediction. You can find the frontend [here](https://github.com/mtlv99/covid-app).

Authors:
- Marco León Vargas
- Dwight García Esquivel

# Technologies used
- **Language**: Python 3.10
- **Web Framework**: Django
- **Machine Learning**: pytorch
- **Data Visualization**: seaborn, matplotlib, weights & biases

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

For test examples, you can check the postman collection, it has some examples of how to use the API.