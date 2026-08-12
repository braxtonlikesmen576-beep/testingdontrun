import os

# Get the Downloads folder path
downloads = os.path.join(os.environ['USERPROFILE'], 'Downloads')

print(f"Looking in: {downloads}")
print("=" * 50)

count = 0
failed = 0

for root, dirs, files in os.walk(downloads):
    for file in files:
        if file.endswith('.encrypted'):
            old_path = os.path.join(root, file)
            new_path = old_path.replace('.encrypted', '')
            try:
                os.rename(old_path, new_path)
                count += 1
                print(f"[OK] {file} -> {file.replace('.encrypted', '')}")
            except Exception as e:
                failed += 1
                print(f"[FAIL] {file} - {e}")

print("=" * 50)
print(f"Done! Renamed: {count}, Failed: {failed}")
input("Press Enter to exit...")
