from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import FloatField, IntegerField
import pandas as pd
import joblib
import os
import shap
from .models import FieldData, Profile
# from .nlp_utils import explain_record
from .nlp import predict_from_text, reflect_prediction
from .forms import UserUpdateForm, ProfileUpdateForm
from transformers import pipeline


# Load the trained model pipeline
model_file = os.path.join(os.path.dirname(__file__), 'data', 'random_forest_model.pkl')
model_pipeline = joblib.load(model_file)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('index')  # Redirect to the home page after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    # Ensure the user has a profile
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'nlp_app/profile.html', context)

@login_required
def index(request):
    # Define specific traits
    specific_traits = [
        {'id': 'CO_334:0000114', 'label': 'boiled storage root color visual 1-3'},
        {'id': 'CO_334:0000181', 'label': 'cassava anthractnose disease incidence in 6-month'},
        {'id': 'CO_334:0000182', 'label': 'cassava anthractnose disease incidence in 9-month'},
        {'id': 'CO_334:0000184', 'label': 'cassava anthractnose disease severity in 6-month'},
        {'id': 'CO_334:0000185', 'label': 'cassava anthractnose disease severity in 9-month'},
        {'id': 'CO_334:0000178', 'label': 'cassava bacterial blight incidence 3-month evaluation'},
        {'id': 'CO_334:0000179', 'label': 'cassava bacterial blight incidence 6-month evaluation'},
        {'id': 'CO_334:0000175', 'label': 'cassava bacterial blight severity 3-month evaluation'},
        {'id': 'CO_334:0000176', 'label': 'cassava bacterial blight severity 6-month evaluation'},
        {'id': 'CO_334:0000189', 'label': 'cassava green mite severity first evaluation'},
        {'id': 'CO_334:0000190', 'label': 'cassava green mite severity second evaluation'},
        {'id': 'CO_334:0000195', 'label': 'cassava mosaic disease incidence 1-month evaluation'},
        {'id': 'CO_334:0000196', 'label': 'cassava mosaic disease incidence 3-month evaluation'},
        {'id': 'CO_334:0000198', 'label': 'cassava mosaic disease incidence 6-month evaluation'},
        {'id': 'CO_334:0000191', 'label': 'cassava mosaic disease severity 1-month evaluation'},
        {'id': 'CO_334:0000192', 'label': 'cassava mosaic disease severity 3-month evaluation'},
        {'id': 'CO_334:0000194', 'label': 'cassava mosaic disease severity 6-month evaluation'},
        {'id': 'CO_334:0000160', 'label': 'cassava mealybug severity first evaluation'},
        {'id': 'CO_334:0000092', 'label': 'cassava storage root yield per plant'},
        {'id': 'CO_334:0000308', 'label': 'cassava storage root yield per plot'},
        {'id': 'CO_334:0000106', 'label': 'height at flowering'},
        {'id': 'CO_334:0000016', 'label': 'height of plant'},
        {'id': 'CO_334:0000012', 'label': 'height'},
        {'id': 'CO_334:0000015', 'label': 'number of root per plant'},
        {'id': 'CO_334:0000009', 'label': 'number of storage roots per plant'},
        {'id': 'CO_334:0000159', 'label': 'number of total roots per plant'},
        {'id': 'CO_334:0000099', 'label': 'percentage of dry matter content'},
        {'id': 'CO_334:0000010', 'label': 'plant architecture'},
        {'id': 'CO_334:0000074', 'label': 'plant height first evaluation'},
        {'id': 'CO_334:0000094', 'label': 'root pulp color 1-9'},
        {'id': 'CO_334:0000022', 'label': 'root shape'},
        {'id': 'CO_334:0000011', 'label': 'root size'},
        {'id': 'CO_334:0000084', 'label': 'storage root diameter in middle'},
        {'id': 'CO_334:0000163', 'label': 'storage root external pests damage severity in'},
        {'id': 'CO_334:0000216', 'label': 'storage root necrosis incidence 3-month'},
        {'id': 'CO_334:0000213', 'label': 'storage root necrosis incidence first evaluation'},
        {'id': 'CO_334:0000215', 'label': 'storage root necrosis incidence second evaluation'},
        {'id': 'CO_334:0000214', 'label': 'storage root necrosis incidence third evaluation'},
        {'id': 'CO_334:0000008', 'label': 'storage root pulp color 1-9'},
        {'id': 'CO_334:0000115', 'label': 'storage root weight'},
        {'id': 'CO_334:0000064', 'label': 'weight of storage roots per plant'},
        {'id': 'CO_334:0000021', 'label': 'width of central leaflet'},
        {'id': 'CO_334:0000020', 'label': 'width of lobe central leaflet'},
        {'id': 'CO_334:0000019', 'label': 'width'},
        {'id': 'CO_334:0000085', 'label': 'total storage root weight per plant'},
        {'id': 'CO_334:0000017', 'label': 'total weight of storage root per plant'},
        {'id': 'CO_334:0000161', 'label': 'cassava mealybug incidence first evaluation'},
        {'id': 'CO_334:0000162', 'label': 'cassava mealybug incidence second evaluation'},
    ]    
    if request.method == 'POST':
        input_fields = [
            'studyYear', 'programDbId', 'programName', 'programDescription',
            'studyDbId', 'studyName', 'studyDescription', 'studyDesign', 'plotWidth', 
            'plotLength', 'fieldSize', 'plantingDate', 'harvestDate', 'locationDbId', 
            'locationName', 'germplasmDbId', 'germplasmName', 'germplasmSynonyms', 
            'observationLevel', 'observationUnitDbId', 'observationUnitName', 'replicate', 
            'blockNumber', 'plotNumber', 'entryType'
        ]
        
        user_input = {field: request.POST.get(field) for field in input_fields}
        
        for trait in specific_traits:
            trait_id = trait['id']
            trait_value = request.POST.get(trait_id)
            user_input[trait_id] = trait_value

        predictions = predict_from_text(user_input)
        formatted_predictions = [round(pred, 2) for pred in predictions]

        interpretation = reflect_prediction(formatted_predictions)

        return JsonResponse({'predictions': formatted_predictions, 'interpretation': interpretation})
    
    context = {'specific_traits': specific_traits}
    return render(request, 'nlp_app/index.html', context)

@login_required
def fielddata_list(request):
    fielddata = FieldData.objects.all()
    fields = [f.name for f in FieldData._meta.get_fields() if isinstance(f, FloatField) or isinstance(f, IntegerField)]
    
    x_field = request.GET.get('x_field', 'fresh_storage_root_weight_per_plot')
    y_field = request.GET.get('y_field', 'top_yield')

    context = {
        'fielddata': fielddata,
        'fields': fields,
        'x_field': x_field,
        'y_field': y_field,
    }
    return render(request, 'nlp_app/fielddata_list.html', context)

'''@login_required
def fielddata_explain(request, pk):
    fielddata = get_object_or_404(FieldData, pk=pk)
    explanations = explain_record(str(fielddata))
    context = {
        'fielddata': fielddata,
        'explanations': explanations,
    }
    return render(request, 'nlp_app/fielddata_explain.html', context)'''

@login_required
def fielddata_detail(request, pk):
    fielddata = get_object_or_404(FieldData, pk=pk)
    return render(request, 'nlp_app/fielddata_detail.html', {'fielddata': fielddata})

@login_required
def fielddata_create(request):
    if request.method == 'POST':
        new_fielddata = FieldData(
            studyYear=request.POST['studyYear'],
            programDbId=request.POST['programDbId'],
            programName=request.POST['programName'],
            programDescription=request.POST['programDescription'],
            studyDbId=request.POST['studyDbId'],
            studyName=request.POST['studyName'],
            studyDescription=request.POST['studyDescription'],
            studyDesign=request.POST['studyDesign'],
            plotWidth=request.POST['plotWidth'],
            plotLength=request.POST['plotLength'],
            fieldSize=request.POST['fieldSize'],
            plantingDate=request.POST['plantingDate'],
            harvestDate=request.POST['harvestDate'],
            locationDbId=request.POST['locationDbId'],
            locationName=request.POST['locationName'],
            germplasmDbId=request.POST['germplasmDbId'],
            germplasmName=request.POST['germplasmName'],
            germplasmSynonyms=request.POST['germplasmSynonyms'],
            observationLevel=request.POST['observationLevel'],
            observationUnitDbId=request.POST['observationUnitDbId'],
            observationUnitName=request.POST['observationUnitName'],
            replicate=request.POST['replicate'],
            blockNumber=request.POST['blockNumber'],
            plotNumber=request.POST['plotNumber'],
            entryType=request.POST['entryType'],
            boiled_storage_root_color=request.POST['boiled_storage_root_color'],
            cassava_anthractnose_disease_incidence_6_month=request.POST['cassava_anthractnose_disease_incidence_6_month'],
            cassava_anthractnose_disease_incidence_9_month=request.POST['cassava_anthractnose_disease_incidence_9_month'],
            cassava_anthractnose_disease_severity_6_month=request.POST['cassava_anthractnose_disease_severity_6_month'],
            cassava_anthractnose_disease_severity_9_month=request.POST['cassava_anthractnose_disease_severity_9_month'],
            cassava_bacterial_blight_incidence_3_month=request.POST['cassava_bacterial_blight_incidence_3_month'],
            cassava_bacterial_blight_incidence_6_month=request.POST['cassava_bacterial_blight_incidence_6_month'],
            cassava_bacterial_blight_severity_3_month=request.POST['cassava_bacterial_blight_severity_3_month'],
            cassava_bacterial_blight_severity_6_month=request.POST['cassava_bacterial_blight_severity_6_month'],
            cassava_green_mite_severity_first_evaluation=request.POST['cassava_green_mite_severity_first_evaluation'],
            cassava_green_mite_severity_second_evaluation=request.POST['cassava_green_mite_severity_second_evaluation'],
            cassava_mosaic_disease_incidence_1_month=request.POST['cassava_mosaic_disease_incidence_1_month'],
            cassava_mosaic_disease_incidence_3_month=request.POST['cassava_mosaic_disease_incidence_3_month'],
            cassava_mosaic_disease_incidence_6_month=request.POST['cassava_mosaic_disease_incidence_6_month'],
            cassava_mosaic_disease_severity_1_month=request.POST['cassava_mosaic_disease_severity_1_month'],
            cassava_mosaic_disease_severity_3_month=request.POST['cassava_mosaic_disease_severity_3_month'],
            cassava_mosaic_disease_severity_6_month=request.POST['cassava_mosaic_disease_severity_6_month'],
            dry_matter_content_specific_gravity_method=request.POST['dry_matter_content_specific_gravity_method'],
            dry_matter_content_percentage=request.POST['dry_matter_content_percentage'],
            ease_of_peeling_root_cortex_visual_rating=request.POST['ease_of_peeling_root_cortex_visual_rating'],
            first_apical_branch_height_cm=request.POST['first_apical_branch_height_cm'],
            fresh_shoot_weight_kg_per_plot=request.POST['fresh_shoot_weight_kg_per_plot'],
            fresh_storage_root_weight_per_plot=request.POST['fresh_storage_root_weight_per_plot'],
            harvest_index_variable=request.POST['harvest_index_variable'],
            initial_vigor_assessment=request.POST['initial_vigor_assessment'],
            number_of_planted_stakes_per_plot=request.POST['number_of_planted_stakes_per_plot'],
            plant_architecture_visual_rating=request.POST['plant_architecture_visual_rating'],
            plant_stands_harvested_counting=request.POST['plant_stands_harvested_counting'],
            poundability_assessment=request.POST['poundability_assessment'],
            proportion_lodged_plants_percentage=request.POST['proportion_lodged_plants_percentage'],
            root_neck_length_visual_rating=request.POST['root_neck_length_visual_rating'],
            root_number_counting=request.POST['root_number_counting'],
            rotted_storage_root_counting=request.POST['rotted_storage_root_counting'],
            specific_gravity=request.POST['specific_gravity'],
            sprout_count_nine_month=request.POST['sprout_count_nine_month'],
            sprout_count_one_month=request.POST['sprout_count_one_month'],
            sprout_count_six_month=request.POST['sprout_count_six_month'],
            sprout_count_three_month=request.POST['sprout_count_three_month'],
            sprouting_proportion=request.POST['sprouting_proportion'],
            storage_root_cortex_color_visual_rating=request.POST['storage_root_cortex_color_visual_rating'],
            storage_root_periderm_color_visual_rating=request.POST['storage_root_periderm_color_visual_rating'],
            storage_root_pulp_color_visual_rating=request.POST['storage_root_pulp_color_visual_rating'],
            storage_root_shape_visual_rating=request.POST['storage_root_shape_visual_rating'],
            storage_root_size_visual_rating=request.POST['storage_root_size_visual_rating'],
            taste_of_boiled_root_rating=request.POST['taste_of_boiled_root_rating'],
            top_yield=request.POST['top_yield'],
            total_carotenoid_chart_1_8=request.POST['total_carotenoid_chart_1_8'],
            total_carotenoid_iCheck_method=request.POST['total_carotenoid_iCheck_method'],
        )
        new_fielddata.save()
        return redirect('fielddata_list')
    return render(request, 'nlp_app/fielddata_form.html')

@login_required
def fielddata_update(request, pk):
    fielddata = get_object_or_404(FieldData, pk=pk)
    if request.method == 'POST':
        fielddata.studyYear = request.POST['studyYear']
        fielddata.programDbId = request.POST['programDbId']
        fielddata.programName = request.POST['programName']
        fielddata.programDescription = request.POST['programDescription']
        fielddata.studyDbId = request.POST['studyDbId']
        fielddata.studyName = request.POST['studyName']
        fielddata.studyDescription = request.POST['studyDescription']
        fielddata.studyDesign = request.POST['studyDesign']
        fielddata.plotWidth = request.POST['plotWidth']
        fielddata.plotLength = request.POST['plotLength']
        fielddata.fieldSize = request.POST['fieldSize']
        fielddata.plantingDate = request.POST['plantingDate']
        fielddata.harvestDate = request.POST['harvestDate']
        fielddata.locationDbId = request.POST['locationDbId']
        fielddata.locationName = request.POST['locationName']
        fielddata.germplasmDbId = request.POST['germplasmDbId']
        fielddata.germplasmName = request.POST['germplasmName']
        fielddata.germplasmSynonyms = request.POST['germplasmSynonyms']
        fielddata.observationLevel = request.POST['observationLevel']
        fielddata.observationUnitDbId = request.POST['observationUnitDbId']
        fielddata.observationUnitName = request.POST['observationUnitName']
        fielddata.replicate = request.POST['replicate']
        fielddata.blockNumber = request.POST['blockNumber']
        fielddata.plotNumber = request.POST['plotNumber']
        fielddata.entryType = request.POST['entryType']
        fielddata.boiled_storage_root_color = request.POST['boiled_storage_root_color']
        fielddata.cassava_anthractnose_disease_incidence_6_month = request.POST['cassava_anthractnose_disease_incidence_6_month']
        fielddata.cassava_anthractnose_disease_incidence_9_month = request.POST['cassava_anthractnose_disease_incidence_9_month']
        fielddata.cassava_anthractnose_disease_severity_6_month = request.POST['cassava_anthractnose_disease_severity_6_month']
        fielddata.cassava_anthractnose_disease_severity_9_month = request.POST['cassava_anthractnose_disease_severity_9_month']
        fielddata.cassava_bacterial_blight_incidence_3_month = request.POST['cassava_bacterial_blight_incidence_3_month']
        fielddata.cassava_bacterial_blight_incidence_6_month = request.POST['cassava_bacterial_blight_incidence_6_month']
        fielddata.cassava_bacterial_blight_severity_3_month = request.POST['cassava_bacterial_blight_severity_3_month']
        fielddata.cassava_bacterial_blight_severity_6_month = request.POST['cassava_bacterial_blight_severity_6_month']
        fielddata.cassava_green_mite_severity_first_evaluation = request.POST['cassava_green_mite_severity_first_evaluation']
        fielddata.cassava_green_mite_severity_second_evaluation = request.POST['cassava_green_mite_severity_second_evaluation']
        fielddata.cassava_mosaic_disease_incidence_1_month = request.POST['cassava_mosaic_disease_incidence_1_month']
        fielddata.cassava_mosaic_disease_incidence_3_month = request.POST['cassava_mosaic_disease_incidence_3_month']
        fielddata.cassava_mosaic_disease_incidence_6_month = request.POST['cassava_mosaic_disease_incidence_6_month']
        fielddata.cassava_mosaic_disease_severity_1_month = request.POST['cassava_mosaic_disease_severity_1_month']
        fielddata.cassava_mosaic_disease_severity_3_month = request.POST['cassava_mosaic_disease_severity_3_month']
        fielddata.cassava_mosaic_disease_severity_6_month = request.POST['cassava_mosaic_disease_severity_6_month']
        fielddata.dry_matter_content_specific_gravity_method = request.POST['dry_matter_content_specific_gravity_method']
        fielddata.dry_matter_content_percentage = request.POST['dry_matter_content_percentage']
        fielddata.ease_of_peeling_root_cortex_visual_rating = request.POST['ease_of_peeling_root_cortex_visual_rating']
        fielddata.first_apical_branch_height_cm = request.POST['first_apical_branch_height_cm']
        fielddata.fresh_shoot_weight_kg_per_plot = request.POST['fresh_shoot_weight_kg_per_plot']
        fielddata.fresh_storage_root_weight_per_plot = request.POST['fresh_storage_root_weight_per_plot']
        fielddata.harvest_index_variable = request.POST['harvest_index_variable']
        fielddata.initial_vigor_assessment = request.POST['initial_vigor_assessment']
        fielddata.number_of_planted_stakes_per_plot = request.POST['number_of_planted_stakes_per_plot']
        fielddata.plant_architecture_visual_rating = request.POST['plant_architecture_visual_rating']
        fielddata.plant_stands_harvested_counting = request.POST['plant_stands_harvested_counting']
        fielddata.poundability_assessment = request.POST['poundability_assessment']
        fielddata.proportion_lodged_plants_percentage = request.POST['proportion_lodged_plants_percentage']
        fielddata.root_neck_length_visual_rating = request.POST['root_neck_length_visual_rating']
        fielddata.root_number_counting = request.POST['root_number_counting']
        fielddata.rotted_storage_root_counting = request.POST['rotted_storage_root_counting']
        fielddata.specific_gravity = request.POST['specific_gravity']
        fielddata.sprout_count_nine_month = request.POST['sprout_count_nine_month']
        fielddata.sprout_count_one_month = request.POST['sprout_count_one_month']
        fielddata.sprout_count_six_month = request.POST['sprout_count_six_month']
        fielddata.sprout_count_three_month = request.POST['sprout_count_three_month']
        fielddata.sprouting_proportion = request.POST['sprouting_proportion']
        fielddata.storage_root_cortex_color_visual_rating = request.POST['storage_root_cortex_color_visual_rating']
        fielddata.storage_root_periderm_color_visual_rating = request.POST['storage_root_periderm_color_visual_rating']
        fielddata.storage_root_pulp_color_visual_rating = request.POST['storage_root_pulp_color_visual_rating']
        fielddata.storage_root_shape_visual_rating = request.POST['storage_root_shape_visual_rating']
        fielddata.storage_root_size_visual_rating = request.POST['storage_root_size_visual_rating']
        fielddata.taste_of_boiled_root_rating = request.POST['taste_of_boiled_root_rating']
        fielddata.top_yield = request.POST['top_yield']
        fielddata.total_carotenoid_chart_1_8 = request.POST['total_carotenoid_chart_1_8']
        fielddata.total_carotenoid_iCheck_method = request.POST['total_carotenoid_iCheck_method']
        fielddata.save()
        return redirect('fielddata_detail', pk=fielddata.pk)
    return render(request, 'nlp_app/fielddata_form.html', {'fielddata': fielddata})

@login_required
def fielddata_delete(request, pk):
    fielddata = get_object_or_404(FieldData, pk=pk)
    if request.method == 'POST':
        fielddata.delete()
        return redirect('fielddata_list')
    return render(request, 'nlp_app/fielddata_confirm_delete.html', {'fielddata': fielddata})

@login_required
def fielddata_predict(request, pk):
    fielddata = get_object_or_404(FieldData, pk=pk)
    # Implement your prediction logic here using fielddata
    prediction_result = perform_prediction(fielddata)
    return render(request, 'nlp_app/fielddata_predict.html', {'fielddata': fielddata, 'prediction_result': prediction_result})

# Load the trained model pipeline
#model_file = os.path.join(settings.BASE_DIR, 'django_nlp_integration/nlp_app/data', 'random_forest_model.pkl')
model_file = os.path.join(os.path.dirname(__file__), 'data', 'random_forest_model.pkl')
#model_file = os.path.join(settings.BASE_DIR, 'random_forest_model.pkl')
model_pipeline = joblib.load(model_file)


def perform_prediction(fielddata):
    # Prepare data for prediction
    new_data = pd.DataFrame({
        'studyYear': [fielddata.studyYear],
        'programDbId': [fielddata.programDbId],
        'programName': [fielddata.programName],
        'programDescription': [fielddata.programDescription],
        'studyDbId': [fielddata.studyDbId],
        'studyName': [fielddata.studyName],
        'studyDescription': [fielddata.studyDescription],
        'studyDesign': [fielddata.studyDesign],
        'plotWidth': [fielddata.plotWidth],
        'plotLength': [fielddata.plotLength],
        'fieldSize': [fielddata.fieldSize],
        'plantingDate': [fielddata.plantingDate],
        'harvestDate': [fielddata.harvestDate],
        'locationDbId': [fielddata.locationDbId],
        'locationName': [fielddata.locationName],
        'germplasmDbId': [fielddata.germplasmDbId],
        'germplasmName': [fielddata.germplasmName],
        'germplasmSynonyms': [fielddata.germplasmSynonyms],
        'observationLevel': [fielddata.observationLevel],
        'observationUnitDbId': [fielddata.observationUnitDbId],
        'observationUnitName': [fielddata.observationUnitName],
        'replicate': [fielddata.replicate],
        'blockNumber': [fielddata.blockNumber],
        'plotNumber': [fielddata.plotNumber],
        'entryType': [fielddata.entryType],
        'boiled_storage_root_color': [fielddata.boiled_storage_root_color],
        'cassava_anthractnose_disease_incidence_6_month': [fielddata.cassava_anthractnose_disease_incidence_6_month],
        'cassava_anthractnose_disease_incidence_9_month': [fielddata.cassava_anthractnose_disease_incidence_9_month],
        'cassava_anthractnose_disease_severity_6_month': [fielddata.cassava_anthractnose_disease_severity_6_month],
        'cassava_anthractnose_disease_severity_9_month': [fielddata.cassava_anthractnose_disease_severity_9_month],
        'cassava_bacterial_blight_incidence_3_month': [fielddata.cassava_bacterial_blight_incidence_3_month],
        'cassava_bacterial_blight_incidence_6_month': [fielddata.cassava_bacterial_blight_incidence_6_month],
        'cassava_bacterial_blight_severity_3_month': [fielddata.cassava_bacterial_blight_severity_3_month],
        'cassava_bacterial_blight_severity_6_month': [fielddata.cassava_bacterial_blight_severity_6_month],
        'cassava_green_mite_severity_first_evaluation': [fielddata.cassava_green_mite_severity_first_evaluation],
        'cassava_green_mite_severity_second_evaluation': [fielddata.cassava_green_mite_severity_second_evaluation],
        'cassava_mosaic_disease_incidence_1_month': [fielddata.cassava_mosaic_disease_incidence_1_month],
        'cassava_mosaic_disease_incidence_3_month': [fielddata.cassava_mosaic_disease_incidence_3_month],
        'cassava_mosaic_disease_incidence_6_month': [fielddata.cassava_mosaic_disease_incidence_6_month],
        'cassava_mosaic_disease_severity_1_month': [fielddata.cassava_mosaic_disease_severity_1_month],
        'cassava_mosaic_disease_severity_3_month': [fielddata.cassava_mosaic_disease_severity_3_month],
        'cassava_mosaic_disease_severity_6_month': [fielddata.cassava_mosaic_disease_severity_6_month],
        'dry_matter_content_specific_gravity_method': [fielddata.dry_matter_content_specific_gravity_method],
        'dry_matter_content_percentage': [fielddata.dry_matter_content_percentage],
        'ease_of_peeling_root_cortex_visual_rating': [fielddata.ease_of_peeling_root_cortex_visual_rating],
        'first_apical_branch_height_cm': [fielddata.first_apical_branch_height_cm],
        'fresh_shoot_weight_kg_per_plot': [fielddata.fresh_shoot_weight_kg_per_plot],
        'fresh_storage_root_weight_per_plot': [fielddata.fresh_storage_root_weight_per_plot],
        'harvest_index_variable': [fielddata.harvest_index_variable],
        'initial_vigor_assessment': [fielddata.initial_vigor_assessment],
        'number_of_planted_stakes_per_plot': [fielddata.number_of_planted_stakes_per_plot],
        'plant_architecture_visual_rating': [fielddata.plant_architecture_visual_rating],
        'plant_stands_harvested_counting': [fielddata.plant_stands_harvested_counting],
        'poundability_assessment': [fielddata.poundability_assessment],
        'proportion_lodged_plants_percentage': [fielddata.proportion_lodged_plants_percentage],
        'root_neck_length_visual_rating': [fielddata.root_neck_length_visual_rating],
        'root_number_counting': [fielddata.root_number_counting],
        'rotted_storage_root_counting': [fielddata.rotted_storage_root_counting],
        'specific_gravity': [fielddata.specific_gravity],
        'sprout_count_nine_month': [fielddata.sprout_count_nine_month],
        'sprout_count_one_month': [fielddata.sprout_count_one_month],
        'sprout_count_six_month': [fielddata.sprout_count_six_month],
        'sprout_count_three_month': [fielddata.sprout_count_three_month],
        'sprouting_proportion': [fielddata.sprouting_proportion],
        'storage_root_cortex_color_visual_rating': [fielddata.storage_root_cortex_color_visual_rating],
        'storage_root_periderm_color_visual_rating': [fielddata.storage_root_periderm_color_visual_rating],
        'storage_root_pulp_color_visual_rating': [fielddata.storage_root_pulp_color_visual_rating],
        'storage_root_shape_visual_rating': [fielddata.storage_root_shape_visual_rating],
        'storage_root_size_visual_rating': [fielddata.storage_root_size_visual_rating],
        'taste_of_boiled_root_rating': [fielddata.taste_of_boiled_root_rating],
        'top_yield': [fielddata.top_yield],
        'total_carotenoid_chart_1_8': [fielddata.total_carotenoid_chart_1_8],
        'total_carotenoid_iCheck_method': [fielddata.total_carotenoid_iCheck_method]
    })
    
    # Debugging: print the raw new data
    print("Raw new data for prediction:", new_data)

    # Ensure all required columns are present in the new data
    numeric_features = model_pipeline.named_steps['preprocessor'].transformers_[0][2]
    categorical_features = model_pipeline.named_steps['preprocessor'].transformers_[1][2]
    
    all_features = list(numeric_features) + list(categorical_features)
    
    for col in all_features:
        if col not in new_data.columns:
            new_data[col] = 0  # Fill with default value, adjust as necessary
    
    # Select only the columns used in training
    new_data = new_data[all_features]

    # Debugging: print the input data
    print("New data for prediction:", new_data)
    
    # Preprocess the new data using the same pipeline
    new_data_preprocessed = model_pipeline.named_steps['preprocessor'].transform(new_data)
    
    # Make predictions on the new data
    new_predictions = model_pipeline.named_steps['regressor'].predict(new_data_preprocessed)
    
    print("Predictions on new data:", new_predictions)

    return new_predictions[0]

# nlp = spacy.load('en_core_web_sm')
'''
@login_required
def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('message')
        doc = nlp(user_input)
        response = {
            'entities': [(ent.text, ent.label_) for ent in doc.ents],
            'message': f"Processed input: {user_input}"
        }
        return JsonResponse(response)
    return render(request, 'chatbot.html') '''




def generate_explanation(features, prediction, shap_values):
    truncated_features = {k: features[k] for k in list(features)[:5]}
    truncated_shap_values = shap_values[:5]
    prompt = (
        "Given the following features of a cassava crop:\n\n"
        f"{truncated_features}\n\n"
        f"The predicted yield is {prediction:.2f}. "
        "Explain how each feature impacts the yield prediction, considering the following SHAP values:\n\n"
        f"{truncated_shap_values}\n\n" 
    )
    generator = pipeline("text-generation", model="gpt2", pad_token_id=50256)
    response = generator(prompt, max_new_tokens=100, num_return_sequences=1)
    explanation = response[0]['generated_text'].strip()
    return explanation

def fielddata_explain(request, pk):
    # Retrieve the FieldData instance by primary key
    fielddata = get_object_or_404(FieldData, pk=pk)

    # Create the new data DataFrame based on FieldData instance
    new_data = pd.DataFrame({
        'studyYear': [fielddata.studyYear],
        'programDbId': [fielddata.programDbId],
        'studyDbId': [fielddata.studyDbId],
        'programName': [fielddata.programName],
        'plotWidth': [fielddata.plotWidth],
        'plotLength': [fielddata.plotLength],
        'locationDbId': [fielddata.locationDbId],
        'locationName': [fielddata.locationName],
        'germplasmDbId': [fielddata.germplasmDbId],
        'germplasmName': [fielddata.germplasmName],
        'observationLevel': [fielddata.observationLevel],
        'replicate': [fielddata.replicate],
        'blockNumber': [fielddata.blockNumber],
        'plotNumber': [fielddata.plotNumber],
        'cassava_anthractnose_disease_incidence_9_month': [fielddata.cassava_anthractnose_disease_incidence_9_month],
        'cassava_anthractnose_disease_severity_9_month': [fielddata.cassava_anthractnose_disease_severity_9_month],
        'cassava_bacterial_blight_incidence_6_month': [fielddata.cassava_bacterial_blight_incidence_6_month],
        'cassava_green_mite_severity_second_evaluation': [fielddata.cassava_green_mite_severity_second_evaluation],
        'fresh_storage_root_weight_per_plot': [fielddata.fresh_storage_root_weight_per_plot],
        'number_of_planted_stakes_per_plot': [fielddata.number_of_planted_stakes_per_plot],
        'plant_architecture_visual_rating': [fielddata.plant_architecture_visual_rating],
        'root_number_counting': [fielddata.root_number_counting],
        'specific_gravity': [fielddata.specific_gravity],
    })
    
    # Ensure all required columns are present in the new data
    numeric_features = model_pipeline.named_steps['preprocessor'].transformers_[0][2]
    categorical_features = model_pipeline.named_steps['preprocessor'].transformers_[1][2]
    
    all_features = list(numeric_features) + list(categorical_features)
    
    for col in all_features:
        if col not in new_data.columns:
            new_data[col] = 0  # Fill with default value, adjust as necessary
    
    # Select only the columns used in training
    new_data = new_data[all_features]

    # Preprocess the new data using the same pipeline
    new_data_preprocessed = model_pipeline.named_steps['preprocessor'].transform(new_data)

    # Retrieve preprocessed feature names
    try:
        preprocessed_numeric_features = model_pipeline.named_steps['preprocessor'].transformers_[0][1].get_feature_names_out(numeric_features).tolist()
        preprocessed_categorical_features = model_pipeline.named_steps['preprocessor'].transformers_[1][1].get_feature_names_out(categorical_features).tolist()
        preprocessed_feature_names = preprocessed_numeric_features + preprocessed_categorical_features
    except ValueError as e:
        print(f"Error retrieving feature names: {e}")
        preprocessed_feature_names = all_features  # Fallback to original feature names

    # Make predictions on the new data
    new_predictions = model_pipeline.named_steps['regressor'].predict(new_data_preprocessed)
    print("Predictions on new data:", new_predictions)

    # Create a SHAP explainer for the model
    explainer = shap.TreeExplainer(model_pipeline.named_steps['regressor'])

    # Calculate SHAP values for the prediction
    shap_values = explainer.shap_values(new_data_preprocessed)    
    
    # Prepare data for explanation generation
    features = new_data.iloc[0].to_dict()
    prediction = new_predictions[0]
    shap_value = shap_values[0]
    explanation = generate_explanation(features, prediction, shap_value)

    # Generate a SHAP summary plot
    shap.summary_plot(shap_values, new_data_preprocessed, feature_names=preprocessed_feature_names)

    # Prepare context for rendering the template
    context = {
        'fielddata': fielddata,
        'explanation': explanation,
    }

    # Render the explanation page
    return render(request, 'nlp_app/fielddata_explain.html', context)
'''
@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        user_message = request.POST.get('message')

        # Here, you'll need to extract the relevant features from user_message
        # For now, we will reuse the data processing from fielddata_explain as an example.
        
        # Dummy implementation: replace this with actual logic to extract or define features based on user_message
        fielddata = get_object_or_404(FieldData, pk=1)  # Adjust this to get the correct FieldData instance
        new_data = pd.DataFrame({
            'studyYear': [fielddata.studyYear],
            'programDbId': [fielddata.programDbId],
            'studyDbId': [fielddata.studyDbId],
            'programName': [fielddata.programName],
            'plotWidth': [fielddata.plotWidth],
            'plotLength': [fielddata.plotLength],
            'locationDbId': [fielddata.locationDbId],
            'locationName': [fielddata.locationName],
            'germplasmDbId': [fielddata.germplasmDbId],
            'germplasmName': [fielddata.germplasmName],
            'observationLevel': [fielddata.observationLevel],
            'replicate': [fielddata.replicate],
            'blockNumber': [fielddata.blockNumber],
            'plotNumber': [fielddata.plotNumber],
            'cassava_anthractnose_disease_incidence_9_month': [fielddata.cassava_anthractnose_disease_incidence_9_month],
            'cassava_anthractnose_disease_severity_9_month': [fielddata.cassava_anthractnose_disease_severity_9_month],
            'cassava_bacterial_blight_incidence_6_month': [fielddata.cassava_bacterial_blight_incidence_6_month],
            'cassava_green_mite_severity_second_evaluation': [fielddata.cassava_green_mite_severity_second_evaluation],
            'fresh_storage_root_weight_per_plot': [fielddata.fresh_storage_root_weight_per_plot],
            'number_of_planted_stakes_per_plot': [fielddata.number_of_planted_stakes_per_plot],
            'plant_architecture_visual_rating': [fielddata.plant_architecture_visual_rating],
            'root_number_counting': [fielddata.root_number_counting],
            'specific_gravity': [fielddata.specific_gravity],
        })

        # Ensure all required columns are present in the new data
        numeric_features = model_pipeline.named_steps['preprocessor'].transformers_[0][2]
        categorical_features = model_pipeline.named_steps['preprocessor'].transformers_[1][2]
        
        all_features = list(numeric_features) + list(categorical_features)
        
        for col in all_features:
            if col not in new_data.columns:
                new_data[col] = 0  # Fill with default value, adjust as necessary
        
        # Select only the columns used in training
        new_data = new_data[all_features]

        # Preprocess the new data using the same pipeline
        new_data_preprocessed = model_pipeline.named_steps['preprocessor'].transform(new_data)

        # Make predictions on the new data
        new_predictions = model_pipeline.named_steps['regressor'].predict(new_data_preprocessed)
        print("Predictions on new data:", new_predictions)

        # Create a SHAP explainer for the model
        explainer = shap.TreeExplainer(model_pipeline.named_steps['regressor'])

        # Calculate SHAP values for the prediction
        shap_values = explainer.shap_values(new_data_preprocessed)    

        # Prepare data for explanation generation
        features = new_data.iloc[0].to_dict()
        prediction = new_predictions[0]
        shap_value = shap_values[0]
        explanation = generate_explanation(features, prediction, shap_value)

        #return HttpResponse("Chatbot endpoint is working!")

        return JsonResponse({'response': explanation})
        #return JsonResponse({'response': response_message})
    return JsonResponse({'error': 'Invalid request'}, status=400) '''

'''
@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        return JsonResponse({'response': 'This is a test response'})
    return JsonResponse({'error': 'Invalid request'}, status=400) '''

'''
@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        user_message = request.POST.get('message')

        # Your existing code starts here
        fielddata = get_object_or_404(FieldData, pk=1)  # Adjust this to get the correct FieldData instance
        new_data = pd.DataFrame({
            'studyYear': [fielddata.studyYear],
            'programDbId': [fielddata.programDbId],
            'studyDbId': [fielddata.studyDbId],
            'programName': [fielddata.programName],
            'plotWidth': [fielddata.plotWidth],
            'plotLength': [fielddata.plotLength],
            'locationDbId': [fielddata.locationDbId],
            'locationName': [fielddata.locationName],
            'germplasmDbId': [fielddata.germplasmDbId],
            'germplasmName': [fielddata.germplasmName],
            'observationLevel': [fielddata.observationLevel],
            'replicate': [fielddata.replicate],
            'blockNumber': [fielddata.blockNumber],
            'plotNumber': [fielddata.plotNumber],
            'cassava_anthractnose_disease_incidence_9_month': [fielddata.cassava_anthractnose_disease_incidence_9_month],
            'cassava_anthractnose_disease_severity_9_month': [fielddata.cassava_anthractnose_disease_severity_9_month],
            'cassava_bacterial_blight_incidence_6_month': [fielddata.cassava_bacterial_blight_incidence_6_month],
            'cassava_green_mite_severity_second_evaluation': [fielddata.cassava_green_mite_severity_second_evaluation],
            'fresh_storage_root_weight_per_plot': [fielddata.fresh_storage_root_weight_per_plot],
            'number_of_planted_stakes_per_plot': [fielddata.number_of_planted_stakes_per_plot],
            'plant_architecture_visual_rating': [fielddata.plant_architecture_visual_rating],
            'root_number_counting': [fielddata.root_number_counting],
            'specific_gravity': [fielddata.specific_gravity],
        })

        # Ensure all required columns are present in the new data
        numeric_features = model_pipeline.named_steps['preprocessor'].transformers_[0][2]
        categorical_features = model_pipeline.named_steps['preprocessor'].transformers_[1][2]
        
        all_features = list(numeric_features) + list(categorical_features)
        
        for col in all_features:
            if col not in new_data.columns:
                new_data[col] = 0  # Fill with default value, adjust as necessary
        
        # Select only the columns used in training
        new_data = new_data[all_features]

        # Preprocess the new data using the same pipeline
        new_data_preprocessed = model_pipeline.named_steps['preprocessor'].transform(new_data)

        # Make predictions on the new data
        new_predictions = model_pipeline.named_steps['regressor'].predict(new_data_preprocessed)
        print("Predictions on new data:", new_predictions)

        # Create a SHAP explainer for the model
        explainer = shap.TreeExplainer(model_pipeline.named_steps['regressor'])

        # Calculate SHAP values for the prediction
        shap_values = explainer.shap_values(new_data_preprocessed)    

        # Prepare data for explanation generation
        features = new_data.iloc[0].to_dict()
        prediction = new_predictions[0]
        shap_value = shap_values[0]
        explanation = generate_explanation(features, prediction, shap_value)

        # Send the explanation back as the response
        return JsonResponse({'response': explanation})
    return JsonResponse({'error': 'Invalid request'}, status=400) '''

@csrf_exempt
def chatbot_response(request, pk):
    if request.method == "POST":
        try:
            user_message = request.POST.get('message')
            print("User message received:", user_message)

            fielddata = get_object_or_404(FieldData, pk=pk)
            print("FieldData fetched:", fielddata)

            # Continue with your data processing and prediction logic
            try:
                new_data = pd.DataFrame({
                    'studyYear': [fielddata.studyYear],
                    'programDbId': [fielddata.programDbId],
                    'studyDbId': [fielddata.studyDbId],
                    'programName': [fielddata.programName],
                    'plotWidth': [fielddata.plotWidth],
                    'plotLength': [fielddata.plotLength],
                    'locationDbId': [fielddata.locationDbId],
                    'locationName': [fielddata.locationName],
                    'germplasmDbId': [fielddata.germplasmDbId],
                    'germplasmName': [fielddata.germplasmName],
                    'observationLevel': [fielddata.observationLevel],
                    'replicate': [fielddata.replicate],
                    'blockNumber': [fielddata.blockNumber],
                    'plotNumber': [fielddata.plotNumber],
                    'cassava_anthractnose_disease_incidence_9_month': [fielddata.cassava_anthractnose_disease_incidence_9_month],
                    'cassava_anthractnose_disease_severity_9_month': [fielddata.cassava_anthractnose_disease_severity_9_month],
                    'cassava_bacterial_blight_incidence_6_month': [fielddata.cassava_bacterial_blight_incidence_6_month],
                    'cassava_green_mite_severity_second_evaluation': [fielddata.cassava_green_mite_severity_second_evaluation],
                    'fresh_storage_root_weight_per_plot': [fielddata.fresh_storage_root_weight_per_plot],
                    'number_of_planted_stakes_per_plot': [fielddata.number_of_planted_stakes_per_plot],
                    'plant_architecture_visual_rating': [fielddata.plant_architecture_visual_rating],
                    'root_number_counting': [fielddata.root_number_counting],
                    'specific_gravity': [fielddata.specific_gravity],
                })

                # Ensure all required columns are present in the new data
                numeric_features = model_pipeline.named_steps['preprocessor'].transformers_[0][2]
                categorical_features = model_pipeline.named_steps['preprocessor'].transformers_[1][2]

                all_features = list(numeric_features) + list(categorical_features)
                
                for col in all_features:
                    if col not in new_data.columns:
                        new_data[col] = 0  # Fill with default value, adjust as necessary

                new_data = new_data[all_features]

                new_data_preprocessed = model_pipeline.named_steps['preprocessor'].transform(new_data)
                new_predictions = model_pipeline.named_steps['regressor'].predict(new_data_preprocessed)
                print("Predictions on new data:", new_predictions)

                explainer = shap.TreeExplainer(model_pipeline.named_steps['regressor'])
                shap_values = explainer.shap_values(new_data_preprocessed)    

                features = new_data.iloc[0].to_dict()
                prediction = new_predictions[0]
                shap_value = shap_values[0]
                explanation = generate_explanation(features, prediction, shap_value)

                return JsonResponse({'response': explanation})
            except Exception as e:
                print("Error during prediction or explanation:", e)
                return JsonResponse({'error': f'Prediction or explanation failed: {str(e)}'}, status=500)

        except Exception as e:
            print("Error during data fetching or preprocessing:", e)
            return JsonResponse({'error': f'Data fetch or preprocessing failed: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)


