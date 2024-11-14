from django.db import models

class NewChangeLogsModel(models.Model):
    username = models.CharField(max_length=255, null=True, blank=True) 
    model_name = models.CharField(max_length=100, null=True, blank=True)
    row_number = models.IntegerField(null=True, blank=True)
    field_name = models.CharField(max_length=100, null=True, blank=True)
    prev_data = models.CharField(max_length=2000, null=True, blank=True)
    new_data = models.CharField(max_length=2000, null=True, blank=True)
    action = models.CharField(max_length=16, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=255, null=True, blank=True)

class FieldValueMappingModel(models.Model):
    model_name = models.CharField(max_length=100, null=False, blank=False)
    field_name = models.CharField(max_length=100, null=False, blank=False)
    view_key_rus = models.CharField(max_length=100, null=False, blank=False)
    view_key_eng = models.CharField(max_length=100, null=False, blank=False)