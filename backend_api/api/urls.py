from rest_framework import routers

from .views import (
    ProjectLineViewSet, 
    ProjectLineTableViewSet,
    BanksSet,
    VendorsSet,
    ChipsSet, 
    PaymentSystemsSet,
    ProductCategoriesSet, 
    ChipColorsSet,
    MaterialTypesSet,
    MaterialColorsSet,
    MagstripeColorsSet,
    MagstripeTracksSet,
    AntennaSizesSet,
    EffectsSet,
    BankEmployeesSet,
    VendorEmployeesSet,
    PaymentSystemEmployeesSet,
    ProcessListSet,
    ProcessDataSet,
    CountriesSet,
    ProductTypesSet,
    CurrenciesSet,
    BankPricesSet,
    VendorPricesSet,
    GeneralProjectStatusesSet,
    ProcessStatusesSet,
    FilesStatusesSet,
    EffectsMatchingSet,
    VendorManufactureCountriesSet,
    FilesFormatsSet,
    FilesTypeNameSet,
    GallerySet,
    FilesSet,
    BanksBIDsSet,
    PaymentSystemApprovalsSet,
    KeyExchangeProjectsSet,
    KeyExchangeStatusesSet,
    CardTestingProjectsSet,
    CardTestingStatusesSet,
    TestCardTransferSet,
    TestCardTypesSet,
    TransferActionsSet,
    ProcessingCentersSet,
    PesroScriptVendorsSet,
    LaminationTypesSet,
    PaymentTypesSet,
    PaymentsInfoSet,
    DeliveriesInfoSet,
    MifareTypesSet,
    StartYearSet,
    ShortProjectLineViewSet,
    RelevantFilesSet,
    ProductionDataSet,
    CardTestingShortRelevantLineSet,
    AnnexesConditionsDataSet,
    POConditionsDataSet,
    MonthListSet,
    AppletTypesSet,
    KeyExchangeTableProjectsSet,
    CardTestingTableProjectsSet,
    FilesTableSet,
    PaymentsInfoTableSet,
    FolderPathSet,
    FoldersSet,
    EffectsCommonViewSet,
    DeliveriesInfoTableSet,
    ReportsNameSet,
    ReportSet
)

router = routers.DefaultRouter()

router.register('projects', ProjectLineViewSet, basename='projects')
router.register('projects-table', ProjectLineTableViewSet, basename='projects-table')
router.register('banks', BanksSet, basename='banks')
router.register('vendors', VendorsSet, basename='vendors')
router.register('chips', ChipsSet, basename='chips')
router.register('countries', CountriesSet, basename='countries')
router.register('payment-systems', PaymentSystemsSet, basename='payment-systems')
router.register('product-categories', ProductCategoriesSet, basename='product-categories')
router.register('chip-colors', ChipColorsSet, basename='chip-colors')
router.register('product-types', ProductTypesSet, basename='product-types')
router.register('material-types', MaterialTypesSet, basename='material-types')
router.register('material-colors', MaterialColorsSet, basename='material-colors')
router.register('magstripe-colors', MagstripeColorsSet, basename='magstripe-colors')
router.register('magstripe-tracks', MagstripeTracksSet, basename='magstripe-tracks')
router.register('antenna-sizes', AntennaSizesSet, basename='antenna-sizes')
router.register('effects', EffectsSet, basename='effects')
router.register('bank-employees', BankEmployeesSet, basename='bank-employees')
router.register('vendor-employees', VendorEmployeesSet, basename='vendor-employees')
router.register('vendor-manufacture-countries', VendorManufactureCountriesSet, basename='vendor-manufacture-countriess')
router.register('ps-employees', PaymentSystemEmployeesSet, basename='ps-employees')
router.register('process-list', ProcessListSet, basename='process-list')
router.register('process-data', ProcessDataSet, basename='process-data')
router.register('currencies', CurrenciesSet, basename='currencies')
router.register('bank-prices', BankPricesSet, basename='bank-prices')
router.register('vendor-prices', VendorPricesSet, basename='vendor-prices')
router.register('general-project-statuses', GeneralProjectStatusesSet, basename='general-project-statuses')
router.register('process-statuses', ProcessStatusesSet, basename='process-statuses')
router.register('files-statuses', FilesStatusesSet, basename='files-statuses')
router.register('effects-matching', EffectsMatchingSet, basename='effects-matching')
router.register('files-formats', FilesFormatsSet, basename='files-formats')
router.register('files-type-names', FilesTypeNameSet, basename='files-type-names')
router.register('galleries', GallerySet, basename='galleries')
router.register('files', FilesSet, basename='files')
router.register('files-table', FilesTableSet, basename='files-table')
router.register('banks-bids', BanksBIDsSet, basename='banks-bids')
router.register('payment-system-approvals', PaymentSystemApprovalsSet, basename='payment-system-approvals')
router.register('key-exchange', KeyExchangeProjectsSet, basename='key-exchange')
router.register('key-exchange-table', KeyExchangeTableProjectsSet, basename='key-exchange-table')
router.register('key-exchange-statuses', KeyExchangeStatusesSet, basename='key-exchange-statuses')
router.register('card-testing-data', CardTestingProjectsSet, basename='card-testing-data')
router.register('card-testing-table', CardTestingTableProjectsSet, basename='card-testing-table')
router.register('card-testing-statuses', CardTestingStatusesSet, basename='card-testing-statuses')
router.register('test-card-types', TestCardTypesSet, basename='test-card-types')
router.register('test-card-transfer-data', TestCardTransferSet, basename='test-card-transfer-data')
router.register('transfer-actions', TransferActionsSet, basename='transfer-actions')
router.register('processing-centers', ProcessingCentersSet, basename='processing-centers')
router.register('perso-script-vendors', PesroScriptVendorsSet, basename='perso-script-vendors')
router.register('lamination-types', LaminationTypesSet, basename='lamination-types')
router.register('payment-types', PaymentTypesSet, basename='payment-types')
router.register('payments-info', PaymentsInfoSet, basename='payments-info')
router.register('payments-info-table', PaymentsInfoTableSet, basename='payments-info-table')
router.register('deliveries-info', DeliveriesInfoSet, basename='deliveries-info')
router.register('deliveries-info-table', DeliveriesInfoTableSet, basename='deliveries-info-table')
router.register('mifare-types', MifareTypesSet, basename='mifare-types')
router.register('start-year', StartYearSet, basename='start-year')
router.register('projects-limited-info', ShortProjectLineViewSet, basename='projects-limited-info')
router.register('relevant-files', RelevantFilesSet, basename='relevant-files')
router.register('production-data', ProductionDataSet, basename='production-data')
router.register('card-testing-short-relevant-data', CardTestingShortRelevantLineSet, basename='card-testing-short-relevant-data')
router.register('annexes-additional-conditions', AnnexesConditionsDataSet, basename='annexes-additional-conditions')
router.register('PO-additional-conditions', POConditionsDataSet, basename='PO-additional-conditions')
router.register('month-list', MonthListSet, basename='month-list')
router.register('applet-types', AppletTypesSet, basename='applet-types')
router.register('folder-path', FolderPathSet, basename='folder-path')
router.register('folders', FoldersSet, basename='folders')
router.register('line-effects-common', EffectsCommonViewSet, basename='line-effects-common')
router.register('reports-name', ReportsNameSet, basename='reports-name')
router.register('report', ReportSet, basename='report')

urlpatterns = []
urlpatterns += router.urls
