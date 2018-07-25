import tkinter as tk

from PIL import Image, ImageTk


class RecordPanel(tk.Frame):
    save_icon = Image.open("resources/iconsave.png")
    remove_icon = Image.open("resources/icontrash.png")

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.grid(row=1, column=0, sticky=("N", "S", "E", "W"))
        self.str_name_f = tk.StringVar()
        self.str_name_l = tk.StringVar()
        self.str_id = tk.StringVar()

        self.output_panel = tk.LabelFrame(self)

        self.id_label = tk.Label(self.output_panel, textvariable=self.str_id, justify="left")
        self.nm_label_f = tk.Label(self.output_panel, textvariable=self.str_name_f, justify=tk.LEFT)
        self.nm_label_l = tk.Label(self.output_panel, textvariable=self.str_name_l, justify=tk.LEFT)

        self.id_entry = tk.Entry(self.output_panel, textvariable=self.str_id)
        self.nm_entry_f = tk.Entry(self.output_panel, textvariable=self.str_name_f)
        self.nm_entry_l = tk.Entry(self.output_panel, textvariable=self.str_name_l)

        self.save_icon.thumbnail((80, 80), Image.ANTIALIAS)
        self.remove_icon.thumbnail((80, 80), Image.ANTIALIAS)

        self._sv_icn = ImageTk.PhotoImage(self.save_icon)
        self._rm_icn = ImageTk.PhotoImage(self.remove_icon)
        self.sv_button = tk.Button(self, image=self._sv_icn)
        self.cc_button = tk.Button(self, image=self._rm_icn)

        self.id_label.grid(sticky=("N", "S", "E", "W"))
        self.nm_label_f.grid(row=1, sticky=("N", "S", "E", "W"))
        self.nm_label_l.grid(row=2, sticky=("N", "S", "E", "W"))
        #
        # self.sv_button.grid(row=2, sticky=("N", "S", "E", "W"))
        # self.cc_button.grid(row=2, column=1, sticky=("N", "S", "E", "W"))
        # self.id_label.pack(side="top", fill="x", expand=True)
        self.output_panel.pack(side="top", fill="both", expand=True)

        # self.md_button.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.sv_button.pack(side="left", expand=True)
        self.cc_button.pack(side="right", expand=True)

        self.disable()

    @property
    def name(self):
        return self.str_name_f.get()[12:], self.str_name_l.get()[11:]

    @name.setter
    def name(self, new):
        first = new[0]
        last = new[1]
        self.str_name_f.set("First Name: {}".format(first))
        self.str_name_l.set("Last Name: {}".format(last))
        if first is None:
            self.nm_entry_f.grid(row=1, sticky=("N", "S", "E", "W"))
            self.nm_label_f.grid_forget()
        else:
            self.nm_label_f.grid(row=1, sticky=("N", "S", "E", "W"))
            self.nm_entry_f.grid_forget()
        if last is None:
            self.nm_entry_l.grid(row=2, sticky=("N", "S", "E", "W"))
            self.nm_label_l.grid_forget()
        else:
            self.nm_label_l.grid(row=2, sticky=("N", "S", "E", "W"))
            self.nm_entry_l.grid_forget()

    @property
    def id(self):
        return self.str_id.get()[12:]

    @id.setter
    def id(self, new):
        self.str_id.set("Student ID: {}".format(new))
        if new is None:
            self.id_label.grid_forget()
            self.id_entry.grid(sticky=("N", "S", "E", "W"))
        else:
            self.id_entry.grid_forget()
            self.id_label.grid(sticky=("N", "S", "E", "W"))

    def disable(self):
        self.name = ("", "")
        self.id = ""
        self.sv_button.configure(state=tk.DISABLED)
        self.cc_button.configure(state=tk.DISABLED)
        self.id_label.configure(state=tk.DISABLED)
        self.nm_label_f.configure(state=tk.DISABLED)

    def set(self, name, sid, success, failure):
        self.name = name
        self.id = sid

        self.sv_button.configure(command=lambda: success(*self.name, self.id), state=tk.NORMAL)
        self.cc_button.configure(command=failure, state=tk.NORMAL)
        self.id_label.configure(state=tk.NORMAL)
        self.nm_label_f.configure(state=tk.NORMAL)
