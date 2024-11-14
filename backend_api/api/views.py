import os
from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.exceptions import NotFound
from django.db.models import Prefetch, Func, Sum, Q, F, Value, ExpressionWrapper, IntegerField, Count, CharField, FloatField, BooleanField, Case, When, Subquery, OuterRef, DateField, DateTimeField
from django.db.models.functions import Coalesce, Concat, Cast, Round, ExtractMonth
from django.db import transaction
from django.conf import settings
import time
from django.core.files.storage import default_storage
from datetime import datetime, date
from moviepy.editor import VideoFileClip
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from changelog.models import NewChangeLogsModel
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.db.models.signals import m2m_changed
import calendar
from django.utils import timezone



from .serializers import (
    BanksSerializer,
    VendorsSerializer,
    ChipsSerializer,
    ProjectLineSerializer,
    PaymentSystemsSerializer,
    ProductCategoriesSerializer,
    ChipColorsSerializer,
    MaterialTypesSerializer,
    MaterialColorsSerializer,
    MagstripeColorsSerializer,
    MagstripeTracksSerializer,
    AntennaSizesSerializer,
    EffectsSerializer,
    BankEmployeesSerializer,
    VendorEmployeesSerializer,
    PaymentSystemEmployeesSerializer,
    ProcessListSerializer,
    ProcessDataSerializer,
    CountriesSerializer,
    ProductTypesSerializer,
    BankPricesSerializer,
    VendorPricesSerializer,
    CurrenciesSerializer,
    GeneralProjectStatusesSerializer,
    EffectsMatchingSerializer,
    ProcessStatusesSerializer,
    FilesStatusesSerializer,
    VendorManufactureCountriesSerializer,
    FilesFormatsSerializer,
    FilesTypeNameSerializer,
    GallerySerializer,
    FilesSerializer,
    BanksBIDsSerializer,
    PaymentSystemApprovalsSerializer,
    KeyExchangeProjectsSerializer,
    KeyExchangeStatusesSerializer,
    CardTestingStatusesSerializer,
    CardTestingProjectsSerializer,
    TestCardTransferSerializer,
    TestCardTypesSerializer,
    TransferActionsSerializer,
    ProcessingCentersSerializer,
    PesroScriptVendorsSerializer,
    LaminationTypesSerializer,
    PaymentTypesSerializer,
    PaymentsInfoSerializer,
    DeliveriesInfoSerializer,
    MifareTypesSerializer,
    StartYearSerializer,
    ShortProjectLineSerializer,
    ProductionDataSerializer,
    CardTestingShortRelevantLineSerializer,
    AnnexesConditionsDataSerializer,
    POConditionsDataSerializer,
    MonthListSerializer,
    AppletTypesSerializer,
    KeyExchangeTableProjectsSerializer,
    CardTestingTableProjectsSerializer,
    FilesTableSerializer,
    PaymentsInfoTableSerializer,
    ProjectLineTableSerializer,
    DeliveriesInfoTableSerializer,
    ReportsNameSerializer,
    ReportSerializer
)

from backend_api.models import (
    ProjectLine,
    Banks,
    Vendors,
    Chips, 
    PaymentSystems, 
    ProductCategories, 
    ChipColors, 
    MaterialTypes, 
    MaterialColors, 
    MagstripeColors,
    MagstripeTracks,
    AntennaSizes,
    Effects,
    BankEmployees,
    VendorEmployees,
    PaymentSystemEmployees,
    ProcessList,
    ProcessData,
    Countries,
    ProductTypes,
    BankPrices,
    VendorPrices,
    Currencies,
    GeneralProjectStatuses,
    ProcessStatuses,
    FilesStatuses,
    EffectsMatching,
    VendorManufactureCountries,
    FilesFormats,
    FilesTypeName,
    Gallery,
    Files,
    BanksBIDs,
    PaymentSystemApprovals,
    KeyExchangeProjects,
    KeyExchangeStatuses,
    CardTestingProjects,
    CardTestingStatuses,
    TestCardTransfer,
    TestCardTypes,
    TransferActions,
    ProcessingCenters,
    PesroScriptVendors,
    LaminationTypes,
    PaymentTypes,
    PaymentsInfo,
    DeliveriesInfo,
    MifareTypes,
    StartYear,
    ProductionData,
    AnnexesConditionsData,
    POConditionsData,
    MonthList,
    AppletTypes,
    Reports
)

def format_with_thousands_separator(value, type):
    if value is None:
        return 'null'
    if type == 'float':
        formatted_value = '{:,.2f}'.format(value)
    else:
        formatted_value = '{:,.0f}'.format(value)
    return formatted_value.replace(',', ' ')

class FormatNumber(Func):
    function = 'FORMAT'
    template = '%(function)s(%(expressions)s, N2)'
    
def format_date(date_obj):
    try:
        if isinstance(date_obj, (datetime, date)):
            return date_obj.strftime('%d.%m.%Y')
        else:
            return date_obj
    except (ValueError, TypeError):
        return date_obj    

def format_month_year(date_obj):
    try:
        month = date_obj.month
        year = date_obj.year

        months = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]

        return f"{months[month - 1]} {year}"
    except (ValueError, TypeError):
        return date_obj
    
def format_month(date_obj):
    try:
        month = date_obj.month

        months = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]

        return f"{months[month - 1]}"
    except (ValueError, TypeError):
        return date_obj
       
def get_start_of_month(date_value: date) -> date:
    return date_value.replace(day=1)

def get_end_of_month(date_value: date) -> date:
    last_day = calendar.monthrange(date_value.year, date_value.month)[1]
    return date_value.replace(day=last_day)

class BaseFilterViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        queryset = self.queryset.all()

        if hasattr(self, 'filter_fields'):
            filters_dict = {}
            filters_except_dict = {}

            for field in self.filter_fields:
                param_value = self.request.query_params.get(field, None)
                if param_value is not None:
                    if param_value.startswith('!'):
                        value = param_value[1:]
                        filters_except_dict[field] = value
                    else:
                        filters_dict[field] = param_value

            if filters_dict:
                for field, value in filters_dict.items():
                    queryset = queryset.filter(**{field: value})   

            if filters_except_dict:
                for field, value in filters_except_dict.items():
                    queryset = queryset.exclude(**{field: value})          

        if hasattr(self, 'filter_include_fields'):
            filters_include_dict = {}
            filters_except_include_dict = {}

            for field in self.filter_include_fields:
                param_value = self.request.query_params.get(field, None)
                if param_value is not None:
                    if param_value.startswith('!'):
                        value = param_value[1:]
                        filters_except_include_dict[field] = value
                    else:
                        filters_include_dict[field] = param_value

            if filters_include_dict:
                for field, value in filters_include_dict.items():
                    items = value.split(',')
                    item_filters = Q()
                    for item in items:
                        item_filters |= Q(**{field + '__contains': item.strip()})
                    queryset = queryset.filter(item_filters)                   

            if filters_except_include_dict:
                for field, value in filters_except_include_dict.items():  
                    items = value.split(',')            
                    item_filters = Q()
                    for item in items:
                        item_filters |= ~Q(**{field + '__contains': item.strip()})
                    queryset = queryset.filter(item_filters)                   

        if hasattr(self, 'filters_many_to_many_dict'):
            filters_many_to_many_dict = {}
            for field in self.filters_many_to_many_dict:
                param_value = self.request.query_params.get(field, None)
                if param_value is not None:
                    filters_many_to_many_dict[field] = param_value

            if filters_many_to_many_dict:
                for field, value in filters_many_to_many_dict.items():
                    values = [int(v) for v in value.split(',') if v.isdigit()]
                    if values:
                        queryset = queryset.filter(**{f"{field}__in": values})
        
        if hasattr(self, 'filter_by_year'):
            filters_by_year = {}
            filters_except_by_year = {}

            for field in self.filter_by_year:
                param_value = self.request.query_params.get(field, None)
                if param_value is not None:
                    if param_value.startswith('!'):
                        value = param_value[1:]
                        try:
                            param_year = int(value)
                        except ValueError:
                            pass
                        else:
                            filters_except_by_year[field + '__year'] = param_year
                    else:
                        try:
                            param_year = int(param_value)
                        except ValueError:
                            pass
                        else:
                            filters_by_year[field + '__year'] = param_year

            if filters_by_year:
                for field, value in filters_by_year.items():
                    queryset = queryset.filter(**{field: value})  

            if filters_except_by_year:
                for field, value in filters_except_by_year.items():
                    queryset = queryset.exclude(**{field: value})   

        return queryset
    
    def perform_update(self, serializer):
        instance = serializer.save()
        for field in instance._meta.many_to_many:
            if hasattr(instance, field.name):
                m2m_changed.send(
                    sender=field.remote_field.through, 
                    instance=instance,
                    action='post_add',
                    request=self.request,
                    request_exist=True
                )

        post_save.send(sender=instance.__class__, instance=instance, request=self.request, request_exist=True)

    def perform_create(self, serializer):
        instance = serializer.save()
        post_save.send(sender=instance.__class__, instance=instance, request=self.request, request_exist=True)

class ProjectLineViewSet(BaseFilterViewSet):
    
    queryset = ProjectLine.objects.all()
    serializer_class = ProjectLineSerializer
    filter_fields = ['id', 'active', 'isProject', 'display_year']   

class ProjectLineTableViewSet(BaseFilterViewSet):
    
    queryset = ProjectLine.objects.all()
    serializer_class = ProjectLineTableSerializer
    filter_fields = ['id', 'active', 'isProject', 'display_year']

    def get_queryset(self):
        queryset = super().get_queryset()

        currency_abbreviations = dict(Currencies.objects.values_list('id', 'abbreviation'))

        ### Подготовка данных для поля 'prepaid_value_bank'
        if not queryset.exists():
            line_currency_totals_prepaid_value_bank = {}
        else:
            aggregated_data_prepaid_value_bank = PaymentsInfo.objects.filter(
                line_number__in=queryset.values_list('id', flat=True),
                company_type='bank',
                payment_type=1,
                deleted=False
            ).values('line_number', 'currency').annotate(
                total_payment_value=Sum('payment_value')
            ).values('line_number', 'currency', 'total_payment_value')

            line_currency_totals_prepaid_value_bank = {}
            for entry in aggregated_data_prepaid_value_bank:
                line_number = entry['line_number']
                currency_id = entry['currency']
                total_payment_value = format_with_thousands_separator(entry['total_payment_value'], 'float')
                currency_abbr = currency_abbreviations.get(currency_id, 'unknown')
                if line_number not in line_currency_totals_prepaid_value_bank:
                    line_currency_totals_prepaid_value_bank[line_number] = []
                line_currency_totals_prepaid_value_bank[line_number].append(
                    f"{total_payment_value} {currency_abbr}"
                )

        def format_prepaid_value_bank(line_number):
            if line_number not in line_currency_totals_prepaid_value_bank or not line_currency_totals_prepaid_value_bank[line_number]:
                return ''
            return ' / '.join(line_currency_totals_prepaid_value_bank[line_number])
        
        ### Подготовка данных для поля 'postpaid_value_bank'
        if not queryset.exists():
            line_currency_totals_postpaid_value_bank = {}
        else:
            aggregated_data_postpaid_value_bank = PaymentsInfo.objects.filter(
                line_number__in=queryset.values_list('id', flat=True),
                company_type='bank',
                payment_type=2,
                deleted=False
            ).values('line_number', 'currency').annotate(
                total_payment_value=Sum('payment_value')
            ).values('line_number', 'currency', 'total_payment_value')

            line_currency_totals_postpaid_value_bank = {}
            for entry in aggregated_data_postpaid_value_bank:
                line_number = entry['line_number']
                currency_id = entry['currency']
                total_payment_value = format_with_thousands_separator(entry['total_payment_value'], 'float')
                currency_abbr = currency_abbreviations.get(currency_id, 'unknown')
                if line_number not in line_currency_totals_postpaid_value_bank:
                    line_currency_totals_postpaid_value_bank[line_number] = []
                line_currency_totals_postpaid_value_bank[line_number].append(
                    f"{total_payment_value} {currency_abbr}"
                )

        def format_postpaid_value_bank(line_number):
            if line_number not in line_currency_totals_postpaid_value_bank or not line_currency_totals_postpaid_value_bank[line_number]:
                return ''
            return ' / '.join(line_currency_totals_postpaid_value_bank[line_number])

        ### Подготовка данных для поля 'prepaid_value_vendor'
        if not queryset.exists():
            line_currency_totals_prepaid_value_vendor = {}
        else:
            aggregated_data_prepaid_value_vendor = PaymentsInfo.objects.filter(
                line_number__in=queryset.values_list('id', flat=True),
                company_type='vendor',
                payment_type=1,
                deleted=False
            ).values('line_number', 'currency').annotate(
                total_payment_value=Sum('payment_value')
            ).values('line_number', 'currency', 'total_payment_value')

            line_currency_totals_prepaid_value_vendor = {}
            for entry in aggregated_data_prepaid_value_vendor:
                line_number = entry['line_number']
                currency_id = entry['currency']
                total_payment_value = format_with_thousands_separator(entry['total_payment_value'], 'float')
                currency_abbr = currency_abbreviations.get(currency_id, 'unknown')
                if line_number not in line_currency_totals_prepaid_value_vendor:
                    line_currency_totals_prepaid_value_vendor[line_number] = []
                line_currency_totals_prepaid_value_vendor[line_number].append(
                    f"{total_payment_value} {currency_abbr}"
                )

        def format_prepaid_value_vendor(line_number):
            if line_number not in line_currency_totals_prepaid_value_vendor or not line_currency_totals_prepaid_value_vendor[line_number]:
                return ''
            return ' / '.join(line_currency_totals_prepaid_value_vendor[line_number])
        
        ### Подготовка данных для поля 'postpaid_value_vendor'
        if not queryset.exists():
            line_currency_totals_postpaid_value_vendor = {}
        else:
            aggregated_data_postpaid_value_vendor = PaymentsInfo.objects.filter(
                line_number__in=queryset.values_list('id', flat=True),
                company_type='vendor',
                payment_type=2,
                deleted=False
            ).values('line_number', 'currency').annotate(
                total_payment_value=Sum('payment_value')
            ).values('line_number', 'currency', 'total_payment_value')

            line_currency_totals_postpaid_value_vendor = {}
            for entry in aggregated_data_postpaid_value_vendor:
                line_number = entry['line_number']
                currency_id = entry['currency']
                total_payment_value = format_with_thousands_separator(entry['total_payment_value'], 'float')
                currency_abbr = currency_abbreviations.get(currency_id, 'unknown')
                if line_number not in line_currency_totals_postpaid_value_vendor:
                    line_currency_totals_postpaid_value_vendor[line_number] = []
                line_currency_totals_postpaid_value_vendor[line_number].append(
                    f"{total_payment_value} {currency_abbr}"
                )

        def format_postpaid_value_vendor(line_number):
            if line_number not in line_currency_totals_postpaid_value_vendor or not line_currency_totals_postpaid_value_vendor[line_number]:
                return ''
            return ' / '.join(line_currency_totals_postpaid_value_vendor[line_number])

        ### Подготовка данных для поля 'paid_value_bank'
        aggregated_data_paid_value_bank = PaymentsInfo.objects.filter(
            line_number__in=queryset.values_list('id', flat=True),
            company_type='bank',
            deleted=False
        ).values('line_number', 'currency').annotate(
            total_payment_value=Sum('payment_value')
        ).values('line_number', 'currency', 'total_payment_value')

        line_currency_totals_paid_value_bank = {}
        for entry in aggregated_data_paid_value_bank:
            line_number = entry['line_number']
            currency_id = entry['currency']
            total_payment_value = format_with_thousands_separator(entry['total_payment_value'], 'float')
            currency_abbr = currency_abbreviations.get(currency_id, 'unknown')
            if line_number not in line_currency_totals_paid_value_bank:
                line_currency_totals_paid_value_bank[line_number] = []
            line_currency_totals_paid_value_bank[line_number].append(
                f"{total_payment_value} {currency_abbr}"
            )

        def format_paid_value_bank(line_number):
            if line_number not in line_currency_totals_paid_value_bank or not line_currency_totals_paid_value_bank[line_number]:
                return ''
            return ' / '.join(line_currency_totals_paid_value_bank[line_number])

        ### Подготовка данных для поля 'paid_value_vendor'
        aggregated_data_paid_value_vendor = PaymentsInfo.objects.filter(
            line_number__in=queryset.values_list('id', flat=True),
            company_type='vendor',
            deleted=False
        ).values('line_number', 'currency').annotate(
            total_payment_value=Sum('payment_value')
        ).values('line_number', 'currency', 'total_payment_value')

        line_currency_totals_paid_value_vendor = {}
        for entry in aggregated_data_paid_value_vendor:
            line_number = entry['line_number']
            currency_id = entry['currency']
            total_payment_value = format_with_thousands_separator(entry['total_payment_value'], 'float')
            currency_abbr = currency_abbreviations.get(currency_id, 'unknown')
            if line_number not in line_currency_totals_paid_value_vendor:
                line_currency_totals_paid_value_vendor[line_number] = []
            line_currency_totals_paid_value_vendor[line_number].append(
                f"{total_payment_value} {currency_abbr}"
            )

        def format_paid_value_vendor(line_number):
            if line_number not in line_currency_totals_paid_value_vendor or not line_currency_totals_paid_value_vendor[line_number]:
                return ''
            return ' / '.join(line_currency_totals_paid_value_vendor[line_number])

        ### Подсчет количества доставленных карт
        vendor_totals = DeliveriesInfo.objects.filter(
            company_type='vendor',
            deleted=False
        ).values('line_number').annotate(
            total_quantity=Sum('quantity')
        ).values('line_number', 'total_quantity')

        vendor_totals_dict = {item['line_number']: item['total_quantity'] for item in vendor_totals}

        bank_totals = DeliveriesInfo.objects.filter(
            company_type='bank',
            deleted=False
        ).values('line_number').annotate(
            total_quantity=Sum('quantity')
        ).values('line_number', 'total_quantity')

        bank_totals_dict = {item['line_number']: item['total_quantity'] for item in bank_totals}

        created_date = NewChangeLogsModel.objects.filter(
            model_name='ProjectLine',
            action='create'
        ).order_by('timestamp')

        created_date_list = list(created_date)

        # Аннотация и предзагрузка данных
        queryset = queryset.select_related(
            'bank', 
            'bank_employee',
            'general_line_status',
            'vendor',
            'vendor_employee',
            'vendor_manufacture_country',
            'product_type',
            'payment_system',
            'product_category',
            'chip',
            'applet',
            'chip_color',
            'mifare',
            'antenna_size',
            'magstripe_color',
            'magstripe_tracks',
            'material_type',
            'material_color',
            'lamination_face',
            'lamination_back',
        ).prefetch_related(
            'product_effects',
            Prefetch('paymentsystemapprovals_set'),
            Prefetch('deliveriesinfo_set'),
            Prefetch('annexesconditionsdata_set'),
            Prefetch('poconditionsdata_set'),
            Prefetch('bankprices_set'),
            Prefetch('vendorprices_set'),
            Prefetch('productiondata_set'),

        ).annotate(
            payment_system_name=Coalesce(F('payment_system__name'), Value('', output_field=CharField())),
            product_category_name=Coalesce(F('product_category__name'), Value('', output_field=CharField())),
            chip_name=Coalesce(F('chip__short_name'), Value('', output_field=CharField())),
            applet_name=Coalesce(F('applet__name'), Value('', output_field=CharField())),
            mifare_text=Case(
                When(mifare=True, then=Value("+ Mifare", output_field=CharField())),
                default=Value('', output_field=CharField())
            ),            
            product_full_name=Concat(
                Coalesce(F('payment_system__name'), Value('')),
                Case(
                    When(product_category__name__isnull=False, payment_system__name__isnull=False, then=Concat(Value(' '), F('product_category__name'))),
                    When(product_category__name__isnull=False, payment_system__name__isnull=True, then=F('product_category__name')),
                    default=Value(''),
                    output_field=CharField()
                ),
                Case(
                    When(product_name__isnull=False, product_category__name__isnull=False, then=Concat(Value(' '), F('product_name'))),
                    When(product_name__isnull=False, product_category__name__isnull=True, payment_system__name__isnull=False, then=Concat(Value(' '), F('product_name'))),
                    When(product_name__isnull=False, product_category__name__isnull=True, payment_system__name__isnull=True, then=F('product_name')),
                    default=Value(''),
                    output_field=CharField()
                )
            ),
            chip_full_name = Concat(
                Case(
                    When(chip__short_name__isnull=False, then=F('chip__short_name')),
                    default=Value(''),
                    output_field=CharField()
                ),
                Case(
                    When(applet__name__isnull=False, chip__short_name__isnull=False, then=Concat(Value(' '), F('applet__name'))),
                    When(applet__name__isnull=False, chip__short_name__isnull=True, then=F('applet__name')),
                    default=Value(''),
                    output_field=CharField()
                ),
                Case(
                    When(mifare_text__isnull=False, applet__name__isnull=False, then=Concat(Value(' '), F('mifare_text'))),
                    When(mifare_text__isnull=False, applet__name__isnull=True, chip__short_name__isnull=False, then=Concat(Value(' '), F('mifare_text'))),
                    When(mifare_text__isnull=False, applet__name__isnull=True, chip__short_name__isnull=True, then=F('mifare_text')),
                    default=Value(''),
                    output_field=CharField()
                )
            ),
            product_effects_qty=Count('product_effects'),
            lead_time_min_bank=Coalesce(F('annexesconditionsdata__lead_time_min'), Value(None, output_field=IntegerField())),
            lead_time_max_bank=Coalesce(F('annexesconditionsdata__lead_time_max'), Value(None, output_field=IntegerField())),
            lead_time_min_str_bank=Cast(F('lead_time_min_bank'), CharField()),
            lead_time_max_str_bank=Cast(F('lead_time_max_bank'), CharField()),
            lead_time_bank=Case(
                When(lead_time_min_bank__isnull=False, lead_time_max_bank__isnull=False, then=Concat(
                    F('lead_time_min_bank'),
                    Value('-'),
                    F('lead_time_max_bank'),
                    output_field=CharField()
                )),
                When(lead_time_min_bank__isnull=False, lead_time_max_bank__isnull=True, then=F('lead_time_min_str_bank')),
                When(lead_time_min_bank__isnull=True, lead_time_max_bank__isnull=False, then=F('lead_time_max_str_bank')),
                default=Value(None, output_field=CharField())
            ),
            deviation_min_bank=Coalesce(F('annexesconditionsdata__deviation_min'), Value(None, output_field=IntegerField())),
            deviation_max_bank=Coalesce(F('annexesconditionsdata__deviation_max'), Value(None, output_field=IntegerField())),
            deviation_bank=Case(
                When(deviation_min_bank__isnull=False, deviation_max_bank__isnull=False, then=Concat(
                    Case(
                        When(deviation_min_bank__lt=0, then=Concat(
                            F('deviation_min_bank'),
                            Value('%'),
                            output_field=CharField()
                        )),
                        When(deviation_min_bank__gte=0, then=Concat(
                            Value('+'),
                            F('deviation_min_bank'),
                            Value('%'),
                            output_field=CharField()
                        )),
                        default=Value('', output_field=CharField())
                    ),
                    Value('/'),
                    Case(
                        When(deviation_max_bank__lt=0, then=Concat(
                            F('deviation_max_bank'),
                            Value('%'),
                            output_field=CharField()
                        )),
                        When(deviation_max_bank__gte=0, then=Concat(
                            Value('+'),
                            F('deviation_max_bank'),
                            Value('%'),
                            output_field=CharField()
                        )),
                        default=Value('', output_field=CharField())
                    ),
                    output_field=CharField()
                )),
                When(deviation_min_bank__isnull=False, deviation_max_bank__isnull=True, then=Case(
                    When(deviation_min_bank__lt=0, then=Concat(
                        F('deviation_min_bank'),
                        Value('%'),
                        output_field=CharField()
                    )),
                    When(deviation_min_bank__gte=0, then=Concat(
                        Value('+'),
                        F('deviation_min_bank'),
                        Value('%'),
                        output_field=CharField()
                    )),
                    default=Value('', output_field=CharField())
                )),
                When(deviation_min_bank__isnull=True, deviation_max_bank__isnull=False, then=Case(
                    When(deviation_max_bank__lt=0, then=Concat(
                        F('deviation_max_bank'),
                        Value('%'),
                        output_field=CharField()
                    )),
                    When(deviation_max_bank__gte=0, then=Concat(
                        Value('+'),
                        F('deviation_max_bank'),
                        Value('%'),
                        output_field=CharField()
                    )),
                    default=Value('', output_field=CharField())
                )),
                default=Value(None, output_field=CharField())
            ),
            lead_time_st_vendor=Coalesce(F('poconditionsdata__lead_time'), Value(None, output_field=IntegerField())),
            lead_time_vendor=Cast(F('lead_time_st_vendor'), CharField()),
            deviation_min_vendor=Coalesce(F('poconditionsdata__deviation_min'), Value(None, output_field=IntegerField())),
            deviation_max_vendor=Coalesce(F('poconditionsdata__deviation_max'), Value(None, output_field=IntegerField())),
            deviation_vendor=Case(
                When(deviation_min_vendor__isnull=False, deviation_max_vendor__isnull=False, then=Concat(
                    Case(
                        When(deviation_min_vendor__lt=0, then=Concat(
                            F('deviation_min_vendor'),
                            Value('%'),
                            output_field=CharField()
                        )),
                        When(deviation_min_vendor__gte=0, then=Concat(
                            Value('+'),
                            F('deviation_min_vendor'),
                            Value('%'),
                            output_field=CharField()
                        )),
                        default=Value('', output_field=CharField())
                    ),
                    Value('/'),
                    Case(
                        When(deviation_max_vendor__lt=0, then=Concat(
                            F('deviation_max_vendor'),
                            Value('%'),
                            output_field=CharField()
                        )),
                        When(deviation_max_vendor__gte=0, then=Concat(
                            Value('+'),
                            F('deviation_max_vendor'),
                            Value('%'),
                            output_field=CharField()
                        )),
                        default=Value('', output_field=CharField())
                    ),
                    output_field=CharField()
                )),
                When(deviation_min_vendor__isnull=False, deviation_max_vendor__isnull=True, then=Case(
                    When(deviation_min_vendor__lt=0, then=Concat(
                        F('deviation_min_vendor'),
                        Value('%'),
                        output_field=CharField()
                    )),
                    When(deviation_min_vendor__gte=0, then=Concat(
                        Value('+'),
                        F('deviation_min_vendor'),
                        Value('%'),
                        output_field=CharField()
                    )),
                    default=Value('', output_field=CharField())
                )),
                When(deviation_min_vendor__isnull=True, deviation_max_vendor__isnull=False, then=Case(
                    When(deviation_max_vendor__lt=0, then=Concat(
                        F('deviation_max_vendor'),
                        Value('%'),
                        output_field=CharField()
                    )),
                    When(deviation_max_vendor__gte=0, then=Concat(
                        Value('+'),
                        F('deviation_max_vendor'),
                        Value('%'),
                        output_field=CharField()
                    )),
                    default=Value('', output_field=CharField())
                )),
                default=Value(None, output_field=CharField())
            ),
            unit_price_int_bank=Coalesce(F('bankprices__unit_price'), Value(None, output_field=FloatField())),
            main_currency_bank=Coalesce(F('bankprices__main_currency__abbreviation'), Value(None, output_field=CharField())),
            unit_price_bank=Case(
                When(unit_price_int_bank__isnull=False, then=ExpressionWrapper(
                     Round(Round(F('unit_price_int_bank'), 3) + Value(0.0005), 2),
                    output_field=FloatField()
                )),             
                default=Value(None, output_field=FloatField())
            ),
            payment_plan_bank=Case(
                When(unit_price_int_bank__isnull=False, product_qty_from_bank__isnull=False, then=ExpressionWrapper(
                    Round(Round(F('unit_price_bank') * F('product_qty_from_bank'), 3) + Value(0.0005), 2),
                    output_field=FloatField()
                )),              
                default=Value(None, output_field=FloatField())
            ),
            exchange_rates_bank_int=Coalesce(F('bankprices__exchange_rates'), Value(None, output_field=FloatField())),
            additional_currency_bank=Coalesce(F('bankprices__additional_currency__abbreviation'), Value(None, output_field=CharField())),
            unit_price_bank_additional=Case(
                When(unit_price_int_bank__isnull=False, additional_currency_bank__isnull=False, exchange_rates_bank_int__isnull=False, then=ExpressionWrapper(
                    Round(Round(F('unit_price_bank') * F('exchange_rates_bank_int'), 3) + Value(0.0005), 2),
                    output_field=FloatField()
                )),               
                default=Value(None, output_field=FloatField())
            ),
            additional_payment_plan_bank=Case(
                When(payment_plan_bank__isnull=False, exchange_rates_bank_int__isnull=False, then=ExpressionWrapper(
                        Round(Round(F('product_qty_from_bank') * F('unit_price_bank_additional'), 3) + Value(0.0005), 2),
                        output_field=FloatField()
                    )
                ),
                default=Value(None, output_field=FloatField())
            ),
            prepaid_percent_int_bank=Coalesce(F('bankprices__prepaid_percent'), Value(None, output_field=IntegerField())),
            prepaid_percent_bank=Case(
                When(prepaid_percent_int_bank__isnull=False, then=Concat(
                    Cast('prepaid_percent_int_bank', CharField()),
                    Value('%')
                )),
                default=Value(None),
                output_field=CharField()
            ),
            postpaid_percent_int_bank=Case(
                When(prepaid_percent_int_bank__isnull=False, then=Cast(100 - F('prepaid_percent_int_bank'), IntegerField())),
                default=Value(None),
                output_field=IntegerField()
            ),
            postpaid_percent_bank=Case(
                When(postpaid_percent_int_bank__isnull=False, then=Concat(
                    F('postpaid_percent_int_bank'),
                    Value('%')
                )),
                default=Value(None),
                output_field=CharField()
            ),
            unit_price_int_vendor=Coalesce(F('vendorprices__unit_price'), Value(None, output_field=FloatField())),
            main_currency_vendor=Coalesce(F('vendorprices__main_currency__abbreviation'), Value(None, output_field=CharField())),
            unit_price_vendor=Case(
                When(unit_price_int_vendor__isnull=False, then=ExpressionWrapper(
                    Round(Round(F('unit_price_int_vendor'), 3) + Value(0.0005), 2),
                    output_field=FloatField()
                )), 
            ),
            payment_plan_vendor=Case(
                When(unit_price_int_vendor__isnull=False, product_qty_to_vendor__isnull=False, then=ExpressionWrapper(
                    Round(Round(F('unit_price_vendor') * F('product_qty_to_vendor'), 3) + Value(0.0005), 2),
                    output_field=FloatField()
                )),              
                default=Value(None, output_field=FloatField())
            ),
            exchange_rates_vendor_int=Coalesce(F('vendorprices__exchange_rates'), Value(None, output_field=FloatField())),
            additional_currency_vendor=Coalesce(F('vendorprices__additional_currency__abbreviation'), Value(None, output_field=CharField())),
            unit_price_vendor_additional=Case(
                When(unit_price_int_vendor__isnull=False, additional_currency_vendor__isnull=False, exchange_rates_vendor_int__isnull=False, then=ExpressionWrapper(
                    Round(Round(F('unit_price_vendor') * F('exchange_rates_vendor_int'), 3) + Value(0.0005), 2),
                    output_field=FloatField()
                )),               
                default=Value(None, output_field=FloatField())
            ),
            additional_payment_plan_vendor=Case(
                When(payment_plan_vendor__isnull=False, exchange_rates_vendor_int__isnull=False, then=ExpressionWrapper(
                        Round(Round(F('product_qty_to_vendor') * F('unit_price_vendor_additional'), 3) + Value(0.0005), 2),
                        output_field=FloatField()
                    )
                ),
                default=Value(None, output_field=FloatField())
            ),
            prepaid_percent_int_vendor=Coalesce(F('vendorprices__prepaid_percent'), Value(None, output_field=IntegerField())),
            prepaid_percent_vendor=Case(
                When(prepaid_percent_int_vendor__isnull=False, then=Concat(
                    Cast('prepaid_percent_int_vendor', CharField()),
                    Value('%')
                )),
                default=Value(None),
                output_field=CharField()
            ),
            postpaid_percent_int_vendor=Case(
                When(prepaid_percent_int_vendor__isnull=False, then=Cast(100 - F('prepaid_percent_int_vendor'), IntegerField())),
                default=Value(None),
                output_field=IntegerField()
            ),
            postpaid_percent_vendor=Case(
                When(postpaid_percent_int_vendor__isnull=False, then=Concat(
                    F('postpaid_percent_int_vendor'),
                    Value('%')
                )),
                default=Value(None),
                output_field=CharField()
            ),
            prepaid_value_bank = Case(
                When(id__in=line_currency_totals_prepaid_value_bank.keys(), then=Value(
                    ' / '.join(format_prepaid_value_bank(line_number) for line_number in queryset.values_list('id', flat=True))
                )),
                default=Value(None),
                output_field=CharField()
            ) if line_currency_totals_prepaid_value_bank else Value(None, output_field=CharField()),
            postpaid_value_bank = Case(
                When(id__in=line_currency_totals_postpaid_value_bank.keys(), then=Value(
                    ' / '.join(format_postpaid_value_bank(line_number) for line_number in queryset.values_list('id', flat=True))
                )),
                default=Value(None),
                output_field=CharField()
            ) if line_currency_totals_postpaid_value_bank else Value(None, output_field=CharField()),
            prepaid_value_vendor = Case(
                When(id__in=line_currency_totals_prepaid_value_vendor.keys(), then=Value(
                    ' / '.join(format_prepaid_value_vendor(line_number) for line_number in queryset.values_list('id', flat=True))
                )),
                default=Value(None),
                output_field=CharField()
            ) if line_currency_totals_prepaid_value_vendor else Value(None, output_field=CharField()),
            postpaid_value_vendor = Case(
                When(id__in=line_currency_totals_postpaid_value_vendor.keys(), then=Value(
                    ' / '.join(format_postpaid_value_vendor(line_number) for line_number in queryset.values_list('id', flat=True))
                )),
                default=Value(None),
                output_field=CharField()
            ) if line_currency_totals_postpaid_value_vendor else Value(None, output_field=CharField()),
            payment_fact_bank = Case(
                When(id__in=line_currency_totals_paid_value_bank.keys(), then=Value(
                    ' / '.join(format_paid_value_bank(line_number) for line_number in queryset.values_list('id', flat=True))
                )),
                default=Value(None),
                output_field=CharField()
            ) if line_currency_totals_paid_value_bank else Value(None, output_field=CharField()),
            payment_fact_vendor = Case(
                When(id__in=line_currency_totals_paid_value_vendor.keys(), then=Value(
                    ' / '.join(format_paid_value_vendor(line_number) for line_number in queryset.values_list('id', flat=True))
                )),
                default=Value(None),
                output_field=CharField()
            ) if line_currency_totals_paid_value_vendor else Value(None, output_field=CharField()),
            bid = Coalesce(F('paymentsystemapprovals__bid__number'), Value(None, output_field=IntegerField())),
            bin = Coalesce(F('paymentsystemapprovals__bin'), Value(None, output_field=CharField())),
            range_low = Coalesce(F('paymentsystemapprovals__range_low'), Value(None, output_field=CharField())),
            range_high = Coalesce(F('paymentsystemapprovals__range_high'), Value(None, output_field=CharField())),
            program_name = Coalesce(F('paymentsystemapprovals__program_name'), Value(None, output_field=CharField())),
            full_name_in_ps = Coalesce(F('paymentsystemapprovals__full_name_in_ps'), Value(None, output_field=CharField())),
            is_requested = Coalesce(F('paymentsystemapprovals__is_requested'), Value(None, output_field=BooleanField())),
            requested_date = Coalesce(F('paymentsystemapprovals__requested_date'), Value(None, output_field=DateField())),
            received_date = Coalesce(F('paymentsystemapprovals__received_date'), Value(None, output_field=DateField())),        
            payment_system_data=Case(
                When(
                    bid__isnull=False,
                    bin__isnull=False,
                    range_low__isnull=False,
                    range_high__isnull=False,
                    program_name__isnull=False,
                    full_name_in_ps__isnull=False,
                    then=Concat(
                        Value('Получено - '),
                        F('received_date')
                    )
                ),
                When(
                    bid__isnull=True,
                    bin__isnull=True,
                    range_low__isnull=True,
                    range_high__isnull=True,
                    program_name__isnull=True,
                    full_name_in_ps__isnull=True,
                    is_requested__isnull=False,
                    then=Concat(
                        Value('Запрошено - '),
                        F('requested_date')
                    )
                ),
                default=Value(None),
                output_field=CharField()
            ),
            approval_date = Coalesce(F('paymentsystemapprovals__approval_date'), Value(None, output_field=DateField())),
            posted_date = Coalesce(F('paymentsystemapprovals__posted_date'), Value(None, output_field=DateField())),
            month_plan = Coalesce(F('productiondata__month_plan'), Value(None, output_field=DateField())),
            date_plan = Coalesce(F('productiondata__date_plan'), Value(None, output_field=DateField())),
            date_client = Coalesce(F('productiondata__date_client'), Value(None, output_field=DateField())),
            date_fact = Coalesce(F('productiondata__date_fact'), Value(None, output_field=DateField())),  
        )

        all_steps = list(ProcessList.objects.values_list('id', flat=True))

        process_data = ProcessData.objects.filter(
            line_number__in=queryset.values_list('pk', flat=True),
            process_step__position_number__in=all_steps
        ).values('line_number', 'process_step__position_number', 'step_status__name_rus', 'step_comment')

        process_data_dict = {}
        for data in process_data:
            key = (data['line_number'], data['process_step__position_number'])
            process_data_dict[key] = {
                'status': data['step_status__name_rus'],
                'comment': data['step_comment']
            }

        ### Подготовка данных перед выгрузкой
        for obj in queryset:
            if obj.product_qty_from_bank is not None:
                formatted_value = format_with_thousands_separator(obj.product_qty_from_bank, 'int')
                obj.product_qty_from_bank = f"{formatted_value}"
            else:
                obj.product_qty_from_bank = ''   

            if obj.product_qty_to_vendor is not None:
                formatted_value = format_with_thousands_separator(obj.product_qty_to_vendor, 'int')
                obj.product_qty_to_vendor = f"{formatted_value}"
            else:
                obj.product_qty_to_vendor = ''   

            if obj.additional_payment_plan_bank is not None:
                formatted_value = format_with_thousands_separator(obj.additional_payment_plan_bank, 'float')
                obj.additional_payment_plan_bank = f"{formatted_value} {obj.additional_currency_bank or 'UNKNOWN'}"
            else:
                obj.additional_payment_plan_bank = ''

            if obj.additional_payment_plan_vendor is not None:
                formatted_value = format_with_thousands_separator(obj.additional_payment_plan_vendor, 'float')
                obj.additional_payment_plan_vendor = f"{formatted_value} {obj.additional_currency_vendor or 'UNKNOWN'}"
            else:
                obj.additional_payment_plan_vendor = ''

            if obj.unit_price_bank is not None:
                formatted_value = format_with_thousands_separator(obj.unit_price_bank, 'float')
                obj.unit_price_bank = f"{formatted_value} {obj.main_currency_bank or 'UNKNOWN'}"
            else:
                obj.unit_price_bank = ''      

            if obj.unit_price_vendor is not None:
                formatted_value = format_with_thousands_separator(obj.unit_price_vendor, 'float')
                obj.unit_price_vendor = f"{formatted_value} {obj.main_currency_vendor or 'UNKNOWN'}"
            else:
                obj.unit_price_vendor = ''    

            if obj.payment_plan_bank is not None:
                formatted_value = format_with_thousands_separator(obj.payment_plan_bank, 'float')
                obj.payment_plan_bank = f"{formatted_value} {obj.main_currency_bank or 'UNKNOWN'}"
            else:
                obj.payment_plan_bank = ''   
            
            if obj.payment_plan_vendor is not None:
                formatted_value = format_with_thousands_separator(obj.payment_plan_vendor, 'float')
                obj.payment_plan_vendor = f"{formatted_value} {obj.main_currency_vendor or 'UNKNOWN'}"
            else:
                obj.payment_plan_vendor = '' 
            
            if obj.exchange_rates_bank_int is not None:
                formatted_value = format_with_thousands_separator(obj.exchange_rates_bank_int, 'float')
                obj.exchange_rates_bank = f"{formatted_value}"
            else:
                obj.exchange_rates_bank = ''          

            if obj.exchange_rates_vendor_int is not None:
                formatted_value = format_with_thousands_separator(obj.exchange_rates_vendor_int, 'float')
                obj.exchange_rates_vendor = f"{formatted_value}"
            else:
                obj.exchange_rates_vendor = ''   

            if obj.unit_price_bank_additional is not None:
                formatted_value = format_with_thousands_separator(obj.unit_price_bank_additional, 'float')
                obj.unit_price_bank_additional = f"{formatted_value} {obj.additional_currency_bank or 'UNKNOWN'}"
            else:
                obj.unit_price_bank_additional = ''          

            if obj.unit_price_vendor_additional is not None:
                formatted_value = format_with_thousands_separator(obj.unit_price_vendor_additional, 'float')
                obj.unit_price_vendor_additional = f"{formatted_value} {obj.additional_currency_vendor or 'UNKNOWN'}"
            else:
                obj.unit_price_vendor_additional = ''  

            if obj.payment_system_data and 'Получено' in obj.payment_system_data:
                if obj.received_date:
                    received_date_str = obj.received_date.strftime('%Y-%m-%d')
                    obj.payment_system_data = obj.payment_system_data.replace(
                        received_date_str, format_date(obj.received_date)
                    )
                else:
                    obj.payment_system_data = ''
            elif obj.payment_system_data and 'Запрошено' in obj.payment_system_data:
                if obj.requested_date:
                    requested_date_str = obj.requested_date.strftime('%Y-%m-%d')
                    obj.payment_system_data = obj.payment_system_data.replace(
                        requested_date_str, format_date(obj.requested_date)
                    )
                else: 
                    obj.payment_system_data = ''
            else:
                obj.payment_system_data = ''

            if obj.approval_date:
                obj.approval_date = f'Согласовано - {format_date(obj.approval_date)}' 
            elif obj.posted_date:
                obj.approval_date = f'Отправлено - {format_date(obj.posted_date)}'

            if obj.month_plan:
                obj.month_plan = format_month_year(obj.month_plan)

            if obj.date_plan:
                obj.date_plan = format_date(obj.date_plan)

            if obj.date_client:
                obj.date_client = format_date(obj.date_client)

            if obj.date_fact:
                obj.date_fact = format_date(obj.date_fact)

            obj.prepaid_value_bank = format_prepaid_value_bank(obj.id)
            obj.postpaid_value_bank = format_postpaid_value_bank(obj.id)
            obj.prepaid_value_vendor = format_prepaid_value_vendor(obj.id)
            obj.postpaid_value_vendor = format_postpaid_value_vendor(obj.id)
            obj.payment_fact_bank = format_paid_value_bank(obj.id)
            obj.payment_fact_vendor = format_paid_value_vendor(obj.id)

            fact_qty_vendor = vendor_totals_dict.get(obj.id, None)
            if fact_qty_vendor is not None:
                formatted_value = format_with_thousands_separator(fact_qty_vendor, 'int')
                obj.fact_qty_vendor = f"{formatted_value}"
            else:
                obj.fact_qty_vendor = ''   

            fact_qty_bank = bank_totals_dict.get(obj.id, None)
            if fact_qty_bank is not None:
                formatted_value = format_with_thousands_separator(fact_qty_bank, 'int')
                obj.fact_qty_bank = f"{formatted_value}"
            else:
                obj.fact_qty_bank = ''             

            created_date_obj = next((entry for entry in created_date_list if entry.row_number == obj.id), None)
            
            if created_date_obj:
                obj.created_date = format_date(created_date_obj.timestamp)
            else:
                obj.created_date = ''

            for step in all_steps:
                key = (obj.pk, step)
                if key in process_data_dict:
                    obj.__dict__[f'process_step_status_{step}'] = process_data_dict[key]['status']
                    obj.__dict__[f'process_step_comment_{step}'] = process_data_dict[key]['comment']
                else:
                    obj.__dict__[f'process_step_status_{step}'] = 'Не начато'
                    obj.__dict__[f'process_step_comment_{step}'] = None

        return queryset
        
class BanksSet(BaseFilterViewSet):

    queryset = Banks.objects.all()
    serializer_class = BanksSerializer
    filter_fields = ['id', 'active', 'country', 'name_rus']  
    
class VendorsSet(BaseFilterViewSet):
    
    queryset = Vendors.objects.all()
    serializer_class = VendorsSerializer
    filter_fields = ['id'] 
    
class CountriesSet(BaseFilterViewSet):
    
    queryset = Countries.objects.all()
    serializer_class = CountriesSerializer
    filter_fields = ['id']

class ChipsSet(BaseFilterViewSet):
    
    queryset = Chips.objects.all()
    serializer_class = ChipsSerializer
    filter_fields = ['id', 'vendor', 'payment_system']

class PaymentSystemsSet(BaseFilterViewSet):
    
    queryset = PaymentSystems.objects.all()
    serializer_class = PaymentSystemsSerializer
    filter_fields = ['id']  

class ProductCategoriesSet(BaseFilterViewSet):
    
    queryset = ProductCategories.objects.all()
    serializer_class = ProductCategoriesSerializer
    filter_fields = ['id', 'payment_system']  
    
class ChipColorsSet(BaseFilterViewSet):
    
    queryset = ChipColors.objects.all()
    serializer_class = ChipColorsSerializer
    filter_fields = ['id', 'chip']
    
class MaterialTypesSet(BaseFilterViewSet):
    
    queryset = MaterialTypes.objects.all()
    serializer_class = MaterialTypesSerializer
    filter_fields = ['id', 'product_type']
    
class ProductTypesSet(BaseFilterViewSet):
    
    queryset = ProductTypes.objects.all()
    serializer_class = ProductTypesSerializer
    filter_fields = ['id', 'vendor']
    
class MaterialColorsSet(BaseFilterViewSet):
    
    queryset = MaterialColors.objects.all()
    serializer_class = MaterialColorsSerializer
    filter_fields = ['id', 'material_type']

class MagstripeColorsSet(BaseFilterViewSet):
    
    queryset = MagstripeColors.objects.all()
    serializer_class = MagstripeColorsSerializer
    filter_fields = ['id', 'vendor', 'magstripe_tracks']
    
class MagstripeTracksSet(BaseFilterViewSet):
    
    queryset = MagstripeTracks.objects.all()
    serializer_class = MagstripeTracksSerializer
    filter_fields = ['id']
    
class AntennaSizesSet(BaseFilterViewSet):
    
    queryset = AntennaSizes.objects.all()
    serializer_class = AntennaSizesSerializer
    filter_fields = ['id', 'vendor']

class EffectsSet(BaseFilterViewSet):
    
    queryset = Effects.objects.all()
    serializer_class = EffectsSerializer
    filter_fields = ['id', 'product_type']
    
class EffectsMatchingSet(BaseFilterViewSet):
    
    queryset = EffectsMatching.objects.all()
    serializer_class = EffectsMatchingSerializer 
    filter_fields = ['id', 'effect']   

class BankEmployeesSet(BaseFilterViewSet):
    
    queryset = BankEmployees.objects.all()
    serializer_class = BankEmployeesSerializer
    filter_fields = ['id', 'bank']

class VendorEmployeesSet(BaseFilterViewSet):
    
    queryset = VendorEmployees.objects.all()
    serializer_class = VendorEmployeesSerializer
    filter_fields = ['id', 'vendor']

class VendorManufactureCountriesSet(BaseFilterViewSet):
    
    queryset = VendorManufactureCountries.objects.all()
    serializer_class = VendorManufactureCountriesSerializer
    filter_fields = ['id', 'vendor']

class PaymentSystemEmployeesSet(BaseFilterViewSet):
    
    queryset = PaymentSystemEmployees.objects.all()
    serializer_class = PaymentSystemEmployeesSerializer
    filter_fields = ['id']
        
class ProcessListSet(viewsets.ModelViewSet):
    
    queryset = ProcessList.objects.all()
    serializer_class = ProcessListSerializer
    
class ProcessDataSet(BaseFilterViewSet):
    
    queryset = ProcessData.objects.all()
    serializer_class = ProcessDataSerializer
    filter_fields = ['id', 'line_number', 'process_step']
    
class CurrenciesSet(viewsets.ModelViewSet):
    
    queryset = Currencies.objects.all()
    serializer_class = CurrenciesSerializer   
    
class BankPricesSet(BaseFilterViewSet):

    queryset = BankPrices.objects.all()
    serializer_class = BankPricesSerializer
    filter_fields = ['id', 'line_number']

class VendorPricesSet(BaseFilterViewSet):

    queryset = VendorPrices.objects.all()
    serializer_class = VendorPricesSerializer
    filter_fields = ['id', 'line_number']     
    
class GeneralProjectStatusesSet(viewsets.ModelViewSet):
    
    queryset = GeneralProjectStatuses.objects.all()
    serializer_class = GeneralProjectStatusesSerializer
    
class ProcessStatusesSet(viewsets.ModelViewSet):
    
    queryset = ProcessStatuses.objects.all()
    serializer_class = ProcessStatusesSerializer
   
class FilesStatusesSet(viewsets.ModelViewSet):
    
    queryset = FilesStatuses.objects.all()
    serializer_class = FilesStatusesSerializer

class FilesFormatsSet(BaseFilterViewSet):
    
    queryset = FilesFormats.objects.all()
    serializer_class = FilesFormatsSerializer 

class FilesTypeNameSet(viewsets.ModelViewSet):
    
    queryset = FilesTypeName.objects.all()
    serializer_class = FilesTypeNameSerializer 

class GallerySet(BaseFilterViewSet):
    
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer  
    filter_include_fields = ['number'] 
    filter_fields = ['model_type', 'process_step', 'active', 'deleted']
 
    def create(self, request, *args, **kwargs):
        action_type = request.data.get('action')

        if action_type == 'add-new-file':
            return self.add_new_file(request)
        elif action_type == 'change-name':
            return self.change_name(request)
        elif action_type == 'change-folder':
            return self.change_folder(request)
        elif action_type == 'delete-file':
            return self.delete_file(request)
        elif action_type == 'change-comment':
            return self.change_comment(request)
        elif action_type == 'to-archive':
            return self.to_archive(request)
        elif action_type == 'from-archive':
            return self.from_archive(request)
        # elif action_type == 'open-location':
        #     return self.open_location(request)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        
    def add_new_file(self, request):
        data = request.data
        file = request.FILES.get('file')
        model_type = data.get('model_type')
        number = data.get('number')
        folder_name = data.get('folder_name')
        name = data.get('name')
        other = data.get('other')

        if not all([file, model_type, folder_name, name]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        file_name, extension = os.path.splitext(file.name)
        full_file_name = f"{name}{extension}"
        folder_list = folder_name.split('/')
        cleaned_folder_list = [folder.rstrip('.') for folder in folder_list]
        cleaned_folder_name = '/'.join(cleaned_folder_list)
        file_path = os.path.join(settings.MEDIA_ROOT, *cleaned_folder_list, full_file_name)
        file_path_name = "/".join(cleaned_folder_list + [full_file_name])
        
        if os.path.exists(file_path):
            return Response({'file-exist': 'File already exists'}, status=status.HTTP_400_BAD_REQUEST)

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        try:
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            file_format = FilesFormats.objects.get(file_extension=extension.replace(".", "").lower())
            file_type = file_format.name.name
        except FilesFormats.DoesNotExist:
            file_type = "unknown"

        try:
            file_mod_time = os.path.getmtime(file_path)
            file_mod_datetime = datetime.fromtimestamp(file_mod_time)
            file_mod_datetime = timezone.make_aware(file_mod_datetime, timezone.get_current_timezone())
        except Exception as e:
            file_mod_datetime = timezone.now()

        file_record = Gallery(
            file=file_path_name,
            model_type=model_type,
            number=number,
            folder_name=cleaned_folder_name,
            other=other,
            name=name,
            file_extension=extension.replace(".", "").lower(),
            file_type=file_type,
            active=True,
            created_date=file_mod_datetime
        )

        valid_formats = FilesFormats.objects.filter(available_for_video_gallery=True).values_list('file_extension', flat=True)
        if extension.replace(".", "").lower() in valid_formats:
            try:
                video_clip = VideoFileClip(file_path)
                preview_filename = f"{name}_preview.jpg"
                preview_path = os.path.join(directory, preview_filename)
                video_clip.save_frame(preview_path, t=1)
                video_clip.close()

                relative_preview_path = "/".join(folder_list + [preview_filename])
                file_record.preview_image = relative_preview_path
                file_record.save()
                post_save.send(sender=file_record.__class__, instance=file_record, request=request, request_exist=True)

            except Exception as e:
                return Response({'error': f"Failed to create video preview: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            file_record.save()
            post_save.send(sender=file_record.__class__, instance=file_record, request=request, request_exist=True)

        return Response(GallerySerializer(file_record).data, status=status.HTTP_201_CREATED)

    def change_name(self, request):
        file = request.data.get('file')
        new_name = request.data.get('name')
        if not new_name:
            return Response({'error': 'Name not provided'}, status=status.HTTP_400_BAD_REQUEST)

        old_file_path = os.path.join(settings.MEDIA_ROOT, file)
        new_file_path = os.path.join(os.path.dirname(old_file_path), f"{new_name}.{file.split('.')[-1]}")

        if old_file_path.replace('/','_').replace('\\', '_').lower() != new_file_path.replace('/','_').replace('\\', '_').lower():
            if default_storage.exists(new_file_path):
                return Response({'error': 'File with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        os.rename(old_file_path, new_file_path)

        extension = file.rsplit('.')[-1]
        file_without_name = "/".join(file.rsplit('/', 1)[:-1])
        new_file_name = f"{file_without_name}/{new_name}.{extension}"

        files_to_update = Gallery.objects.filter(file=file)
        for file_instance in files_to_update:
            file_instance.name = new_name
            file_instance.file = new_file_name
            file_instance.save()

            post_save.send(sender=file_instance.__class__, instance=file_instance, request=request, request_exist=True)

        return Response({'message': 'Name updated successfully'}, status=status.HTTP_200_OK)

    def change_comment(self, request):
        file = request.data.get('file')
        other = request.data.get('other')

        files_to_update = Gallery.objects.filter(file=file)
        for file_instance in files_to_update:
            file_instance.other = other
            file_instance.save()

            post_save.send(sender=file_instance.__class__, instance=file_instance, request=request, request_exist=True)

        return Response({'message': 'Comment updated successfully'}, status=status.HTTP_200_OK)

    def change_folder(self, request):
        file = request.data.get('file')
        new_folder = request.data.get('folder_name')
        folder_list = new_folder.split('/')
        cleaned_folder_list = [folder.rstrip('.') for folder in folder_list]
        cleaned_folder_name = '/'.join(cleaned_folder_list)

        if not new_folder:
            return Response({'error': 'Folder not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_file_path = os.path.join(settings.MEDIA_ROOT, file)
        new_file_path = os.path.join(settings.MEDIA_ROOT, cleaned_folder_name, os.path.basename(file))

        preview_image = Gallery.objects.filter(file=file).first().preview_image
        if preview_image:
            file_preview_image_name = preview_image.rsplit('/')[-1]
            file_type = Gallery.objects.filter(file=file).first().file_type
            old_preview_image_path = os.path.join(settings.MEDIA_ROOT, preview_image) if file_type == 'video' else None
            new_preview_image_path = os.path.join(settings.MEDIA_ROOT, cleaned_folder_name, file_preview_image_name) if file_type == 'video' else None

            if new_preview_image_path and default_storage.exists(new_preview_image_path):
                current_time = datetime.now().strftime('%d%m%Y%H%M')
                file_name, file_extension = os.path.splitext(new_preview_image_path)
                new_preview_image_path = f"{file_name}_{current_time}{file_extension}"

        if default_storage.exists(new_file_path):
            return Response({'error': 'File already exists in the new folder'}, status=status.HTTP_400_BAD_REQUEST)

        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        os.rename(old_file_path, new_file_path)

        if old_preview_image_path and new_preview_image_path:
            os.makedirs(os.path.dirname(new_preview_image_path), exist_ok=True)
            os.rename(old_preview_image_path, new_preview_image_path)          

        name = file.rsplit('/')[-1]
        new_file_name = f"{cleaned_folder_name}/{name}" 

        preview_image_name = new_preview_image_path.rsplit('\\')[-1] if new_preview_image_path else None
        new_preview_image_name = f"{cleaned_folder_name}/{preview_image_name}" if preview_image else None

        files_to_update = Gallery.objects.filter(file=file)
        for file_instance in files_to_update:
            file_instance.folder_name = cleaned_folder_name
            file_instance.file = new_file_name
            file_instance.preview_image = new_preview_image_name
            file_instance.save()

            post_save.send(sender=file_instance.__class__, instance=file_instance, request=request, request_exist=True)

        return Response({'message': 'Folder updated successfully'}, status=status.HTTP_200_OK)

    def delete_file(self, request):
        file = request.data.get('file')
        file_path = os.path.join(settings.MEDIA_ROOT, file)
        try:
            default_storage.delete(file_path)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        files_to_update = Gallery.objects.filter(file=file)
        for file_instance in files_to_update:
            file_instance.deleted = True
            file_instance.save()

            post_save.send(sender=file_instance.__class__, instance=file_instance, request=request, request_exist=True)

        return Response({'message': 'File deleted successfully'}, status=status.HTTP_200_OK)

    def to_archive(self, request):
        id = request.data.get('id')
        try:
            file_record = Gallery.objects.get(pk=id)
            file_record.active = False
            file_record.save()

            post_save.send(sender=file_record.__class__, instance=file_record, request=request, request_exist=True)

            return Response({'message': 'Record marked as inactive'}, status=status.HTTP_200_OK)
        except Gallery.DoesNotExist:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def from_archive(self, request):
        id = request.data.get('id')
        try:
            file_record = Gallery.objects.get(pk=id)
            file_record.active = True
            file_record.save()

            post_save.send(sender=file_record.__class__, instance=file_record, request=request, request_exist=True)

            return Response({'message': 'Record marked as inactive'}, status=status.HTTP_200_OK)
        except Gallery.DoesNotExist:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def open_location(self, request):
    #     folder_name = request.data.get('folder_name')
    #     file_path = os.path.join(settings.MEDIA_ROOT, folder_name)
    #     file_path = os.path.normpath(file_path)
    #     if platform.system() == 'Windows':
    #         os.startfile(file_path)
    #         return Response({'message': 'Location was opened successfully'}, status=status.HTTP_200_OK)
    #     else:
    #         raise OSError('Unsupported operating system')

class FilesSet(BaseFilterViewSet):
    
    queryset = Files.objects.all()
    serializer_class = FilesSerializer
    filter_fields = ['model_type', 'process_step', 'status', 'active', 'number', 'deleted']  
    filter_by_year = ['created_date']

    def create(self, request, *args, **kwargs):
        action_type = request.data.get('action')

        if action_type == 'add-new-file':
            return self.add_new_file(request)
        elif action_type == 'add-exist-file':
            return self.add_existing_file(request)
        elif action_type == 'change-status':
            return self.change_status(request)
        elif action_type == 'change-name':
            return self.change_name(request)
        elif action_type == 'change-folder':
            return self.change_folder(request)
        elif action_type == 'delete-file':
            return self.delete_file(request)
        elif action_type == 'change-comment':
            return self.change_comment(request)
        elif action_type == 'change-receiver':
            return self.change_receiver(request)
        elif action_type == 'to-archive':
            return self.to_archive(request)
        elif action_type == 'from-archive':
            return self.from_archive(request)
        # elif action_type == 'open-location':
        #     return self.open_location(request)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    def add_new_file(self, request):
        data = request.data
        file = request.FILES.get('file')
        model_type = data.get('model_type')
        number = data.get('number')
        process_step_id = data.get('process_step')
        folder_name = data.get('folder_name')
        name = data.get('name')
        received_from = data.get('received_from')
        other = data.get('other')

        if not all([file, model_type, folder_name, name]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            process_step = ProcessList.objects.get(pk=process_step_id) if process_step_id else None
        except ProcessList.DoesNotExist:
            return Response({'error': 'Invalid process_step ID'}, status=status.HTTP_400_BAD_REQUEST)

        file_name, extension = os.path.splitext(file.name)
        full_file_name = f"{name}{extension}"
        folder_list = folder_name.split('/')
        cleaned_folder_list = [folder.rstrip('.') for folder in folder_list]
        cleaned_folder_name = '/'.join(cleaned_folder_list)
        file_path = os.path.join(settings.MEDIA_ROOT, *cleaned_folder_list, full_file_name)
        file_path_name = "/".join(cleaned_folder_list + [full_file_name])

        if os.path.exists(file_path):
            return Response({'file-exist': 'File already exists'}, status=status.HTTP_400_BAD_REQUEST)

        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        try:
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            file_format = FilesFormats.objects.get(file_extension=extension.replace(".", "").lower())
            file_type = file_format.name.name
        except FilesFormats.DoesNotExist:
            file_type = "unknown"

        try:
            file_mod_time = os.path.getmtime(file_path)
            file_mod_datetime = datetime.fromtimestamp(file_mod_time)
            file_mod_datetime = timezone.make_aware(file_mod_datetime, timezone.get_current_timezone())
        except Exception as e:
            file_mod_datetime = timezone.now()

        file_record = Files(
            file=file_path_name,
            model_type=model_type,
            number=number,
            process_step=process_step,
            folder_name=cleaned_folder_name,
            received_from=received_from,
            other=other,
            name=name,
            file_extension=extension.replace(".", "").lower(),
            file_type=file_type,
            active=True,
            created_date=file_mod_datetime
        )

        file_record.save()
        post_save.send(sender=file_record.__class__, instance=file_record, request=request, request_exist=True)

        return Response(FilesSerializer(file_record).data, status=status.HTTP_201_CREATED)

    def add_existing_file(self, request):

        file = request.data.get('file')
        model_type = request.data.get('model_type')
        number = request.data.get('number')
        process_step_id = request.data.get('process_step')
        folder_name = request.data.get('folder_name')

        if not all([file, model_type, folder_name]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            process_step = ProcessList.objects.get(pk=process_step_id) if process_step_id else None
        except ProcessList.DoesNotExist:
            return Response({'error': 'Invalid process_step ID'}, status=status.HTTP_400_BAD_REQUEST)
        name = file.rsplit('/')[-1].rsplit('.', 1)[0]
        file_extension = file.rsplit('.')[-1].lower()

        try:
            file_format = FilesFormats.objects.get(file_extension=file_extension)
            file_type = file_format.name.name
        except FilesFormats.DoesNotExist:
            file_type = "unknown"

        file_record = Files(
            file=file,
            model_type=model_type,
            number=number,
            process_step=process_step,
            folder_name=folder_name,
            name=name,
            file_extension=file_extension,
            file_type=file_type
        )

        existing_file = Files.objects.filter(file=file).first()
        if existing_file:
            file_record.status = existing_file.status
            file_record.received_from = existing_file.received_from
            file_record.other = existing_file.other
            file_record.created_date = existing_file.created_date
        else:
            file_record.active = True
            file_record.received_from = None
            file_record.other = None
            file_record.created_date = timezone.now()

        file_record.save()
        post_save.send(sender=file_record.__class__, instance=file_record, request=request, request_exist=True)

        return Response({'message': 'File record added successfully'}, status=status.HTTP_201_CREATED)

    def change_status(self, request):
        file = request.data.get('file')
        status_id = request.data.get('status')
        if not status_id:
            return Response({'error': 'Status not provided'}, status=status.HTTP_400_BAD_REQUEST)

        new_status = get_object_or_404(FilesStatuses, pk=status_id)
        files_to_update = Files.objects.filter(file=file)
        for file_instance in files_to_update:
            file_instance.status = new_status
            file_instance.save()

            post_save.send(sender=file_instance.__class__, instance=file_instance, request=request, request_exist=True)
        
        return Response({'message': 'Status updated successfully'}, status=status.HTTP_200_OK)

    def change_name(self, request):
        file = request.data.get('file')
        new_name = request.data.get('name')
        if not new_name:
            return Response({'error': 'Name not provided'}, status=status.HTTP_400_BAD_REQUEST)

        old_file_path = os.path.join(settings.MEDIA_ROOT, file)
        new_file_path = os.path.join(os.path.dirname(old_file_path), f"{new_name}.{file.split('.')[-1]}")

        if old_file_path.replace('/','_').replace('\\', '_').lower() != new_file_path.replace('/','_').replace('\\', '_').lower():
            if default_storage.exists(new_file_path):
                return Response({'error': 'File with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        os.rename(old_file_path, new_file_path)

        extension = file.rsplit('.')[-1]
        file_without_name = "/".join(file.rsplit('/', 1)[:-1])
        new_file_name = f"{file_without_name}/{new_name}.{extension}"

        files_to_update = Files.objects.filter(file=file)
        for file_instance in files_to_update:
            file_instance.file = new_file_name
            file_instance.name = new_name
            file_instance.save()

            post_save.send(sender=file_instance.__class__, instance=file_instance, request=request, request_exist=True)

        return Response({'message': 'Name updated successfully'}, status=status.HTTP_200_OK)

    def change_comment(self, request):
        file = request.data.get('file')
        other = request.data.get('other')

        files_to_update = Files.objects.filter(file=file)
        for file_instance in files_to_update:
            file_instance.other = other
            file_instance.save()

            post_save.send(sender=file_instance.__class__, instance=file_instance, request=request, request_exist=True)

        return Response({'message': 'Comment updated successfully'}, status=status.HTTP_200_OK)

    def change_receiver(self, request):
        file = request.data.get('file')
        received_from = request.data.get('received_from')

        files_to_update = Files.objects.filter(file=file)
        for file_instance in files_to_update:
            file_instance.received_from = received_from
            file_instance.save()

            post_save.send(sender=file_instance.__class__, instance=file_instance, request=request, request_exist=True)

        return Response({'message': 'Receiver updated successfully'}, status=status.HTTP_200_OK)

    def change_folder(self, request):
        file = request.data.get('file')
        new_folder = request.data.get('folder_name')
        folder_list = new_folder.split('/')
        cleaned_folder_list = [folder.rstrip('.') for folder in folder_list]
        cleaned_folder_name = '/'.join(cleaned_folder_list)

        if not new_folder:
            return Response({'error': 'Folder not provided'}, status=status.HTTP_400_BAD_REQUEST)

        old_file_path = os.path.join(settings.MEDIA_ROOT, file)
        new_file_path = os.path.join(settings.MEDIA_ROOT, cleaned_folder_name, os.path.basename(file))

        if default_storage.exists(new_file_path):
            return Response({'error': 'File already exists in the new folder'}, status=status.HTTP_400_BAD_REQUEST)

        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        os.rename(old_file_path, new_file_path)

        name = file.rsplit('/')[-1]
        new_file_name = f"{cleaned_folder_name}/{name}"        

        files_to_update = Files.objects.filter(file=file)
        for file_instance in files_to_update:
            file_instance.folder_name = cleaned_folder_name
            file_instance.file = new_file_name
            file_instance.save()

            post_save.send(sender=file_instance.__class__, instance=file_instance, request=request, request_exist=True)

        return Response({'message': 'Folder updated successfully'}, status=status.HTTP_200_OK)

    def delete_file(self, request):
        file = request.data.get('file')
        file_path = os.path.join(settings.MEDIA_ROOT, file)
        try:
            default_storage.delete(file_path)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        files_to_update = Files.objects.filter(file=file)
        for file_instance in files_to_update:
            file_instance.deleted = True
            file_instance.save()

            post_save.send(sender=file_instance.__class__, instance=file_instance, request=request, request_exist=True)

        return Response({'message': 'File deleted successfully'}, status=status.HTTP_200_OK)

    def to_archive(self, request):
        id = request.data.get('id')
        try:
            file_record = Files.objects.get(pk=id)
            file_record.active = False
            file_record.save()

            post_save.send(sender=file_record.__class__, instance=file_record, request=request, request_exist=True)

            return Response({'message': 'Record marked as inactive'}, status=status.HTTP_200_OK)
        except Files.DoesNotExist:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def from_archive(self, request):
        id = request.data.get('id')
        try:
            file_record = Files.objects.get(pk=id)
            file_record.active = True
            file_record.save()

            post_save.send(sender=file_record.__class__, instance=file_record, request=request, request_exist=True)

            return Response({'message': 'Record marked as inactive'}, status=status.HTTP_200_OK)
        except Files.DoesNotExist:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def open_location(self, request):
    #     folder_name = request.data.get('folder_name')
    #     file_path = os.path.join(settings.MEDIA_ROOT, folder_name)
    #     file_path = os.path.normpath(file_path)
    #     if platform.system() == 'Windows':
    #         os.startfile(file_path)
    #         return Response({'message': 'Location was opened successfully'}, status=status.HTTP_200_OK)
    #     # elif platform.system() == 'Darwin':
    #     #     subprocess.run(['open', file_path])
    #     #     return Response({'message': 'Location was opened successfully'}, status=status.HTTP_200_OK)
    #     # elif platform.system() == 'Linux':
    #     #     subprocess.run(['xdg-open', file_path])
    #     #     return Response({'message': 'Location was opened successfully'}, status=status.HTTP_200_OK)
    #     else:
    #         raise OSError('Unsupported operating system')

class FilesTableSet(BaseFilterViewSet):
    
    queryset = Files.objects.all()
    serializer_class = FilesTableSerializer
    filter_fields = ['model_type', 'process_step', 'status', 'active', 'number', 'deleted'] 

    def get_queryset(self):

        queryset = super().get_queryset()

        queryset = queryset.select_related(
            'process_step',
            'status'
        )
        
        return queryset

class BanksBIDsSet(BaseFilterViewSet):
    
    queryset = BanksBIDs.objects.all()
    serializer_class = BanksBIDsSerializer  
    filter_fields = ['id', 'bank']

class PaymentSystemApprovalsSet(BaseFilterViewSet):
    
    queryset = PaymentSystemApprovals.objects.all()
    serializer_class = PaymentSystemApprovalsSerializer  
    filter_fields = ['id', 'line_number']

class KeyExchangeStatusesSet(viewsets.ModelViewSet):
    
    queryset = KeyExchangeStatuses.objects.all()
    serializer_class = KeyExchangeStatusesSerializer 

class KeyExchangeProjectsSet(BaseFilterViewSet):
    
    queryset = KeyExchangeProjects.objects.all()
    serializer_class = KeyExchangeProjectsSerializer
    filter_fields = ['id', 'active', 'bank'] 

class KeyExchangeTableProjectsSet(BaseFilterViewSet):
    
    queryset = KeyExchangeProjects.objects.all()
    serializer_class = KeyExchangeTableProjectsSerializer
    filter_fields = ['active'] 

    def get_queryset(self):

        queryset = super().get_queryset()

        queryset = queryset.select_related(
            'status', 
            'bank',
            'bank_KMC_name',
            'vendor', 
            'vendor_origin', 
            'vendor_KMC_name',
            'vendor_consultant'
        )

        for obj in queryset:
            if obj.request_date:
                obj.request_date = format_date(obj.request_date)

        return queryset
    
class CardTestingProjectsSet(BaseFilterViewSet):
    
    queryset = CardTestingProjects.objects.all()
    serializer_class = CardTestingProjectsSerializer 
    filter_fields = ['id', 'active', 'bank', 'type_card'] 

class CardTestingTableProjectsSet(BaseFilterViewSet):
    
    queryset = CardTestingProjects.objects.all()
    serializer_class = CardTestingTableProjectsSerializer
    filter_fields = ['active', 'type_card']

    def get_queryset(self):

        queryset = super().get_queryset()
        queryset = queryset.annotate(
            received=Coalesce(
                Sum(
                    'card_testing_project__transfer_quantity',
                    filter=Q(card_testing_project__action=1, card_testing_project__deleted=False)
                ),
                Value(0)
            ),
            sent=Coalesce(
                Sum(
                    'card_testing_project__transfer_quantity',
                    filter=Q(card_testing_project__action=2, card_testing_project__deleted=False)
                ),
                Value(0)
            )
        ).annotate(
            on_stock=Coalesce(
                ExpressionWrapper(
                    F('received') - F('sent'),
                    output_field=IntegerField()
                ),
                Value(0)
            )
        # )
        ).select_related(
            'status', 
            'bank', 
            'vendor', 
            'vendor_origin',
            'chip', 
            'applet', 
            'mifare',
            'product_type', 
            'type_card', 
            'KCV', 
            'antenna_size', 
            'material_type',
            'material_color', 
            'magstripe_color', 
            'magstripe_tracks',
            'lamination_face', 
            'lamination_back', 
            'signed_by'
        )

        for obj in queryset:
            if obj.request_date:
                obj.request_date = format_date(obj.request_date)
                
        return queryset

class CardTestingStatusesSet(viewsets.ModelViewSet):
    
    queryset = CardTestingStatuses.objects.all()
    serializer_class = CardTestingStatusesSerializer 

class TestCardTypesSet(viewsets.ModelViewSet):
    
    queryset = TestCardTypes.objects.all()
    serializer_class = TestCardTypesSerializer 

class TestCardTransferSet(viewsets.ViewSet):
    
    def list(self, request):
        allTestCardTransfers = TestCardTransfer.objects
        if 'card_testing_project' in request.GET.keys():
            if 'deleted' in request.GET.keys():
                queryset = allTestCardTransfers.filter(
                    card_testing_project_id=request.GET['card_testing_project'],
                    deleted=request.GET['deleted']
                )
            else:
                queryset = allTestCardTransfers.filter(card_testing_project_id=request.GET['card_testing_project'])
        else:
            queryset = allTestCardTransfers.all()

        serializer = TestCardTransferSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request):
        data = request.data.copy()
        data['action'] = 1 if int(request.data['action']) == 1 else 2
        queryset = TestCardTransferSerializer(data=data)
        queryset.is_valid(raise_exception=True)  
        if int(request.data['action']) == 1:  
            instance = queryset.save()
            post_save.send(sender=TestCardTransfer, instance=instance, request=request, request_exist=True)

            return Response(queryset.data, status=status.HTTP_201_CREATED)
        
        else:
            transfers = TestCardTransfer.objects.filter(card_testing_project_id=request.data['card_testing_project'])
            total_added = transfers.filter(action_id=1, deleted=False).aggregate(total_quantity=Sum('transfer_quantity'))['total_quantity'] or 0
            total_moved = transfers.filter(action_id=2, deleted=False).aggregate(total_quantity=Sum('transfer_quantity'))['total_quantity'] or 0
            if request.data['transfer_quantity'] <= total_added - total_moved:
                data = request.data

                if int(request.data['action']) == 2 or int(request.data['action']) == 4:
                    cardTestingProjectFrom = CardTestingProjects.objects.filter(id=data['card_testing_project'])
                    cardTestingProjectTo = CardTestingProjects.objects.filter(id=data['to_card_testing_project'])
                    newLineFrom = {
                        "card_testing_project": queryset.data.get('card_testing_project', None),
                        "action": 2,
                        "transfer_date": queryset.data.get('transfer_date', None),
                        "transfer_quantity": queryset.data.get('transfer_quantity', None),
                        "other": queryset.data.get('other', None),
                        "comment": f"Передано в {cardTestingProjectTo[0].number}",
                    }
                    newLineDataFrom = TestCardTransferSerializer(data=newLineFrom)
                    newLineDataFrom.is_valid(raise_exception=True)
                    instance = newLineDataFrom.save()
                    post_save.send(sender=TestCardTransfer, instance=instance, request=request, request_exist=True)

                    newLineTo = {
                        "card_testing_project": data.get('to_card_testing_project', None),
                        "action": 1,
                        "transfer_date": data.get('transfer_date', None),
                        "transfer_quantity": data.get('transfer_quantity', None),
                        "other": None,
                        "comment": f"Получено из {cardTestingProjectFrom[0].number}",
                    }
                    newLineDataTo = TestCardTransferSerializer(data=newLineTo)
                    newLineDataTo.is_valid(raise_exception=True)
                    instance = newLineDataTo.save()
                    post_save.send(sender=TestCardTransfer, instance=instance, request=request, request_exist=True)

                    return Response(queryset.data, status=status.HTTP_201_CREATED)

                elif int(request.data['action']) == 3: 
                    cardTestingProject = CardTestingProjects.objects.filter(id=data['card_testing_project'])
                    newCardTestingProject = {
                        "type_card": cardTestingProject[0].type_card_id,
                        "is_for_bank": True if data.get('bank', None) else False,
                        "bank": data.get('bank', None),
                        "vendor": cardTestingProject[0].vendor_id,
                        "vendor_origin": cardTestingProject[0].vendor_origin_id,
                        "vendor_consultant": cardTestingProject[0].vendor_consultant_id,
                        "chip": cardTestingProject[0].chip_id,
                        "applet": cardTestingProject[0].applet_id,
                        "mifare": cardTestingProject[0].mifare_id,
                        "mifare_access_key": cardTestingProject[0].mifare_access_key,
                        "antenna_size": cardTestingProject[0].antenna_size_id,
                        "product_type": cardTestingProject[0].product_type_id,
                        "material_type": cardTestingProject[0].material_type_id,
                        "material_color": cardTestingProject[0].material_color_id,
                        "magstripe_color": cardTestingProject[0].magstripe_color_id,
                        "magstripe_tracks": cardTestingProject[0].magstripe_tracks_id,
                        "lamination_face": cardTestingProject[0].lamination_face_id,
                        "lamination_back": cardTestingProject[0].lamination_back_id,
                        "input_code": cardTestingProject[0].input_code,
                        "based_on": cardTestingProject[0].based_on_id,
                        "product_type": cardTestingProject[0].product_type_id,
                    }
                    newCardTestingProjectData = CardTestingProjectsSerializer(data=newCardTestingProject)
                    newCardTestingProjectData.is_valid(raise_exception=True)
                    newCardTestProjectId = newCardTestingProjectData.save()   
                    post_save.send(sender=CardTestingProjects, instance=newCardTestProjectId, request=request, request_exist=True)

                    newLineFrom = {
                        "card_testing_project": queryset.data.get('card_testing_project', None),
                        "action": 2,
                        "transfer_date": queryset.data.get('transfer_date', None),
                        "transfer_quantity": queryset.data.get('transfer_quantity', None),
                        "other": queryset.data.get('other', None),
                        "comment": f"Передано в {newCardTestProjectId.number}",
                    }
                    newLineDataFrom = TestCardTransferSerializer(data=newLineFrom)
                    newLineDataFrom.is_valid(raise_exception=True)
                    instance = newLineDataFrom.save()   
                    post_save.send(sender=TestCardTransfer, instance=instance, request=request, request_exist=True)

                    newLineTo = {
                        "card_testing_project": newCardTestProjectId.pk,
                        "action": 1,
                        "transfer_date": data.get('transfer_date', None),
                        "transfer_quantity": data.get('transfer_quantity', None),
                        "other": None,
                        "comment": f"Получено из {cardTestingProject[0].number}",
                    }
                    newLineDataTo = TestCardTransferSerializer(data=newLineTo)
                    newLineDataTo.is_valid(raise_exception=True)
                    instance = newLineDataTo.save()   
                    post_save.send(sender=TestCardTransfer, instance=instance, request=request, request_exist=True)
                    
                    return Response(queryset.data, status=status.HTTP_201_CREATED)

                elif int(request.data['action']) == 5 or int(request.data['action']) == 6: 
                    queryset.is_valid(raise_exception=True)
                    instance = queryset.save()   
                    post_save.send(sender=TestCardTransfer, instance=instance, request=request, request_exist=True)
                    return Response(queryset.data, status=status.HTTP_201_CREATED)
            else:
                return Response(f'Количество карт не достаточно. В наличии {total_added - total_moved} шт', status=status.HTTP_400_BAD_REQUEST)     

    def partial_update(self, request, pk=None):
        instance = TestCardTransfer.objects.get(pk=pk)
        transfers = TestCardTransfer.objects.filter(card_testing_project_id=instance.card_testing_project)
        total_added = transfers.filter(action_id=1, deleted=False).aggregate(total_quantity=Sum('transfer_quantity'))['total_quantity'] or 0
        total_moved = transfers.filter(action_id=2, deleted=False).aggregate(total_quantity=Sum('transfer_quantity'))['total_quantity'] or 0
        if int(request.data['action']) == 7:
            data = request.data.copy()
            if instance.action.pk == 2 and data.get('transfer_quantity'):
                if (total_added - total_moved + instance.transfer_quantity - data.get('transfer_quantity')) < 0:
                    return Response(f'Количество карт при изменении не достаточно.', status=status.HTTP_400_BAD_REQUEST)     
            elif instance.action.pk == 1 and data.get('transfer_quantity'):
                if (total_added - total_moved - instance.transfer_quantity + data.get('transfer_quantity')) < 0:
                    return Response(f'Количество карт при изменении не достаточно.', status=status.HTTP_400_BAD_REQUEST)     

            newData = {
                "transfer_date": data.get('transfer_date') if 'transfer_date' in data else instance.transfer_date,
                "transfer_quantity": data.get('transfer_quantity') if 'transfer_quantity' in data else instance.transfer_quantity,
                "other": data.get('other') if 'other' in data else instance.other,
            }
            updatedData = TestCardTransferSerializer(instance, data=newData, partial=True)
            updatedData.is_valid(raise_exception=True)
            instance = updatedData.save()   
            post_save.send(sender=TestCardTransfer, instance=instance, request=request, request_exist=True)
            
            return Response(updatedData.data, status=status.HTTP_200_OK)           

        elif int(request.data['action']) == 8:
            if instance.action.pk == 1:
                if (total_added - total_moved - instance.transfer_quantity) < 0:
                    return Response(f'Количество карт при удалении не достаточно.', status=status.HTTP_400_BAD_REQUEST)     

            newData = {
                "deleted": True
            }
            updatedData = TestCardTransferSerializer(instance, data=newData, partial=True)
            updatedData.is_valid(raise_exception=True)
            instance = updatedData.save()   
            post_save.send(sender=TestCardTransfer, instance=instance, request=request, request_exist=True)
            
            return Response(updatedData.data, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)     

class TransferActionsSet(viewsets.ModelViewSet):
    
    queryset = TransferActions.objects.all()
    serializer_class = TransferActionsSerializer 

class ProcessingCentersSet(BaseFilterViewSet):
    
    queryset = ProcessingCenters.objects.all()
    serializer_class = ProcessingCentersSerializer 
    filter_fields = ['id']

class PesroScriptVendorsSet(BaseFilterViewSet):
    
    queryset = PesroScriptVendors.objects.all()
    serializer_class = PesroScriptVendorsSerializer 
    filter_fields = ['id']

class LaminationTypesSet(BaseFilterViewSet):
    
    queryset = LaminationTypes.objects.all()
    serializer_class = LaminationTypesSerializer
    filter_fields = ['id', 'vendor']

class PaymentTypesSet(viewsets.ModelViewSet):
    
    queryset = PaymentTypes.objects.all()
    serializer_class = PaymentTypesSerializer 

class PaymentsInfoSet(BaseFilterViewSet):
    
    queryset = PaymentsInfo.objects.all()
    serializer_class = PaymentsInfoSerializer
    filter_fields = ['id', 'line_number', 'company_type', 'deleted']

class PaymentsInfoTableSet(BaseFilterViewSet):
    
    queryset = PaymentsInfo.objects.all()
    serializer_class = PaymentsInfoTableSerializer
    filter_fields = ['id', 'line_number', 'company_type', 'deleted']

    def get_queryset(self):

        queryset = super().get_queryset()

        queryset = queryset.select_related(
            'currency',
            'payment_type',
        )
        
        for obj in queryset:
            if obj.payment_value is not None:
                formatted_value = format_with_thousands_separator(obj.payment_value, 'float')
                obj.payment_value = f"{formatted_value}"
            else:
                obj.payment_value = '' 

        return queryset

class DeliveriesInfoTableSet(BaseFilterViewSet):
    
    queryset = DeliveriesInfo.objects.all()
    serializer_class = DeliveriesInfoTableSerializer
    filter_fields = ['id', 'line_number', 'company_type', 'deleted']

    def get_queryset(self):

        queryset = super().get_queryset()
        
        for obj in queryset:
            if obj.quantity is not None:
                formatted_value = format_with_thousands_separator(obj.quantity, 'int')
                obj.quantity = f"{formatted_value}"
            else:
                obj.quantity = '' 

        return queryset

class DeliveriesInfoSet(BaseFilterViewSet):
    
    queryset = DeliveriesInfo.objects.all()
    serializer_class = DeliveriesInfoSerializer
    filter_fields = ['id', 'line_number', 'company_type', 'deleted']

class MifareTypesSet(viewsets.ModelViewSet):
    serializer_class = MifareTypesSerializer

    def get_queryset(self):
        queryset = MifareTypes.objects.all()
        
        id_param = self.request.query_params.get('id', None)
        chip_param = self.request.query_params.get('chip', None)
        
        if id_param is not None:
            queryset = queryset.filter(id=id_param)
        
        if chip_param is not None:
            chip = Chips.objects.filter(id=chip_param).first()
            if not chip:
                raise NotFound(detail="Chip not found")

            mifare_available = chip.mifare_available.all()
            mifare_available_ids = [item.id for item in mifare_available]
            queryset = queryset.filter(id__in=mifare_available_ids)
        return queryset
    
class AppletTypesSet(viewsets.ModelViewSet):
    serializer_class = AppletTypesSerializer

    def get_queryset(self):
        queryset = AppletTypes.objects.all()
        
        id_param = self.request.query_params.get('id', None)
        chip_param = self.request.query_params.get('chip', None)
        payment_system = self.request.query_params.get('payment_system', None)
        
        if id_param is not None:
            queryset = queryset.filter(id=id_param)
        
        if chip_param is not None:
            chip = Chips.objects.filter(id=chip_param).first()
            if not chip:
                raise NotFound(detail="Chip not found")

            applet_available = chip.applet_available.all()
            applet_available_ids = [item.id for item in applet_available]
            queryset = queryset.filter(id__in=applet_available_ids)

        if payment_system is not None:
            queryset = queryset.filter(payment_system=payment_system)

        return queryset

class StartYearSet(viewsets.ModelViewSet):
    
    queryset = StartYear.objects.all()
    serializer_class = StartYearSerializer

class ShortProjectLineViewSet(BaseFilterViewSet):
    
    queryset = ProjectLine.objects.all()
    serializer_class = ShortProjectLineSerializer
    filter_fields = ['id', 'active']  

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = queryset.select_related(
            'bank', 
            'vendor',
            'product_type',
            'payment_system',
            'product_category',
            'chip',
            'applet',
            'mifare',
        ).annotate(
            payment_system_name=Coalesce(F('payment_system__name'), Value('', output_field=CharField())),
            product_category_name=Coalesce(F('product_category__name'), Value('', output_field=CharField())),
            chip_name=Coalesce(F('chip__short_name'), Value('', output_field=CharField())),
            applet_name=Coalesce(F('applet__name'), Value('', output_field=CharField())),
            mifare_text=Case(
                When(mifare=True, then=Value("+ Mifare", output_field=CharField())),
                default=Value('', output_field=CharField())
            ), 
            product_full_name=Concat(
                Coalesce(F('payment_system__name'), Value('')),
                Case(
                    When(product_category__name__isnull=False, payment_system__name__isnull=False, then=Concat(Value(' '), F('product_category__name'))),
                    When(product_category__name__isnull=False, payment_system__name__isnull=True, then=F('product_category__name')),
                    default=Value(''),
                    output_field=CharField()
                ),
                Case(
                    When(product_name__isnull=False, product_category__name__isnull=False, then=Concat(Value(' '), F('product_name'))),
                    When(product_name__isnull=False, product_category__name__isnull=True, payment_system__name__isnull=False, then=Concat(Value(' '), F('product_name'))),
                    When(product_name__isnull=False, product_category__name__isnull=True, payment_system__name__isnull=True, then=F('product_name')),
                    default=Value(''),
                    output_field=CharField()
                )
            ),
            chip_full_name = Concat(
                Case(
                    When(chip__short_name__isnull=False, then=F('chip__short_name')),
                    default=Value(''),
                    output_field=CharField()
                ),
                Case(
                    When(applet__name__isnull=False, chip__short_name__isnull=False, then=Concat(Value(' '), F('applet__name'))),
                    When(applet__name__isnull=False, chip__short_name__isnull=True, then=F('applet__name')),
                    default=Value(''),
                    output_field=CharField()
                ),
                Case(
                    When(mifare_text__isnull=False, applet__name__isnull=False, then=Concat(Value(' '), F('mifare_text'))),
                    When(mifare_text__isnull=False, applet__name__isnull=True, chip__short_name__isnull=False, then=Concat(Value(' '), F('mifare_text'))),
                    When(mifare_text__isnull=False, applet__name__isnull=True, chip__short_name__isnull=True, then=F('mifare_text')),
                    default=Value(''),
                    output_field=CharField()
                )
            ),
        )    

        received_id=self.request.query_params.get('id', None)
        if received_id:
            clean_id = received_id.replace('!', '')
            bank_id = ProjectLine.objects.filter(id=clean_id).first().bank
            queryset = queryset.filter(bank=bank_id)
        

        return queryset

class ProductionDataSet(BaseFilterViewSet):
    
    queryset = ProductionData.objects.all()
    serializer_class = ProductionDataSerializer  
    filter_fields = ['id', 'line_number']

class RelevantFilesSet(BaseFilterViewSet):
    
    queryset = Files.objects.all()
    serializer_class = FilesSerializer  
    filter_fields = ['id', 'model_type', 'process_step']
    filter_include_fields = ['number'] 

    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
  
        if (self.request.query_params.get('model_type', 'ProjectLine')):
            bank_param_value = self.request.query_params.get('bank', None)
            if bank_param_value is not None:
                bank = int(bank_param_value)
                
                project_lines = [line.strip() for line in queryset.filter(model_type='ProjectLine').values_list('number', flat=True).distinct()]
                
                valid_numbers_set = set()
                for project_line in project_lines:
                    
                    numbers = [int(num.strip()) for num in project_line.split(',') if num.strip().isdigit()]
                    
                    for number in numbers:
                        if ProjectLine.objects.filter(id=number, bank=bank).exists():
                            valid_numbers_set.add(number)
                            
                valid_numbers = list(valid_numbers_set)
                if valid_numbers:
                    q_objects = Q()
                    for number in valid_numbers:
                        q_objects |= Q(number__contains=str(number))
                    queryset = queryset.filter(q_objects)
                else:
                    queryset = queryset.none()
            
        return queryset

class AnnexesConditionsDataSet(BaseFilterViewSet):
    
    queryset = AnnexesConditionsData.objects.all()
    serializer_class = AnnexesConditionsDataSerializer  
    filter_fields = ['id', 'line_number']

class POConditionsDataSet(BaseFilterViewSet):
    
    queryset = POConditionsData.objects.all()
    serializer_class = POConditionsDataSerializer  
    filter_fields = ['id', 'line_number']
        
class MonthListSet(viewsets.ModelViewSet):
    
    queryset = MonthList.objects.all()
    serializer_class = MonthListSerializer

class CardTestingShortRelevantLineSet(viewsets.ViewSet):
    
    def list(self, request):
        allCardTestsingProjects = CardTestingProjects.objects
        if 'id' in request.GET.keys():
            queryset = allCardTestsingProjects.filter(id=request.GET['id'])
            serializer = CardTestingShortRelevantLineSerializer(queryset, many=True)
            id_line = serializer.data[0]
            another_id = allCardTestsingProjects.exclude(id=request.GET['id'])
            filtered_lines = another_id.filter(
                type_card_id=id_line['type_card'],
                vendor_id=id_line['vendor'],
                chip_id=id_line['chip'],
                applet_id=id_line['applet'],
                mifare_id=id_line['mifare'],
                mifare_access_key=id_line['mifare_access_key'],
                antenna_size_id=id_line['antenna_size'],
                product_type_id=id_line['product_type'],
                material_type_id=id_line['material_type'],
                material_color_id=id_line['material_color'],
                magstripe_color_id=id_line['magstripe_color'],
                magstripe_tracks_id=id_line['magstripe_tracks'],
                lamination_face_id=id_line['lamination_face'],
                lamination_back_id=id_line['lamination_back'],
                active=id_line['active']
            )

            if id_line['is_for_bank']:                                
                serializer2 = CardTestingShortRelevantLineSerializer(filtered_lines.filter(is_for_bank = 0), many=True)
                return Response(serializer2.data, status=status.HTTP_201_CREATED)
            else:
                serializer2 = CardTestingShortRelevantLineSerializer(filtered_lines, many=True)
                return Response(serializer2.data, status=status.HTTP_201_CREATED)
        else:
            queryset = allCardTestsingProjects.all()

        serializer = CardTestingShortRelevantLineSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class FolderPathSet(viewsets.ViewSet):
    def list(self, request):
        model_name = request.GET.get('model_name', '').lower()
        model_type = request.GET.get('model_type', '').lower()
        component_name = request.GET.get('component_name', '')
        number = request.GET.get('number', '')

        folder_path = self.get_main_folder(model_name, model_type, component_name, number)
        return Response(folder_path, status=status.HTTP_200_OK)

    def get_main_folder(self, model_name, model_type, component_name, number):
        if model_name == 'files':

            if model_type == 'projectline':
                main_path = 'Заказы'
                subfolder = ''
                try:
                    ModelClass = apps.get_model(app_label='backend_api', model_name=model_type)
                    project = ModelClass.objects.get(pk=number)

                    if component_name == 'Исходники':
                        subfolder = 'Дизайны'
                    elif component_name == 'Макеты':
                        subfolder = 'Дизайны'
                    elif component_name == 'Доставки от вендора':
                        component_name = "Инвойсы"
                    elif component_name == 'Доставки в банк':
                        component_name = "Акты" 
                    elif component_name == 'PO':
                        vendor = project.vendor.name
                        component_name = f'PO/{vendor}'

                    country_name = project.bank.country.name_rus
                    bank_name = project.bank.name_eng
                    display_year = project.display_year
                    
                    if not subfolder:
                        full_path = f'{main_path}/{component_name}/{country_name}/{bank_name}/{display_year}'
                    else:    
                        full_path = f'{main_path}/{subfolder}/{component_name}/{country_name}/{bank_name}/{display_year}'

                    return full_path
                
                except ObjectDoesNotExist:
                    return main_path
            
            elif model_type == 'keyexchangeprojects':
                main_path = 'Тестирование/ZMK'

                try:
                    ModelClass = apps.get_model(app_label='backend_api', model_name=model_type)
                    project = ModelClass.objects.get(pk=number)
                    country_name = project.bank.country.name_rus
                    bank_name = project.bank.name_eng
                    
                    full_path = f"{main_path}/{country_name}/{bank_name}"
                    return full_path
                
                except ObjectDoesNotExist:
                    return main_path
                
            elif model_type == 'cardtestingprojects':
                main_path = 'Тестирование/CARDS'

                try:
                    ModelClass = apps.get_model(app_label='backend_api', model_name=model_type)
                    project = ModelClass.objects.get(pk=number)
                    type_card = project.type_card.name

                    try:
                        country_name = project.bank.country.name_rus
                        bank_name = project.bank.name_eng
                        path = f'{country_name}/{bank_name}'
                    except:
                        path = 'Another'

                    chip = project.chip.short_name if project.chip else 'NoChip'
                    applet = project.applet.name if project.applet else ''

                    if applet:
                        full_path = f"{main_path}/{type_card}/{path}/{chip} {applet}"
                    else:
                        full_path = f"{main_path}/{type_card}/{path}/{chip}"
                    return full_path
                
                except ObjectDoesNotExist:
                    return main_path   

            elif model_type == 'doctemplates':
                main_path = 'Шаблоны документов'

                return main_path 
            
            elif model_type == 'instructions':
                main_path = 'Инструкции'

                return main_path 
            else:
                return 'Другое'
            
        elif model_name == 'gallery':
            if model_type == 'projectline':
                main_path = 'Галерея'
                subfolder = 'Заказы'
                try:
                    ModelClass = apps.get_model(app_label='backend_api', model_name=model_type)
                    project = ModelClass.objects.get(pk=number)                      

                    country_name = project.bank.country.name_rus
                    bank_name = project.bank.name_eng
                    display_year = project.display_year

                    payment_system_name = getattr(project.payment_system, 'name', None)
                    product_category_name = getattr(project.product_category, 'name', None)     
                    product_name = project.product_name
                    product_code = project.product_code
                    product_revision = project.product_revision

                    payment_system_name if payment_system_name else None
                    product_category_name if product_category_name else None
                    product_name if product_name else None
                    product_code if product_code else None
                    product_revision if product_revision else None
  
                    full_name = ' '.join(part for part in [payment_system_name, product_category_name, product_name, product_code, product_revision] if part)
                    full_path = f'{main_path}/{subfolder}/{country_name}/{bank_name}/{display_year}/{full_name if full_name else "New folder"}'

                    return full_path
                
                except ObjectDoesNotExist:
                    return main_path

            elif model_type == 'magstripecolors':
                return 'Галерея/Магнитная полоса'
            elif model_type == 'laminationtypes':
                return 'Галерея/Ламинация'
            elif model_type == 'materialcolors':
                return 'Галерея/Цвет края'
            elif model_type == 'effects':
                return 'Галерея/Эффекты'
            else:
                return 'Другое'
        else:
            return 'Другое'

class FoldersSet(viewsets.ViewSet):
    def list(self, request):
        path = settings.MEDIA_ROOT
        if not os.path.exists(path):
            return Response({'error': 'Path does not exist'}, status=404)

        def get_directory_structure(rootdir):
            dir_structure = []
            id_counter = 1
            for root, dirs, files in os.walk(rootdir):
                root_relative = os.path.relpath(root, rootdir)
                if root_relative == '.':
                    root_relative = ''
                root_parts = root_relative.split(os.sep) if root_relative else []
                
                for name in dirs:
                    dir_structure.append({
                        'id': id_counter,
                        'filePath': root_parts + [name],
                        'size': None,
                        'dateModified': None,
                        'type': 'folder',
                        'name': name
                    })
                    id_counter += 1
                for name in files:
                    full_path = os.path.join(root, name)
                    size = os.path.getsize(full_path)
                    date_modified = time.strftime('%b %d %Y %I:%M:%S %p', time.localtime(os.path.getmtime(full_path)))
                    dir_structure.append({
                        'id': id_counter,
                        'filePath': root_parts + [name],
                        'size': size,
                        'dateModified': date_modified,
                        'type': 'file',
                        'name': name
                    })
                    id_counter += 1
            return dir_structure

        folders_files = get_directory_structure(path)
        return Response(folders_files)
    
class EffectsCommonViewSet(viewsets.ViewSet):

    def list(self, request):
        try:
            id=request.GET.get('id', '')
            project=ProjectLine.objects.filter(id=id).first()

            chip_name = getattr(project.chip, 'full_name', '')
            applet_name = getattr(project.applet, 'short_name', '')
            mifare=project.mifare
            mifare_text="+ Mifare" if mifare else ''
            chip_full_name=' '.join(part for part in [chip_name, applet_name, mifare_text] if part)
            chip_color_rus = getattr(project.chip_color, 'name_rus', '')
            chip_color_eng = getattr(project.chip_color, 'name_eng', '')
            chip_color_rus_with_label = f'{chip_color_rus.lower()} модуль' if chip_color_rus else ''
            chip_color_eng_with_label = f'{chip_color_eng.lower()} module' if chip_color_eng else ''

            material_type_rus = getattr(project.material_type, 'name_rus', '')
            material_type_eng = getattr(project.material_type, 'name_eng', '')
            material_color_rus = getattr(project.material_color, 'name_rus', '')
            material_color_eng = getattr(project.material_color, 'name_eng', '')
            material_rus = (f"{material_color_rus.lower()}" if material_color_rus else '') + (f" {material_type_rus.lower()}" if material_type_rus else '')
            material_eng = (f"{material_color_eng.lower()}" if material_color_eng else '') + (f" {material_type_eng.lower()}" if material_type_eng else '')

            magstripe_color_rus = getattr(project.magstripe_color, 'name_rus', '')
            magstripe_color_eng = getattr(project.magstripe_color, 'name_eng', '')
            magstripe_track_rus = getattr(project.magstripe_tracks, 'name_rus', '')
            magstripe_track_eng = getattr(project.magstripe_tracks, 'name_eng', '')

            magstripe_rus = (f"{magstripe_color_rus.lower()} магнитная полоса" if magstripe_color_rus else '') + (f" ({magstripe_track_rus.lower()})" if magstripe_track_rus else '')
            magstripe_eng = (f"{magstripe_color_eng.lower()} magstripe" if magstripe_color_eng else '') + (f" ({magstripe_track_eng.lower()})" if magstripe_track_eng else '')


            effects_rus = [effect.common_name_rus.lower() for effect in project.product_effects.all()]
            effects_eng = [effect.common_name_eng.lower() for effect in project.product_effects.all()]

            effects_rus_string = ', '.join(effects_rus) if effects_rus else ''
            effects_eng_string = ', '.join(effects_eng) if effects_eng else ''

            full_string_rus = ', '.join(part for part in [chip_full_name, chip_color_rus_with_label, material_rus, magstripe_rus, effects_rus_string] if part)
            full_string_eng = ', '.join(part for part in [chip_full_name, chip_color_eng_with_label, material_eng, magstripe_eng, effects_eng_string] if part)

            my_response = {
                "rus": full_string_rus,
                "eng": full_string_eng
            }

            return Response(my_response, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Ошибка получения данных'}, status=status.HTTP_400_BAD_REQUEST)
        
class ReportsNameSet(viewsets.ModelViewSet):
    
    queryset = Reports.objects.all()
    serializer_class = ReportsNameSerializer
    
class ReportSet(viewsets.ModelViewSet): 

    queryset = ProjectLine.objects.all()
    serializer_class = ReportSerializer

    def list(self, request, *args, **kwargs):
        queryset = super().get_queryset()
        query_params = request.query_params
        report_name = query_params.get('report_name')

        if report_name == 'MonthlyAccountingReport':
            queryset = queryset.filter(active=True, isProject = False)
            date_from = query_params.get('date_from')
            date_to = query_params.get('date_to')
            statuses = query_params.get('statuses')
            banks = query_params.get('banks')
            vendors = query_params.get('vendors')

            statuses_list = statuses.split(',') if statuses else []
            banks_list = banks.split(',') if banks else []
            vendors_list = vendors.split(',') if vendors else []
            date_from = None if date_from == "null" else date_from
            date_to = None if date_to == "null" else date_to

            if statuses_list:
                queryset = queryset.filter(general_line_status__in=statuses_list)
            if banks_list:
                queryset = queryset.filter(bank__in=banks_list)
            if vendors_list:
                queryset = queryset.filter(vendor__in=vendors_list)           

            queryset = queryset.select_related(
                'bank', 
                'vendor',
                'payment_system',
                'product_category',
            ).prefetch_related(
                Prefetch('productiondata_set'),
                Prefetch('annexesconditionsdata_set'),
                Prefetch('poconditionsdata_set'),
                Prefetch('bankprices_set'),
                Prefetch('vendorprices_set'),                
            ).annotate(
                payment_system_name=Coalesce(F('payment_system__name'), Value(None, output_field=CharField())),
                product_category_name=Coalesce(F('product_category__name'), Value(None, output_field=CharField())),
                unit_price_int_bank=Coalesce(F('bankprices__unit_price'), Value(None, output_field=FloatField())),
                main_currency_bank=Coalesce(F('bankprices__main_currency__name'), Value(None, output_field=CharField())),
                unit_price_bank=Case(
                    When(unit_price_int_bank__isnull=False, then=ExpressionWrapper(
                        Round(Round(F('unit_price_int_bank'), 3) + Value(0.0005), 2),
                        output_field=FloatField()
                    )),             
                    default=Value(None, output_field=FloatField())
                ),
                payment_plan_bank=Case(
                    When(unit_price_int_bank__isnull=False, product_qty_from_bank__isnull=False, then=ExpressionWrapper(
                        Round(Round(F('unit_price_bank') * F('product_qty_from_bank'), 3) + Value(0.0005), 2),
                        output_field=FloatField()
                    )),              
                    default=Value(None, output_field=FloatField())
                ),
                exchange_rates_bank_int=Coalesce(F('bankprices__exchange_rates'), Value(None, output_field=FloatField())),
                additional_currency_bank=Coalesce(F('bankprices__additional_currency__name'), Value(None, output_field=CharField())),
                unit_price_bank_additional=Case(
                    When(unit_price_int_bank__isnull=False, additional_currency_bank__isnull=False, exchange_rates_bank_int__isnull=False, then=ExpressionWrapper(
                        Round(Round(F('unit_price_bank') * F('exchange_rates_bank_int'), 3) + Value(0.0005), 2),
                        output_field=FloatField()
                    )),               
                    default=Value(None, output_field=FloatField())
                ),
                additional_payment_plan_bank=Case(
                    When(payment_plan_bank__isnull=False, exchange_rates_bank_int__isnull=False, then=ExpressionWrapper(
                            Round(Round(F('product_qty_from_bank') * F('unit_price_bank_additional'), 3) + Value(0.0005), 2),
                            output_field=FloatField()
                        )
                    ),
                    default=Value(None, output_field=FloatField())
                ),
                unit_price_int_vendor=Coalesce(F('vendorprices__unit_price'), Value(None, output_field=FloatField())),
                main_currency_vendor=Coalesce(F('vendorprices__main_currency__name'), Value(None, output_field=CharField())),
                unit_price_vendor=Case(
                    When(unit_price_int_vendor__isnull=False, then=ExpressionWrapper(
                        Round(Round(F('unit_price_int_vendor'), 3) + Value(0.0005), 2),
                        output_field=FloatField()
                    )), 
                ),
                payment_plan_vendor=Case(
                    When(unit_price_int_vendor__isnull=False, product_qty_to_vendor__isnull=False, then=ExpressionWrapper(
                        Round(Round(F('unit_price_vendor') * F('product_qty_to_vendor'), 3) + Value(0.0005), 2),
                        output_field=FloatField()
                    )),              
                    default=Value(None, output_field=FloatField())
                ),
                exchange_rates_vendor_int=Coalesce(F('vendorprices__exchange_rates'), Value(None, output_field=FloatField())),
                additional_currency_vendor=Coalesce(F('vendorprices__additional_currency__name'), Value(None, output_field=CharField())),
                unit_price_vendor_additional=Case(
                    When(unit_price_int_vendor__isnull=False, additional_currency_vendor__isnull=False, exchange_rates_vendor_int__isnull=False, then=ExpressionWrapper(
                        Round(Round(F('unit_price_vendor') * F('exchange_rates_vendor_int'), 3) + Value(0.0005), 2),
                        output_field=FloatField()
                    )),               
                    default=Value(None, output_field=FloatField())
                ),
                additional_payment_plan_vendor=Case(
                    When(payment_plan_vendor__isnull=False, exchange_rates_vendor_int__isnull=False, then=ExpressionWrapper(
                            Round(Round(F('product_qty_to_vendor') * F('unit_price_vendor_additional'), 3) + Value(0.0005), 2),
                            output_field=FloatField()
                        )
                    ),
                    default=Value(None, output_field=FloatField())
                ),
                month_plan=Coalesce(F('productiondata__month_plan'), Value(None, output_field=DateField())),
                date_plan=Coalesce(F('productiondata__date_plan'), Value(None, output_field=DateField())),
                country=F('bank__country__short_name'),
                contract=Coalesce(F('annexesconditionsdata__name'), Value('', output_field=CharField())),
                PO=Coalesce(F('poconditionsdata__name'), Value('', output_field=CharField()))
            ).order_by(
                'month_plan',
                'country',
                'bank',
                'contract'
            )

            if date_from is not None:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                date_from = get_start_of_month(date_from)
                queryset = queryset.filter(
                    Q(month_plan__isnull=True) | Q(month_plan__gte=date_from)
                )
            if date_to is not None:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                date_to = get_end_of_month(date_to)
                queryset = queryset.filter(
                    Q(month_plan__isnull=True) | Q(month_plan__lte=date_to)
                )

            def get_full_name(payment_system_name, product_category_name, product_name):
                product_name if product_name else None     
                return ' '.join(part for part in [payment_system_name, product_category_name, product_name] if part)

            for obj in queryset:
                if obj.month_plan is not None:
                    obj.month = format_month(obj.month_plan)
                else:
                    obj.month = ''

                obj.card_name = get_full_name(obj.payment_system_name, obj.product_category_name, obj.product_name)

                if obj.product_qty_from_bank is not None:
                    obj.bank_qty = f"{obj.product_qty_from_bank}"
                else:
                    obj.bank_qty = '' 

                if obj.product_qty_to_vendor is not None:
                    obj.vendor_qty = f"{obj.product_qty_to_vendor}"
                else:
                    obj.vendor_qty = ''  

                if obj.additional_currency_bank is not None:
                    obj.bank_currency = obj.additional_currency_bank
                elif obj.additional_currency_bank is None and obj.main_currency_bank is not None:
                    obj.bank_currency = obj.main_currency_bank
                else:
                    obj.bank_currency = ''

                if obj.additional_currency_vendor is not None:
                    obj.vendor_currency = obj.additional_currency_vendor
                elif obj.additional_currency_vendor is None and obj.main_currency_vendor is not None:
                    obj.vendor_currency = obj.main_currency_vendor
                else:
                    obj.vendor_currency = ''                   

                if obj.additional_payment_plan_bank is not None:
                    obj.bank_price = obj.additional_payment_plan_bank
                else:
                    if obj.payment_plan_bank is not None:
                        obj.bank_price = obj.payment_plan_bank
                    else:
                        obj.bank_price = ''   
                if obj.additional_payment_plan_vendor is not None:
                    obj.vendor_price = obj.additional_payment_plan_vendor
                else:
                    if obj.payment_plan_vendor is not None:
                        obj.vendor_price = obj.payment_plan_vendor
                    else:
                        obj.vendor_price = '' 

            lines_to_update = Reports.objects.filter(component_name='MonthlyAccountingReport')
            for line_to_update in lines_to_update:
                line_to_update.last_upload = timezone.now()
                line_to_update.save()

                post_save.send(sender=line_to_update.__class__, instance=line_to_update, request=request, request_exist=True)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Invalid report name'}, status=status.HTTP_400_BAD_REQUEST)


        