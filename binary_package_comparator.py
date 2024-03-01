import json
import requests
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException


class BinaryPackageComparator:
    """
    A class for comparing lists of binary packages of two branches.

    Attributes:
        p10_file (str): Path to the file with package data for branch p10.
        sisyphus_file (str): Path to the file with package data for the sisyphus branch.
        output (str): Path to the file where the comparison result will be saved.
    """

    def __init__(self, p10_file, sisyphus_file, output=None):
        """
        Initializing the BinaryPackageComparator object.

        Args:
            p10_file (str): Path to the file with package data for branch p10.
            sisyphus_file (str): Path to the file with package data for the sisyphus branch.
            output (str, optional): Path to the file to save the comparison result. Default is None.
        """
        self.p10_file = p10_file
        self.sisyphus_file = sisyphus_file
        self.output = output

    def get_branch_binary_packages(self, branch, filename, retries=3):
        """
        Получает данные о бинарных пакетах из указанной ветки и сохраняет их в файл.

        Args:
            branch (str): Название ветки (p10 или sisyphus).
            filename (str): Путь к файлу для сохранения данных.
            retries (int, optional): Количество попыток повторной загрузки в случае ошибки. По умолчанию 3.

        Returns:
            dict: Словарь с данными о бинарных пакетах.
        """
        url = f"https://rdb.altlinux.org/api/export/branch_binary_packages/{branch}"
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            packages = response.json()

            with open(filename, "w") as file:
                json.dump(packages, file, indent=4)

            return packages
        except RequestException as e:
            print(f"Failed to retrieve binary packages for branch {branch}: {e}")
            return {}

    def load_packages(self, file_path):
        """
        Loads package data from a JSON file.

        Args:
            file_path (str): Path to the JSON file.

        Returns:
            list: List of packages if the file is found and can be downloaded, otherwise an empty list.
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

    def compare_packages(self, p10_packages, sisyphus_packages):
        """
        Compares the package lists of the p10 and sisyphus branches.

        Args:
            p10_packages (list): List of packages of the p10 branch.
            sisyphus_packages (list): List of packages of the sisyphus branch.

        Returns:
            dict: The result of the comparison, containing three categories:
                - packages that are in p10, but not in sisyphus,
                - packages that are in sisyphus, but not in p10,
                - packages with newer version in sisyphus compared to p10.
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

    def run_comparison(self):
        """
        Performs a comparison of packages and saves the result to a file or outputs it to the console.
        """
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(self.get_branch_binary_packages, "p10", self.p10_file)
            executor.submit(self.get_branch_binary_packages, "sisyphus", self.sisyphus_file)

        comparison_result = self.compare_packages(self.load_packages(self.p10_file), self.load_packages(self.sisyphus_file))

        if self.output:
            with open(self.output, 'w') as f:
                json.dump(comparison_result, f, indent=4)
        else:
            print(json.dumps(comparison_result, indent=4))



