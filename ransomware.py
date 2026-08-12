import os

def rename_files():
    count = 0
    user = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
    dirs = [user+'\\Desktop', user+'\\Documents', user+'\\Downloads', user+'\\Pictures', user+'\\Music', user+'\\Videos']
    for d in dirs:
        if os.path.exists(d):
            for root,_,files in os.walk(d):
                for f in files:
                    if f.endswith('.encrypted'):
                        old = os.path.join(root, f)
                        new = old.replace('.encrypted', '')
                        os.rename(old, new)
                        count += 1
                        print(f"Renamed: {f}")
    return count

print("Removing .encrypted from files...")
count = rename_files()
print(f"Done! Renamed {count} files.")
input("Press Enter to exit...")
