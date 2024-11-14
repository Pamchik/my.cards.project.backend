# cards.project.backend


Проект создан на Djando

Проект написан с использованием Python 3.11.5

Для запуска проекта:
  1. Скачайте Python с официального сайта
  2. Установите виртуальную среду
    ### `py -m venv venv`
  3. Активируйте окружение
    ### в директории проекта, например `С:/Users/User/Desktop/project` запустите `& "С:/Users/User/Desktop/project/venv/Scripts/Activate.ps1"`

В текущем проекте установите зависимости:
  ### `pip install -r requirements.txt` (для сохранения новых `pip freeze > requirements.txt`)

Создайте таблицу в БД (как указано в settings.py) - если необходимо
  ### По дефолту используется тестовая база данных на сервере

Сделайте миграции
  ### `python manage.py makemigrations`
  ### `python manage.py migrate`

Для добавлению в базу значений по дефолту (только если таблица пустая):

  1. Если нужно все сразу загрузить:
    ### `python collect_fixtures.py` - если были обновления в списках
    ### `python manage.py loaddata combined_fixtures`

  2. Если нужно по отдельности:
    ### `python manage.py loaddata month_list`
    ### `python manage.py loaddata chip_colors`
    ### `python manage.py loaddata currencies`
    ### `python manage.py loaddata files_statuses`
    ### `python manage.py loaddata files_type_name`
    ### `python manage.py loaddata files_formats`  
    ### `python manage.py loaddata general_project_statuses`
    ### `python manage.py loaddata magstripe_tracks`
    ### `python manage.py loaddata process_list`
    ### `python manage.py loaddata process_statuses`
    ### `python manage.py loaddata key_exchange_statuses`
    ### `python manage.py loaddata test_card_types`
    ### `python manage.py loaddata card_testing_statuses`
    ### `python manage.py loaddata transfer_actions`
    ### `python manage.py loaddata payment_types`
    ### `python manage.py loaddata start_year`

Для правильной сборки логов создать записи в модели "FieldValueMappingModel", где прописать соответствие ключей к названием, например:
  - model_name - модель, которая имеет запись
  - field_name - поле с ключом
  - view_key_eng/rus - какое поле просматривать в моделе по ключу

Для сохранения изображений в нужную папку, создайте файл media_settings.txt в корневой папке проекта.
  ### Для глобального использования файлы сохраняются в следующей директории:
    MEDIA_ROOT = '//kz-fs-01/Public/Sales/S_Cards/Orders_system'
    MEDIA_URL = '/Orders_system/'
  ### Если файл не создан, то дефолтное расположение файлов в корне проекта ("media"):
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'

В текущем проекте запустите:
  ### `python manage.py runserver`

Приложение запустится в режиме разработки в браузере:
[http://127.0.0.1:8000/]

Настройке пользователя по ссылке: `http://127.0.0.1:8000/api/auth/register` в формате:
{
    "username": "test",
    "email": "test@test.kz",
    "password": "Test12345"
}

Перед размещение в prod нужно:
1. Сделать сборку статичных файлов 
  ### `python manage.py collectstatic`

2. Обновить версию 
    - Если это серьезное изменение (исправление ошибок) в вашем приложении, используйте:
    ### `python increment_version.py major`

    - Если это незначительное изменение (исправление ошибок) в вашем приложении, используйте:
    ### `python increment_version.py minor`

    - А если это просто обновление патча, например изменение форматов в коде, используйте:
    ### `python increment_version.py patch`

3. Перед переносом на сервер проверить файл "settings.py"
    - DEBUG = False
    - CORS_ALLOW_ALL_ORIGINS - скрыть для prod
    - DATABASES - в соответствии с нужнами, либо CardsOrdersTest, либо CardsOrders

    и наличие файла "media_settings.txt", как указано выше