from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import FieldData
from .nlp import predict_from_text, reflect_prediction

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

def fielddata_list(request):
    fielddata = FieldData.objects.all()
    return render(request, 'nlp_app/fielddata_list.html', {'fielddata': fielddata})

def fielddata_detail(request, pk):
    fielddata = get_object_or_404(FieldData, pk=pk)
    return render(request, 'nlp_app/fielddata_detail.html', {'fielddata': fielddata})

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

def fielddata_delete(request, pk):
    fielddata = get_object_or_404(FieldData, pk=pk)
    if request.method == 'POST':
        fielddata.delete()
        return redirect('fielddata_list')
    return render(request, 'nlp_app/fielddata_confirm_delete.html', {'fielddata': fielddata})
