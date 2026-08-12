import os

def rename_files():
    count = 0
    user = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
    
    # All directories
    dirs = [
        user + '\\Desktop',
        user + '\\Documents',
        user + '\\Downloads',
        user + '\\Pictures',
        user + '\\Music',
        user + '\\Videos'
    ]
    
    print("Removing .encrypted from ALL files...")
    print("=" * 60)
    
    for d in dirs:
        if os.path.exists(d):
            print(f"\nChecking: {d}")
            for root, dirs, files in os.walk(d):
                for file in files:
                    if file.endswith('.encrypted'):
                        old_path = os.path.join(root, file)
                        # Remove ONLY the .encrypted part
                        new_path = old_path.replace('.encrypted', '')
                        try:
                            os.rename(old_path, new_path)
                            count += 1
                            print(f"  [OK] {file}")
                        except Exception as e:
                            print(f"  [FAIL] {file} - {e}")
    
    return count

print("F SOCIETY FILE RENAMER")
print("=" * 60)
total = rename_files()
print(f"\nDone! Renamed {total} files.")
input("\nPress Enter to exit...")
