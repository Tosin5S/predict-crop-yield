from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import FloatField, IntegerField
import pandas as pd
import joblib
import os
from .models import FieldData
from .nlp_utils import explain_record
from .nlp import predict_from_text, reflect_prediction

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
def index(request):
    specific_traits = [
        {'id': 'CO_334:0000114', 'label': 'boiled storage root color visual 1-3'},
        # Add other traits here
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

@login_required
def fielddata_explain(request, pk):
    fielddata = get_object_or_404(FieldData, pk=pk)
    explanations = explain_record(str(fielddata))
    context = {
        'fielddata': fielddata,
        'explanations': explanations,
    }
    return render(request, 'nlp_app/fielddata_explain.html', context)

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
            stay_green_assessment=request.POST['stay_green_assessment'],
            storage_root_length_cm=request.POST['storage_root_length_cm'],
            storage_root_weight_kg_per_plot=request.POST['storage_root_weight_kg_per_plot'],
            total_number_storage_roots_counting=request.POST['total_number_storage_roots_counting'],
            total_storage_root_weight_kg_per_plot=request.POST['total_storage_root_weight_kg_per_plot'],
            usable_storage_root_weight_kg_per_plot=request.POST['usable_storage_root_weight_kg_per_plot'],
            weight_of_stake_kg=request.POST['weight_of_stake_kg'],
            weevil_infestation_incidence=request.POST['weevil_infestation_incidence'],
            weevil_infestation_severity=request.POST['weevil_infestation_severity'],
        )
        new_fielddata.save()
        return redirect('fielddata_list')
    return render(request, 'nlp_app/fielddata_create.html')

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
        fielddata.stay_green_assessment = request.POST['stay_green_assessment']
        fielddata.storage_root_length_cm = request.POST['storage_root_length_cm']
        fielddata.storage_root_weight_kg_per_plot = request.POST['storage_root_weight_kg_per_plot']
        fielddata.total_number_storage_roots_counting = request.POST['total_number_storage_roots_counting']
        fielddata.total_storage_root_weight_kg_per_plot = request.POST['total_storage_root_weight_kg_per_plot']
        fielddata.usable_storage_root_weight_kg_per_plot = request.POST['usable_storage_root_weight_kg_per_plot']
        fielddata.weight_of_stake_kg = request.POST['weight_of_stake_kg']
        fielddata.weevil_infestation_incidence = request.POST['weevil_infestation_incidence']
        fielddata.weevil_infestation_severity = request.POST['weevil_infestation_severity']
        fielddata.save()
        return redirect('fielddata_list')
    return render(request, 'nlp_app/fielddata_update.html', {'fielddata': fielddata})

@login_required
def fielddata_delete(request, pk):
    fielddata = get_object_or_404(FieldData, pk=pk)
    if request.method == 'POST':
        fielddata.delete()
        return redirect('fielddata_list')
    return render(request, 'nlp_app/fielddata_delete.html', {'fielddata': fielddata})
