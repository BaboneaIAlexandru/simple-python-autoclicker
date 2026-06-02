import customtkinter as ctk
from time import sleep
from threading import Thread,Event
from pynput.keyboard import Listener,Key
from pynput.mouse import Controller,Button

mouse=Controller()
mouse_button=Button.left

delay=1.0
clicker_active=False
hotkey=Key.f6

stop_event=Event()

def check_pressed_key(pressed_key):
    global clicker_active
    if pressed_key==hotkey:
        clicker_active=not clicker_active
        if not clicker_active:
            stop_event.set()
    
def auto_clicker():
    while True:
        if clicker_active:
            mouse.click(mouse_button)
            stop_event.clear()
            stop_event.wait(delay)
        else:
            sleep(0.1)

Thread(target=auto_clicker,daemon=True).start()

class AutoClickerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simple AutoClicker")
        self.geometry("450x220")
        self.resizable(False,False)
        
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        
        mouse_buttons=["Left","Right","Middle"]
        hotkeys=["F6","F7","F8","F9","CapsLock"]

        self.info_text = ctk.StringVar(value=f"Delay: 1.0 seconds | Mouse button: Left | Hotkey: F6")

        def closing():
            global clicker_active
            clicker_active=False
            stop_event.set()
            listener.stop()
            self.destroy()
        
        self.protocol("WM_DELETE_WINDOW", closing)

        def validate_entry(entry_text,action_type):
            if entry_text=="":
                return True
            if action_type=="0" and entry_text==".":
                self.entry_select_delay.after(1,lambda: self.entry_select_delay.delete(0,"end"))
                return True
            if entry_text.count(".")<=1:
                no_dot_entry=entry_text.replace(".","",1)
                if no_dot_entry=="" or no_dot_entry.isdigit():
                    if "." in entry_text:
                        parts=entry_text.split(".")
                        integer_part=parts[0]
                        decimal_part=parts[1]
                        if len(integer_part)>4 or len(decimal_part)>3:
                            return False
                    else:
                        if len(entry_text)>4:
                            return False
                    return True
            return False
        
        def update_info_label():
            global delay
            
            hotkey_text=self.combobox_select_hotkey.get()
            mouse_button_text=self.combobox_select_mouse_button.get()

            self.info_text.set(value=f"Delay: {delay} seconds | Mouse button: {mouse_button_text} | Hotkey: {hotkey_text}")

        def delay_entry_submit(event):
            global delay
            submit_value=self.entry_select_delay.get()

            if submit_value=="" or submit_value==".":
                delay=1.0
                self.entry_select_delay.delete(0,"end")
                self.entry_select_delay.insert(0,str(delay))
                update_info_label()
                return

            try:
                float_submit_value=float(submit_value)
                if 0.001<=float_submit_value<=3600:
                    delay=float_submit_value
                elif float_submit_value<0.001:
                    delay=0.001
                elif float_submit_value>3600:
                    delay=3600

                self.entry_select_delay.delete(0,"end")
                self.entry_select_delay.insert(0,str(delay))   

            except ValueError:
                pass
            update_info_label()

        def update_mouse_button(choice):
            global mouse_button
            if choice=="Left":
                mouse_button=Button.left
            elif choice=="Right":
                mouse_button=Button.right
            elif choice=="Middle":
                mouse_button=Button.middle
            update_info_label()

        def update_hotkey(choice):
            global hotkey
            if choice=="CapsLock":
                hotkey=Key.caps_lock
            else:
                hotkey=getattr(Key,choice.lower(),Key.f6)
            update_info_label()
        
        self.label_select_mouse_button=ctk.CTkLabel(self,anchor="w",font=("Arial",15),text="Select mouse button:")
        self.label_select_mouse_button.grid(row=0,column=0,sticky="w",pady=(25,0),padx=(15,0))
        self.combobox_select_mouse_button=ctk.CTkComboBox(self,values=mouse_buttons,state="readonly",command=update_mouse_button)
        self.combobox_select_mouse_button.grid(row=0,column=1,pady=(25,0),padx=(0,15))
        self.combobox_select_mouse_button.set("Left")

        self.label_select_delay=ctk.CTkLabel(self,anchor="w",font=("Arial",15),text="Select delay between inputs (seconds):")
        self.label_select_delay.grid(row=1,column=0,sticky="w",pady=(25,0),padx=(15,0))
        self.entry_select_delay=ctk.CTkEntry(self,placeholder_text="ex: 0.05",validate="key",validatecommand=(self.register(validate_entry),"%P","%d"))
        self.entry_select_delay.grid(row=1,column=1,pady=(25,0),padx=(0,15))
        self.entry_select_delay.bind("<Return>",delay_entry_submit)
        self.label_min_max_delay_info=ctk.CTkLabel(self,text="min. 0.001 - max. 3600",anchor="n",font=("Arial",10))
        self.label_min_max_delay_info.grid(row=2,column=1,sticky="n",padx=(0,15))

        self.label_select_hotkey=ctk.CTkLabel(self,anchor="w",font=("Arial",15),text="Select start/stop hotkey:")
        self.label_select_hotkey.grid(row=3,column=0,sticky="w",pady=(5,0),padx=(15,0))
        self.combobox_select_hotkey=ctk.CTkComboBox(self,values=hotkeys,state="readonly",command=update_hotkey)
        self.combobox_select_hotkey.grid(row=3,column=1,pady=(5,0),padx=(0,15))
        self.combobox_select_hotkey.set("F6")

        self.label_info=ctk.CTkLabel(self,textvariable=self.info_text)
        self.label_info.grid(row=4,column=0,columnspan=2,pady=(10,0))

app=AutoClickerGUI()
with Listener(on_press=check_pressed_key) as listener:
    app.mainloop()
