from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
# views.py
from django.shortcuts import render, redirect
from .forms import ImageUploadForm
from .models import UploadedImage
from .utils import perform_inference
from django.http import JsonResponse

def home_view(request):
    return render(request, 'home.html')


def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save()
            inference_results = perform_inference(image_instance.image.path)
            return JsonResponse({'report': inference_results})
    else:
        form = ImageUploadForm()

    return render(request, 'upload_template.html', {'form': form})

