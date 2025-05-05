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

    for dataset_type in ['train', 'test']:
        dataset_path = Path(dataset_dir) / dataset_type
        if not dataset_path.exists():
            continue

        for category_folder in dataset_path.iterdir():
            label = category_folder.name.lower().replace(' ', '_')
            for image_file in category_folder.glob('*.*'):
                relative_path = image_file.relative_to(dataset_dir)
                all_images.append({
                    'url': base_url + str(relative_path).replace('\\', '/'),
                    'type': dataset_type,
                    'label': label,
                    'filename': image_file.name
                })

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

    img_file = request.FILES.get('image')
    filter_type = request.GET.get('filter', 'raw')

    if not img_file:
        return JsonResponse({'error': 'No image file provided'}, status=400)

    # Directory where images will be stored
    user_dir = Path(settings.MEDIA_ROOT) / 'user_generated'
    user_dir.mkdir(parents=True, exist_ok=True)

    # Determine next ID
    existing = sorted(user_dir.glob('*_original.*'))
    if existing:
        last_id = int(existing[-1].name.split('_')[0])
        next_id = last_id + 1
    else:
        next_id = 1

    # Save original file
    original_path = user_dir / f"{next_id}_original.jpg"
    with open(original_path, 'wb') as f:
        for chunk in img_file.chunks():
            f.write(chunk)

    # Load using OpenCV
    img = cv2.imread(str(original_path))
    if img is None:
        return JsonResponse({'error': 'Invalid image format'}, status=400)

    if filter_type == 'bilateral':
        img_filtered = cv2.bilateralFilter(img, 9, 75, 75)
    elif filter_type == 'canny':
        img_filtered = cv2.Canny(img, 100, 200)
        img_filtered = cv2.cvtColor(img_filtered, cv2.COLOR_GRAY2BGR)
    else:  # raw
        img_filtered = img
        # No need to duplicate image if no filtering
        filtered_path = original_path
    if filter_type != 'raw':
        filtered_path = user_dir / f"{next_id}_{filter_type}.jpg"
        cv2.imwrite(str(filtered_path), img_filtered)

    media_url = request.build_absolute_uri(settings.MEDIA_URL + f"user_generated/{filtered_path.name}")

    return JsonResponse({
        'id': next_id,
        'filter': filter_type,
        'url': media_url
    })

@csrf_exempt
def predict_image(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
        img_path = data.get('path')
        filter_type = data.get('filter')
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not img_path or not filter_type:
        return JsonResponse({'error': 'Missing path or filter'}, status=400)

    abs_path = Path(settings.MEDIA_ROOT) / Path(img_path).relative_to('/media/')
    if not abs_path.exists():
        return JsonResponse({'error': 'Image not found'}, status=404)

    try:
        pred_class, confidence = predict_image_with_model(abs_path, filter_type)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({
        'prediction': pred_class,
        'confidence': confidence
    })