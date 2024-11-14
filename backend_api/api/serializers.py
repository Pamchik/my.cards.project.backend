from rest_framework import serializers


from ..models import (
    ProjectLine, 
    Banks,
    Vendors,
    Chips, 
    PaymentSystems, 
    ProductCategories, 
    ChipColors,
    ProductTypes,
    MaterialTypes,
    MaterialColors,
    MagstripeColors,
    MagstripeTracks,
    AntennaSizes,
    Effects,
    Countries,
    BankEmployees,
    VendorEmployees,
    PaymentSystemEmployees,
    ProcessList,
    ProcessData,
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

class GeneralProjectStatusesSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeneralProjectStatuses
        fields = '__all__'
        
class ProcessStatusesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessStatuses
        fields = '__all__'    
        
class FilesStatusesSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilesStatuses
        fields = '__all__'       

class CurrenciesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Currencies
        fields = '__all__'

class CountriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Countries
        fields = '__all__'

class BanksSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banks
        fields = '__all__' 
        
class VendorsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Vendors
        fields = '__all__'    

class EffectsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Effects
        fields = '__all__'

class EffectsMatchingSerializer(serializers.ModelSerializer):

    class Meta:
        model = EffectsMatching
        fields = '__all__'

class MagstripeColorsSerializer(serializers.ModelSerializer):

    class Meta:
        model = MagstripeColors
        fields = '__all__'       

class MagstripeTracksSerializer(serializers.ModelSerializer):

    class Meta:
        model = MagstripeTracks
        fields = '__all__'  
        
class AntennaSizesSerializer(serializers.ModelSerializer):

    class Meta:
        model = AntennaSizes
        fields = '__all__'  

class PaymentSystemsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PaymentSystems
        fields = '__all__'  
        
class ChipsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Chips
        fields = '__all__'        

class ProductCategoriesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductCategories
        fields = '__all__'

class ChipColorsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ChipColors
        fields = '__all__'

class ProductTypesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProductTypes
        fields = '__all__'
        
class MaterialTypesSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = MaterialTypes
        fields = '__all__'
        
class MaterialColorsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MaterialColors
        fields = '__all__'  

class BankEmployeesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BankEmployees
        fields = '__all__' 
        
class VendorEmployeesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VendorEmployees
        fields = '__all__'   
  
class VendorManufactureCountriesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VendorManufactureCountries
        fields = '__all__'   
              
class ProjectLineSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProjectLine
        fields = '__all__' 

class ProjectLineTableSerializer(serializers.ModelSerializer):
    
    bank = serializers.CharField(source='bank.name_eng', read_only=True)
    bank_employee = serializers.CharField(source='bank_employee.name', read_only=True)
    country = serializers.CharField(source='bank.country.short_name', read_only=True)
    general_line_status = serializers.CharField(source='general_line_status.name', read_only=True)
    vendor = serializers.CharField(source='vendor.name', read_only=True)
    vendor_employee = serializers.CharField(source='vendor_employee.name', read_only=True)
    vendor_manufacture_country = serializers.CharField(source='vendor_manufacture_country.name', read_only=True)
    product_type = serializers.CharField(source='product_type.name_rus', read_only=True)
    product_name = serializers.CharField(read_only=True)
    payment_system = serializers.CharField(source='payment_system.name', read_only=True)
    product_category = serializers.CharField(source='product_category.name', read_only=True)
    product_full_name = serializers.CharField(read_only=True)
    chip = serializers.CharField(source='chip.short_name', read_only=True)
    applet = serializers.CharField(source='applet.name', read_only=True)
    chip_full_name = serializers.CharField(read_only=True)
    chip_color = serializers.CharField(source='chip_color.name_rus', read_only=True)
    mifare = serializers.CharField(source='mifare.name', read_only=True)
    antenna_size = serializers.CharField(source='antenna_size.name_rus', read_only=True)   
    magstripe_color = serializers.CharField(source='magstripe_color.name_rus', read_only=True) 
    magstripe_tracks = serializers.CharField(source='magstripe_tracks.name_rus', read_only=True) 
    material_type = serializers.CharField(source='material_type.name_rus', read_only=True) 
    material_color = serializers.CharField(source='material_color.name_rus', read_only=True) 
    lamination_face = serializers.CharField(source='lamination_face.name_rus', read_only=True) 
    lamination_back = serializers.CharField(source='lamination_back.name_rus', read_only=True) 
    product_effects = serializers.SerializerMethodField()
    product_effects_common = serializers.SerializerMethodField()
    product_effects_qty = serializers.SerializerMethodField()
    product_qty_from_bank = serializers.CharField(read_only=True)
    product_qty_to_vendor = serializers.CharField(read_only=True)
    fact_qty_vendor = serializers.CharField(read_only=True)
    fact_qty_bank = serializers.CharField(read_only=True)
    lead_time_bank = serializers.CharField(read_only=True)
    deviation_bank = serializers.CharField(read_only=True)
    lead_time_vendor = serializers.CharField(read_only=True)
    deviation_vendor = serializers.CharField(read_only=True)
    unit_price_bank = serializers.CharField(read_only=True)
    exchange_rates_bank = serializers.CharField(read_only=True)
    unit_price_bank_additional = serializers.CharField(read_only=True)
    prepaid_percent_bank = serializers.CharField(read_only=True)
    postpaid_percent_bank = serializers.CharField(read_only=True)
    unit_price_vendor = serializers.CharField(read_only=True)
    unit_price_vendor_additional = serializers.CharField(read_only=True)
    prepaid_percent_vendor = serializers.CharField(read_only=True)
    postpaid_percent_vendor = serializers.CharField(read_only=True)
    prepaid_value_bank = serializers.CharField(read_only=True)
    postpaid_value_bank = serializers.CharField(read_only=True)
    prepaid_value_vendor = serializers.CharField(read_only=True)
    postpaid_value_vendor = serializers.CharField(read_only=True)
    payment_plan_bank = serializers.CharField(read_only=True)
    additional_payment_plan_bank = serializers.CharField(read_only=True)
    payment_plan_vendor = serializers.CharField(read_only=True)
    additional_payment_plan_vendor = serializers.CharField(read_only=True)
    payment_fact_bank = serializers.CharField(read_only=True)
    payment_fact_vendor = serializers.CharField(read_only=True)
    payment_system_data = serializers.CharField(read_only=True)
    approval_date = serializers.CharField(read_only=True)
    month_plan = serializers.CharField(read_only=True)
    date_plan = serializers.CharField(read_only=True)
    date_client = serializers.CharField(read_only=True)
    date_fact = serializers.CharField(read_only=True)
    created_date = serializers.CharField(read_only=True)

    def get_product_effects(self, obj):
        return [f"- {effect.name_rus}" for effect in obj.product_effects.all()]

    def get_product_effects_common(self, obj):
        return [f"- {effect.common_name_rus}" for effect in obj.product_effects.all()]

    def get_product_effects_qty(self, obj):
        return f"{obj.product_effects_qty} шт."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_steps = list(ProcessList.objects.values_list('id', flat=True))
        
        for step in all_steps:
            self.fields[f'process_step_status_{step}'] = serializers.CharField(allow_null=True, required=False)
            self.fields[f'process_step_comment_{step}'] = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = ProjectLine
        fields = '__all__'

    def get_queryset(self):
        queryset = ProjectLine.objects.select_related(
            'bank', 
            'bank_employee',
            'general_line_status',
            'vendor',
            'vendor_employee',
            'vendor_manufacture_country',
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
        ).prefetch_related('product_effects')

        return queryset

class PaymentSystemEmployeesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PaymentSystemEmployees
        fields = '__all__' 

class ProcessListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProcessList
        fields = '__all__' 

class ProcessDataSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProcessData
        fields = '__all__' 

class BankPricesSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankPrices
        fields = '__all__'  
               
class VendorPricesSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorPrices
        fields = '__all__'

class FilesFormatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilesFormats
        fields = '__all__'

class FilesTypeNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilesTypeName
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'

class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = '__all__'

class FilesTableSerializer(serializers.ModelSerializer):
    process_step = serializers.CharField(source='process_step.component_name', read_only=True)
    status = serializers.CharField(source='status.name', read_only=True)

    class Meta:
        model = Files
        fields = '__all__'

    def get_queryset(self):
        queryset = Files.objects.select_related(
            'process_step',
            'status',
        )

        return queryset

class BanksBIDsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BanksBIDs
        fields = '__all__'

class PaymentSystemApprovalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSystemApprovals
        fields = '__all__'

class KeyExchangeStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyExchangeStatuses
        fields = '__all__'

class KeyExchangeProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyExchangeProjects
        fields = '__all__'

class KeyExchangeTableProjectsSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='status.name', read_only=True)
    bank = serializers.CharField(source='bank.name_eng', read_only=True)
    bank_KMC_name = serializers.CharField(source='bank_KMC_name.name', read_only=True, default=None)
    vendor = serializers.CharField(source='vendor.name', read_only=True)
    vendor_origin = serializers.CharField(source='vendor_origin.name', read_only=True, default=None)
    vendor_KMC_name = serializers.CharField(source='vendor_KMC_name.name', read_only=True, default=None)
    vendor_consultant = serializers.CharField(source='vendor_consultant.name', read_only=True, default=None)
    request_date = serializers.CharField(read_only=True)

    class Meta:
        model = KeyExchangeProjects
        fields = '__all__'

    def get_queryset(self):
        queryset = KeyExchangeProjects.objects.select_related(
            'status', 
            'bank',
            'bank_KMC_name',
            'vendor', 
            'vendor_origin', 
            'vendor_KMC_name',
            'vendor_consultant'
        )

        return queryset

class CardTestingProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardTestingProjects
        fields = '__all__'

class CardTestingTableProjectsSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='status.name', read_only=True)
    bank = serializers.CharField(source='bank.name_eng', read_only=True)
    vendor = serializers.CharField(source='vendor.name', read_only=True)
    vendor_origin = serializers.CharField(source='vendor_origin.name', read_only=True, default=None)
    chip = serializers.CharField(source='chip.short_name', read_only=True, default=None)
    applet = serializers.CharField(source='applet.name', read_only=True, default=None)
    mifare = serializers.CharField(source='mifare.name', read_only=True, default=None)
    product_type = serializers.CharField(source='product_type.name_rus', read_only=True, default=None)
    type_card = serializers.CharField(source='type_card.name', read_only=True, default=None)
    KCV = serializers.CharField(source='KCV.name', read_only=True, default=None)
    antenna_size = serializers.CharField(source='antenna_size.name_rus', read_only=True, default=None)
    material_type = serializers.CharField(source='material_type.name_rus', read_only=True, default=None)
    material_color = serializers.CharField(source='material_color.name_rus', read_only=True, default=None)
    magstripe_color = serializers.CharField(source='magstripe_color.name_rus', read_only=True, default=None)
    magstripe_tracks = serializers.CharField(source='magstripe_tracks.name_rus', read_only=True, default=None)
    lamination_face = serializers.CharField(source='lamination_face.name_rus', read_only=True, default=None)
    lamination_back = serializers.CharField(source='lamination_back.name_rus', read_only=True, default=None)
    signed_by = serializers.CharField(source='signed_by.name', read_only=True, default=None)
    received = serializers.IntegerField(read_only=True)
    sent = serializers.IntegerField(read_only=True)
    on_stock = serializers.IntegerField(read_only=True)
    request_date = serializers.CharField(read_only=True)

    class Meta:
        model = CardTestingProjects
        fields = '__all__'

    def get_queryset(self):
        queryset = CardTestingProjects.objects.select_related(
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

        return queryset

class CardTestingStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardTestingStatuses
        fields = '__all__'

class TestCardTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCardTypes
        fields = '__all__'

class TestCardTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCardTransfer
        fields = '__all__'

class TransferActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferActions
        fields = '__all__'

class ProcessingCentersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingCenters
        fields = '__all__'

class PesroScriptVendorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PesroScriptVendors
        fields = '__all__'

class LaminationTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaminationTypes
        fields = '__all__'

class PaymentTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTypes
        fields = '__all__'

class PaymentsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentsInfo
        fields = '__all__'

class PaymentsInfoTableSerializer(serializers.ModelSerializer):
    currency = serializers.CharField(source='currency.name', read_only=True)
    payment_type = serializers.CharField(source='payment_type.name', read_only=True)
    payment_value = serializers.CharField(read_only=True)

    class Meta:
        model = PaymentsInfo
        fields = '__all__'

    def get_queryset(self):
        queryset = PaymentsInfo.objects.select_related(
            'currency',
            'payment_type',
        )

        return queryset   

class DeliveriesInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveriesInfo
        fields = '__all__'

class DeliveriesInfoTableSerializer(serializers.ModelSerializer):
    quantity = serializers.CharField(read_only=True)

    class Meta:
        model = DeliveriesInfo
        fields = '__all__'

class MifareTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MifareTypes
        fields = '__all__'

class AppletTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppletTypes
        fields = '__all__'

class StartYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartYear
        fields = '__all__'

class ShortProjectLineSerializer(serializers.ModelSerializer):
    
    bank = serializers.CharField(source='bank.name_eng', read_only=True)
    vendor = serializers.CharField(source='vendor.name', read_only=True)
    product_full_name = serializers.CharField(read_only=True)
    chip_full_name = serializers.CharField(read_only=True)
    product_type = serializers.CharField(source='product_type.name_rus', read_only=True)

    class Meta:
        model = ProjectLine
        fields = ('id', 'number', 'bank', 'vendor', 'product_type', 'product_full_name', 'chip_full_name', 'display_year')

    def get_queryset(self):
        queryset = ProjectLine.objects.select_related(
            'bank', 
            'vendor',
            'payment_system',
            'product_category',
            'chip',
            'applet',
            'mifare',
        )

        return queryset


class ProductionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionData
        fields = '__all__' 

class CardTestingShortRelevantLineSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CardTestingProjects
        fields = '__all__'

class AnnexesConditionsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnexesConditionsData
        fields = '__all__'

class POConditionsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = POConditionsData
        fields = '__all__'

class MonthListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthList
        fields = '__all__'

class ReportsNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reports
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):

    month = serializers.CharField(read_only=True)
    country = serializers.CharField(read_only=True)
    bank = serializers.CharField(source='bank.name_eng', read_only=True)
    vendor = serializers.CharField(source='vendor.name', read_only=True)
    card_name = serializers.CharField(read_only=True)
    contract = serializers.CharField(read_only=True)
    PO = serializers.CharField(read_only=True)
    bank_qty = serializers.CharField(read_only=True)
    vendor_qty = serializers.CharField(read_only=True)
    bank_currency = serializers.CharField(read_only=True)
    bank_price = serializers.CharField(read_only=True)
    vendor_currency = serializers.CharField(read_only=True)
    vendor_price = serializers.CharField(read_only=True)

    class Meta:
        model = ProjectLine
        fields = (
            'month',
            'country',
            'bank',
            'vendor',
            'card_name',
            'contract',
            'PO',
            'bank_qty',
            'vendor_qty',
            'bank_currency',
            'bank_price',
            'vendor_currency',
            'vendor_price'
        )
        