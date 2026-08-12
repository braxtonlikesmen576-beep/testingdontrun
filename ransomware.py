import os

def rename_files():
    count = 0
    user = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
    
    # All directories including Downloads
    dirs = [
        user + '\\Desktop',
        user + '\\Documents',
        user + '\\Downloads',
        user + '\\Pictures',
        user + '\\Music',
        user + '\\Videos'
    ]
    
    print("Scanning for files with .encrypted extension...")
    print("=" * 60)
    
    for d in dirs:
        if os.path.exists(d):
            print(f"\nChecking: {d}")
            for root, dirs, files in os.walk(d):
                for file in files:
                    if file.endswith('.encrypted'):
                        old_path = os.path.join(root, file)
                        new_path = old_path.replace('.encrypted', '')
                        try:
                            os.rename(old_path, new_path)
                            count += 1
                            print(f"  [OK] Renamed: {file}")
                        except Exception as e:
                            print(f"  [FAIL] {file} - {e}")
    
    print("\n" + "=" * 60)
    return count

print("F SOCIETY FILE RENAMER")
print("Removing .encrypted extension from all files...")
print("=" * 60)

total = rename_files()
print(f"\nDone! Renamed {total} files.")
input("\nPress Enter to exit...")
