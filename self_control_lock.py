import tkinter as tk
from tkinter import messagebox
import datetime, time, threading, json, os, sys
import winreg
from pynput import keyboard

STATE_FILE = 'lock_state.json'

class FinalSelfControlLock:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('自控锁机')
        self.root.geometry('600x400')
        self.root.configure(bg='#0a0a0a')

        self.lock_start_datetime = None
        self.lock_end_datetime = None
        self.max_clicks = 3000
        self.click_count = 0
        self.is_locked = False
        self.autostart = False

        self.keyboard_listener = None

        self.load_state()
        self.setup_ui()
        threading.Thread(target=self.check_lock_time, daemon=True).start()

    def setup_ui(self):
        self.frame = tk.Frame(self.root, bg='#0a0a0a')
        self.frame.pack(expand=True, fill='both')

        tk.Label(self.frame, text='自控锁机系统', font=('Segoe UI', 24, 'bold'), bg='#0a0a0a', fg='white').pack(pady=10)

        tk.Label(self.frame, text='开始时间 (月.日.时:分)', font=('Segoe UI', 12), bg='#0a0a0a', fg='#888').pack()
        self.start_entry = tk.Entry(self.frame, font=('Segoe UI', 12), justify='center')
        self.start_entry.pack(pady=2)

        tk.Label(self.frame, text='结束时间 (月.日.时:分)', font=('Segoe UI', 12), bg='#0a0a0a', fg='#888').pack()
        self.end_entry = tk.Entry(self.frame, font=('Segoe UI', 12), justify='center')
        self.end_entry.pack(pady=2)

        tk.Label(self.frame, text='紧急退出点击次数', font=('Segoe UI', 12), bg='#0a0a0a', fg='#888').pack()
        self.click_entry = tk.Entry(self.frame, font=('Segoe UI', 12), justify='center')
        self.click_entry.insert(0, str(self.max_clicks))
        self.click_entry.pack(pady=2)

        self.autostart_var = tk.IntVar(value=int(self.autostart))
        tk.Checkbutton(self.frame, text='开机自启动', variable=self.autostart_var, bg='#0a0a0a', fg='white', selectcolor='#0a0a0a').pack(pady=5)

        tk.Button(self.frame, text='开始锁机', font=('Segoe UI', 14, 'bold'), bg='#00aa88', fg='white', width=20, command=self.start_lock_session).pack(pady=10)

        if self.is_locked and self.lock_end_datetime > datetime.datetime.now():
            self.frame.destroy()
            self.setup_lock_ui()

    def start_lock_session(self):
        try:
            s = self.start_entry.get().strip()
            e = self.end_entry.get().strip()
            clicks = int(self.click_entry.get().strip())
            self.autostart = bool(self.autostart_var.get())

            sm, sd, shm = s.split('.')
            sh, smi = map(int, shm.split(':'))
            em, ed, ehm = e.split('.')
            eh, emi = map(int, ehm.split(':'))

            now = datetime.datetime.now()
            year = now.year
            self.lock_start_datetime = datetime.datetime(year, int(sm), int(sd), sh, smi)
            self.lock_end_datetime = datetime.datetime(year, int(em), int(ed), eh, emi)

            if self.lock_end_datetime <= self.lock_start_datetime:
                messagebox.showerror('错误','结束时间必须大于开始时间')
                return

            if clicks < 100:
                messagebox.showerror('错误','点击次数不能低于100')
                return

            self.max_clicks = clicks
            if self.lock_start_datetime < now:
                self.lock_start_datetime = now

        except:
            example = (datetime.datetime.now() + datetime.timedelta(minutes=1))
            messagebox.showerror('错误', f'时间格式错误，示例: {example.month}.{example.day}.{example.hour:02d}:{example.minute:02d}')
            return

        self.save_state()
        self.frame.destroy()
        self.setup_lock_ui()

    def setup_lock_ui(self):
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.canvas = tk.Canvas(self.root, bg='#0a0a0a', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self.text_main = self.canvas.create_text(300, 150, text='已锁定', fill='white', font=('Segoe UI', 32, 'bold'))
        self.text_time = self.canvas.create_text(300, 220, text='', fill='#aaa', font=('Segoe UI', 14))
        self.text_remaining = self.canvas.create_text(300, 260, text='', fill='#888', font=('Segoe UI', 12))
        self.text_progress = self.canvas.create_text(300, 300, text=f'点击进度: {self.click_count}/{self.max_clicks}', fill='yellow', font=('Segoe UI', 12))

        self.btn_exit = tk.Button(self.root, text='紧急退出', font=('Segoe UI', 14), bg='red', fg='white', command=self.click_exit)
        self.btn_exit.place(relx=0.5, rely=0.85, anchor='center')

        self.lock_computer()

    def click_exit(self):
        self.click_count += 1
        if self.click_count >= self.max_clicks:
            self.unlock_computer()
        self.canvas.itemconfig(self.text_progress, text=f'点击进度: {self.click_count}/{self.max_clicks}')
        self.save_state()

    def lock_computer(self):
        self.is_locked = True
        self.disable_task_manager()
        self.start_input_block()

    def unlock_computer(self):
        self.is_locked = False
        self.enable_task_manager()
        self.stop_input_block()
        self.save_state()
        messagebox.showinfo('解锁','已解锁')
        self.root.destroy()

    def start_input_block(self):
        self.keyboard_listener = keyboard.Listener(on_press=lambda key: False)
        self.keyboard_listener.start()

    def stop_input_block(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def disable_task_manager(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'DisableTaskMgr', 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except: pass

    def enable_task_manager(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r'Software\Microsoft\Windows\CurrentVersion\Policies\System', 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'DisableTaskMgr', 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
        except: pass

    def check_lock_time(self):
        while True:
            now = datetime.datetime.now()
            if self.is_locked:
                remaining = self.lock_end_datetime - now
                if remaining.total_seconds() <= 0:
                    self.unlock_computer()
                    break
                self.canvas.itemconfig(self.text_time, text=f'{self.lock_start_datetime} → {self.lock_end_datetime}')
                self.canvas.itemconfig(self.text_remaining, text=f'剩余时间: {str(remaining).split(".")[0]}')
            time.sleep(1)

    def save_state(self):
        state = {
            'lock_start': self.lock_start_datetime.isoformat() if self.lock_start_datetime else None,
            'lock_end': self.lock_end_datetime.isoformat() if self.lock_end_datetime else None,
            'max_clicks': self.max_clicks,
            'click_count': self.click_count,
            'is_locked': self.is_locked,
            'autostart': self.autostart
        }
        with open(STATE_FILE,'w') as f:
            json.dump(state,f)

        try:
            key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,key_path,0,winreg.KEY_SET_VALUE)
            if self.autostart:
                python_path = sys.executable
                script_path = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(reg_key,'SelfControlLock',0,winreg.REG_SZ,f'"{python_path}" "{script_path}"')
            else:
                try: winreg.DeleteValue(reg_key,'SelfControlLock')
                except: pass
            winreg.CloseKey(reg_key)
        except: pass

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE,'r') as f:
                    state = json.load(f)
                    if state['lock_start']:
                        self.lock_start_datetime = datetime.datetime.fromisoformat(state['lock_start'])
                    if state['lock_end']:
                        self.lock_end_datetime = datetime.datetime.fromisoformat(state['lock_end'])
                    self.max_clicks = state.get('max_clicks',3000)
                    self.click_count = state.get('click_count',0)
                    self.is_locked = state.get('is_locked',False)
                    self.autostart = state.get('autostart',False)
            except: pass

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    FinalSelfControlLock().run()