import os

user = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
dirs = [user + '\\Downloads', user + '\\Desktop', user + '\\Documents']

for d in dirs:
    if os.path.exists(d):
        print(f"\nFiles in {d}:")
        for root, _, files in os.walk(d):
            for f in files[:10]:
                print(f"  {f}")
            if len(files) > 10:
                print(f"  ... and {len(files)-10} more")
