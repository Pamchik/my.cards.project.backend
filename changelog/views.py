from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from django.db.models import Subquery


from .models import (
    NewChangeLogsModel
)

from backend_api.models import (
    BankPrices,
    ProductionData,
    VendorPrices,
    PaymentsInfo,
    ProcessData,
    PaymentSystemApprovals,
    DeliveriesInfo,
    AnnexesConditionsData,
    POConditionsData,
    Files,
    Gallery,
    ProjectLine,
    KeyExchangeProjects,
    CardTestingProjects,
    TestCardTransfer
)

def format_str_date(date_obj):
    try:
        return date_obj.strftime('%d.%m.%Y %H:%M')
    except (ValueError, TypeError):
        return date_obj

class ChangeLogsSet(viewsets.ViewSet):
    
    def list(self, request):

        def get_response(latest_change):
            if latest_change:
                response_data = {
                    "timestamp": format_str_date(latest_change.timestamp),
                    "username": latest_change.username,
                }
                return response_data
            else:
                response_data = {
                    "timestamp": None,
                    "username": None,
                }
                return response_data

        def get_subquery(model_class, id_value):
                return model_class.objects.filter(
                    line_number=id_value
                ).values('id')  
    
        def get_delivery_subquery(model_class, id_value, process_step):
            if process_step == '12':
                return model_class.objects.filter(
                    line_number=id_value,
                    company_type='vendor'
                ).values('id')  
            else:
                return model_class.objects.filter(
                    line_number=id_value,
                    company_type='bank'
                ).values('id')            

        def get_payment_subquery(model_class, id_value, process_step):
            if process_step == '5':
                return model_class.objects.filter(
                    line_number=id_value,
                    company_type='vendor'
                ).values('id')  
            else:
                return model_class.objects.filter(
                    line_number=id_value,
                    company_type='bank'
                ).values('id')    
                    
        def get_files_gallery_subquery(model_class, id_value):
            return model_class.objects.filter(
                model_type=model_name,
                number=id_value
            ).values('id')
        
        def get_files_process_subquery(model_class, id_value):
            return model_class.objects.filter(
                model_type='ProjectLine',
                number=id_value,
                process_step=process_step
            ).values('id')
        
        def get_card_testing_subquery(model_class, id_value):
            return model_class.objects.filter(
                card_testing_project=id_value
            ).values('id')

        def get_latest_change(id_value, *models):
            queries = Q()
            for model_class in models:

                if model_class in [Files, Gallery]:
                    subquery = get_files_gallery_subquery(model_class, id_value)
                elif model_class == TestCardTransfer:
                    subquery = get_card_testing_subquery(model_class, id_value)
                else:
                    subquery = get_subquery(model_class, id_value)

                queries |= Q(
                    model_name=model_class.__name__,
                    row_number__in=Subquery(subquery),
                )

            queries |= Q(
                model_name=model_name,
                row_number=id_value,
                action='update'
            )
            
            latest_change = (
                NewChangeLogsModel.objects
                    .filter(queries)
                    .order_by('-timestamp')
                    .first()
            )

            result = get_response(latest_change)
            return result
        
        def get_latest_process_change(process_step, id_value, *models):

            queries = Q()
            for model_class in models:
                if model_class == DeliveriesInfo:
                    subquery = get_delivery_subquery(model_class, id_value, process_step)
                elif model_class == PaymentsInfo:
                    subquery = get_payment_subquery(model_class, id_value, process_step)
                elif model_class in [Files, Gallery]:
                    subquery = get_files_process_subquery(model_class, id_value)
                else:
                    subquery = get_subquery(model_class, id_value)

                queries |= Q(
                    model_name=model_class.__name__,
                    row_number__in=Subquery(subquery),
                    action='update'
                )

            queries |= Q(
                model_name="ProcessData",
                row_number__in=Subquery(
                    ProcessData.objects.filter(
                        line_number=id_value,
                        process_step=process_step,
                    ).values('id')
                ),
                action='update'
            )                

            latest_change = (
                NewChangeLogsModel.objects
                    .filter(queries)
                    .order_by('-timestamp')
                    .first()
            )
        
            result = get_response(latest_change)
            return result

        def get_create_changelog(id_value, model_name, process_step):
            if model_name == 'ProcessData':
                latest_change = (
                    NewChangeLogsModel.objects
                    .filter(
                        model_name=model_name,
                        row_number__in=Subquery(
                            ProcessData.objects.filter(
                                line_number=id_value,
                                process_step=process_step
                            ).values('id')
                        ),
                        action='create'
                    )
                    .order_by('timestamp')
                    .first()
                )
                result = get_response(latest_change)
                return result
            else:
                latest_change = (
                    NewChangeLogsModel.objects
                    .filter(
                        model_name=model_name,
                        row_number=id_value,
                        action='create'
                    )
                    .order_by('timestamp')
                    .first()
                )
                result = get_response(latest_change)
                return result
        def get_update_changelog(id_value, model_name, process_step):  
            if model_name == 'ProjectLine':
                latest_date = get_latest_change(
                    id_value, 
                    ProductionData, 
                    BankPrices, 
                    VendorPrices, 
                    PaymentsInfo, 
                    ProcessData, 
                    PaymentSystemApprovals, 
                    DeliveriesInfo,
                    AnnexesConditionsData,
                    POConditionsData,
                    Files,
                    Gallery,
                )
                return latest_date                
            elif model_name == 'KeyExchangeProjects':
                latest_date = get_latest_change(
                    id_value, 
                    Files,
                )
                return latest_date
            elif model_name == 'CardTestingProjects':
                latest_date = get_latest_change(
                    id_value, 
                    Files,
                    TestCardTransfer
                )
                return latest_date
            elif model_name == 'ProcessData':
                if process_step in ['1', '2', '3', '8', '10']:
                    latest_date = get_latest_process_change(
                        process_step,
                        id_value, 
                        Files
                    )
                    return latest_date                    
                elif process_step == '4':
                    latest_date = get_latest_process_change(
                        process_step,
                        id_value, 
                        AnnexesConditionsData,
                        Files
                    )
                    return latest_date
                elif process_step == '5':
                    latest_date = get_latest_process_change(
                        process_step,
                        id_value, 
                        VendorPrices,     
                        Files,
                        PaymentsInfo                    
                    )
                    return latest_date
                elif process_step == '6':
                    latest_date = get_latest_process_change(
                        process_step,
                        id_value, 
                        BankPrices, 
                        Files,
                        PaymentsInfo                    
                    )
                    return latest_date
                elif process_step == '7':
                    latest_date = get_latest_process_change(
                        process_step,
                        id_value, 
                        POConditionsData,
                        Files
                    )
                    return latest_date
                elif process_step == '9':
                    latest_date = get_latest_process_change(
                        process_step,
                        id_value, 
                        PaymentSystemApprovals,
                        Files
                    )
                    return latest_date
                elif process_step == '11':
                    latest_date = get_latest_process_change(
                        process_step,
                        id_value, 
                        ProductionData,
                        Files
                    )
                    return latest_date
                elif process_step == '12':
                    latest_date = get_latest_process_change(
                        process_step,
                        id_value, 
                        DeliveriesInfo,
                        Files
                    )
                    return latest_date
                elif process_step == '13':
                    latest_date = get_latest_process_change(
                        process_step,
                        id_value, 
                        DeliveriesInfo,
                        Files
                    )
                    return latest_date
                else:
                    return Response({'error': 'Некорректный process_step'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Не определена модель'}, status=status.HTTP_400_BAD_REQUEST) 

        try:
            id_value = request.GET.get('id', '')
            model_name = request.GET.get('model_name', '')
            process_step = request.GET.get('process_step', '')

            response_create_changelog = get_create_changelog(id_value, model_name, process_step)
            response_update_changelog = get_update_changelog(id_value, model_name, process_step)

            total_changelod_data = {'create': response_create_changelog, 'update': response_update_changelog}

            return Response(total_changelod_data, status=status.HTTP_200_OK)

        except:
            return Response({'error': 'Ошибка получения данных'}, status=status.HTTP_400_BAD_REQUEST)