from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ImageUploadForm
from .models import UploadedImage
from .utils import load_detectron2_model
from django.http import JsonResponse
import cv2
import json
import os
from django.conf import settings

def home_view(request):
    return render(request, 'home.html')


def upload_image(request):
    print("Reached upload_image view")
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            plate_name = form.cleaned_data['plate_name']
            images = request.FILES.getlist('image')  

            results_list = [] 

            model_path = '/Users/joaokasprowicz/MasterDegree/MestradoExample/models/model_final.pth'
            config_path = '/Users/joaokasprowicz/MasterDegree/MestradoExample/models/config.yaml'
            predictor = load_detectron2_model(model_path, config_path)

            for image_file in images:
                image_instance = UploadedImage(image=image_file, plate_name=plate_name)
                image_instance.save()

                image_path = image_instance.image.path
                image = cv2.imread(image_path)
                outputs = predictor(image)

                pred_boxes = outputs["instances"].pred_boxes.tensor.tolist()
                scores = outputs["instances"].scores.tolist()
                pred_classes = outputs["instances"].pred_classes.tolist()

                image_relative_path = os.path.relpath(image_path, settings.MEDIA_ROOT)

                results = {
                    'pred_boxes': pred_boxes,
                    'scores': scores,
                    'pred_classes': pred_classes,
                    'image_path': image_relative_path,
                }

                results_list.append(results)

            
            return JsonResponse({'report': results_list})

        
        form = ImageUploadForm()

    return render(request, 'upload_template.html', {'form': form})


