import os
from typing import List, Dict
import glob
from pathlib import Path

# Import the create_embeddings function from the existing file
from pipelines.embedding.embeddings import create_embeddings

def read_markdown_file(file_path: str) -> str:
    """
    Read the content of a markdown file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        The content of the file as a string
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def convert_md_to_embeddings(raw_folder_path: str, output_folder_path: str = None) -> Dict[str, List[float]]:
    """
    Convert markdown files in the raw folder to embeddings.
    
    Args:
        raw_folder_path: Path to the folder containing markdown files
        output_folder_path: Optional path to save the embeddings
        
    Returns:
        A dictionary mapping file names to their embeddings
    """
    # Get all markdown files in the raw folder
    md_files = glob.glob(os.path.join(raw_folder_path, "*.md"))
    
    if not md_files:
        print(f"No markdown files found in {raw_folder_path}")
        return {}
    
    # Read the content of each file
    file_contents = {}
    for file_path in md_files:
        file_name = os.path.basename(file_path)
        content = read_markdown_file(file_path)
        file_contents[file_name] = content
    
    # Create embeddings for the file contents
    texts = list(file_contents.values())
    file_names = list(file_contents.keys())
    
    # Call the create_embeddings function
    embeddings = create_embeddings(texts)
    
    # Map file names to their embeddings
    result = {file_names[i]: embeddings[i] for i in range(len(file_names))}
    
    # Save embeddings if output folder is provided
    if output_folder_path:
        os.makedirs(output_folder_path, exist_ok=True)
        
        import json
        for file_name, embedding in result.items():
            output_file = os.path.join(output_folder_path, f"{os.path.splitext(file_name)[0]}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"file_name": file_name, "embedding": embedding}, f)
    
    return result

# Example usage
if __name__ == "__main__":
    # Path to the raw folder containing markdown files
    raw_folder = "data/raw"
    # Path to save the embeddings
    output_folder = "data/embeddings"
    
    # Convert markdown files to embeddings
    embeddings_dict = convert_md_to_embeddings(raw_folder, output_folder)
    
    print(f"Created embeddings for {len(embeddings_dict)} files")
    for file_name in embeddings_dict:
        print(f"- {file_name}")