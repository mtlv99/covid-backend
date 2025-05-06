import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from django.conf import settings

# Dispositivo de ejecución (GPU si está disponible)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Ruta absoluta a training/models
MODEL_DIR = os.path.join(settings.BASE_DIR, "training", "models")

# Mapeo de filtros a rutas de modelos VGG16
MODEL_PATHS = {
    "raw": os.path.join(MODEL_DIR, "vgg16_conjunto_raw.pth"),
    "bilateral": os.path.join(MODEL_DIR, "vgg16_conjunto_bilateral.pth"),
    "canny": os.path.join(MODEL_DIR, "vgg16_conjunto_canny.pth"),
}

# Etiquetas del modelo
CLASS_NAMES = ['covid', 'normal', 'pneumonia']

# Caché de modelos cargados
_loaded_models = {}

def load_model(filter_type):
    if filter_type not in MODEL_PATHS:
        raise ValueError(f"Unsupported filter type: {filter_type}")

    if filter_type in _loaded_models:
        return _loaded_models[filter_type]

    model_path = MODEL_PATHS[filter_type]
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")

    # Cargar arquitectura VGG16 y adaptar la capa final
    model = models.vgg16(pretrained=False)
    model.classifier[6] = nn.Linear(model.classifier[6].in_features, len(CLASS_NAMES))

    model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()

    _loaded_models[filter_type] = model
    return model

def predict_image_with_model(image_path, filter_type):
    model = load_model(filter_type)

    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # Tamaño estándar para VGG16
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # Imagen RGB normalizada (estándar ImageNet)
            std=[0.229, 0.224, 0.225]
        ),
    ])

    # Cargar y preprocesar imagen
    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(DEVICE)

    # Ejecutar predicción
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.softmax(output, dim=1)
        confidence, pred_class_idx = torch.max(probabilities, dim=1)

    predicted_class = CLASS_NAMES[pred_class_idx.item()]
    return predicted_class, round(confidence.item(), 4)
