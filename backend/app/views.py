from django.http import JsonResponse
from .models import YieldPrediction
from .random_forest import RandomForestRegressor

def predict_yield(request):
    if request.method == 'POST':
        germplasmDbId = request.POST.get('germplasmDbId')
        cassava_mosaic_disease_severity = request.POST.get('cassava_mosaic_disease_severity')
        
        # Create a new instance of the YieldPrediction model
        new_df = YieldPrediction(germplasmDbId=germplasmDbId, cassava_mosaic_disease_severity=cassava_mosaic_disease_severity)
        
        # Make predictions
        predictions = RandomForestRegressor().predict(new_df)
        
        # Return the predictions as JSON
        return JsonResponse({'yield_prediction': predictions[0]})
    else:
        return JsonResponse({'error': 'Invalid request'})