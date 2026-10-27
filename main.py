import os, sys, json, shutil, platform, subprocess, tempfile, webbrowser, threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_NAME = "PC NEXUS ULTIMATE"
VERSION = "2.0.0"
APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "PCNexus"
APP_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = APP_DIR / "pc_nexus.log"
SETTINGS_FILE = APP_DIR / "settings.json"
BACKUP_DIR = APP_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

def log(msg):
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\\n")
    except OSError:
        pass

def cmd(args, timeout=20):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, shell=False,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()
    except Exception as e:
        return 1, str(e)

def fmt_bytes(n):
    try: n = float(n)
    except (TypeError, ValueError): return "—"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB": return f"{n:.1f} {unit}"
        n /= 1024

def admin():
    try:
        import ctypes
        return os.name == "nt" and bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: return False

def open_target(target):
    try:
        if target.startswith(("ms-settings:", "windowsdefender:", "shell:")):
            os.startfile(target)
        elif target.lower().endswith(".msc"):
            subprocess.Popen(["mmc.exe", target], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        elif target.startswith("cmd:"):
            subprocess.Popen(["cmd.exe", "/k", target[4:]])
        elif target.startswith("powershell:"):
            subprocess.Popen(["powershell.exe", "-NoExit", "-NoProfile", "-Command", target[11:]])
        elif target.lower() in {"taskmgr","resmon","msinfo32","perfmon","dxdiag","cleanmgr","winver","regedit",
                                "devmgmt.msc","diskmgmt.msc","services.msc","eventvwr.msc","taskschd.msc",
                                "wf.msc","certmgr.msc","appwiz.cpl","powercfg.cpl","ncpa.cpl",
                                "systempropertiesprotection","control","optionalfeatures"}:
            subprocess.Popen([target], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        elif target.startswith("shell-open:"):
            os.startfile(target[11:])
        else:
            os.startfile(target)
        log(f"Opened {target}")
    except Exception as e:
        messagebox.showerror("Не удалось открыть", f"{target}\\n\\n{e}")

class NexusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} — Windows Toolkit")
        self.geometry("1120x760")
        self.minsize(920, 640)
        self.configure(bg="#10141d")
        self.settings = self.load_settings()
        self.style_setup()
        self.build()
        self.refresh_system()

    def load_settings(self):
        try: return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception: return {"theme":"dark"}

    def style_setup(self):
        s = ttk.Style(self)
        try: s.theme_use("clam")
        except tk.TclError: pass
        s.configure(".", font=("Segoe UI", 10))
        s.configure("TFrame", background="#10141d")
        s.configure("Panel.TFrame", background="#1a2230")
        s.configure("TLabel", background="#10141d", foreground="#e7edf7")
        s.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), foreground="#72e0ed")
        s.configure("Sub.TLabel", foreground="#9cabc0")
        s.configure("TButton", padding=(9,7), background="#28364a", foreground="#f4f7fb")
        s.map("TButton", background=[("active","#3a4c65")])
        s.configure("Accent.TButton", padding=(11,8), background="#087e8b", foreground="white")
        s.map("Accent.TButton", background=[("active","#0a9baa")])
        s.configure("Treeview", background="#1a2230", foreground="#e7edf7", fieldbackground="#1a2230", rowheight=26)
        s.configure("Treeview.Heading", background="#28364a", foreground="#e7edf7")
        s.configure("TNotebook", background="#10141d", borderwidth=0)
        s.configure("TNotebook.Tab", background="#202b3b", foreground="#e7edf7", padding=(12,8))
        s.map("TNotebook.Tab", background=[("selected","#087e8b")])

    def build(self):
        header = ttk.Frame(self, padding=(20,14)); header.pack(fill="x")
        ttk.Label(header,text="PC NEXUS ULTIMATE",style="Title.TLabel").pack(side="left")
        ttk.Label(header,text=f"v{VERSION}  •  Gaming + Windows + Tools",style="Sub.TLabel").pack(side="left",padx=14,pady=(8,0))
        self.admin_tag = ttk.Label(header,text=("ADMIN" if admin() else "Обычный запуск"),style="Sub.TLabel")
        self.admin_tag.pack(side="right",pady=(8,0))
        self.tabs = ttk.Notebook(self); self.tabs.pack(fill="both",expand=True,padx=16,pady=(0,12))
        self.pages = {}
        for key,title in [("home","Обзор"),("gaming","Gaming"),("clean","Очистка"),("hardware","Железо"),("network","Сеть"),
                          ("windows","Windows"),("privacy","Приватность"),("secret","Секретная комната")]:
            frame=ttk.Frame(self.tabs,padding=16); self.tabs.add(frame,text=title); self.pages[key]=frame
        self.build_home(); self.build_gaming(); self.build_clean(); self.build_hardware()
        self.build_network(); self.build_windows(); self.build_privacy(); self.build_secret()
        foot=ttk.Frame(self,padding=(16,0,16,8)); foot.pack(fill="x")
        ttk.Label(foot,text=f"Журнал: {LOG_FILE}",style="Sub.TLabel").pack(side="left")
        ttk.Button(foot,text="Открыть журнал",command=lambda: open_target(str(LOG_FILE))).pack(side="right")

    def section(self,p,title,sub):
        ttk.Label(p,text=title,style="Title.TLabel").pack(anchor="w",pady=(0,4))
        ttk.Label(p,text=sub,style="Sub.TLabel",wraplength=980).pack(anchor="w",pady=(0,12))

    def button_grid(self,p,items,cols=3):
        grid=ttk.Frame(p); grid.pack(fill="x",pady=4)
        for i,(label,fn) in enumerate(items):
            ttk.Button(grid,text=label,command=fn).grid(row=i//cols,column=i%cols,sticky="ew",padx=4,pady=4)
        for c in range(cols): grid.columnconfigure(c,weight=1)

    def build_home(self):
        p=self.pages["home"]; self.section(p,"Панель управления","Сводка о ПК и быстрый запуск системных инструментов.")
        cards=ttk.Frame(p); cards.pack(fill="x",pady=4); self.cards={}
        for key,title in [("os","Windows"),("cpu","Процессор"),("ram","ОЗУ"),("disk","Диск"),("gpu","Видеокарта")]:
            card=ttk.Frame(cards,style="Panel.TFrame",padding=12); card.pack(side="left",fill="both",expand=True,padx=4)
            ttk.Label(card,text=title,style="Sub.TLabel").pack(anchor="w")
            lab=ttk.Label(card,text="Сбор данных…",background="#1a2230",wraplength=150); lab.pack(anchor="w",pady=(7,0))
            self.cards[key]=lab
        self.button_grid(p,[("Обновить сводку",self.refresh_system),("Диспетчер задач",lambda:open_target("taskmgr")),
            ("Монитор ресурсов",lambda:open_target("resmon")),("Сведения о системе",lambda:open_target("msinfo32")),
            ("Защита системы / точки восстановления",lambda:open_target("systempropertiesprotection")),("Параметры Windows",lambda:open_target("ms-settings:"))],3)
        self.home_report=tk.Text(p,height=14,bg="#1a2230",fg="#e7edf7",insertbackground="white",relief="flat",wrap="word",padx=12,pady=12)
        self.home_report.pack(fill="both",expand=True,pady=8)

    def refresh_system(self):
        self.cards["os"].configure(text=f"{platform.system()} {platform.release()}")
        self.cards["cpu"].configure(text=platform.processor() or os.getenv("PROCESSOR_IDENTIFIER","Не определён"))
        try:
            import psutil
            mem=psutil.virtual_memory(); disk=psutil.disk_usage(os.getenv("SystemDrive","C:")+"\\\\")
            cpu=psutil.cpu_percent(interval=0.2)
            self.cards["ram"].configure(text=f"{mem.percent}% занято\\n{fmt_bytes(mem.available)} свободно")
            self.cards["disk"].configure(text=f"{disk.percent}% занято\\n{fmt_bytes(disk.free)} свободно")
            detail=f"Загрузка CPU: {cpu}%\\nОЗУ: {fmt_bytes(mem.used)} / {fmt_bytes(mem.total)}\\nДоступно ОЗУ: {fmt_bytes(mem.available)}"
        except Exception:
            detail="Для подробной статистики установи зависимости: py -m pip install -r requirements.txt"
            self.cards["ram"].configure(text="Нет psutil"); self.cards["disk"].configure(text="Нет psutil")
        code,out=cmd(["powershell","-NoProfile","-Command","Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"])
        self.cards["gpu"].configure(text=(out.splitlines()[0] if code==0 and out else "Не определена")[:90])
        self.home_report.delete("1.0","end")
        self.home_report.insert("end",f"Система: {platform.platform()}\\nАрхитектура: {platform.machine()}\\nPython: {sys.version.split()[0]}\\n"
             f"{detail}\\n\\nРекомендации:\\n• Проверь температуры и загрузку во время игры.\\n"
             "• Убирай приложения из автозагрузки только если понимаешь, что это за программа.\\n"
             "• Создай точку восстановления перед системными изменениями.\\n"
             "• Прирост FPS не гарантируется: он зависит от железа, драйверов и игры.")
        log("System overview refreshed")

    def build_gaming(self):
        p=self.pages["gaming"]; self.section(p,"Gaming Center","Быстрые переходы к игровым настройкам Windows и полезным диагностическим инструментам.")
        self.button_grid(p,[
            ("Игровой режим",lambda:open_target("ms-settings:gaming-gamemode")),
            ("Настройки графики / GPU",lambda:open_target("ms-settings:display-advancedgraphics")),
            ("Xbox Game Bar",lambda:open_target("ms-settings:gaming-gamebar")),
            ("Питание",lambda:open_target("powercfg.cpl")),
            ("Автозагрузка",lambda:open_target("ms-settings:startupapps")),
            ("Экран / герцовка",lambda:open_target("ms-settings:display-advanced")),
            ("Звук и микрофон",lambda:open_target("ms-settings:sound")),
            ("DirectX Diagnostic",lambda:open_target("dxdiag")),
            ("Диспетчер задач",lambda:open_target("taskmgr")),
            ("Очистка диска",lambda:open_target("cleanmgr")),
            ("Параметры записи игр",lambda:open_target("ms-settings:gaming-captures")),
            ("Открыть план электропитания",lambda:open_target("powercfg.cpl"))
        ],3)
        note=ttk.LabelFrame(p,text="Профиль «Перед игрой»",padding=12); note.pack(fill="x",pady=12)
        ttk.Label(note,text="Открывает игровые настройки для ручной проверки; ничего не меняет автоматически.").pack(anchor="w",pady=(0,8))
        ttk.Button(note,text="Открыть игровые настройки по очереди",style="Accent.TButton",
                   command=lambda:self.sequence(["ms-settings:gaming-gamemode","ms-settings:display-advancedgraphics","ms-settings:startupapps"])).pack(anchor="w")
        ttk.Label(p,text="Совет: для измерения FPS используй встроенный оверлей игры или проверенное ПО. Температуры датчиков зависят от поддержки оборудования.",style="Sub.TLabel",wraplength=950).pack(anchor="w",pady=8)

    def sequence(self,items):
        for item in items: open_target(item)

    def build_clean(self):
        p=self.pages["clean"]; self.section(p,"Очистка и дисковое пространство","Сначала анализ, затем действие с подтверждением. Чистится только временная папка текущего пользователя.")
        self.button_grid(p,[("Посчитать временные файлы",self.scan_temp),("Очистить временную папку",self.clean_temp),
            ("Очистка диска Windows",lambda:open_target("cleanmgr")),("Открыть корзину",lambda:open_target("shell-open:shell:RecycleBinFolder")),
            ("Папка загрузок",lambda:open_target(str(Path.home()/"Downloads"))),("Анализатор хранилища Windows",lambda:open_target("ms-settings:storagesense"))],3)
        self.clean_out=tk.Text(p,bg="#1a2230",fg="#e7edf7",insertbackground="white",relief="flat",wrap="word",padx=12,pady=12)
        self.clean_out.pack(fill="both",expand=True,pady=10)
        self.clean_out.insert("end","Нажми «Посчитать временные файлы». Файлы, используемые приложениями, могут быть пропущены.")

    def scan_temp(self):
        self.clean_out.delete("1.0","end"); self.clean_out.insert("end","Сканирование временных файлов…"); self.update_idletasks()
        root=Path(tempfile.gettempdir()); count=size=errors=0
        for f in root.rglob("*"):
            try:
                if f.is_file(): count+=1; size+=f.stat().st_size
            except OSError: errors+=1
        self.clean_out.delete("1.0","end"); self.clean_out.insert("end",f"Каталог: {root}\\nФайлов: {count}\\nОбъём: {fmt_bytes(size)}\\nПропущено: {errors}")
        log(f"Temp scan count={count} size={size}")

    def clean_temp(self):
        if not messagebox.askyesno("Подтверждение","Удалить доступные файлы из временной папки пользователя? Файлы, занятые приложениями, останутся."):
            return
        root=Path(tempfile.gettempdir()); count=size=errors=0
        for f in root.iterdir():
            try:
                if f.is_file() or f.is_symlink():
                    n=f.stat().st_size if f.is_file() else 0; f.unlink(); count+=1; size+=n
                elif f.is_dir():
                    for sub in f.rglob("*"):
                        try:
                            if sub.is_file() or sub.is_symlink():
                                n=sub.stat().st_size if sub.is_file() else 0; sub.unlink(); count+=1; size+=n
                        except OSError: errors+=1
                    for sub in sorted(f.rglob("*"),key=lambda x:len(x.parts),reverse=True):
                        try:
                            if sub.is_dir(): sub.rmdir()
                        except OSError: pass
                    try: f.rmdir()
                    except OSError: pass
            except OSError: errors+=1
        self.clean_out.delete("1.0","end"); self.clean_out.insert("end",f"Готово. Удалено файлов: {count}\\nОсвобождено примерно: {fmt_bytes(size)}\\nОшибок/пропусков: {errors}")
        log(f"Temp cleanup count={count} size={size} errors={errors}")

    def build_hardware(self):
        p=self.pages["hardware"]; self.section(p,"Hardware Lab","Мониторинг базовых показателей и ярлыки для диагностики железа.")
        self.button_grid(p,[("Обновить показатели",self.refresh_system),("Диспетчер устройств",lambda:open_target("devmgmt.msc")),
            ("Управление дисками",lambda:open_target("diskmgmt.msc")),("Монитор ресурсов",lambda:open_target("resmon")),
            ("Монитор производительности",lambda:open_target("perfmon")),("Диагностика DirectX",lambda:open_target("dxdiag")),
            ("Отчёт батареи",self.battery_report),("Сведения о системе",lambda:open_target("msinfo32")),
            ("Диспетчер задач",lambda:open_target("taskmgr"))],3)
        ttk.Label(p,text="Температуры GPU/CPU не читаются напрямую во всех системах: для этого нужен совместимый источник датчиков. Не отключай защитное термоуправление.",style="Sub.TLabel",wraplength=950).pack(anchor="w",pady=12)

    def battery_report(self):
        out=Path.home()/"battery-report.html"; code,msg=cmd(["powercfg","/batteryreport","/output",str(out)])
        if code==0 and out.exists(): messagebox.showinfo("Батарея",f"Отчёт сохранён: {out}"); open_target(str(out))
        else: messagebox.showwarning("Батарея",msg or "Отчёт недоступен на этом устройстве.")

    def build_network(self):
        p=self.pages["network"]; self.section(p,"Network Lab","Диагностика подключения, DNS и IP. Сброс Winsock может повлиять на VPN и потребовать перезагрузки.")
        self.button_grid(p,[("Параметры сети",lambda:open_target("ms-settings:network-status")),
            ("Сетевые адаптеры",lambda:open_target("ncpa.cpl")),("Ping 1.1.1.1",lambda:self.net_action("Ping",["ping","-n","4","1.1.1.1"])),
            ("Проверить DNS",lambda:self.net_action("DNS",["nslookup","example.com"])),
            ("Очистить DNS-кэш",self.flush_dns),("IP-конфигурация",lambda:self.net_action("IP config",["ipconfig","/all"])),
            ("Сброс Winsock",self.reset_winsock),("Открыть брандмауэр",lambda:open_target("wf.msc"))],2)
        self.net_out=tk.Text(p,bg="#1a2230",fg="#e7edf7",insertbackground="white",relief="flat",wrap="word",padx=12,pady=12)
        self.net_out.pack(fill="both",expand=True,pady=10)

    def net_action(self,title,args):
        self.net_out.delete("1.0","end"); self.net_out.insert("end",f"{title}…"); self.update_idletasks()
        code,out=cmd(args,timeout=25); self.net_out.delete("1.0","end")
        self.net_out.insert("end",f"{title} | exit={code}\\n\\n{out[:16000]}"); log(f"Network {title}: exit={code}")

    def flush_dns(self):
        if messagebox.askyesno("DNS","Очистить локальный DNS-кэш?"): self.net_action("Очистка DNS",["ipconfig","/flushdns"])

    def reset_winsock(self):
        if not admin():
            messagebox.showwarning("Нужен администратор","Перезапусти PC NEXUS от имени администратора для сброса Winsock."); return
        if messagebox.askyesno("Сброс Winsock","Это меняет сетевую конфигурацию; может потребоваться перезагрузка и настройка VPN. Продолжить?"):
            self.net_action("Winsock reset",["netsh","winsock","reset"])
            messagebox.showinfo("Сброс сети","Если команда прошла успешно, перезагрузи ПК.")

    def build_windows(self):
        p=self.pages["windows"]; self.section(p,"Windows Toolkit","Панель системных утилит, восстановления, журналов и настроек.")
        self.button_grid(p,[("Службы Windows",lambda:open_target("services.msc")),("Просмотр событий",lambda:open_target("eventvwr.msc")),
            ("Планировщик заданий",lambda:open_target("taskschd.msc")),("Редактор реестра",lambda:open_target("regedit")),
            ("Установленные программы",lambda:open_target("appwiz.cpl")),("Доп. компоненты Windows",lambda:open_target("optionalfeatures")),
            ("Защита системы",lambda:open_target("systempropertiesprotection")),("Параметры восстановления",lambda:open_target("ms-settings:recovery")),
            ("Обновление Windows",lambda:open_target("ms-settings:windowsupdate")),("Параметры запуска",lambda:open_target("ms-settings:startupapps")),
            ("Проверка SFC",self.run_sfc),("DISM CheckHealth",self.run_dism)],3)
        ttk.Label(p,text="SFC/DISM запускаются в отдельном окне командной строки. Для ремонта могут потребоваться права администратора и интернет.",style="Sub.TLabel",wraplength=950).pack(anchor="w",pady=10)

    def run_sfc(self):
        if messagebox.askyesno("SFC","Запустить проверку системных файлов sfc /scannow?"):
            open_target("cmd:sfc /scannow")

    def run_dism(self):
        if messagebox.askyesno("DISM","Запустить DISM /Online /Cleanup-Image /CheckHealth?"):
            open_target("cmd:DISM /Online /Cleanup-Image /CheckHealth")

    def build_privacy(self):
        p=self.pages["privacy"]; self.section(p,"Privacy Center","Быстрые ссылки на настройки приватности. Решения о разрешениях остаются за пользователем.")
        self.button_grid(p,[("Общие разрешения",lambda:open_target("ms-settings:privacy")),
            ("Местоположение",lambda:open_target("ms-settings:privacy-location")),
            ("Камера",lambda:open_target("ms-settings:privacy-webcam")),
            ("Микрофон",lambda:open_target("ms-settings:privacy-microphone")),
            ("Фоновые приложения / разрешения",lambda:open_target("ms-settings:privacy-backgroundapps")),
            ("Диагностика и отзывы",lambda:open_target("ms-settings:privacy-feedback")),
            ("Защита Windows",lambda:open_target("windowsdefender:")),
            ("Брандмауэр",lambda:open_target("wf.msc"))],2)
        ttk.Label(p,text="Приложение намеренно не отключает Defender, UAC, брандмауэр или обновления безопасности.",style="Sub.TLabel",wraplength=950).pack(anchor="w",pady=12)

    def build_secret(self):
        p=self.pages["secret"]; self.section(p,"Секретная комната","Продвинутые ярлыки и пасхалки. «God Mode» — коллекция системных ссылок Windows, а не магический ускоритель.")
        self.button_grid(p,[("Создать / открыть God Mode",self.god_mode),("Папка профиля",lambda:open_target(str(Path.home()))),
            ("AppData",lambda:open_target(os.getenv("APPDATA",str(Path.home())))),("Temp",lambda:open_target(tempfile.gettempdir())),
            ("Папка автозагрузки",lambda:open_target("shell:startup")),("Отчёт батареи",self.battery_report),
            ("Экспорт системного отчёта",self.export_report),("Открыть GitHub",lambda:webbrowser.open("https://github.com/")),
            ("Просмотр событий",lambda:open_target("eventvwr.msc")),("Winver",lambda:open_target("winver"))],2)
        ttk.Label(p,text="Пасхалка: нажми на заголовок PC NEXUS пять раз 😉",style="Sub.TLabel").pack(anchor="w",pady=12)
        self.secret_clicks=0
        # Bind title label by adding a hidden easter-egg trigger to the root title.
        self.bind_title_egg()

    def bind_title_egg(self):
        for child in self.winfo_children():
            if isinstance(child,ttk.Frame):
                for sub in child.winfo_children():
                    if isinstance(sub,ttk.Label) and "PC NEXUS" in str(sub.cget("text")):
                        sub.bind("<Button-1>",self.title_egg)

    def title_egg(self,event=None):
        self.secret_clicks+=1
        if self.secret_clicks>=5:
            messagebox.showinfo("Пасхалка","NEXUS LEVEL UNLOCKED ✦\\nТы нашёл секретную комнату. Удачной игры!")
            self.secret_clicks=0

    def god_mode(self):
        desktop=Path(os.getenv("USERPROFILE",str(Path.home())))/"Desktop"
        if not desktop.exists(): desktop=Path.home()
        folder=desktop/"God Mode.{ED7BA470-8E54-465E-825C-99712043E01C}"
        try: folder.mkdir(exist_ok=True); open_target(str(folder))
        except OSError as e: messagebox.showerror("God Mode",str(e))

    def export_report(self):
        path=filedialog.asksaveasfilename(title="Сохранить отчёт",defaultextension=".txt",initialfile="pc_nexus_report.txt",
                                          filetypes=[("Text","*.txt"),("JSON","*.json")])
        if not path:return
        report={"app":APP_NAME,"version":VERSION,"generated":datetime.now().isoformat(),"os":platform.platform(),
                "machine":platform.machine(),"processor":platform.processor(),"python":sys.version}
        try:
            import psutil
            m=psutil.virtual_memory(); d=psutil.disk_usage(os.getenv("SystemDrive","C:")+"\\\\")
            report["memory"]={"total":m.total,"available":m.available,"percent":m.percent}
            report["system_disk"]={"total":d.total,"free":d.free,"percent":d.percent}
        except Exception: pass
        if path.lower().endswith(".json"): Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        else: Path(path).write_text("\\n".join(f"{k}: {v}" for k,v in report.items()),encoding="utf-8")
        messagebox.showinfo("Экспорт",f"Отчёт сохранён:\\n{path}"); log(f"Report exported: {path}")

if __name__=="__main__":
    if os.name!="nt":
        print("PC NEXUS ULTIMATE рассчитан на Windows 10/11.")
    NexusApp().mainloop()
