"""
Script to extract embedded images from Jupyter notebooks and replace attachment references.
This converts attachment:image.png to local image files that work in deployed websites.
"""

import json
import base64
from pathlib import Path


def extract_attachments(notebook_path):
    """Extract attachments from notebook to images folder and update references."""
    nb_path = Path(notebook_path)
    
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    image_folder = nb_path.parent / "images"
    image_folder.mkdir(exist_ok=True)
    
    extracted_count = 0
    updated = False
    
    for i, cell in enumerate(nb['cells']):
        if 'attachments' in cell and cell['attachments']:
            for filename, file_data in cell['attachments'].items():
                for mime_type, base64_data in file_data.items():
                    # Decode base64 image
                    try:
                        image_data = base64.b64decode(base64_data)
                        # Save to images folder
                        image_path = image_folder / filename
                        image_path.write_bytes(image_data)
                        extracted_count += 1
                        print(f"  [+] Extracted {image_path.name}")
                        
                        # Update markdown to reference file instead of attachment
                        if 'source' in cell and isinstance(cell['source'], list):
                            new_source = []
                            for line in cell['source']:
                                if isinstance(line, str):
                                    # Replace attachment: references
                                    if f'attachment:{filename}' in line:
                                        line = line.replace(f'attachment:{filename}', f'images/{filename}')
                                        updated = True
                                    new_source.append(line)
                                else:
                                    new_source.append(line)
                            cell['source'] = new_source
                    except Exception as e:
                        print(f"  [X] Error extracting {filename}: {e}")
    
    # Save updated notebook if changes were made
    if updated:
        with open(nb_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        return extracted_count, True
    
    return extracted_count, False


def main():
    """Process all notebooks in the project."""
    print("Extracting embedded images from Jupyter notebooks...\n")
    
    total_extracted = 0
    total_updated = 0
    
    # Find all notebooks (excluding venv and _build)
    for notebook in Path(".").rglob("*.ipynb"):
        if "venv" in str(notebook) or "_build" in str(notebook):
            continue
            
        print(f"\nProcessing: {notebook.relative_to('.')}")
        try:
            extracted, updated = extract_attachments(notebook)
            total_extracted += extracted
            if updated:
                total_updated += 1
        except Exception as e:
            print(f"  [X] Error processing notebook: {e}")
    
    print(f"\n{'='*60}")
    print(f"[+] Extracted {total_extracted} image(s)")
    print(f"[+] Updated {total_updated} notebook(s)")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("1. Add images/ folders to git: git add */images/")
    print("2. Update .gitignore to ignore *_files/ folders")
    print("3. Rebuild website: jupyter-book build .")
    print("4. Deploy: ghp-import -n -p -f _build/html")


if __name__ == "__main__":
    main()

