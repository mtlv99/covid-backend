import cv2
import numpy as np
import json
from pathlib import Path
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import InMemoryUploadedFile
from .predictions import predict_image_with_model

def image_list(request):
    dataset_dir = settings.MEDIA_ROOT
    base_url = request.build_absolute_uri(settings.MEDIA_URL)
    all_images = []

    # Nuevo parámetro de filtro
    location_filter = request.GET.get('location')
    locations_to_scan = [location_filter] if location_filter else ['train', 'test', 'user_generated']

    for location in locations_to_scan:
        location_path = Path(dataset_dir) / location
        if not location_path.exists():
            continue

        if location in ['train', 'test']:
            for category_folder in location_path.iterdir():
                label = category_folder.name.lower().replace(' ', '_')
                for image_file in category_folder.glob('*.*'):
                    relative_path = image_file.relative_to(dataset_dir)
                    all_images.append({
                        'url': base_url + str(relative_path).replace('\\', '/'),
                        'type': location,
                        'label': label,
                        'source_path': f"/media/{relative_path}".replace("\\", "/")
                    })

        elif location == 'user_generated':
            for image_file in location_path.glob('*.*'):
                relative_path = image_file.relative_to(dataset_dir)
                label = image_file.name.split('_')[-1].split('.')[0]
                all_images.append({
                    'url': base_url + str(relative_path).replace('\\', '/'),
                    'type': location,
                    'label': label,
                    'source_path': f"/media/{relative_path}".replace("\\", "/")
                })

    # Paginación
    page_number = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    paginator = Paginator(all_images, page_size)
    page = paginator.get_page(page_number)

    return JsonResponse({
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'results': list(page)
    })

@csrf_exempt
def upload_and_filter_image(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    filter_type = request.GET.get('filter', 'raw')
    source_path_param = request.GET.get('source_path')
    img_file = request.FILES.get('image')

    user_dir = Path(settings.MEDIA_ROOT) / 'user_generated'
    user_dir.mkdir(parents=True, exist_ok=True)

    final_source_path = ""
    raw_url = ""
    filtered_filename = None

    if source_path_param:
        try:
            relative_path = Path(source_path_param).relative_to('/media/')
            source_abs_path = Path(settings.MEDIA_ROOT) / relative_path
        except Exception:
            return JsonResponse({'error': 'Invalid source_path'}, status=400)

        if not source_abs_path.exists():
            return JsonResponse({'error': 'Image not found at source_path'}, status=404)

        img = cv2.imread(str(source_abs_path))
        if img is None:
            return JsonResponse({'error': 'Failed to read image at source_path'}, status=400)

        final_source_path = str(relative_path).replace("\\", "/")
        raw_url = request.build_absolute_uri(settings.MEDIA_URL + final_source_path)

        # Imagen viene de user_generated → mantener ID
        if 'user_generated' in final_source_path:
            try:
                image_id = int(Path(source_path_param).name.split('_')[0])
                filtered_filename = f"{image_id}_{filter_type}.jpg"
            except Exception:
                return JsonResponse({'error': 'Could not determine ID from source_path'}, status=400)

        # Imagen de dataset → generar nombre informativo
        else:
            try:
                split = relative_path.parts[0]       # train / test
                class_name = relative_path.parts[1]  # Covid / Normal / etc.
                original_name = Path(relative_path.name).stem  # e.g., '01'
            except Exception:
                return JsonResponse({'error': 'Invalid dataset path format'}, status=400)

            filtered_filename = f"{split}_{class_name.lower()}_{original_name}_{filter_type}.jpg"

    elif img_file:
        existing = user_dir.glob('*_original.*')
        ids = [int(f.name.split('_')[0]) for f in existing if f.name.split('_')[0].isdigit()]
        next_id = max(ids) + 1 if ids else 1

        original_filename = f"{next_id}_original.jpg"
        original_path = user_dir / original_filename

        with open(original_path, 'wb') as f:
            for chunk in img_file.chunks():
                f.write(chunk)

        img = cv2.imread(str(original_path))
        if img is None:
            return JsonResponse({'error': 'Invalid image format'}, status=400)

        final_source_path = f"user_generated/{original_filename}"
        raw_url = request.build_absolute_uri(settings.MEDIA_URL + final_source_path)
        filtered_filename = f"{next_id}_{filter_type}.jpg"

    else:
        return JsonResponse({'error': 'Provide either image or source_path'}, status=400)

    # Aplicar filtro
    if filter_type == 'bilateral':
        img_filtered = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    elif filter_type == 'canny':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_filtered = cv2.Canny(gray, 100, 200)
    else:
        img_filtered = img
        filtered_filename = None

    # Guardar imagen procesada si no es raw
    if filtered_filename:
        filtered_path = user_dir / filtered_filename
        cv2.imwrite(str(filtered_path), img_filtered)
        processed_url = request.build_absolute_uri(settings.MEDIA_URL + f"user_generated/{filtered_filename}")
    else:
        processed_url = ""

    return JsonResponse({
        'source_path': f"/media/{final_source_path}",
        'filter': filter_type,
        'raw_url': raw_url,
        'processed_url': processed_url
    })


@csrf_exempt
def predict_image(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
        source_path = data.get('source_path')
        filter_type = data.get('filter')
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not source_path or not filter_type:
        return JsonResponse({'error': 'Missing source_path or filter'}, status=400)

    try:
        relative_path = Path(source_path).relative_to('/media/')
        abs_path = Path(settings.MEDIA_ROOT) / relative_path
    except Exception:
        return JsonResponse({'error': 'Invalid source_path format'}, status=400)

    if not abs_path.exists():
        return JsonResponse({'error': 'Image not found at source_path'}, status=404)

    try:
        pred_class, confidence = predict_image_with_model(abs_path, filter_type)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({
        'prediction': pred_class,
        'confidence': confidence
    })
