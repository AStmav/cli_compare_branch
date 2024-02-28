import requests
import json
import argparse
from requests.exceptions import RequestException

def get_branch_binary_packages(branch, filename, retries=3):
    url = f"https://rdb.altlinux.org/api/export/branch_binary_packages/{branch}"
    try:
        for _ in range(retries):
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Генерировать исключение в случае ошибки
            packages = response.json()

            # Сохранение данных в файл
            with open(filename, "w") as file:
                json.dump(packages, file, indent=4)

            return packages
    except RequestException as e:
        print(f"Failed to retrieve binary packages for branch {branch}: {e}")
        return {}

def load_packages(file_path):
    """
    Загружает данные о пакетах из JSON файла.

    Args:
        file_path (str): Путь к JSON файлу.

    Returns:
        list: Список пакетов, если файл найден и может быть загружен, в противном случае - пустой список.
    """
    try:
        with open(file_path) as f:
            data = json.load(f)
            return data.get('packages', [])
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Unable to decode JSON from '{file_path}'.")
        return []

def compare_packages(p10_packages, sisyphus_packages):
    """
    Сравнивает списки пакетов веток p10 и sisyphus.

    Args:
        p10_packages (list): Список пакетов ветки p10.
        sisyphus_packages (list): Список пакетов ветки sisyphus.

    Returns:
        dict: Результат сравнения, содержащий три категории:
              - пакеты, которые есть в p10, но отсутствуют в sisyphus,
              - пакеты, которые есть в sisyphus, но отсутствуют в p10,
              - пакеты с более новой версией в sisyphus по сравнению с p10.
    """
    result = {
        'p10_not_in_sisyphus': [],
        'sisyphus_not_in_p10': [],
        'greater_in_sisyphus': []
    }

    p10_names = {pkg['name'] for pkg in p10_packages}
    sisyphus_names = {pkg['name'] for pkg in sisyphus_packages}

    for pkg in p10_packages:
        if pkg['name'] not in sisyphus_names:
            result['p10_not_in_sisyphus'].append(pkg)

    for pkg in sisyphus_packages:
        if pkg['name'] not in p10_names:
            result['sisyphus_not_in_p10'].append(pkg)
        else:
            p10_version = next((p['version'] for p in p10_packages if p['name'] == pkg['name']), None)
            if p10_version and pkg['version'] > p10_version:
                result['greater_in_sisyphus'].append(pkg)

    return result

def main():
    """
    Основная функция для работы с CLI утилитой.
    """
    parser = argparse.ArgumentParser(description="Compare binary package lists of sisyphus and p10 branches.")
    parser.add_argument("p10_file", help="Path to the p10 branch JSON file")
    parser.add_argument("sisyphus_file", help="Path to the sisyphus branch JSON file")
    parser.add_argument("--output", "-o", metavar="OUTPUT", help="Path to the output JSON file")
    args = parser.parse_args()

    # Получение данных о пакетах ветки p10 и сохранение их в файл
    p10_packages = get_branch_binary_packages("p10", args.p10_file)

    # Получение данных о пакетах ветки sisyphus и сохранение их в файл
    sisyphus_packages = get_branch_binary_packages("sisyphus", args.sisyphus_file)

    # Сравнение пакетов и вывод результата в консоль или сохранение в файл
    comparison_result = compare_packages(load_packages(args.p10_file), load_packages(args.sisyphus_file))
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(comparison_result, f, indent=4)
    else:
        print(json.dumps(comparison_result, indent=4))

if __name__ == "__main__":
    main()


