import os

def mass_replace(root_dir, old_str, new_dir):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if old_str in content:
                    print(f"Replacing in {path}")
                    new_content = content.replace(old_str, new_dir)
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == "__main__":
    mass_replace("src", "triangle_alert", "alert-triangle")
    mass_replace("src", "triangle-alert", "alert-triangle")
