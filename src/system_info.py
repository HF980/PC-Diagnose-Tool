#********************************************#
# @ #!/usr/bin/env
# @Project: pc_diagnose_tool
# @file name: systeminfo.py
# @author: Houssein
# @creation date: 30.06.2025
# @lastmodified: 30.06.2025
# @version: 1.0
# @copyright: © 2025 Houssein. All rights reserved.
#********************************************#

# system_info.py
import psutil
import platform
import socket
from datetime import datetime
import time
import os
import cpuinfo # Neu hinzugefügt

class SystemInfoFetcher:
    def __init__(self):
        # Speichert den letzten Wert von net_io_counters für die Ratenberechnung
        self._last_net_io_counters = psutil.net_io_counters()
        self._last_net_io_time = time.time()
        self._cpu_model = None # Cache für das CPU-Modell

    def get_cpu_model(self):
        """
        Gibt den Modellnamen der CPU zurück. Verwendet Caching, da sich dieser Wert nicht ändert.
        """
        if self._cpu_model is None:
            try:
                # cpuinfo ist eine externe Bibliothek
                info = cpuinfo.get_cpu_info()
                self._cpu_model = info.get('brand_original', info.get('brand_raw', 'Unbekannt'))
            except Exception as e:
                # print(f"Fehler beim Abrufen des CPU-Modells mit cpuinfo: {e}")
                self._cpu_model = "Unbekannt (Fehler beim Abruf)"
        return self._cpu_model

    def get_cpu_info(self):
        cpu_info = {
            "total_percent": psutil.cpu_percent(interval=0.1), # Non-blocking
            "per_cpu_percent": psutil.cpu_percent(interval=0.1, percpu=True),
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "current_frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "min_frequency_mhz": psutil.cpu_freq().min if psutil.cpu_freq() else None,
            "max_frequency_mhz": psutil.cpu_freq().max if psutil.cpu_freq() else None,
        }
        return cpu_info

    def get_memory_info(self):
        svmem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        mem_info = {
            "total_ram_gb": round(svmem.total / (1024**3), 2),
            "available_ram_gb": round(svmem.available / (1024**3), 2),
            "used_ram_gb": round(svmem.used / (1024**3), 2),
            "ram_percent": svmem.percent,
            "total_swap_gb": round(swap.total / (1024**3), 2),
            "used_swap_gb": round(swap.used / (1024**3), 2),
            "swap_percent": swap.percent
        }
        return mem_info

    def get_network_info(self):
        net_info = {}
        net_info["Hostname"] = socket.gethostname()
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80)) # Google DNS
            net_info["Primary IP"] = s.getsockname()[0]
            s.close()
        except Exception:
            net_info["Primary IP"] = "N/A"

        # Bytes gesendet/empfangen seit Systemstart
        current_net_io = psutil.net_io_counters()
        net_info["Bytes Sent (GB)"] = round(current_net_io.bytes_sent / (1024**3), 2)
        net_info["Bytes Received (GB)"] = round(current_net_io.bytes_recv / (1024**3), 2)

        net_info["Interfaces"] = {}
        addrs = psutil.net_if_addrs()
        for interface_name, interface_addrs in addrs.items():
            net_info["Interfaces"][interface_name] = []
            for addr in interface_addrs:
                addr_info = {}
                if addr.family == socket.AF_INET:
                    addr_info["IPv4"] = addr.address
                    addr_info["Netzmaske"] = addr.netmask
                elif addr.family == socket.AF_INET6:
                    addr_info["IPv6"] = addr.address
                elif addr.family == psutil.AF_LINK: # MAC-Adresse
                    addr_info["MAC"] = addr.address
                if addr_info:
                    net_info["Interfaces"][interface_name].append(addr_info)
        return net_info

    def get_network_io_rates(self):
        """
        Berechnet die aktuellen Sende- und Empfangsraten in KB/s.
        """
        current_net_io = psutil.net_io_counters()
        current_time = time.time()

        time_diff = current_time - self._last_net_io_time
        
        if time_diff <= 0: # Vermeide Division durch Null oder negative Werte
            return {
                "bytes_sent_rate_kbs": 0.0,
                "bytes_recv_rate_kbs": 0.0
            }

        bytes_sent_diff = current_net_io.bytes_sent - self._last_net_io_counters.bytes_sent
        bytes_recv_diff = current_net_io.bytes_recv - self._last_net_io_counters.bytes_recv

        sent_rate_bps = bytes_sent_diff / time_diff
        recv_rate_bps = bytes_recv_diff / time_diff

        sent_rate_kbs = sent_rate_bps / 1024
        recv_rate_kbs = recv_rate_bps / 1024

        self._last_net_io_counters = current_net_io
        self._last_net_io_time = current_time

        return {
            "bytes_sent_rate_kbs": sent_rate_kbs,
            "bytes_recv_rate_kbs": recv_rate_kbs
        }

    def get_processes_info(self):
        processes_list = []
        attrs_to_get = ['pid', 'name', 'status', 'num_threads', 'cpu_percent', 'memory_info', 'username', 'create_time']
        
        for proc in psutil.process_iter(attrs=attrs_to_get):
            try:
                pinfo = proc.info
                
                if pinfo is None:
                    continue

                cpu_percent = proc.cpu_percent(interval=0.01) # Kleiner Interval, um aktuelle Nutzung zu bekommen
                mem_info = proc.memory_info()

                if mem_info is None:
                    memory_rss_mb = 0.0
                    memory_vms_mb = 0.0
                else:
                    memory_rss_mb = round(mem_info.rss / (1024**2), 2)
                    memory_vms_mb = round(mem_info.vms / (1024**2), 2)


                processes_list.append({
                    "pid": pinfo.get('pid'),
                    "name": pinfo.get('name'),
                    "status": pinfo.get('status'),
                    "num_threads": pinfo.get('num_threads'),
                    "cpu_percent": cpu_percent,
                    "memory_rss_mb": memory_rss_mb,
                    "memory_vms_mb": memory_vms_mb,
                    "username": pinfo.get('username'),
                    "create_time": datetime.fromtimestamp(pinfo.get('create_time')).strftime("%Y-%m-%d %H:%M:%S")
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError) as e:
                # print(f"Fehler beim Abrufen der Prozess-Info für PID {proc.pid}: {e}")
                continue
            except Exception as e:
                # print(f"Unerwarteter Fehler beim Abrufen der Prozess-Info für PID {proc.pid}: {e}")
                continue

        processes_list.sort(key=lambda x: x.get('cpu_percent', 0.0), reverse=True)
        
        return processes_list

    def get_installed_programs(self):
        programs = []
        if platform.system() == "Windows":
            try:
                import winreg # winreg ist nur unter Windows verfügbar
                keys = [
                    winreg.HKEY_LOCAL_MACHINE,
                    winreg.HKEY_CURRENT_USER
                ]
                sub_keys = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
                ]

                for key in keys:
                    for sub_key in sub_keys:
                        try:
                            with winreg.OpenKey(key, sub_key) as reg_key:
                                i = 0
                                while True:
                                    try:
                                        program_guid = winreg.EnumKey(reg_key, i)
                                        with winreg.OpenKey(reg_key, program_guid) as program_key:
                                            display_name = winreg.QueryValueEx(program_key, "DisplayName")[0]
                                            if display_name and display_name not in programs: # Prüfe auf leere Namen
                                                programs.append(display_name)
                                    except OSError:
                                        break
                                    i += 1
                        except FileNotFoundError:
                            continue
            except ImportError:
                # print("Warnung: winreg Modul nicht gefunden (nur für Windows).")
                pass
            except Exception as e:
                # print(f"Fehler beim Abrufen der installierten Programme unter Windows: {e}")
                pass

        elif platform.system() == "Darwin": # macOS
            app_paths = [
                "/Applications",
                os.path.expanduser("~/Applications")
            ]
            for app_path in app_paths:
                if os.path.exists(app_path):
                    for item in os.listdir(app_path):
                        if item.endswith(".app"):
                            programs.append(item.replace(".app", ""))
        elif platform.system() == "Linux":
            # Unter Linux ist es komplexer. Eine einfache Lösung:
            # Man könnte 'dpkg-query' (Debian/Ubuntu), 'rpm' (RedHat/Fedora)
            # oder nach .desktop-Dateien suchen. Dies ist ein Placeholder.
            programs.append("Linux: Programmliste ist komplex und nicht implementiert.") # Placeholder
        
        programs.sort()
        return programs

    def get_system_snapshot(self):
        cpu_info = self.get_cpu_info()
        mem_info = self.get_memory_info()
        net_info = self.get_network_info()

        cpu_percent = cpu_info.get("total_percent", 0.0)
        ram_percent = mem_info.get("ram_percent", 0.0)
        ram_used_gb = mem_info.get("used_ram_gb", 0.0)
        bytes_sent_gb = net_info.get("Bytes Sent (GB)", 0.0)
        bytes_recv_gb = net_info.get("Bytes Received (GB)", 0.0)

        snapshot = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_percent": cpu_percent,
            "ram_percent": ram_percent,
            "ram_used_gb": ram_used_gb,
            "bytes_sent_gb": bytes_sent_gb,
            "bytes_recv_gb": bytes_recv_gb
        }
        return snapshot