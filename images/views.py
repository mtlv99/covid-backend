import os
from pathlib import Path
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings

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
