import os
import json
import math

def create_output_directory(input_file):
    """Create output directory based on input filename"""
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(os.path.dirname(input_file), base_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def split_text_file(input_file, chunk_size):
    """Split text file into chunks of specified size"""
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        return

    # Create output directory
    output_dir = create_output_directory(input_file)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Read the entire file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Calculate total chunks needed
    total_chars = len(text)
    total_chunks = math.ceil(total_chars / chunk_size)

    # Split and save chunks
    for i in range(total_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, total_chars)
        chunk = text[start:end]

        # Create output filename
        output_file = os.path.join(output_dir, f"{base_name}_part{i+1}.txt")

        # Write chunk to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(chunk)

        print(f"Created {output_file}")

def main():
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), "split_config.json")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in configuration file {config_path}")
        return

    default_chunk_size = config.get('default_chunk_size', 500000)

    # Process each file in configuration
    for file_config in config.get('files', []):
        input_file = file_config['input_file']
        chunk_size = file_config.get('chunk_size', default_chunk_size)
        
        print(f"\nProcessing {input_file}")
        print(f"Chunk size: {chunk_size} characters")
        
        split_text_file(input_file, chunk_size)

if __name__ == "__main__":
    main()
