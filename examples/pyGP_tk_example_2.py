import tkinter as tk
from tkinter import RIGHT, Y, YES, END

from pyGuardPoint_Build.pyGuardPoint import GuardPointError, Cardholder, GuardPointAsync


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.wm_title("TK with pyGuardPoint")
        self.gp = GuardPointAsync(host="sensoraccess.duckdns.org", pwd="password")
        self.build_gui()

    def lookup_finished(self, response):
        if isinstance(response, GuardPointError):
            self.lookup_result_lbl.config(text=f"{response}")
        if isinstance(response, list):
            cardholders = response
            if len(cardholders) > 0:
                self.lookup_result_lbl.config(text=f"Found: {cardholders[0].firstName} {cardholders[0].lastName}\n "
                                                   f"within the {cardholders[0].insideArea.name}")
            else:
                self.lookup_result_lbl.config(text=f"No Cardholder Found")

    def lookup_start(self):
        self.lookup_result_lbl.config(text=f"Searching ....")
        area_filter_list = []
        for i in self.area_listbox.curselection():
            for area in self.area_list:
                if self.area_listbox.get(i) == area.name:
                    area_filter_list.append(area)
        self.gp.get_card_holders(self.lookup_finished,
                                 search_terms=self.lookup_entry.get(),
                                 areas=area_filter_list,
                                 filter_expired=False)  # TODO: JOSH ADD TOGGLE BUTTON

    def got_areas(self, response):
        if isinstance(response, GuardPointError):
            self.lookup_result_lbl.config(text=f"{response}")
        if isinstance(response, list):
            self.area_list = response
            for area in self.area_list:
                self.area_listbox.insert(END, area.name)

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

        # ListBox
        yscrollbar = tk.Scrollbar(master=self)
        yscrollbar.pack(side=RIGHT, fill=Y)
        self.area_listbox = tk.Listbox(master=self, selectmode="multiple",
                                       yscrollcommand=yscrollbar.set)
        self.area_listbox.pack(padx=10, pady=10,
                               expand=YES, fill="both")
        yscrollbar.config(command=self.area_listbox.yview)

        self.gp.get_areas(on_finished=self.got_areas)

        self.lookup_lbl = tk.Label(master=self, text="Enter search phrase below: ")
        self.lookup_lbl.pack()
        self.lookup_entry = tk.Entry(master=self, fg="blue", bg="white", width=50)
        self.lookup_entry.insert(tk.END, "john")
        self.lookup_entry.pack()
        self.lookup_btn = tk.Button(master=self, text="Lookup Cardholder",
                                    command=self.lookup_start)
        self.lookup_btn.pack()
        self.lookup_result_lbl = tk.Label(master=self, text=" - ", font=("Arial", 20))
        self.lookup_result_lbl.pack()


if __name__ == "__main__":
    app = App()

    # display GUI
    app.mainloop()
