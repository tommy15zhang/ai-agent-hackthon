import os


def generate_directory_tree(start_path):
    """Generates a visual representation of the directory tree, ignoring hidden files and directories."""
    tree = []
    
    for root, dirs, files in os.walk(start_path):
        # Remove hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        tree.append(f'{indent}{os.path.basename(root)}/')
        
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            if not f.startswith('.'):  # Ignore hidden files
                tree.append(f'{sub_indent}{f}')
    
    return '\n'.join(tree)

    
    