import tkinter as tk
import TkTreectrl as treectrl
from get_input import Recorder
from send_input import PressKey, ReleaseKey
from win32.win32api import GetAsyncKeyState
from threading import Thread
import time


def print_keys(dic):
    keys = []
    for i in dic:
        keys.append(dic[i])

    return "+".join(keys)


class MainApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.pack()

        self.start_pressing = False

        self.keys = []
        self.switch_key = None

        self.var = tk.IntVar()

        self.key_table = treectrl.MultiListbox(self)
        self.key_table.pack(side="bottom")
        self.key_table.config(columns=("Button Name", "Interval"))

        self.title = tk.Label(self, text="Pycro.")
        self.title.pack()

        self.add_key_button = tk.Button(self, text="Add Button", bg="white", command=self.open_key_window)
        self.add_key_button.pack()

        self.main_key_label = tk.Label(self, text="Switch hotkey is not set yet.")
        self.main_key_label.pack()

        self.main_key_button = tk.Button(self, text="Set Switch Hotkey", command=self.set_switch_key)
        self.main_key_button.pack()

        Thread(target=self.scan_switch).start()

    def set_switch_key(self):
        r = Recorder()
        self.switch_key = r.record()

        print(f"Switch key has been set: {self.switch_key}")

        self.main_key_label.config(text=f"Switch Hotkey: {print_keys(self.switch_key)}")

    def read_key(self):
        self.scanned_key = None

        self.key_status_label.config(text="Scanning...")

        r = Recorder()
        self.scanned_key = r.record()
        print(f"Key has been scanned: {self.scanned_key}")

        self.key_status_label.config(text=f"Successfully scanned hotkey: {print_keys(self.scanned_key)}")

        self.read_key_button.config(text="Try Again", command=self.read_key)

    def open_key_window(self):
        self.key_window = tk.Toplevel(self)
        self.key_status_label = tk.Label(self.key_window,
                                         text="No hotkeys scanned. Press your desired hotkey after clicking the button below.")
        self.key_status_label.pack()
        self.read_key_button = tk.Button(self.key_window, text="Scan a Hotkey", command=self.read_key)
        self.read_key_button.pack()
        display = tk.Label(self.key_window, text="Select Mode")
        display.pack()

        self.hold_button = tk.Radiobutton(self.key_window, text="Hold", variable=self.var, value=1,
                                          command=self.close_interval_box)
        self.hold_button.pack()
        self.repeat_button = tk.Radiobutton(self.key_window, text="Repeat every", variable=self.var, value=2,
                                            command=self.open_interval_box)
        self.repeat_button.pack()
        self.interval_box = tk.Entry(self.key_window, state="disabled")
        if self.var.get() == 2:
            self.interval_box.config(state="normal")
        self.interval_box.pack()

        confirm_button = tk.Button(self.key_window, text="Confirm", bg="white", command=self.confirm_add_key)
        confirm_button.pack()
        cancel_button = tk.Button(self.key_window, text="Cancel", command=self.key_window.destroy)
        cancel_button.pack()

    def open_interval_box(self):
        self.interval_box.config(state="normal")

    def close_interval_box(self):
        self.interval_box.config(state="disabled")

    def confirm_add_key(self):
        if self.var.get() == 0:
            pass

        elif self.var.get() == 1:
            self.keys.append([self.scanned_key, 0])
            self.key_table.insert("end", print_keys(self.scanned_key), "Hold")
            self.scanned_key = None
            self.key_window.destroy()

        elif self.var.get() == 2:

            try:
                interval = int(self.interval_box.get())
            except:
                pass

            self.keys.append([(self.scanned_key), interval])
            self.key_table.insert("end", print_keys(self.scanned_key), self.interval_box.get() + "ms")
            self.scanned_key = None
            self.key_window.destroy()

        print(f"List of keys: {self.keys}")

    def scan_switch(self):
        while True:
            try:
                if len(self.switch_key) == 1:
                    for key in self.switch_key:
                        key_state = GetAsyncKeyState(key)
                        # if key_state == -32768 or key_state == -32767 or key_state == 1:
                        if key_state == -32767:
                            if self.start_pressing == False:
                                print("Enabling keys.")
                                self.start_pressing = True
                                for key in self.keys:
                                    Thread(target=self.press_key, args=(key,)).start()
                            else:
                                print("Disabling keys.")
                                self.start_pressing = False
                        time.sleep(0.05)
                else:
                    pressed_all = True
                    for key in self.switch_key:
                        key_state = GetAsyncKeyState(key)
                        # if key_state == -32768 or key_state == -32767 or key_state == 1:
                        if key_state == 0:
                            pressed_all = False

                    if pressed_all:
                        if self.start_pressing == False:
                            print("Enabling keys.")
                            self.start_pressing = True
                            for key in self.keys:
                                Thread(target=self.press_key, args=(key,)).start()
                        else:
                            print("Disabling keys.")
                            self.start_pressing = False
                    time.sleep(0.1)

            except TypeError:
                time.sleep(0.2)
                pass

    def press_key(self, key):
        pressed = False
        interval = key[1]
        key = key[0]
        key_codes = [x for x in key]
        while True:
            if not self.start_pressing:
                for key_code in key_codes:
                    # print(f"Releasing {key_code}")
                    ReleaseKey(key_code)
                break

            elif interval == 0:
                if not pressed:
                    for key_code in key_codes:
                        # print(f"Pressing {key_code}.")
                        PressKey(key_code)
                        pressed = True

            else:
                for key_code in key_codes:
                    # print(f"Pressing {key_code}.")
                    PressKey(key_code)

                for key_code in key_codes:
                    # print(f"Releasing {key_code}")
                    ReleaseKey(key_code)
                time.sleep(interval / 1000)


root = tk.Tk()
root.title("Pycro")
app = MainApp(master=root)
app.mainloop()
