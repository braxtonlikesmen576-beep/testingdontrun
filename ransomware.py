import os

def rename_files():
    count = 0
    user = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
    dirs = [
        user + '\\Desktop',
        user + '\\Documents',
        user + '\\Downloads',
        user + '\\Pictures',
        user + '\\Music',
        user + '\\Videos',
        user + '\\AppData\\Local',
        user + '\\AppData\\Roaming',
        'C:\\ProgramData',
        'C:\\Users\\Public\\Documents',
        'C:\\Users\\Public\\Desktop'
    ]
    
    for d in dirs:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
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

print("Removing .encrypted from all files...")
count = rename_files()
print(f"Done! Renamed {count} files.")
input("Press Enter to exit...")
