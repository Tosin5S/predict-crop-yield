from django.db import models

class YieldPrediction(models.Model):
    germplasmDbId = models.CharField(max_length=20)
    cassava_mosaic_disease_severity = models.IntegerField()
    fresh_root_yield = models.FloatField()