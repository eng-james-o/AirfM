import os
import json

def find_files(root_dir, extensions, exclude_dirs):
    """Finds all files with given extensions in a directory, excluding specified subdirectories."""
    file_paths = []
    for root, dirs, files in os.walk(root_dir):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                # Construct the relative path
                relative_path = os.path.relpath(os.path.join(root, file), root_dir)
                file_paths.append(relative_path.replace('\\', '/'))
    return file_paths

def update_pyproject(project_dir):
    """Updates the main.pyproject file with the latest list of .py and .qml files."""
    pyproject_path = os.path.join(project_dir, "main.pyproject")
    
    # Find all .py and .qml files
    python_files = find_files(project_dir, [".py"], [".venv", "__pycache__"])
    qml_files = [os.path.join("qml", file).replace('\\', '/') for file in find_files(os.path.join(project_dir, "qml"), [".qml"], [])]
    
    # Create a combined set of files
    all_files = set(python_files + qml_files)
    
    # Read the existing pyproject file
    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r') as f:
            try:
                data = json.load(f)
                existing_files = set(data.get("files", []))
            except json.JSONDecodeError:
                existing_files = set()
                data = {"files": []}
    else:
        existing_files = set()
        data = {"files": []}
        
    # Add new files and update existing qml files
    new_files = set()
    for f in existing_files:
        if f.endswith(".qml") and not f.startswith("qml/"):
            new_files.add(f"qml/{f}")
        else:
            new_files.add(f)
            
    for f in all_files:
        new_files.add(f)
    
    data["files"] = sorted(list(new_files))
    
    # Write the updated data back to the file
    with open(pyproject_path, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    project_directory = os.path.dirname(os.path.abspath(__file__))
    update_pyproject(project_directory)
    print("main.pyproject has been updated successfully.")