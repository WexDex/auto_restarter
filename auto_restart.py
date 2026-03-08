import tkinter as tk
from tkinter import messagebox, filedialog
import datetime
import os
import json
import subprocess

CONFIG_FILE = "config.json"
LOG_FILE = "restart_log.txt"

class AutoRestartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatic PC Restart")
        self.root.geometry("1100x520")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)
        
        self.unsaved_changes = False

        self.restart_hour = 0
        self.restart_minute = 0

        self.backend_hours = 1
        self.process_name = ""
        self.process_path = ""

        self.backend_next_restart = None
        
        self.backend_enabled = True

        self.load_config()
        self.create_ui()

        self.update_pc_countdown()
        self.update_backend_countdown()

    # ---------------- CONFIG ---------------- #

    def load_config(self):

        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)

                self.restart_hour = data.get("hour", 0)
                self.restart_minute = data.get("minute", 0)

                self.backend_hours = data.get("backend_hours", 1)
                self.process_name = data.get("process_name", "")
                self.process_path = data.get("process_path", "")
        else:
            self.save_config()

        self.backend_next_restart = datetime.datetime.now() + datetime.timedelta(hours=self.backend_hours)

    def save_config(self):

        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "hour": self.restart_hour,
                "minute": self.restart_minute,
                "backend_hours": self.backend_hours,
                "process_name": self.process_name,
                "process_path": self.process_path,
                "backend_enabled": self.backend_enabled
            }, f, indent=4)

    # ---------------- UI ---------------- #

    def create_ui(self):

        main = tk.Frame(self.root, bg="#1e1e1e")
        main.pack(fill="both", expand=True)

        left = tk.Frame(main, bg="#1e1e1e")
        left.pack(side="left", fill="both", expand=True, padx=30)

        right = tk.Frame(main, bg="#1e1e1e")
        right.pack(side="right", fill="both", expand=True, padx=30)

        # ---------- LEFT PANEL (PC RESTART) ---------- #

        title = tk.Label(left,text="PC AUTO RESTART",font=("Segoe UI",24,"bold"),bg="#1e1e1e",fg="white")
        title.pack(pady=20)

        time_frame = tk.Frame(left,bg="#1e1e1e")
        time_frame.pack()

        tk.Label(time_frame,text="Restart Time:",font=("Segoe UI",14),bg="#1e1e1e",fg="#ccc").pack(side="left")

        self.hour_entry = tk.Entry(time_frame,width=4,font=("Segoe UI",16),justify="center")
        self.hour_entry.pack(side="left")
        self.hour_entry.insert(0,f"{self.restart_hour:02d}")

        tk.Label(time_frame,text=":",font=("Segoe UI",16),bg="#1e1e1e",fg="white").pack(side="left")

        self.minute_entry = tk.Entry(time_frame,width=4,font=("Segoe UI",16),justify="center")
        self.minute_entry.pack(side="left")
        self.minute_entry.insert(0,f"{self.restart_minute:02d}")

        btn_frame = tk.Frame(left,bg="#1e1e1e")
        btn_frame.pack(pady=15)

        tk.Button(btn_frame,text="Save Time",command=self.update_time,bg="#4caf50",fg="white",width=12).pack(side="left",padx=10)

        tk.Button(btn_frame,text="View Logs",command=self.open_logs,bg="#2196f3",fg="white",width=12).pack(side="left",padx=10)

        tk.Label(left,text="TEMPS RESTANT",font=("Segoe UI",28,"bold"),bg="#1e1e1e",fg="white").pack()

        self.countdown_label = tk.Label(left,text="00:00:00",font=("Segoe UI",50,"bold"),bg="#1e1e1e",fg="#00e676")
        self.countdown_label.pack(pady=25)

        # ---------- RIGHT PANEL (BACKEND RESTART) ---------- #

        title2 = tk.Label(right,text="BACKEND AUTO RESTART",font=("Segoe UI",24,"bold"),bg="#1e1e1e",fg="white")
        title2.pack(pady=20)
        
        toggle_frame = tk.Frame(right, bg="#1e1e1e")
        toggle_frame.pack(pady=6)

        self.backend_toggle_btn = tk.Button(
            toggle_frame,
            text="Disable Backend Restart" if self.backend_enabled else "Enable Backend Restart",
            font=("Segoe UI", 11),
            command=self.toggle_backend,
            bg="#b33a3a" if self.backend_enabled else "#3a7fb3",
            fg="white",
            width=20
        )

        self.backend_toggle_btn.pack(side="left", padx=10)

        self.backend_status_label = tk.Label(
            toggle_frame,
            text="ACTIVE" if self.backend_enabled else "STOPPED",
            font=("Segoe UI", 12, "bold"),
            fg="#00e676" if self.backend_enabled else "#ff5252",
            bg="#1e1e1e"
        )

        self.backend_status_label.pack(side="left")

        hours_frame = tk.Frame(right,bg="#1e1e1e")
        hours_frame.pack(pady=5)

        tk.Label(hours_frame,text="Restart every (hours):",font=("Segoe UI",12),bg="#1e1e1e",fg="#ccc").pack(side="left")

        self.backend_hours_entry = tk.Entry(hours_frame,width=5,font=("Segoe UI",14))
        self.backend_hours_entry.pack(side="left",padx=10)
        self.backend_hours_entry.insert(0,str(self.backend_hours))

        name_frame = tk.Frame(right,bg="#1e1e1e")
        name_frame.pack(pady=5)

        tk.Label(name_frame,text="Process Name:",font=("Segoe UI",12),bg="#1e1e1e",fg="#ccc").pack(side="left")

        self.process_name_entry = tk.Entry(name_frame,width=25)
        self.process_name_entry.pack(side="left",padx=10)
        self.process_name_entry.insert(0,self.process_name)
        
        tk.Label(name_frame,text="default : electron.exe",font=("Segoe UI",9),bg="#1e1e1e",fg="#ccc").pack(side="right")

        path_frame = tk.Frame(right,bg="#1e1e1e")
        path_frame.pack(pady=5)

        tk.Label(path_frame,text="Process Path:",font=("Segoe UI",12),bg="#1e1e1e",fg="#ccc").pack(side="left")

        self.process_path_entry = tk.Entry(path_frame,width=50)
        self.process_path_entry.pack(side="left",padx=5)
        self.process_path_entry.insert(0,self.process_path)

        tk.Button(
            path_frame,
            text="Browse",
            command=self.browse_process,
            bg="#555",
            fg="white",
            width=8
        ).pack(side="left", padx=5)

        btn_frame2 = tk.Frame(right,bg="#1e1e1e")
        btn_frame2.pack(pady=15)

        tk.Button(btn_frame2,text="Save",command=self.save_backend,bg="#4caf50",fg="white",width=12).pack(side="left",padx=10)

        tk.Button(btn_frame2,text="Restart Now",command=self.restart_backend_now,bg="#ff9800",fg="white",width=12).pack(side="left",padx=10)

        tk.Button(btn_frame2,text="View Logs",command=self.open_logs,bg="#2196f3",fg="white",width=12).pack(side="left",padx=10)
        
        self.process_name_entry.bind("<KeyRelease>", self.mark_unsaved)
        self.process_path_entry.bind("<KeyRelease>", self.mark_unsaved)
        self.backend_hours_entry.bind("<KeyRelease>", self.mark_unsaved)
        
        self.unsaved_label = tk.Label(
            right,
            text="",
            font=("Segoe UI", 10),
            bg="#1e1e1e",
            fg="#ffcc00"
        )
        self.unsaved_label.pack(pady=2)

        tk.Label(right,text="NEXT BACKEND RESTART",font=("Segoe UI",18,"bold"),bg="#1e1e1e",fg="white").pack()

        self.backend_timer = tk.Label(right,text="00:00:00",font=("Segoe UI",36,"bold"),bg="#1e1e1e",fg="#00e676")
        self.backend_timer.pack(pady=25)

    # ---------------- PC TIMER ---------------- #

    def update_time(self):

        try:

            self.restart_hour = int(self.hour_entry.get())
            self.restart_minute = int(self.minute_entry.get())

            self.save_config()

            messagebox.showinfo("Saved","Restart time updated")

        except:
            messagebox.showerror("Error","Invalid time")

    def get_next_restart(self):

        now = datetime.datetime.now()

        target = now.replace(hour=self.restart_hour,minute=self.restart_minute,second=0,microsecond=0)

        if target <= now:
            target += datetime.timedelta(days=1)

        return target

    def update_pc_countdown(self):

        target = self.get_next_restart()

        remaining = target - datetime.datetime.now()

        total = int(remaining.total_seconds())

        if total <= 0:
            self.log("PC Restart")
            os.system("shutdown /r /t 0")
            return

        h = total//3600
        m = (total%3600)//60
        s = total%60

        self.countdown_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")

        self.root.after(1000,self.update_pc_countdown)

    # ---------------- BACKEND ---------------- #

    def save_backend(self):

        try:

            self.backend_hours = int(self.backend_hours_entry.get())
            self.process_name = self.process_name_entry.get()
            self.process_path = self.process_path_entry.get()

            self.backend_next_restart = datetime.datetime.now()+datetime.timedelta(hours=self.backend_hours)

            self.save_config()
            
            self.unsaved_changes = False
            self.unsaved_label.config(text="")

            messagebox.showinfo("Saved","Backend config saved")

        except:
            messagebox.showerror("Error","Invalid backend settings")
            
    def restart_backend_now(self):
        if self.unsaved_changes:

            answer = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes.\n\nSave before restarting?"
            )

            if answer is None:
                return

            if answer:
                self.save_backend()

        self.restart_backend()
    
    def restart_backend(self):
        if not self.backend_enabled:
            return
        try:

            if self.process_name:
                os.system(f"taskkill /f /im {self.process_name}")

            if self.process_path:

                process_dir = os.path.dirname(self.process_path)

                if self.process_path.lower().endswith(".bat"):
                    subprocess.Popen(
                        ["cmd", "/c", self.process_path],
                        cwd=process_dir
                    )
                else:
                    subprocess.Popen(
                        self.process_path,
                        cwd=process_dir
                    )

            self.backend_next_restart = datetime.datetime.now()+datetime.timedelta(hours=self.backend_hours)

            self.log("Backend Restart")

        except Exception as e:
            messagebox.showerror("Error",str(e))
            
    def toggle_backend(self):

        self.backend_enabled = not self.backend_enabled

        if self.backend_enabled:

            self.backend_toggle_btn.config(
                text="Disable Backend Restart",
                bg="#b33a3a"
            )

            self.backend_status_label.config(
                text="ACTIVE",
                fg="#00e676"
            )

            self.backend_timer.config(fg="#00e676")

            self.log("Backend auto restart ENABLED")

        else:

            self.backend_toggle_btn.config(
                text="Enable Backend Restart",
                bg="#3a7fb3"
            )

            self.backend_status_label.config(
                text="STOPPED",
                fg="#ff5252"
            )

            self.backend_timer.config(
                text="STOPPED",
                fg="#ff5252"
            )

            self.log("Backend auto restart DISABLED")

        self.save_config()

    def update_backend_countdown(self):
        if not self.backend_enabled:
            self.backend_timer.config(
                text="STOPPED",
                fg="#ff5252"
            )
            self.root.after(1000, self.update_backend_countdown)
            return
        remaining = self.backend_next_restart - datetime.datetime.now()

        total = int(remaining.total_seconds())

        if total <= 0:
            self.restart_backend()

        h = total//3600
        m = (total%3600)//60
        s = total%60

        self.backend_timer.config(text=f"{h:02d}:{m:02d}:{s:02d}")

        self.root.after(1000,self.update_backend_countdown)
        
    def browse_process(self):

        file_path = filedialog.askopenfilename(
            title="Select Backend Program",
            filetypes=[
                ("Executable or Batch", "*.exe *.bat"),
                ("Executable Files", "*.exe"),
                ("Batch Files", "*.bat"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self.process_path_entry.delete(0, tk.END)
            self.process_path_entry.insert(0, file_path)
            
    def mark_unsaved(self, event=None):

        self.unsaved_changes = True

        self.unsaved_label.config(
            text="⚠ Unsaved changes",
            fg="#ffcc00"
        )

    # ---------------- LOG ---------------- #

    def log(self,msg):

        now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(LOG_FILE,"a") as f:
            f.write(f"[{now}] {msg}\n")

    def open_logs(self):

        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE,"w") as f:
                f.write("=== Restart Log ===\n")

        os.startfile(LOG_FILE)


# ---------------- RUN ---------------- #

if __name__=="__main__":

    root=tk.Tk()
    app=AutoRestartApp(root)
    root.mainloop()