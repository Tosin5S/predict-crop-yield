from django.shortcuts import render
from django.http import JsonResponse
import json
from .nlp import predict_from_text

def index(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        predictions = predict_from_text(user_input)
        return JsonResponse({'predictions': predictions.tolist()})
    return render(request, 'nlp_app/index.html')
