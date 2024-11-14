import os
import re
from django.db import models
import datetime
from functools import partial

def get_year():
    return str(datetime.datetime.now().year)

def get_default_status(model_class):
    if model_class.objects.filter(id=1).exists():
        return 1
    else:
        return None

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def upload_Preview(instance, filename):
    main_folder = 'Заказы/Превью'
    name, extension = filename.rsplit(".", 1) if "." in filename else (filename, "")
    country = instance.bank.country.name_rus
    bank_name = instance.bank.name_eng
    payment_system_name = getattr(instance.payment_system, 'name', None)
    product_category_name = getattr(instance.product_category, 'name', None)  
    product_name = instance.product_name

    full_product_name = ''
    if bank_name:
        full_product_name += bank_name   
    if payment_system_name:
        full_product_name += " " + payment_system_name
    if product_category_name:
        full_product_name += " " + product_category_name
    if product_name:
        full_product_name += " " + product_name

    full_product_name = f'{full_product_name}.{extension}'
    file_name = f'{sanitize_filename(country)}\{sanitize_filename(bank_name)}\{sanitize_filename(full_product_name)}'
    return os.path.join(main_folder, file_name)


class MonthList(models.Model):
    number = models.IntegerField(null=False, blank=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    name_roditelskiy_padezh = models.CharField(max_length=255, null=True, blank=True)

class Countries(models.Model):
    short_name = models.CharField(max_length=255, null=False, blank=False)
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)

class ProcessingCenters(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(null=False, blank=False, default=True)
    other = models.TextField(null=True, blank=True)

class PesroScriptVendors(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(null=False, blank=False, default=True)
    other = models.TextField(null=True, blank=True)

class Vendors(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(null=False, blank=False, default=True)
    other = models.TextField(null=True, blank=True)

class VendorEmployees(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)

class VendorManufactureCountries(models.Model):
    name = models.CharField(max_length=255)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)
    other = models.TextField(null=True, blank=True)

class Banks(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    full_name_eng = models.CharField(max_length=255, null=True, blank=True)
    full_name_rus = models.CharField(max_length=255, null=True, blank=True)
    address_eng = models.CharField(max_length=255, null=True, blank=True)
    address_rus = models.CharField(max_length=255, null=True, blank=True)
    country = models.ForeignKey(Countries, on_delete=models.CASCADE, null=False, blank=False)
    processing = models.ForeignKey(ProcessingCenters, on_delete=models.CASCADE, null=True, blank=True)
    pesro_script_vendor = models.ForeignKey(PesroScriptVendors, on_delete=models.CASCADE, null=True, blank=True)
    tolerance = models.IntegerField(null=True, blank=True)
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=True, blank=True, default=True)

class BankEmployees(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    bank = models.ForeignKey(Banks, on_delete=models.CASCADE, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)

class BanksBIDs(models.Model):
    number = models.IntegerField(null=False, blank=False)
    bank = models.ForeignKey(Banks, on_delete=models.CASCADE, null=False, blank=False)
    active = models.BooleanField(default=True, null=False, blank=False)
    other = models.TextField(null=True, blank=True)

class PaymentSystems(models.Model):
    name = models.CharField(max_length=255)    
    active = models.BooleanField(null=False, blank=False, default=True)
    other = models.TextField(null=True, blank=True)
    
class PaymentSystemEmployees(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    ps = models.ForeignKey(PaymentSystems, on_delete=models.CASCADE, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)

class AntennaSizes(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)

class ChipColors(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)

class MifareTypes(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)
    other = models.TextField(null=True, blank=True)

class AppletTypes(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    short_name = models.CharField(max_length=255, null=False, blank=False)
    payment_system = models.ForeignKey(PaymentSystems, on_delete=models.CASCADE)
    active = models.BooleanField(null=False, blank=False, default=True)
    other = models.TextField(null=True, blank=True)

class Chips(models.Model):
    short_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    # test_key = models.ForeignKey(TestKeys, on_delete=models.CASCADE, null=True)
    kmc_test = models.CharField(max_length=255, null=True, blank=True)
    kcv_test = models.CharField(max_length=255, null=True, blank=True)    
    # payment_system = models.ForeignKey(PaymentSystems, on_delete=models.CASCADE, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)
    mifare_available = models.ManyToManyField(MifareTypes, blank=True, null=True)
    applet_available = models.ManyToManyField(AppletTypes, blank=True, null=True)

class GeneralProjectStatuses(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(null=False, blank=False, default=True)

class ProcessStatuses(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)

class FilesStatuses(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(null=False, blank=False, default=True)

class ProductTypes(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)

class MaterialTypes(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    product_type = models.ForeignKey(ProductTypes, on_delete=models.CASCADE, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)
    
class MaterialColors(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    material_type = models.ForeignKey(MaterialTypes, on_delete=models.CASCADE, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)
 
class MagstripeTracks(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)

class MagstripeColors(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    magstripe_tracks = models.ForeignKey(MagstripeTracks, on_delete=models.CASCADE, null=False, blank=False)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)

class LaminationTypes(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, null=False, blank=False)
    active = models.BooleanField(null=False, blank=False, default=True)    

class Effects(models.Model):
    name_eng = models.CharField(max_length=255, null=False, blank=False)
    name_rus = models.CharField(max_length=255, null=False, blank=False)
    common_name_eng = models.CharField(max_length=255, null=False, blank=False)
    common_name_rus = models.CharField(max_length=255, null=False, blank=False)
    product_type = models.ForeignKey(ProductTypes, on_delete=models.CASCADE, null=False, blank=False) 
    other = models.TextField(null=True, blank=True)   
    active = models.BooleanField(null=False, blank=False, default=True)
    
class EffectsMatching(models.Model):
    effect = models.ForeignKey(Effects, on_delete=models.CASCADE, null=False, blank=False, related_name='effect_name')
    matches = models.ManyToManyField(Effects, blank=True, null=True, related_name='matches')
    mismatches = models.ManyToManyField(Effects, blank=True, null=True, related_name='mismatches')
    
class ProductCategories(models.Model):
    name = models.CharField(max_length=255)
    payment_system = models.ForeignKey(PaymentSystems, on_delete=models.CASCADE, null=False, blank=False)
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)

class Currencies(models.Model):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=255, default='null')
    active = models.BooleanField(null=False, blank=False, default=True)

class ProcessList(models.Model):
    url_name = models.CharField(max_length=255)
    component_name = models.CharField(max_length=255)
    position_number = models.IntegerField()

class ProjectLine(models.Model):
        
    number = models.SlugField(unique=True, blank=True, null=True)
    general_line_status = models.ForeignKey(
        GeneralProjectStatuses,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=partial(get_default_status, GeneralProjectStatuses)
    )
    bank = models.ForeignKey(Banks, on_delete=models.CASCADE, null=False, blank=False)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, null=False, blank=False)
    bank_employee = models.ForeignKey(BankEmployees, on_delete=models.CASCADE, blank=True, null=True)
    vendor_employee = models.ForeignKey(VendorEmployees, on_delete=models.CASCADE, blank=True, null=True)    
    vendor_manufacture_country = models.ForeignKey(VendorManufactureCountries, on_delete=models.CASCADE, blank=True, null=True)  
    product_type = models.ForeignKey(ProductTypes, on_delete=models.CASCADE, null=False, blank=False)
    payment_system = models.ForeignKey(PaymentSystems, on_delete=models.CASCADE, null=False, blank=False)
    product_category = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    product_code = models.CharField(max_length=255, blank=True, null=True) 
    product_revision = models.CharField(max_length=255, blank=True, null=True) 
    product_qty_from_bank = models.IntegerField(blank=True, null=True)
    product_qty_to_vendor = models.IntegerField(blank=True, null=True)
    chip = models.ForeignKey(Chips, on_delete=models.CASCADE, blank=True, null=True)
    applet = models.ForeignKey(AppletTypes, on_delete=models.CASCADE, null=True, blank=True)
    chip_color = models.ForeignKey(ChipColors, on_delete=models.CASCADE, blank=True, null=True)
    mifare = models.ForeignKey(MifareTypes, on_delete=models.CASCADE, blank=True, null=True)
    mifare_access_key = models.CharField(max_length=255, blank=True, null=True)  
    antenna_size = models.ForeignKey(AntennaSizes, on_delete=models.CASCADE, blank=True, null=True)
    material_type = models.ForeignKey(MaterialTypes, on_delete=models.CASCADE, blank=True, null=True)
    material_color = models.ForeignKey(MaterialColors, on_delete=models.CASCADE, blank=True, null=True)    
    magstripe_color = models.ForeignKey(MagstripeColors, on_delete=models.CASCADE, blank=True, null=True)  
    magstripe_tracks = models.ForeignKey(MagstripeTracks, on_delete=models.CASCADE, blank=True, null=True) 
    lamination_face = models.ForeignKey(LaminationTypes, on_delete=models.CASCADE, blank=True, null=True, related_name="lamination_face") 
    lamination_back = models.ForeignKey(LaminationTypes, on_delete=models.CASCADE, blank=True, null=True, related_name="lamination_back") 
    product_effects = models.ManyToManyField(Effects, blank=True, null=True)
    bank_communication = models.TextField(blank=True, null=True)
    vendor_communication = models.TextField(blank=True, null=True) 
    general_comment = models.TextField(blank=True, null=True) 
    display_year = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(null=False, blank=False, default=True)
    preview_image = models.FileField(max_length=250, upload_to=upload_Preview, blank=True, null=True)    
    isUrgent = models.BooleanField(null=False, blank=False, default=False)
    isProject = models.BooleanField(null=False, blank=False, default=True)

    def __str__(self):
        return f"{self.bank.name_eng} {self.payment_system.name} {self.product_name}"
    
    def save(self, *args, **kwargs):
        if not self.display_year:
            self.display_year = datetime.datetime.now().year

        if self.mifare:
            if not self.mifare_access_key:
                self.mifare_access_key = "Virgin (FFF…)"
        else:
            self.mifare_access_key = None

        if self.general_line_status.name == "Проект":
            self.isProject = True
            self.number = None
        elif self.general_line_status.name == "В архиве":
            self.isProject = False   
        else:
            self.isProject = False
            if not self.number:
                latest_number = ProjectLine.objects.aggregate(models.Max('number'))['number__max']
                new_number = 1 if not latest_number else int(latest_number[1:]) + 1
                self.number = f'O{new_number:05d}'

        if self.general_line_status.name == "В архиве":
            self.active = False
        else:
            self.active = True

        super(ProjectLine, self).save(*args, **kwargs)
   
class BankPrices(models.Model):
    line_number = models.ForeignKey(ProjectLine, on_delete=models.CASCADE, blank=False, null=False)   
    unit_price = models.FloatField(blank=True, null=True)
    main_currency = models.ForeignKey(Currencies, on_delete=models.CASCADE, blank=True, null=True, related_name='bank_main_currency')    
    additional_currency = models.ForeignKey(Currencies, on_delete=models.CASCADE, blank=True, null=True, related_name='bank_additional_currency')    
    exchange_rates = models.FloatField(blank=True, null=True)    
    exchange_rates_by_bank = models.ForeignKey(Banks, on_delete=models.CASCADE, blank=True, null=True)    
    exchange_rates_by_date = models.DateField(blank=True, null=True)
    payment_сurrency = models.ForeignKey(Currencies, on_delete=models.CASCADE, blank=True, null=True, related_name='bank_payment_сurrency')  
    prepaid_percent = models.IntegerField(blank=True, null=True) 
        
class VendorPrices(models.Model):
    line_number = models.ForeignKey(ProjectLine, on_delete=models.CASCADE, blank=False, null=False)    
    unit_price = models.FloatField(blank=True, null=True)
    main_currency = models.ForeignKey(Currencies, on_delete=models.CASCADE, blank=True, null=True, related_name='vendor_main_currency')  
    additional_currency = models.ForeignKey(Currencies, on_delete=models.CASCADE, blank=True, null=True, related_name='vendor_additional_currency')    
    exchange_rates = models.FloatField(blank=True, null=True)    
    exchange_rates_by_bank = models.ForeignKey(Banks, on_delete=models.CASCADE, blank=True, null=True)    
    exchange_rates_by_date = models.DateField(blank=True, null=True)
    payment_сurrency = models.ForeignKey(Currencies, on_delete=models.CASCADE, blank=True, null=True, related_name='vendor_payment_сurrency')  
    prepaid_percent = models.IntegerField(blank=True, null=True)     
    epson_proof_cost = models.FloatField(blank=True, null=True)
    payment_system_approval_cost = models.FloatField(blank=True, null=True)
    certificate_of_origin_cost = models.FloatField(blank=True, null=True)

class PaymentTypes(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(null=False, blank=False, default=True)

class PaymentsInfo(models.Model):
    line_number = models.ForeignKey(ProjectLine, on_delete=models.CASCADE, blank=False, null=False)  
    company_type = models.CharField(max_length=255, blank=False, null=False)    
    currency = models.ForeignKey(Currencies, on_delete=models.CASCADE, blank=False, null=False)
    payment_type = models.ForeignKey(PaymentTypes, on_delete=models.CASCADE, blank=False, null=False)
    payment_value = models.FloatField(blank=False, null=False)
    payment_date = models.DateField(blank=False, null=False)
    other = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(null=False, blank=False, default=False)

class ProcessData(models.Model):
    line_number = models.ForeignKey(ProjectLine, null=False, blank=False, on_delete=models.CASCADE)
    process_step = models.ForeignKey(ProcessList, null=False, blank=False, on_delete=models.CASCADE)
    step_status = models.ForeignKey(
        ProcessStatuses,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=partial(get_default_status, ProcessStatuses)
    )
    step_comment = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super(ProcessData, self).save(*args, **kwargs)

class FilesTypeName(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True) 

class FilesFormats(models.Model):
    name = models.ForeignKey(FilesTypeName, blank=False, null=False, on_delete=models.CASCADE) 
    file_extension = models.CharField(max_length=255, blank=False, null=False)
    available_for_image_gallery = models.BooleanField(blank=False, null=False, default=False)
    available_for_video_gallery = models.BooleanField(blank=False, null=False, default=False)
    available_for_file_gallery = models.BooleanField(blank=False, null=False, default=False)
    # icon = 
    
class Gallery(models.Model):
    file = models.CharField(max_length=2000)
    folder_name = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    file_extension = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=255, blank=True, null=True)
    preview_image = models.CharField(max_length=2000, blank=True, null=True)
    created_date = models.DateTimeField() 
    model_type = models.CharField(max_length=255, blank=False, null=False)
    number = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(null=True, blank=True) 
    deleted = models.BooleanField(null=False, blank=False, default=False)
    other = models.TextField(null=True, blank=True) 
    
class Files(models.Model):
    file = models.CharField(max_length=2000)
    folder_name = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    file_extension = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField()
    model_type = models.CharField(max_length=255, blank=False, null=False)
    number = models.IntegerField(blank=True, null=True)
    process_step = models.ForeignKey(ProcessList, null=True, blank=True, on_delete=models.CASCADE)
    status = models.ForeignKey(
        FilesStatuses,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=partial(get_default_status, FilesStatuses)
    )
    received_from = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(null=False, blank=False, default=True)
    deleted = models.BooleanField(null=False, blank=False, default=False)
    other = models.TextField(null=True, blank=True)

class PaymentSystemApprovals(models.Model):
    line_number = models.ForeignKey(ProjectLine, on_delete=models.CASCADE, null=False, blank=False)
    number = models.CharField(max_length=255, null=True, blank=True)
    bid = models.ForeignKey(BanksBIDs, on_delete=models.CASCADE, null=True, blank=True)
    bin = models.CharField(max_length=255, null=True, blank=True)
    range_low = models.CharField(max_length=255, null=True, blank=True)
    range_high = models.CharField(max_length=255, null=True, blank=True)
    program_name = models.CharField(max_length=255, null=True, blank=True)
    full_name_in_ps = models.CharField(max_length=255, null=True, blank=True)
    other = models.TextField(null=True, blank=True)
    is_requested = models.BooleanField(blank=True, null=True)
    requested_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    posted_date = models.DateField(null=True, blank=True)
    approval_date = models.DateField(blank=True, null=True) 

    def save(self, *args, **kwargs):
        
        if self.requested_date:
            self.is_requested = True
        else:
            self.is_requested = False

        super().save(*args, **kwargs)    

class KeyExchangeStatuses(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(null=False, blank=False, default=True)
    
class KeyExchangeProjects(models.Model):
    number = models.SlugField(unique=True, blank=True, null=True)
    status = models.ForeignKey(KeyExchangeStatuses, on_delete=models.CASCADE, null=True, blank=True, default=partial(get_default_status, KeyExchangeStatuses))
    # display_year = models.IntegerField(blank=True, null=True)
    request_date = models.DateField(blank=True, null=True)   
    bank = models.ForeignKey(Banks, on_delete=models.CASCADE, null=False, blank=False)
    bank_KMC_name = models.ForeignKey(BankEmployees, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, null=False, blank=False)
    vendor_origin = models.ForeignKey(VendorManufactureCountries, on_delete=models.CASCADE, null=True, blank=True)
    vendor_KMC_name = models.ForeignKey(VendorEmployees, on_delete=models.CASCADE, null=True, blank=True, related_name='vendor_KMC_name')
    KCV = models.CharField(max_length=50, blank=True, null=True)
    key_label = models.CharField(max_length=50, blank=True, null=True)
    vendor_consultant = models.ForeignKey(VendorEmployees, on_delete=models.CASCADE, null=True, blank=True, related_name='vendor_consultant')
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)
    isUrgent = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return f"{self.number}"
    
    def save(self, *args, **kwargs):
        if not self.number:
            latest_number = KeyExchangeProjects.objects.aggregate(models.Max('number'))['number__max']
            new_number = 1 if not latest_number else int(latest_number[1:]) + 1
            self.number = f'K{new_number:05d}'
        
        super(KeyExchangeProjects, self).save(*args, **kwargs)

class CardTestingStatuses(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(null=False, blank=False, default=True)
    
class TestCardTypes(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(null=False, blank=False, default=True)

class CardTestingProjects(models.Model):
    number = models.SlugField(unique=True, blank=True, null=True)
    status = models.ForeignKey(CardTestingStatuses, on_delete=models.CASCADE, null=True, blank=True, default=partial(get_default_status, CardTestingStatuses))
    type_card = models.ForeignKey(TestCardTypes, on_delete=models.CASCADE, null=True, blank=True, default=partial(get_default_status, TestCardTypes))
    KCV = models.ForeignKey(KeyExchangeProjects, on_delete=models.CASCADE, null=True, blank=True)
    # display_year = models.IntegerField(blank=True, null=True)
    request_date = models.DateField(blank=True, null=True)   
    is_for_bank = models.BooleanField(null=False, blank=False, default=False)
    bank = models.ForeignKey(Banks, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(Vendors, on_delete=models.CASCADE, null=False, blank=False)
    vendor_origin = models.ForeignKey(VendorManufactureCountries, on_delete=models.CASCADE, null=True, blank=True)
    vendor_consultant = models.ForeignKey(VendorEmployees, on_delete=models.CASCADE, null=True, blank=True)
    chip = models.ForeignKey(Chips, on_delete=models.CASCADE, null=True, blank=True)
    applet = models.ForeignKey(AppletTypes, on_delete=models.CASCADE, null=True, blank=True)
    mifare = models.ForeignKey(MifareTypes, on_delete=models.CASCADE, blank=True, null=True)
    mifare_access_key = models.CharField(max_length=255, blank=True, null=True)  
    antenna_size = models.ForeignKey(AntennaSizes, on_delete=models.CASCADE, blank=True, null=True)
    product_type = models.ForeignKey(ProductTypes, on_delete=models.CASCADE, blank=False, null=False)
    material_type = models.ForeignKey(MaterialTypes, on_delete=models.CASCADE, blank=True, null=True)
    material_color = models.ForeignKey(MaterialColors, on_delete=models.CASCADE, blank=True, null=True)    
    magstripe_color = models.ForeignKey(MagstripeColors, on_delete=models.CASCADE, blank=True, null=True)  
    magstripe_tracks = models.ForeignKey(MagstripeTracks, on_delete=models.CASCADE, blank=True, null=True) 
    lamination_face = models.ForeignKey(LaminationTypes, on_delete=models.CASCADE, blank=True, null=True, related_name="cardtestingprojects_lamination_face") 
    lamination_back = models.ForeignKey(LaminationTypes, on_delete=models.CASCADE, blank=True, null=True, related_name="cardtestingprojects_lamination_back") 
    requested_quantity = models.IntegerField(blank=True, null=True)
    input_code = models.CharField(max_length=100, blank=True, null=True)
    signed_form_date = models.DateField(blank=True, null=True)
    signed_by = models.ForeignKey(BankEmployees, on_delete=models.CASCADE, null=True, blank=True)
    other = models.TextField(null=True, blank=True)
    active = models.BooleanField(null=False, blank=False, default=True)
    isUrgent = models.BooleanField(null=False, blank=False, default=False)
    based_on = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.number}"
    
    def save(self, *args, **kwargs):
        if not self.number:
            latest_number = CardTestingProjects.objects.aggregate(models.Max('number'))['number__max']
            new_number = 1 if not latest_number else int(latest_number[1:]) + 1
            self.number = f'T{new_number:05d}'
        
        if self.mifare:
            if not self.mifare_access_key:
                self.mifare_access_key = "Virgin (FFF…)"
        else:
            self.mifare_access_key = None

        super(CardTestingProjects, self).save(*args, **kwargs)

class TransferActions(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(null=False, blank=False, default=True)

class TestCardTransfer(models.Model):
    card_testing_project = models.ForeignKey(CardTestingProjects, on_delete=models.CASCADE, null=False, blank=False, related_name='card_testing_project')
    action = models.ForeignKey(TransferActions, on_delete=models.CASCADE, null=False, blank=False)
    is_for_bank = models.BooleanField(null=False, blank=False, default=False)
    recipient = models.ForeignKey(BankEmployees, on_delete=models.CASCADE, null=True, blank=True)
    transfer_date = models.DateField(blank=True, null=True)
    transfer_quantity = models.IntegerField(blank=False, null=False)
    other = models.TextField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(null=False, blank=False, default=False)

class DeliveriesInfo(models.Model):
    line_number = models.ForeignKey(ProjectLine, on_delete=models.CASCADE, blank=False, null=False)  
    company_type = models.CharField(max_length=255, blank=False, null=False)    
    quantity = models.IntegerField(blank=False, null=False)
    date = models.DateField(blank=False, null=False)
    other = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(null=False, blank=False, default=False)

class StartYear(models.Model):
    year_number = models.IntegerField(blank=False, null=False)

class ProductionData(models.Model):
    line_number = models.ForeignKey(ProjectLine, on_delete=models.CASCADE, null=False, blank=False)
    month_plan = models.DateField(blank=True, null=True)
    date_plan = models.DateField(blank=True, null=True)
    date_client = models.DateField(blank=True, null=True)
    date_fact = models.DateField(blank=True, null=True)
    other = models.TextField(null=True, blank=True)

class AnnexesConditionsData(models.Model):
    line_number = models.ForeignKey(ProjectLine, on_delete=models.CASCADE, null=False, blank=False)
    deviation_min = models.IntegerField(blank=True, null=True)
    deviation_max = models.IntegerField(blank=True, null=True)
    lead_time_min = models.IntegerField(blank=True, null=True)
    lead_time_max = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

class POConditionsData(models.Model):
    line_number = models.ForeignKey(ProjectLine, on_delete=models.CASCADE, null=False, blank=False)
    deviation_min = models.IntegerField(blank=True, null=True)
    deviation_max = models.IntegerField(blank=True, null=True)
    lead_time = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

class Reports(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.CharField(max_length=2000, blank=True, null=True)
    last_upload = models.DateTimeField(blank=True, null=True)
    component_name = models.CharField(max_length=100, blank=False, null=False)
    active = models.BooleanField(null=False, blank=False, default=True)
