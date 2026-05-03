#!/usr/bin/env python3
import subprocess
import re
import random
import sys
import os
import json
from datetime import datetime

class MACChanger:
    def __init__(self):
        self.oui_list = self.load_oui()
        self.backup_file = "backup/original_macs.json"
        
    def show_banner(self):
        os.system('clear')
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ███╗   ███╗ █████╗  ██████╗███████╗██╗     ██╗██████╗     ║
║   ████╗ ████║██╔══██╗██╔════╝██╔════╝██║     ██║██╔══██╗    ║
║   ██╔████╔██║███████║██║     █████╗  ██║     ██║██████╔╝    ║
║   ██║╚██╔╝██║██╔══██║██║     ██╔══╝  ██║     ██║██╔═══╝     ║
║   ██║ ╚═╝ ██║██║  ██║╚██████╗██║     ███████╗██║██║         ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝     ╚══════╝╚═╝╚═╝         ║
║                                                               ║
║           MAC ADDRESS CHANGER SUITE v1.0                      ║
║           Developed by Abhishek                              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def load_oui(self):
        oui = {
            '00:11:22': 'Apple',
            '00:14:51': 'Samsung',
            '00:1A:11': 'Intel',
            '00:1C:42': 'Cisco',
            '00:23:32': 'Dell',
            '00:25:9C': 'HP',
            '00:50:56': 'VMware',
            '08:00:27': 'VirtualBox',
            '00:0C:29': 'VMware',
            '00:1B:63': 'Broadcom',
            '00:1E:68': 'Qualcomm',
            '00:22:68': 'Realtek',
            '00:24:D6': 'Nokia',
            '00:26:82': 'Sony',
            '00:30:48': 'IBM',
            '00:40:96': 'Huawei',
            '00:50:BA': 'MikroTik',
            '00:60:2F': 'Zyxel',
            '00:80:77': 'Netgear',
            '00:90:4C': 'TP-Link'
        }
        return oui
    
    def get_current_mac(self, interface):
        try:
            result = subprocess.run(['ip', 'link', 'show', interface], 
                                  capture_output=True, text=True)
            match = re.search(r'link/ether\s+([0-9a-f:]{17})', result.stdout)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def get_interfaces(self):
        result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
        interfaces = re.findall(r'\d+: (\w+):', result.stdout)
        return [i for i in interfaces if i != 'lo']
    
    def change_mac(self, interface, new_mac):
        print(f"[*] Changing MAC on {interface}")
        
        subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], capture_output=True)
        subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'address', new_mac], capture_output=True)
        subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], capture_output=True)
        
        new_current = self.get_current_mac(interface)
        if new_current == new_mac:
            return True
        return False
    
    def generate_random_mac(self, vendor=None):
        if vendor and vendor in self.oui_list:
            prefix = vendor
        else:
            prefix = random.choice(list(self.oui_list.keys()))
        
        suffix = ':'.join(['%02x' % random.randint(0, 255) for _ in range(3)])
        return f"{prefix}:{suffix}"
    
    def validate_mac(self, mac):
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return re.match(pattern, mac) is not None
    
    def save_original_mac(self, interface, original_mac):
        os.makedirs('backup', exist_ok=True)
        
        if os.path.exists(self.backup_file):
            with open(self.backup_file, 'r') as f:
                backups = json.load(f)
        else:
            backups = {}
        
        backups[interface] = {
            'original_mac': original_mac,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(self.backup_file, 'w') as f:
            json.dump(backups, f, indent=2)
        
        print(f"[+] Original MAC saved for {interface}")
    
    def restore_original_mac(self, interface):
        if not os.path.exists(self.backup_file):
            print("[-] No backup found")
            return False
        
        with open(self.backup_file, 'r') as f:
            backups = json.load(f)
        
        if interface not in backups:
            print(f"[-] No backup for {interface}")
            return False
        
        original_mac = backups[interface]['original_mac']
        return self.change_mac(interface, original_mac)
    
    def show_vendors(self):
        print("\n[+] Available Vendors:\n")
        vendors = sorted(set(self.oui_list.values()))
        for i, vendor in enumerate(vendors, 1):
            print(f"    {i:2}. {vendor}")
        print()
    
    def run(self):
        self.show_banner()
        
        if os.geteuid() != 0:
            print("[!] Root privileges required. Run with: sudo python macflip.py")
            sys.exit(1)
        
        interfaces = self.get_interfaces()
        if not interfaces:
            print("[-] No network interfaces found")
            sys.exit(1)
        
        print("[+] Available Interfaces:\n")
        for i, iface in enumerate(interfaces, 1):
            mac = self.get_current_mac(iface)
            print(f"    {i}. {iface} - {mac}")
        
        print("\n")
        
        print("""
┌─────────────────────────────────────────────────────────────┐
│                        OPTIONS                              │
├─────────────────────────────────────────────────────────────┤
│  [1] Change MAC to random                                   │
│  [2] Change MAC to random with specific vendor              │
│  [3] Change MAC to custom address                           │
│  [4] Restore original MAC from backup                       │
│  [5] Show current MAC only                                  │
│  [6] Show vendor list                                       │
│  [0] Exit                                                   │
└─────────────────────────────────────────────────────────────┘
        """)
        
        choice = input("macflip@tool:~$ ")
        
        if choice == '0':
            print("\n[*] Exiting...")
            sys.exit(0)
        
        if not choice.isdigit():
            print("[-] Invalid choice")
            return
        
        choice = int(choice)
        
        if 1 <= choice <= 5:
            print("\n[?] Select interface:")
            for i, iface in enumerate(interfaces, 1):
                print(f"    {i}. {iface}")
            
            iface_choice = input("\nEnter number: ")
            if not iface_choice.isdigit() or int(iface_choice) > len(interfaces):
                print("[-] Invalid interface")
                return
            
            interface = interfaces[int(iface_choice) - 1]
            original_mac = self.get_current_mac(interface)
            
            if choice == 1:
                new_mac = self.generate_random_mac()
                print(f"[*] New MAC: {new_mac}")
                self.save_original_mac(interface, original_mac)
                if self.change_mac(interface, new_mac):
                    print(f"[+] MAC changed to {new_mac}")
                else:
                    print("[-] Failed to change MAC")
            
            elif choice == 2:
                self.show_vendors()
                vendor_name = input("Enter vendor name: ")
                vendor_prefix = None
                for prefix, name in self.oui_list.items():
                    if name.lower() == vendor_name.lower():
                        vendor_prefix = prefix
                        break
                
                if vendor_prefix:
                    new_mac = self.generate_random_mac(vendor_prefix)
                    print(f"[*] New MAC: {new_mac}")
                    self.save_original_mac(interface, original_mac)
                    if self.change_mac(interface, new_mac):
                        print(f"[+] MAC changed to {new_mac}")
                    else:
                        print("[-] Failed to change MAC")
                else:
                    print("[-] Vendor not found")
            
            elif choice == 3:
                new_mac = input("Enter new MAC address (format: xx:xx:xx:xx:xx:xx): ")
                if self.validate_mac(new_mac):
                    self.save_original_mac(interface, original_mac)
                    if self.change_mac(interface, new_mac):
                        print(f"[+] MAC changed to {new_mac}")
                    else:
                        print("[-] Failed to change MAC")
                else:
                    print("[-] Invalid MAC format")
            
            elif choice == 4:
                self.restore_original_mac(interface)
            
            elif choice == 5:
                print(f"\n[+] Current MAC: {original_mac}")
        
        elif choice == 6:
            self.show_vendors()
        
        else:
            print("[-] Invalid choice")

if __name__ == "__main__":
    while True:
        ch = MACChanger()
        ch.run()
        input("\nPress Enter to continue...")
