from ctypes import windll
import signal
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import RIGHT, Y, YES, END

from pyGuardPoint import GuardPoint, GuardPointError, SortAlgorithm

windll.shcore.SetProcessDpiAwareness(1)  # Fix Win10 DPI issue

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.wm_title("TK with pyGuardPoint")

        # Options Menu
        '''self.options = ['one', 'two', 'three']
        self.om_variable = tk.StringVar(self)
        self.om_variable.set(self.options[0])
        self.om_variable.trace('w', self.option_select)
        self.om = tk.OptionMenu(self, self.om_variable, *self.options)
        self.om.pack()'''

        # -------------------- GUI Build -------------------- #

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

        self.var_Lookup_isFuzzy = tk.BooleanVar()
        self.var_Lookup_thresholdLvl = tk.IntVar()
        self.var_Lookup_isExpired = tk.BooleanVar()

        self.frmLookup = ttk.LabelFrame(self, text=" Cardholder Lookup ", padding=padding)

        self.txtLookup = ttk.Entry(self.frmLookup, foreground="blue", background="white", width=30)
        self.btnLookup = ttk.Button(self.frmLookup, text="Lookup Cardholder", command=self.lookup_start)
        self.chkLookup_fuzzy = ttk.Checkbutton(self.frmLookup, text="Fuzzy search", variable=self.var_Lookup_isFuzzy)
        self.sclLookup_threshold = ttk.Scale(self.frmLookup, variable=self.var_Lookup_thresholdLvl, from_=0, to=100,
                                             state="disabled")
        self.lblLookup_threshold = ttk.Label(self.frmLookup, relief=tk.SUNKEN, width=4, text="-", anchor=tk.CENTER,
                                             state="disabled")
        self.chkLookup_expired = ttk.Checkbutton(self.frmLookup, text="Include expired",
                                                 variable=self.var_Lookup_isExpired)
        self.lblLookup_result = ttk.Label(self.frmLookup, text=" - ", font=("Arial", 16), relief="sunken", )

        self.txtLookup.grid(row=1, column=1, columnspan=2, sticky="WE", padx=padding, pady=padding)
        self.btnLookup.grid(row=1, column=3, columnspan=2, sticky="WE", padx=padding, pady=padding)
        self.chkLookup_expired.grid(row=2, column=1, sticky="W", padx=padding, pady=padding)
        self.chkLookup_fuzzy.grid(row=2, column=2, sticky="W", padx=padding, pady=padding)
        self.sclLookup_threshold.grid(row=2, column=3, padx=padding, pady=padding)
        self.lblLookup_threshold.grid(row=2, column=4, padx=padding, pady=padding)
        self.lblLookup_result.grid(row=3, column=1, columnspan=4, sticky="WE", padx=padding, pady=padding)
        self.frmLookup.columnconfigure(1, weight=1)

        self.var_Lookup_isFuzzy.trace_add("write", self._app_set_search)
        self.var_Lookup_thresholdLvl.trace_add("write", lambda *_: self.lblLookup_threshold.config(
            text=str(self.var_Lookup_thresholdLvl.get())))
        self.var_Lookup_isExpired.set(True)

        # -------------------- Main Window -------------------- #

        self.frmCHList.grid(row=1, column=1, sticky='NSWE', padx=padding * 2, pady=padding * 2)
        self.frmLookup.grid(row=2, column=1, sticky='NSWE', padx=padding * 2, pady=padding * 2)
        self.columnconfigure(1, weight=1, pad=padding)
        self.rowconfigure(1, weight=1, pad=padding)

        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

        self.protocol('WM_DELETE_WINDOW', self.quit)
        signal.signal(signal.SIGINT, self.quit)

        # -------------------- End GUI Build -------------------- #

        self.gp = GuardPoint(host="sensoraccess.duckdns.org", pwd="password")
        self.gp.get_areas(on_finished=self.got_areas)

    def _app_set_search(self, *_):
        self.sclLookup_threshold.config(state="enabled" if self.var_Lookup_isFuzzy.get() else "disabled")
        self.lblLookup_threshold.config(state="enabled" if self.var_Lookup_isFuzzy.get() else "disabled")

    def lookup_finished(self, response):
        if isinstance(response, GuardPointError):
            self.lblLookup_result.config(text=f"{response}")
        if isinstance(response, list):
            cardholders = response
            if len(cardholders) > 0:
                self.lblLookup_result.config(text=f"Found: {cardholders[0].firstName} {cardholders[0].lastName}\n"
                                                  f"Company: {cardholders[0].cardholderPersonalDetail.company}\n"
                                                  f"Email: {cardholders[0].cardholderPersonalDetail.email}\n"
                                                  f"Area: {cardholders[0].insideArea.name}")
            else:
                self.lblLookup_result.config(text=f"No Cardholder Found")

    def lookup_start(self):
        self.lblLookup_result.config(text=f"Searching ....")
        area_filter_list = []
        for i in self.lstCHList.curselection():
            for area in self.area_list:
                if self.lstCHList.get(i) == area.name:
                    area_filter_list.append(area)
        filter_expired = (not self.var_Lookup_isExpired.get())
        self.gp.get_card_holders(self.lookup_finished,
                                 search_terms=self.txtLookup.get(),
                                 areas=area_filter_list,
                                 filter_expired=filter_expired,
                                 sort_algorithm=SortAlgorithm.FUZZY_MATCH if self.var_Lookup_isFuzzy.get() else SortAlgorithm.SERVER_DEFAULT,
                                 threshold=self.var_Lookup_thresholdLvl.get())

    def got_areas(self, response):
        if isinstance(response, GuardPointError):
            self.lblLookup_result.config(text=f"{response}")
        if isinstance(response, list):
            self.area_list = response
            for area in self.area_list:
                self.lstCHList.insert(END, area.name)

    def option_select(self, *args):
        print(self.om_variable.get())


if __name__ == "__main__":
    app = App()
    app.txtLookup.insert(tk.END, "john")

    # display GUI
    app.mainloop()
