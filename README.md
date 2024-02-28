# CLI Binary Packages Comparator

This command-line utility compares binary package lists of the Sisyphus and p10 branches of the Alt Linux distribution.

## Installation

Before using the utility, make sure you have Python installed on your system.

1. Clone this repository:
git clone https://github.com/AStmav/cli_compare_branch.git


2. Navigate to the project directory:
cd cli_compare_branch

markdown
Copy code
3. Install dependencies:
pip install -r requirements.txt

bash
Copy code

## Usage
This will download the package data from the p10 and sisyphus branches, save it in p10.json and sisyphus.json respectively, and then perform the comparison and print the result to the console.
Run the utility by executing the following command:
```bash
python compare_branches.py p10.json sisyphus.json

python compare_branches.py p10.json sisyphus.json --output comparison_result.json
```


### Arguments:

- `p10.json`: Path to the JSON file containing binary packages of the p10 branch.
- `sisyphus.json`: Path to the JSON file containing binary packages of the Sisyphus branch.
- `--output` or `-o`: Optional. Path to the output JSON file to save the comparison result.

### Example:

To compare binary packages of the p10 and Sisyphus branches and save the result to `comparison_result.json`, run:
```bash
python compare_branches.py p10.json sisyphus.json --output comparison_result.json
```


## Result Interpretation

The comparison result will be saved in the specified output file in JSON format. The result contains three categories:

- `p10_not_in_sisyphus`: Packages that are present in the p10 branch but absent in the Sisyphus branch.
- `sisyphus_not_in_p10`: Packages that are present in the Sisyphus branch but absent in the p10 branch.
- `greater_in_sisyphus`: Packages with a newer version in the Sisyphus branch compared to the p10 branch.

Each category contains details about the packages, such as name, version, architecture, etc.
