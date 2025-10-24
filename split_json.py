#!/usr/bin/env python3
"""
Split large JSON file into smaller chunks
"""

import json
import os
import math

def split_json_file(input_file, output_dir, num_chunks=10):
    """
    Split a JSON file into multiple smaller files

    Args:
        input_file: Path to the input JSON file
        output_dir: Directory to save the split files
        num_chunks: Number of files to split into (default: 10)
    """
    print(f"Reading {input_file}...")

    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check if it's a list or dict
    if isinstance(data, list):
        items = data
        is_list = True
    elif isinstance(data, dict):
        # Check for common array keys
        if 'properties' in data:
            items = data['properties']
            wrapper_key = 'properties'
        elif 'data' in data:
            items = data['data']
            wrapper_key = 'data'
        elif 'results' in data:
            items = data['results']
            wrapper_key = 'results'
        elif 'items' in data:
            items = data['items']
            wrapper_key = 'items'
        else:
            # Take the first list value found
            for key, value in data.items():
                if isinstance(value, list):
                    items = value
                    wrapper_key = key
                    break
            else:
                print("Error: Could not find a list in the JSON structure")
                return
        is_list = False
    else:
        print("Error: JSON root must be a list or object")
        return

    total_items = len(items)
    items_per_chunk = math.ceil(total_items / num_chunks)

    print(f"Total items: {total_items}")
    print(f"Items per chunk: {items_per_chunk}")
    print(f"Creating {num_chunks} files...")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get base filename
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Split and save
    for i in range(num_chunks):
        start_idx = i * items_per_chunk
        end_idx = min((i + 1) * items_per_chunk, total_items)
        chunk = items[start_idx:end_idx]

        # Create output filename
        output_file = os.path.join(output_dir, f"{base_name}_part_{i+1:02d}_of_{num_chunks:02d}.json")

        # Prepare data to save
        if is_list:
            output_data = chunk
        else:
            # Preserve the original structure
            output_data = {wrapper_key: chunk}
            # Copy any metadata from original
            for key, value in data.items():
                if key != wrapper_key and not isinstance(value, list):
                    output_data[key] = value

        # Save chunk
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Created {os.path.basename(output_file)} ({len(chunk)} items)")

    print(f"\nSuccessfully split into {num_chunks} files in {output_dir}")


if __name__ == "__main__":
    input_file = "/Users/ryan/Downloads/get_all_properties.json"
    output_dir = "/Users/ryan/Downloads/properties_split"

    split_json_file(input_file, output_dir, num_chunks=10)
