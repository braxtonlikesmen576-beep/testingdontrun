import os
import base64
import re

DECRYPT_KEY = "agent77"

def decrypt_file(file_path, key, iv):
    try:
        with open(file_path, 'rb') as f:
            iv_data = f.read(16)
            encrypted_data = f.read()
        xor_key = key[:16]
        decrypted_data = bytes([encrypted_data[i] ^ xor_key[i % len(xor_key)] for i in range(len(encrypted_data))])
        original_path = file_path.replace('.encrypted', '')
        with open(original_path, 'wb') as f:
            f.write(decrypted_data)
        os.remove(file_path)
        return True
    except:
        return False

def decrypt_all(key, iv):
    count = 0
    user = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
    dirs = [user+'\\Desktop', user+'\\Documents', user+'\\Downloads', user+'\\Pictures', user+'\\Music', user+'\\Videos', user+'\\AppData\\Local', user+'\\AppData\\Roaming']
    for d in dirs:
        if os.path.exists(d):
            for root,_,files in os.walk(d):
                for f in files:
                    if f.endswith('.encrypted'):
                        full_path = os.path.join(root, f)
                        if decrypt_file(full_path, key, iv):
                            count += 1
                            print(f"  Decrypted: {f}")
    return count

print("="*50)
print("F SOCIETY DECRYPTOR")
print("="*50)

key_input = input("Enter decryption key: ").strip()
if key_input != DECRYPT_KEY:
    print("Invalid key")
    input("Press Enter to exit...")
    exit()

key = None
iv = None

# Try to find the key file in multiple locations
key_locations = [
    os.environ.get('TEMP', 'C:\\Temp') + '\\fsociety_backup.key',
    os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop\\fsociety_backup.key',
    'C:\\fsociety_backup.key'
]

for loc in key_locations:
    if os.path.exists(loc):
        print(f"[+] Found backup key at: {loc}")
        with open(loc, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 3 and lines[2].strip() == DECRYPT_KEY:
                key = base64.b64decode(lines[0].strip())
                iv = base64.b64decode(lines[1].strip())
                print("[+] Key loaded from backup")
                break

# If not found, try ransom note
if key is None:
    note = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop\\README_FSOCIETY.txt'
    if os.path.exists(note):
        print("[+] Found ransom note")
        with open(note, 'r') as f:
            content = f.read()
            km = re.search(r'Key: (\S+)', content)
            im = re.search(r'IV: (\S+)', content)
            if km and im:
                key = base64.b64decode(km.group(1))
                iv = base64.b64decode(im.group(1))
                print("[+] Key loaded from ransom note")

if key is None:
    print("[-] Could not find encryption key anywhere")
    print("[-] Looked in:")
    for loc in key_locations:
        print(f"    {loc}")
    print(f"    {os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop\\README_FSOCIETY.txt'}")
    input("Press Enter to exit...")
    exit()

print("[+] Starting decryption...")
count = decrypt_all(key, iv)
print(f"[+] Decrypted {count} files!")

# Cleanup
try:
    for loc in key_locations:
        if os.path.exists(loc):
            os.remove(loc)
except:
    pass
try:
    note = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop\\README_FSOCIETY.txt'
    if os.path.exists(note):
        os.remove(note)
except:
    pass

input("Press Enter to exit...")
