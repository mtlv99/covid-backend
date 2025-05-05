import cv2
import numpy as np
import base64
from pathlib import Path
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.uploadedfile import InMemoryUploadedFile

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
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    uploaded_file: InMemoryUploadedFile = request.FILES.get('image')
    if not uploaded_file:
        return JsonResponse({'error': 'No image uploaded'}, status=400)

    filter_type = request.GET.get('filter', 'raw')

    # Convert uploaded image to OpenCV format
    np_arr = np.frombuffer(uploaded_file.read(), np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Apply selected filter
    if filter_type == 'bilateral':
        filtered = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    elif filter_type == 'canny':
        filtered = cv2.Canny(img, threshold1=100, threshold2=200)
    else:  # raw or unknown
        filtered = img

    # Encode image to base64
    is_color = len(filtered.shape) == 3
    _, buffer = cv2.imencode('.jpg', filtered if is_color else cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR))
    b64_encoded = base64.b64encode(buffer).decode('utf-8')

    return JsonResponse({
        'filename': uploaded_file.name,
        'filter': filter_type,
        'image_base64': b64_encoded
    })