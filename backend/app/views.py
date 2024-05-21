import pandas as pd
from django.http import JsonResponse
from .models import YieldPrediction
from .random_forest_regressor import RandomForestRegressorWrapper
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def predict_yield(request):
    if request.method == 'POST':
        
        cassava_mosaic_disease_severity = request.POST.get('cassava mosaic disease severity 6-month evaluation|CO_334:0000194')
        
        # Create a new instance of the RandomForestRegressorWrapper
        rf_wrapper = RandomForestRegressorWrapper()
        X = rf_wrapper.get_X()
        new_df = pd.DataFrame(columns=X.columns)
        new_df.loc['cassava mosaic disease severity 6-month evaluation|CO_334:0000194'] = cassava_mosaic_disease_severity
        
        # Make predictions
        predictions = rf_wrapper.predict(new_df)
        
        # Return the predictions as JSON
        return JsonResponse({'fresh root yield|CO_334:0000013': predictions[0]})
    else:
        return JsonResponse({'error': 'Invalid request'})