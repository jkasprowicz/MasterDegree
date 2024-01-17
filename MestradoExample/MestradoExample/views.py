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

def home_view(request):
    return render(request, 'home.html')


def upload_image(request):
    print("Reached upload_image view")
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            plate_name = form.cleaned_data['plate_name']
            image_instance = form.save(commit=False)
            image_instance.plate_name = plate_name  # Add plate_name to the image instance
            image_instance.save()

            model_path = '/Users/joaokasprowicz/MasterDegree/MestradoExample/models/model_final.pth'
            config_path = '/Users/joaokasprowicz/MasterDegree/MestradoExample/models/config.yaml'
            predictor = load_detectron2_model(model_path, config_path)

            # Load model and perform inference
            image_path = image_instance.image.path
            image = cv2.imread(image_path)
            outputs = predictor(image)

                        # Extract relevant information from the Instances object
            pred_boxes = outputs["instances"].pred_boxes.tensor.tolist()
            scores = outputs["instances"].scores.tolist()
            pred_classes = outputs["instances"].pred_classes.tolist()

            # Convert the information to a serializable format
            results = {
                'pred_boxes': pred_boxes,
                'scores': scores,
                'pred_classes': pred_classes,
            }

            print(outputs)            

            print(json.dumps({'report': results}))


            # Return the results as JSON
            return JsonResponse({'report': json.dumps(results)})
        
        form = ImageUploadForm()

    return render(request, 'upload_template.html', {'form': form})