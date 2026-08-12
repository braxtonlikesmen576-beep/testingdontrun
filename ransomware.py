import os

def rename_files():
    count = 0
    user = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
    
    # Only Downloads folder
    downloads = user + '\\Downloads'
    
    if os.path.exists(downloads):
        for root, dirs, files in os.walk(downloads):
            for file in files:
                if file.endswith('.encrypted'):
                    old_path = os.path.join(root, file)
                    new_path = old_path.replace('.encrypted', '')
                    try:
                        os.rename(old_path, new_path)
                        count += 1
                        print(f"Renamed: {file}")
                    except:
                        print(f"Failed: {file}")
    
    return count

print("Removing .encrypted from Downloads folder...")
count = rename_files()
print(f"Done! Renamed {count} files in Downloads.")
input("Press Enter to exit...")
