import argparse
from binary_package_comparator import BinaryPackageComparator



def main():
    parser = argparse.ArgumentParser(description="Compare binary package lists of sisyphus and p10 branches.")
    parser.add_argument("p10_file", help="Path to the p10 branch JSON file")
    parser.add_argument("sisyphus_file", help="Path to the sisyphus branch JSON file")
    parser.add_argument("--output", "-o", metavar="OUTPUT", help="Path to the output JSON file")
    args = parser.parse_args()

    comparator = BinaryPackageComparator(args.p10_file, args.sisyphus_file, args.output)
    comparator.run_comparison()


if __name__ == "__main__":
    main()
