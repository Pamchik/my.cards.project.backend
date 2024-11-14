import os
import json

# Папка с fixtures
fixtures_dir = 'backend_api/fixtures'

# Собираем все имена файлов в папке fixtures
fixture_files = [
  'month_list.json',
  'chip_colors.json',
  'currencies.json',
  'files_statuses.json',
  'files_type_name.json',
  'files_formats.json',
  'general_project_statuses.json',
  'magstripe_tracks.json',
  'process_list.json',
  'process_statuses.json',
  'key_exchange_statuses.json',
  'test_card_types.json',
  'card_testing_statuses.json',
  'transfer_actions.json',
  'payment_types.json',
  'start_year.json',
]

# Список для хранения данных из всех файлов
all_data = []

# Читаем данные из каждого файла и добавляем их в список
for file in fixture_files:
    with open(os.path.join(fixtures_dir, file), 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_data.extend(data)

# Записываем объединенные данные в новый файл
output_file = 'backend_api/fixtures/combined_fixtures.json'
with open(output_file, 'w') as f:
    json.dump(all_data, f)

print(f'Собраны данные из {len(fixture_files)} файла(ов) и записаны в {output_file}')