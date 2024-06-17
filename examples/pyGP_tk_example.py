import tkinter as tk
from types import NoneType

from pyGuardPoint import GuardPoint

from pyGuardPoint import GuardPointError, Cardholder, GuardPointAsyncIO

GP_HOST = 'https://sensoraccess.duckdns.org'
# GP_HOST = 'http://localhost/'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "/Users/johnowen/Downloads/MobileGuardDefault.p12"
#TLS_P12 = None
TLS_P12_PWD = "test"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.wm_title("TK with pyGuardPoint")
        self.gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)
        self.build_gui()

    def lookup_finished(self, response):
        print("lookup finished")
        if isinstance(response, NoneType):
            self.lookup_result_lbl.config(text=f"Nothing found")
        if isinstance(response, GuardPointError):
            self.lookup_result_lbl.config(text=f"{response}")
        if isinstance(response, Cardholder):
            cardholder = response
            self.lookup_result_lbl.config(text=f"Found: {cardholder.firstName} {cardholder.lastName}\n "
                                               f"within the {cardholder.insideArea.name}")

    def lookup_start(self):
        print("lookup started")
        try:
            cardholder = self.gp.get_card_holder(card_code=self.lookup_entry.get())
            self.lookup_finished(cardholder)
        except Exception as e:
            self.lookup_result_lbl.config(text=f"{str(e)}")


    def build_gui(self):
        self.lookup_lbl = tk.Label(master=self, text="Enter card-code below: ")
        self.lookup_lbl.pack()
        self.lookup_entry = tk.Entry(master=self, fg="blue", bg="white", width=50)
        self.lookup_entry.insert(tk.END, "1B1A1B1C")
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
