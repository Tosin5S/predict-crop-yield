from django.db import models
from datetime import date
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class YourModel(models.Model):
    # Define your model fields here
    name = models.CharField(max_length=100)
    # other fields...

    def __str__(self):
        return self.name

class FieldData(models.Model):
    studyYear = models.IntegerField(default=0)
    programDbId = models.CharField(max_length=255, default='')
    programName = models.CharField(max_length=255, default='')
    programDescription = models.TextField(default='')
    studyDbId = models.CharField(max_length=255, default='')
    studyName = models.CharField(max_length=255, default='')
    studyDescription = models.TextField(default='')
    studyDesign = models.CharField(max_length=255, default='')
    plotWidth = models.FloatField(default=0.0)
    plotLength = models.FloatField(default=0.0)
    fieldSize = models.FloatField(default=0.0)
    plantingDate = models.DateField(default=date(2024, 1, 1))
    harvestDate = models.DateField(default=date(2024, 1, 1))
    locationDbId = models.CharField(max_length=255, default='')
    locationName = models.CharField(max_length=255, default='')
    germplasmDbId = models.CharField(max_length=255, default='')
    germplasmName = models.CharField(max_length=255, default='')
    germplasmSynonyms = models.CharField(max_length=255, blank=True, null=True, default='')
    observationLevel = models.CharField(max_length=255, default='')
    observationUnitDbId = models.CharField(max_length=255, default='')
    observationUnitName = models.CharField(max_length=255, default='')
    replicate = models.IntegerField(default=0)
    blockNumber = models.IntegerField(default=0)
    plotNumber = models.IntegerField(default=0)
    entryType = models.CharField(max_length=255, default='Unknown')
    boiled_storage_root_color = models.CharField(max_length=255, default='Unknown')
    cassava_anthractnose_disease_incidence_6_month = models.FloatField(default=0.0)
    cassava_anthractnose_disease_incidence_9_month = models.FloatField(default=0.0)
    cassava_anthractnose_disease_severity_6_month = models.FloatField(default=0.0)
    cassava_anthractnose_disease_severity_9_month = models.FloatField(default=0.0)
    cassava_bacterial_blight_incidence_3_month = models.FloatField(default=0.0)
    cassava_bacterial_blight_incidence_6_month = models.FloatField(default=0.0)
    cassava_bacterial_blight_severity_3_month = models.FloatField(default=0.0)
    cassava_bacterial_blight_severity_6_month = models.FloatField(default=0.0)
    cassava_green_mite_severity_first_evaluation = models.FloatField(default=0.0)
    cassava_green_mite_severity_second_evaluation = models.FloatField(default=0.0)
    cassava_mosaic_disease_incidence_1_month = models.FloatField(default=0.0)
    cassava_mosaic_disease_incidence_3_month = models.FloatField(default=0.0)
    cassava_mosaic_disease_incidence_6_month = models.FloatField(default=0.0)
    cassava_mosaic_disease_severity_1_month = models.FloatField(default=0.0)
    cassava_mosaic_disease_severity_3_month = models.FloatField(default=0.0)
    cassava_mosaic_disease_severity_6_month = models.FloatField(default=0.0)
    dry_matter_content_specific_gravity_method = models.FloatField(default=0.0)
    dry_matter_content_percentage = models.FloatField(default=0.0)
    ease_of_peeling_root_cortex_visual_rating = models.IntegerField(default=0)
    first_apical_branch_height_cm = models.FloatField(default=0.0)
    fresh_shoot_weight_kg_per_plot = models.FloatField(default=0.0)
    fresh_storage_root_weight_per_plot = models.FloatField(default=0.0)
    harvest_index_variable = models.FloatField(default=0.0)
    initial_vigor_assessment = models.IntegerField(default=0)
    number_of_planted_stakes_per_plot = models.IntegerField(default=0)
    plant_architecture_visual_rating = models.IntegerField(default=0)
    plant_stands_harvested_counting = models.IntegerField(default=0)
    poundability_assessment = models.IntegerField(default=0)
    proportion_lodged_plants_percentage = models.FloatField(default=0.0)
    root_neck_length_visual_rating = models.IntegerField(default=0)
    root_number_counting = models.IntegerField(default=0)
    rotted_storage_root_counting = models.IntegerField(default=0)
    specific_gravity = models.FloatField(default=0.0)
    sprout_count_nine_month = models.IntegerField(default=0)
    sprout_count_one_month = models.IntegerField(default=0)
    sprout_count_six_month = models.IntegerField(default=0)
    sprout_count_three_month = models.IntegerField(default=0)
    sprouting_proportion = models.FloatField(default=0.0)
    storage_root_cortex_color_visual_rating = models.IntegerField(default=0)
    storage_root_periderm_color_visual_rating = models.IntegerField(default=0)
    storage_root_pulp_color_visual_rating = models.IntegerField(default=0)
    storage_root_shape_visual_rating = models.IntegerField(default=0)
    storage_root_size_visual_rating = models.IntegerField(default=0)
    taste_of_boiled_root_rating = models.IntegerField(default=0)
    top_yield = models.FloatField(default=0.0)
    total_carotenoid_chart_1_8 = models.FloatField(default=0.0)
    total_carotenoid_iCheck_method = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.programName} - {self.studyName}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()