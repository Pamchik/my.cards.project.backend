from django.db import models
from django.apps import apps
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, m2m_changed
from changelog.models import NewChangeLogsModel, FieldValueMappingModel
from django.db import transaction


backend_api_models = []
backend_api_config = apps.get_app_config('backend_api')

for model in backend_api_config.get_models():
    backend_api_models.append(f'{model._meta.app_label}.{model.__name__}')

def get_changed_fields(instance):
    changed_fields = {}
    for field in instance._meta.fields:
        field_name = field.name
        old_value = getattr(instance._old_instance, field_name, None)
        new_value = getattr(instance, field_name, None)
        if old_value != new_value:
            changed_fields[field_name] = {'old': old_value, 'new': new_value}
    return changed_fields

def format_data_with_mapping(model_name, field_name, value):
    try:
        mapping = FieldValueMappingModel.objects.get(
            model_name=model_name,
            field_name=field_name
        )

        if isinstance(value, models.Model):
            rus_value = getattr(value, mapping.view_key_rus, None)
            eng_value = getattr(value, mapping.view_key_eng, None)
        else:
            rus_value = value
            eng_value = value


        formatted_value = {
            'rus': rus_value if rus_value else '',
            'eng': eng_value if eng_value else '',
        }
        return formatted_value
    except FieldValueMappingModel.DoesNotExist:
        formatted_value = {
            'rus': value if value else '',
            'eng': value if value else ''
        }
        return formatted_value

def get_related_values(queryset, model_name, field_name):
    try:
        mapping = FieldValueMappingModel.objects.get(
            model_name=model_name,
            field_name=field_name
        )

        rus_values = []
        eng_values = []

        for rel_inst in queryset:
            if isinstance(rel_inst, models.Model):
                rus_value = getattr(rel_inst, mapping.view_key_rus, None)
                eng_value = getattr(rel_inst, mapping.view_key_eng, None)
            else:
                rus_value = eng_value = rel_inst

            rus_values.append(rus_value)
            eng_values.append(eng_value)

        return {'rus': '; '.join(rus_values), 'eng': '; '.join(eng_values)}

    except FieldValueMappingModel.DoesNotExist:
        rus_values = [str(rel_inst) for rel_inst in queryset]
        eng_values = [str(rel_inst) for rel_inst in queryset]
        return {'rus': '; '.join(rus_values), 'eng': '; '.join(eng_values)}


# Сигнал для обычных полей
@receiver(pre_save)
def save_previous_values(sender, instance, **kwargs):
    model_label = f'{sender._meta.app_label}.{sender.__name__}'
    if model_label in backend_api_models:
        if instance.pk:
            try:
                instance._old_instance = sender.objects.filter(pk=instance.pk).first()
            except sender.DoesNotExist:
                instance._old_instance = None
        else:
            instance._old_instance = None

@receiver(post_save)
def log_changes_on_save(sender, instance, **kwargs):
    request_exist = kwargs.get('request_exist', False)

    if request_exist:
        request = kwargs.get('request')
        if request:
            username = request.username
            source = request.host
        else:
            username = 'unknown'
            source = 'unknown'    

        model_label = f'{sender._meta.app_label}.{sender.__name__}'
        if model_label in backend_api_models:
            def log_change():
                row_number = instance.id
                changed_fields = get_changed_fields(instance)

                for field_name, values in changed_fields.items():
                    prev_data = values['old'] if values['old'] is not None else None
                    new_data = values['new'] if values['new'] is not None else None

                    prev_data = format_data_with_mapping(sender.__name__, field_name, prev_data)
                    new_data = format_data_with_mapping(sender.__name__, field_name, new_data)

                    if field_name == 'id':
                        NewChangeLogsModel.objects.create(
                            username=username,
                            model_name=sender.__name__,
                            row_number=row_number,
                            field_name=field_name,
                            prev_data=prev_data,
                            new_data=new_data,
                            action='create',
                            source=source,
                        )
                    else:
                        NewChangeLogsModel.objects.create(
                            username=username,
                            model_name=sender.__name__,
                            row_number=row_number,
                            field_name=field_name,
                            prev_data=prev_data,
                            new_data=new_data,
                            action='update',
                            source=source,
                        )
            transaction.on_commit(log_change)

# Сигнал для полей ManyToMany
@receiver(pre_save)
def store_m2m_prev_data(sender, instance, **kwargs):
    if not instance.pk:
        return
    instance._m2m_prev_data = {}
    for field in instance._meta.many_to_many:
        field_name = field.name
        instance._m2m_prev_data[field_name] = set(field.related_model.objects.filter(id__in=getattr(instance, field_name).values_list('id', flat=True)))

@receiver(m2m_changed)
def log_m2m_changes(sender, instance, action, **kwargs):
    request = kwargs.get('request')
    request_exist = kwargs.get('request_exist', False)
    if request_exist:
        if request:
            username = request.username
            source = request.host
        else:
            username = 'unknown'
            source = 'unknown'  

        if action not in ["post_add", "post_remove", "post_clear"]:
            return
        if not hasattr(instance, '_m2m_prev_data'):
            instance._m2m_prev_data = {}

        for field in instance._meta.many_to_many:
            if field.remote_field.through._meta.model_name == sender._meta.model_name:
                field_name = field.name
                break
        else:
            return

        with transaction.atomic():

            prev_data = get_related_values(instance._m2m_prev_data.get(field_name, ''), instance.__class__.__name__, field_name)
            new_data = get_related_values(getattr(instance, field_name).all(), instance.__class__.__name__, field_name)

            if prev_data != new_data:
                NewChangeLogsModel.objects.create(
                    username=username,
                    model_name=instance.__class__.__name__,
                    row_number=instance.id,
                    field_name=field_name,
                    prev_data=prev_data,
                    new_data=new_data,
                    action='update',
                    source=source,
                )

