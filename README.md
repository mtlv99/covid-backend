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

### 3. Add the dataset and pretrained models.

Download the dataset from [here](https://www.kaggle.com/datasets/pranavraikokte/covid19-image-dataset). The dataset should be in `training/Covid19-dataset`.

For the dataset, include the models in the `training/models` folder. The models should be in the format `vgg16_conjunto_[filterType].pt` (PyTorch models).

Should include the following models:
- `vgg16_conjunto_raw.pt`: No filters applied. The images are resized to 224x224.
- `vgg16_conjunto_canny.pt`: Canny filter applied to the images. The images are resized to 224x224.
- `vgg16_conjunto_bilateral.pt`: Bilteral filter applied to the images. The images are also resized to 224x224.


### 4. Run the server

```bash
python manage.py runserver
```


### Exit the virtual environment

```bash
deactivate  # On Windows use: .\venv\Scripts\deactivate
```

## Test Examples

For test examples, you can check the postman collection, it has some examples of how to use the API.

User content will be saved in: `training/Covid19-dataset/user_generated`