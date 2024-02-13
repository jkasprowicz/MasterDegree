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
from math import sqrt


def home_view(request):
    return render(request, 'home.html')

def resize_image(img_path, size):
    img = cv2.imread(img_path)
    img_resized = cv2.resize(img, size)
    cv2.imwrite(img_path, img_resized)


def calculate_distance(box1, box2):
    # Calculate the Euclidean distance between the centers of two bounding boxes
    center1 = ((box1[0] + box1[2]) / 2, (box1[1] + box1[3]) / 2)
    center2 = ((box2[0] + box2[2]) / 2, (box2[1] + box2[3]) / 2)
    return sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)


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

                resize_image(image_path, (512, 512))

                image = cv2.imread(image_path)
                outputs = predictor(image)

                pred_boxes_raw = outputs["instances"].pred_boxes.tensor.tolist()
                scores_raw = outputs["instances"].scores.tolist()
                pred_classes_raw = outputs["instances"].pred_classes.tolist()

                image_relative_path = os.path.relpath(image_path, settings.MEDIA_ROOT)

                cell_info = {}


                distance_threshold = 10.0

                # Iterate through the predictions
                for i, box in enumerate(pred_boxes_raw):
                    # Convert the box coordinates to a tuple for easier comparison
                    box_tuple = tuple(box)

                    # Check if the box is already in the dictionary
                    if not any(calculate_distance(box, stored_box['box']) < distance_threshold for stored_box in cell_info.values()):
                        cell_info[box_tuple] = {'class': pred_classes_raw[i], 'score': scores_raw[i], 'box': box}
                    else:
                        # If the current score is higher than the stored score, update the information for the cell
                        existing_box = next(info for info in cell_info.values() if calculate_distance(box, info['box']) < distance_threshold)
                        if scores_raw[i] > existing_box['score']:
                            cell_info[box_tuple] = {'class': pred_classes_raw[i], 'score': scores_raw[i], 'box': box}

                # Extract the filtered data - Keep only the highest scoring bounding box for each cell
                pred_boxes = [info['box'] for info in cell_info.values()]
                scores = [info['score'] for info in cell_info.values()]
                pred_classes = [info['class'] for info in cell_info.values()]

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
