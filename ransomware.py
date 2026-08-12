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
    dirs = [user+'\\Desktop', user+'\\Documents', user+'\\Downloads', user+'\\Pictures', user+'\\Music', user+'\\Videos']
    for d in dirs:
        if os.path.exists(d):
            for root,_,files in os.walk(d):
                for f in files:
                    if f.endswith('.encrypted'):
                        if decrypt_file(os.path.join(root,f), key, iv):
                            count += 1
    return count

print("="*50)
print("F SOCIETY DECRYPTOR")
print("="*50)

key_input = input("Enter decryption key: ").strip()
if key_input != DECRYPT_KEY:
    print("Invalid key")
    input("Press Enter to exit...")
    exit()

# Try backup
hidden = os.environ.get('TEMP','C:\\Temp')+'\\fsociety_backup.key'
if os.path.exists(hidden):
    print("[+] Found backup key")
    with open(hidden,'r') as f:
        lines = f.readlines()
        if len(lines) >= 3 and lines[2].strip() == DECRYPT_KEY:
            key = base64.b64decode(lines[0].strip())
            iv = base64.b64decode(lines[1].strip())
            count = decrypt_all(key, iv)
            print(f"[+] Decrypted {count} files")
            try: os.remove(hidden)
            except: pass
            input("Press Enter to exit...")
            exit()

# Try ransom note
note = os.environ.get('USERPROFILE','C:\\Users\\Default')+'\\Desktop\\README_FSOCIETY.txt'
if os.path.exists(note):
    print("[+] Found ransom note")
    with open(note,'r') as f:
        content = f.read()
        km = re.search(r'Key: (\S+)', content)
        im = re.search(r'IV: (\S+)', content)
        if km and im:
            key = base64.b64decode(km.group(1))
            iv = base64.b64decode(im.group(1))
            count = decrypt_all(key, iv)
            print(f"[+] Decrypted {count} files")
            try: os.remove(note)
            except: pass
            input("Press Enter to exit...")
            exit()

print("[-] Could not find encryption key")
input("Press Enter to exit...")
