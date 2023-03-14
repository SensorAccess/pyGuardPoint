from ctypes import windll
import signal
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import RIGHT, Y, YES, END

import pkg_resources
from pyGuardPoint import GuardPointAsync, GuardPointError, SortAlgorithm

windll.shcore.SetProcessDpiAwareness(1)  # Fix Win10 DPI issue

py_gp_version = pkg_resources.get_distribution("pyGuardPoint").version
print("pyGuardPoint Version:" + py_gp_version)
py_gp_version_int = int(py_gp_version.replace('.', ''))
if py_gp_version_int < 45:
    print("Please Update pyGuardPoint")
    print("\t (Within a Terminal Window) Run > 'pip install pyGuardPoint --upgrade'")
    exit()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.wm_title("TK with pyGuardPoint")
        self.gp = GuardPointAsync(host="sensoraccess.duckdns.org", pwd="password")
        self.build_gui()
        
        self.protocol('WM_DELETE_WINDOW', self.quit)
        signal.signal(signal.SIGINT, self.quit)

    def lookup_finished(self, response):
        if isinstance(response, GuardPointError):
            self.lblLookup_result.config(text=f"{response}")
        if isinstance(response, list):
            cardholders = response
            if len(cardholders) > 0:
                self.lblLookup_result.config(text=f"Found: {cardholders[0].firstName} {cardholders[0].lastName}\n "
                                                   f"within the {cardholders[0].insideArea.name}")
            else:
                self.lblLookup_result.config(text=f"No Cardholder Found")

    def lookup_start(self):
        self.lblLookup_result.config(text=f"Searching ....")
        area_filter_list = []
        for i in self.lstCHList.curselection():
            for area in self.area_list:
                if self.lstCHList.get(i) == area.name:
                    area_filter_list.append(area)
        filter_expired=(not self.var_chkLookup_expired.get())
        self.gp.get_card_holders(self.lookup_finished,
                                 search_terms=self.txtLookup.get(),
                                 areas=area_filter_list,
                                 filter_expired=filter_expired,
                                 sort_algorithm=SortAlgorithm.SERVER_DEFAULT,
                                 threshold=20)

    def got_areas(self, response):
        if isinstance(response, GuardPointError):
            self.lblLookup_result.config(text=f"{response}")
        if isinstance(response, list):
            self.area_list = response
            for area in self.area_list:
                self.lstCHList.insert(END, area.name)

    def option_select(self, *args):
        print(self.om_variable.get())

    def build_gui(self):
        # Options Menu
        '''self.options = ['one', 'two', 'three']
        self.om_variable = tk.StringVar(self)
        self.om_variable.set(self.options[0])
        self.om_variable.trace('w', self.option_select)
        self.om = tk.OptionMenu(self, self.om_variable, *self.options)
        self.om.pack()'''

        padding = 4

        # -------------------- CH List Frame -------------------- #

        self.frmCHList = ttk.LabelFrame(self, text=" Cardholder List ", padding=padding)

        self.lstCHList = tk.Listbox(self.frmCHList, selectmode="multiple", height=10)
        self.scbCHList = ttk.Scrollbar(self.frmCHList, orient=tk.VERTICAL, command=self.lstCHList.yview)
        self.lstCHList.configure(yscrollcommand=self.scbCHList.set)

        self.lstCHList.grid(row=1, column=1, sticky="NSWE", padx=(padding, 0), pady=padding)
        self.scbCHList.grid(row=1, column=2, sticky="NS", padx=(0, padding), pady=padding)
        self.frmCHList.columnconfigure(1, weight=1)
        self.frmCHList.rowconfigure(1, weight=1)

        # -------------------- Lookup Frame -------------------- #

        self.var_chkLookup_expired = tk.IntVar()

        self.frmLookup = ttk.LabelFrame(self, text=" Cardholder Lookup ", padding=padding)

        self.txtLookup = ttk.Entry(self.frmLookup, foreground="blue", background="white", width=50)
        self.chkLookup_expired = ttk.Checkbutton(self.frmLookup, text="Include expired", variable=self.var_chkLookup_expired)
        self.btnLookup = ttk.Button(self.frmLookup, text="Lookup Cardholder", command=self.lookup_start)
        self.lblLookup_result = ttk.Label(self.frmLookup, text=" - ", font=("Arial", 16), relief="sunken")

        self.txtLookup.grid(row=1, column=1, columnspan=2, sticky="WE", padx=padding, pady=padding)
        self.chkLookup_expired.grid(row=2, column=1, sticky="W", padx=padding, pady=padding)
        self.btnLookup.grid(row=2, column=2, padx=padding, sticky="E", pady=padding)
        self.lblLookup_result.grid(row=3, column=1, columnspan=2, sticky="WE", padx=padding, pady=padding)

        self.frmLookup.columnconfigure(1, weight=1)

        # -------------------- Main Window -------------------- #

        self.frmCHList.grid(row=1, column=1, sticky='NSWE', padx=padding*2, pady=padding*2)
        self.frmLookup.grid(row=2, column=1, sticky='NSWE', padx=padding*2, pady=padding*2)
        self.columnconfigure(1, weight=1, pad=padding)
        self.rowconfigure(1, weight=1, pad=padding)

        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

        self.gp.get_areas(on_finished=self.got_areas)


if __name__ == "__main__":
    app = App()
    app.txtLookup.insert(tk.END, "john")

    # display GUI
    app.mainloop()
