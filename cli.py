import argparse
import json
import sys
import os

sys.path.insert(0, "src")
from transformer import transform
from config_loader import load_config, apply_config

def main():
    parser = argparse.ArgumentParser(description="Eightfold Candidate Data Transformer")
    parser.add_argument("--csv", help="Path to CSV file")
    parser.add_argument("--json", help="Path to JSON file")
    parser.add_argument("--txt", help="Path to TXT notes file")
    parser.add_argument("--config", help="Path to config JSON", default=None)
    parser.add_argument("--output", help="Output file path", default=None)
    args = parser.parse_args()
    
    sources = {}
    if args.csv: sources["csv"] = args.csv
    if args.json: sources["json"] = args.json
    if args.txt: sources["txt"] = args.txt
    
    if not sources:
        print("Error: provide at least one source (--csv, --json, or --txt)")
        sys.exit(1)
    
    results = transform(sources)
    
    if args.config:
        config = load_config(args.config)
        results = [apply_config(r, config) for r in results]
    
    output_json = json.dumps(results, indent=2)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"✅ Output written to {args.output}")
    else:
        print(output_json)

if __name__ == "__main__":
    main()