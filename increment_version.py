import re
import sys

def increment_version(version, level):
    major, minor, patch = map(int, version.split('.'))
    if level == 'major':
        major += 1
    elif level == 'minor':
        minor += 1
    elif level == 'patch':
        patch += 1
    else:
        raise ValueError('Неверно указан уровень изменения. Введите major, minor или patch')
    return f'{major}.{minor}.{patch}'

def main():
    if len(sys.argv) != 2:
        print('Используйте: python increment_version.py [major|minor|patch]')
        return

    level = sys.argv[1]
    with open('setup.py', 'r') as f:
        content = f.read()
    
    version_match = re.search(r"version='(.*?)'", content)
    if version_match:
        current_version = version_match.group(1)
        new_version = increment_version(current_version, level)
        new_content = re.sub(r"version='.*?'", f"version='{new_version}'", content)
        
        with open('setup.py', 'w') as f:
            f.write(new_content)
        
        print(f'Увеличена версия с {current_version} до {new_version}')
    else:
        print('Не найден номер версии в файле setup.py')

if __name__ == '__main__':
    main()