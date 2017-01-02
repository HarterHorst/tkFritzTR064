#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO Add description
"""
Add description here.
"""

import datetime
import tkinter.ttk
import xml.etree.ElementTree as eTree
import argparse
import pkg_resources
import platform
from tkinter import Tk, Menu, Label, Frame, messagebox
from fritzconnection import FritzConnection
from fritzconnection.fritzconnection import ServiceError, ActionError

__version__ = '0.5.2'

# Default Values
FRITZ_IP_ADDRESS = '192.168.0.1'
FRITZ_TCP_PORT = 49000
FRITZ_USERNAME = "admin"
FRITZ_PASSWORD = ""

# ---- to do list ----
# - TODO check if pack() method leads to a better result in linux environment
# - TODO Check console output for errors and add exception handling in code


def get_version():
    return __version__


class GUI:
    connection = FritzConnection()
    currentservice = "empty"
    currentaction = "empty"

    def __init__(self, window):
        framepadx = 10   # define the gap between the frames in the upper windows section
        self.varanonymlogin = tkinter.IntVar()

        # ----------------------------------------------------------
        # Create menu bar
        # ----------------------------------------------------------
        menubar = Menu(window)

        mprogram = Menu(menubar)
        mprogram["tearoff"] = 0
        mprogram.add_command(label="Exit", command=self.ende)

        mabout = Menu(menubar)
        mabout["tearoff"] = 0
        mabout.add_command(label="Credits", command=self.showcredits)
        mabout.add_command(label="About", command=self.showabout)

        mcallmonitor = Menu(menubar)
        mcallmonitor["tearoff"] = 0
        mcallmonitor.add_command(label="Call Monitor", command=self.ende)

        menubar.add_cascade(label="Program", menu=mprogram)
        menubar.add_cascade(label="Call Monitor", menu=mcallmonitor)
        menubar.add_cascade(label="Help", menu=mabout)

        window["menu"] = menubar

        # ----------------------------------------------------------
        # Frame: Top level
        # ----------------------------------------------------------

        infoframe = Frame(window, height=150, width=1100, bd=6)
        infoframe.grid(row=0, column=0, sticky="NW")
        infoframe.grid_propagate(0)

        # User credentials frame

        self.ttkframe = tkinter.LabelFrame(infoframe,
                                           text="Connection and user credentials",
                                           height=140,
                                           width=300,
                                           padx=5,
                                           pady=15)
        self.ttkframe.grid(row=0, column=0, sticky="NW", padx=framepadx)
        self.ttkframe.grid_propagate(False)

        self.fritzboxaddress_label = tkinter.Label(self.ttkframe, text="IP-Address", padx=5, pady=3)
        self.fritzboxaddress_label.grid(row=1, column=1, sticky="NW")
        self.fritzboxaddress_value = tkinter.Entry(self.ttkframe, width=15)
        self.fritzboxaddress_value.grid(row=1, column=2)
        self.fritzboxaddress_value.insert(0, FRITZ_IP_ADDRESS)

        self.fritzboxport_label = tkinter.Label(self.ttkframe, text="Port Address", padx=5, pady=3)
        self.fritzboxport_label.grid(row=2, column=1, sticky="NW")
        self.fritzboxport_value = tkinter.Entry(self.ttkframe, width=15)
        self.fritzboxport_value.grid(row=2, column=2)
        self.fritzboxport_value.insert(0, FRITZ_TCP_PORT)

        self.fritzboxuser_label = tkinter.Label(self.ttkframe, text="Username", padx=5, pady=3)
        self.fritzboxuser_label.grid(row=3, column=1, sticky="NW")
        self.fritzboxuser_value = tkinter.Entry(self.ttkframe, width=15)
        self.fritzboxuser_value.grid(row=3, column=2)
        self.fritzboxuser_value.insert(0, FRITZ_USERNAME)

        self.fritzboxpassword_label = tkinter.Label(self.ttkframe, text="Password", padx=5, pady=3)
        self.fritzboxpassword_label.grid(row=4, column=1, sticky="NW")
        self.fritzboxpassword_value = tkinter.Entry(self.ttkframe, width=15, show="*")
        self.fritzboxpassword_value.grid(row=4, column=2)
        self.fritzboxpassword_value.insert(0, FRITZ_PASSWORD)

        # Connect button

        self.connectbutton = tkinter.Button(self.ttkframe, text="Connect", command=lambda: self.connect2fritz(
            self.fritzboxaddress_value.get(),
            self.fritzboxport_value.get(),
            self.fritzboxuser_value.get(),
            self.fritzboxpassword_value.get(),
            self.ServiceListBox
        ))
        self.connectbutton.grid(row=1, column=3, rowspan=2, padx=10)

        # Anonymous login checkbox

        self.anonymousloginlabel = tkinter.Label(self.ttkframe, text="Anonymous login", padx=5, pady=3)
        self.anonymousloginlabel.grid(row=3, column=3, sticky="NW")

        self.chbuttonanonymlogin = tkinter.Checkbutton(self.ttkframe,
                                                       borderwidth=0,
                                                       padx=0,
                                                       pady=0,
                                                       variable=self.varanonymlogin,
                                                       command=self.anonymouslogin)

        self.chbuttonanonymlogin.grid(row=4, column=3, padx=10)

        # fritzbox information frame

        self.fritzinfoframe = tkinter.LabelFrame(infoframe,
                                                 text="Fritzbox information",
                                                 height=140,
                                                 width=250,
                                                 padx=5,
                                                 pady=15)
        self.fritzinfoframe.grid(row=0, column=1, sticky="NW", padx=framepadx)
        self.fritzinfoframe.grid_propagate(False)

        self.fritzboxtype_label = tkinter.Label(self.fritzinfoframe, text="Type", padx=0, pady=3)
        self.fritzboxtype_label.grid(row=1, column=0, sticky="NW")
        self.fritzboxtype_value = tkinter.Entry(self.fritzinfoframe, width=25)
        self.fritzboxtype_value.config(state="disabled", disabledbackground="white")
        self.fritzboxtype_value.grid(row=1, column=2)

        self.fritzboxver_label = tkinter.Label(self.fritzinfoframe, text="Version", padx=0, pady=3)
        self.fritzboxver_label.grid(row=2, column=0, sticky="NW")
        self.fritzboxver_value = tkinter.Entry(self.fritzinfoframe, width=25)
        self.fritzboxver_value.config(state="disabled", disabledbackground="white")
        self.fritzboxver_value.grid(row=2, column=2)

        self.fritzboxmgmt_label = tkinter.Label(self.fritzinfoframe, text="Mgmt URL ", padx=0, pady=3)
        self.fritzboxmgmt_label.grid(row=3, column=0, sticky="NW")
        self.fritzboxmgmt_value = tkinter.Entry(self.fritzinfoframe, width=25)
        self.fritzboxmgmt_value.grid(row=3, column=2)

        # permissions frame

        rightsframe = tkinter.LabelFrame(infoframe,
                                         text="User Rights",
                                         height=140,
                                         width=110,
                                         padx=5,
                                         pady=0)
        rightsframe.grid(row=0, column=2, sticky="NW", padx=framepadx)
        rightsframe.grid_propagate(False)

        varboxadmin = tkinter.IntVar()
        self.chbuttonrightboxadmin = tkinter.Checkbutton(rightsframe, borderwidth=0, padx=0, pady=0, text="BoxAdmin",
                                                         variable=varboxadmin)
        self.chbuttonrightboxadmin.grid(row=1, column=6, sticky="NW", ipadx=0, ipady=0, padx=0, pady=0)
        self.chbuttonrightboxadmin.config(state="disabled", disabledforeground="black")

        varphone = tkinter.IntVar()
        self.chbuttonrightphone = tkinter.Checkbutton(rightsframe, borderwidth=0, padx=0, pady=0, text="Phone",
                                                      variable=varphone)
        self.chbuttonrightphone.grid(row=2, column=6, sticky="NW", ipadx=0, ipady=0, padx=0, pady=0)
        self.chbuttonrightphone.config(state="disabled", disabledforeground="black")

        vardial = tkinter.IntVar()
        self.chbuttonrightdial = tkinter.Checkbutton(rightsframe, borderwidth=0, padx=0, text="Dial",
                                                     variable=vardial)
        self.chbuttonrightdial.grid(row=3, column=6, sticky="NW", ipadx=0, ipady=0, padx=0, pady=0)
        self.chbuttonrightdial.config(state="disabled", disabledforeground="black")

        varnas = tkinter.IntVar()
        self.chbuttonrightnas = tkinter.Checkbutton(rightsframe, borderwidth=0, padx=0, pady=0, text="Nas",
                                                    variable=varnas)
        self.chbuttonrightnas.grid(row=4, column=6, sticky="NW", ipadx=0, ipady=0, padx=0, pady=0)
        self.chbuttonrightnas.config(state="disabled", disabledforeground="black")

        varhomeauto = tkinter.IntVar()
        self.chbuttonrighthome = tkinter.Checkbutton(rightsframe, borderwidth=0, padx=0, pady=0, text="HomeAuto",
                                                     variable=varhomeauto)
        self.chbuttonrighthome.grid(row=5, column=6, sticky="NW", ipadx=0, ipady=0, padx=0, pady=0)
        self.chbuttonrighthome.config(state="disabled", disabledforeground="black")

        varapp = tkinter.IntVar()
        self.chbuttonrightapp = tkinter.Checkbutton(rightsframe, borderwidth=0, padx=0, pady=0, text="App",
                                                    variable=varapp)
        self.chbuttonrightapp.grid(row=6, column=6, sticky="NW", ipadx=0, ipady=0, padx=0, pady=0)
        self.chbuttonrightapp.config(state="disabled", disabledforeground="black")

        # status information frame

        statusframe = tkinter.LabelFrame(infoframe, text="Status Information", height=140, width=315, padx=15, pady=15)
        statusframe.grid(row=0, column=3, sticky="NW", padx=framepadx)
        statusframe.grid_propagate(False)

        self.connectiondetailsscrollbar = tkinter.Scrollbar(statusframe, orient="vertical")
        self.connectiondetailsscrollbar.grid(row=0, column=1, sticky="NS")

        self.connectiondetails = tkinter.Text(statusframe, height=6, width=43, background="black", foreground="green",
                                              font=(1, 8), yscrollcommand=self.connectiondetailsscrollbar.set)
        self.connectiondetails.grid(row=0, column=0, sticky="NW")

        self.connectiondetailsscrollbar.config(command=self.connectiondetails.yview)

        dataframe = Frame(window, height=400, width=1100, bd=6)
        dataframe.grid(row=1, column=0, sticky="NW")
        dataframe.grid_propagate(0)

        # ----------------------------------------------------------
        # Frame: Service Frame LEFT
        # ----------------------------------------------------------

        self.ServiceFrame = Frame(dataframe, height=400, width=300, bd=1)
        self.ServiceFrame.grid(row=0, column=0, sticky="NW")

        self.ServiceText = tkinter.Label(self.ServiceFrame, text="Fritzbox Services")
        self.ServiceText.grid(row=0, column=0, sticky="NS")

        self.ServiceListBoxScrollbar = tkinter.Scrollbar(self.ServiceFrame, orient="vertical")
        self.ServiceListBoxScrollbar.grid(row=1, column=1, sticky="NS")
        self.ServiceListBox = tkinter.Listbox(self.ServiceFrame,
                                              height=20,
                                              width=40,
                                              bd=2,
                                              selectmode="tk.SINGLE",
                                              exportselection=0)
        self.ServiceListBox.bind("<ButtonRelease-1>", self.actions)

        self.ServiceListBox.config(yscrollcommand=self.ServiceListBoxScrollbar.set)
        self.ServiceListBoxScrollbar.config(command=self.ServiceListBox.yview)
        self.ServiceListBox.grid(row=1, column=0, sticky="NW")

        self.ServiceFrame.grid_propagate(0)

        # ----------------------------------------------------------
        # Frame:  Action Frame MID
        # ----------------------------------------------------------

        self.ActionFrame = Frame(dataframe, height=400, width=300, bd=1)
        self.ActionFrame.grid(row=0, column=1, sticky="NW")

        self.ActionText = Label(self.ActionFrame, text="Service Actions")
        self.ActionText.grid(row=0, column=0, sticky="NS")

        self.ActionListScrollbar = tkinter.Scrollbar(self.ActionFrame, orient="vertical")
        self.ActionListScrollbar.grid(row=1, column=1, sticky="NS")
        self.ActionListBox = tkinter.Listbox(self.ActionFrame, height=20, width=40, bd=2, selectmode="tk.SINGLE",
                                             exportselection=0)
        self.ActionListBox.bind("<ButtonRelease-1>", self.actiondoubleclick)

        self.ActionListBox.config(yscrollcommand=self.ActionListScrollbar.set)
        self.ActionListScrollbar.config(command=self.ActionListBox.yview)
        self.ActionListBox.grid(row=1, column=0, sticky="NW")

        self.ActionFrame.grid_propagate(0)

        # ----------------------------------------------------------
        # Frame:  TreeViewFrame RIGHT
        # ----------------------------------------------------------

        self.TreeViewFrame = tkinter.Frame(dataframe, height=400, width=800, bd=3)
        self.TreeViewFrame.grid(row=0, column=3, sticky="NW")

        self.DetailText = Label(self.TreeViewFrame, text="Details")
        self.DetailText.grid(row=0, column=0)

        self.TreeViewListScrollbar = tkinter.Scrollbar(self.TreeViewFrame, orient="vertical")
        self.TreeViewListScrollbar.grid(row=1, column=1, sticky="NS")

        self.tree = tkinter.ttk.Treeview(self.TreeViewFrame)
        self.tree["columns"] = ("one", "two")
        self.tree.column("one", width=100)
        self.tree.column("two", width=100)
        self.tree.heading("one", text="in/out")
        self.tree.heading("two", text="Format")
        self.tree.grid(row=1, column=0, sticky="NW")

        self.tree.config(yscrollcommand=self.TreeViewListScrollbar.set)
        self.TreeViewListScrollbar.config(command=self.tree.yview)
        self.tree.bind("<ButtonRelease-1>", self.queryaction)
        self.TreeViewFrame.grid_propagate(0)

        # Query Results

        self.DetailText = tkinter.Label(self.TreeViewFrame, text="Query Result")
        self.DetailText.grid(row=2, column=0)

        self.Actionresultscrollbar = tkinter.Scrollbar(self.TreeViewFrame, orient="vertical")
        self.Actionresultscrollbar.grid(row=3, column=1, sticky="NS")

        self.ActionResult = tkinter.Text(self.TreeViewFrame,
                                         height=5,
                                         width=67,
                                         background="black",
                                         foreground="green",
                                         font=(1, 8),
                                         yscrollcommand=self.Actionresultscrollbar.set)
        self.ActionResult.grid(row=3, column=0, sticky="NW")

    def anonymouslogin(self):
        if self.varanonymlogin.get() == 1:
            self.fritzboxuser_value.config(state=tkinter.DISABLED)
            self.fritzboxpassword_value.config(state=tkinter.DISABLED)
        else:
            self.fritzboxuser_value.config(state=tkinter.NORMAL)
            self.fritzboxpassword_value.config(state=tkinter.NORMAL)

    def addstatusentry(self, string):
        now = datetime.datetime.now().time()
        self.connectiondetails.insert(tkinter.END, now.strftime("%H:%M:%S - ") + string)
        self.connectiondetails.update()
        self.connectiondetails.see(tkinter.END)

    @staticmethod
    def ende():
        main.destroy()

    @staticmethod
    def showcredits():
        messagebox.showinfo("Credits", "The following sources have been used to create this software:\n\n"
                                       "Fritzconnection by Klaus Bremer\n "
                                       "https://bitbucket.org/kbr/fritzconnection\n\n"
                                       "py-fritz-monitor by Robin Meis\n"
                                       " https://github.com/HcDevel/py-fritz-monitor\n")

    @staticmethod
    def showabout():
        messagebox.showinfo("Version Information",
                            " Name: tkFritzInfo \n Version %s \n Horst@skat-foundation" % str(get_version()))

    def connect2fritz(self, address, port, name, password, servicelistbox):
        servicelistbox.delete(0, tkinter.END)
        self.ActionListBox.delete(0, tkinter.END)
        self.tree.delete(*self.tree.get_children())

        if self.varanonymlogin.get() == 1:
            GUI.connection = FritzConnection(address=address, port=port, user="", password="")
            self.addstatusentry("Initiating anonymous connection...\n")
            self.chbuttonrightboxadmin.deselect()
            self.chbuttonrightphone.deselect()
            self.chbuttonrightdial.deselect()
            self.chbuttonrightnas.deselect()
            self.chbuttonrighthome.deselect()
            self.chbuttonrightapp.deselect()

        else:
            GUI.connection = FritzConnection(address=address, port=port, user=name, password=password)
            self.addstatusentry("Initiating user connection...\n")

            # Check the level of permission for the user given in the authentication credentials
            # Test if given password works by executing an action that required an authenticated user
            connectstatus = GUI.connection.call_action("LANConfigSecurity", "X_AVM-DE_GetCurrentUser")
            xml = connectstatus["NewX_AVM-DE_CurrentUserRights"]
            root = eTree.fromstring(xml)

            if root.tag != "rights":
                self.addstatusentry("Error: File is not a Fritzbox rights XML file.\n")
                exit()
            i = 0
            self.addstatusentry("Show user rights...\n")
            self.addstatusentry("Getting services...\n")

            for child in root:
                if child.tag == "path":
                    if root[i].text == "BoxAdmin":
                        if root[i+1].text == "readwrite":
                            self.chbuttonrightboxadmin.select()
                        else:
                            self.chbuttonrightboxadmin.deselect()
                    elif root[i].text == "Phone":
                        if root[i+1].text == "readwrite":
                            self.chbuttonrightphone.select()
                        else:
                            self.chbuttonrightphone.deselect()
                    elif root[i].text == "Dial":
                        if root[i + 1].text == "readwrite":
                            self.chbuttonrightdial.select()
                        else:
                            self.chbuttonrightdial.deselect()
                    elif root[i].text == "NAS":
                        if root[i + 1].text == "readwrite":
                            self.chbuttonrightnas.select()
                        else:
                            self.chbuttonrightnas.deselect()
                    elif root[i].text == "HomeAuto":
                        if root[i + 1].text == "readwrite":
                            self.chbuttonrighthome.select()
                        else:
                            self.chbuttonrighthome.deselect()
                    elif root[i].text == "App":
                        if root[i+1].text == "readwrite":
                            self.chbuttonrightapp.select()
                        else:
                            self.chbuttonrightapp.deselect()
                i += 1

            # fill fritzbox information fields

            fritzinfo = GUI.connection.call_action("DeviceInfo", "GetInfo")

            self.fritzboxtype_value.config(state="normal")
            self.fritzboxtype_value.delete(0, tkinter.END)
            self.fritzboxtype_value.insert(tkinter.END, fritzinfo["NewHardwareVersion"])
            self.fritzboxtype_value.config(state="disabled", disabledforeground="black")

            self.fritzboxver_value.config(state="normal")
            self.fritzboxver_value.delete(0, tkinter.END)
            self.fritzboxver_value.insert(tkinter.END, fritzinfo["NewSoftwareVersion"])
            self.fritzboxver_value.config(state="disabled", disabledforeground="black")

            mgmtinfo = GUI.connection.call_action("ManagementServer", "GetInfo")

            self.fritzboxmgmt_value.config(state="normal")
            self.fritzboxmgmt_value.delete(0, tkinter.END)
            self.fritzboxmgmt_value.insert(tkinter.END, mgmtinfo["NewURL"])

        if GUI.connection.modelname is not None:
            for name in sorted(GUI.connection.services.keys()):
                servicelistbox.insert("end", name)
        else:
            self.addstatusentry("Error: Connection failure.\n")
            exit()

    def actions(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        self.ServiceListBox.activate(index)
        self.ServiceListBox.selection_set(index)
        value = w.get(index)
        self.ActionListBox.delete(0, "end")
        GUI.currentservice = value
        for name in sorted(GUI.connection.services[value].actions.keys()):
            self.ActionListBox.insert("end", name)

    def actiondoubleclick(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        GUI.currentaction = value
        self.tree.delete(*self.tree.get_children())
        id2 = self.tree.insert("", 1, value, text=value)
        for argument in sorted(
                GUI.connection.get_action_arguments(GUI.currentservice, value)):
            self.tree.insert(id2, "end", argument[0], text=argument[0], values=(argument[1], argument[2]))
        self.tree.item(id2, open="true")

    def queryaction(self, evt):
        self.addstatusentry("Receiving data...\n")
        w = evt.widget
        self.ActionResult.delete("1.0", "end")
        valuedictionary = w.item(w.focus())
        action = valuedictionary["text"]
        error = ActionError
        status = dict

        if valuedictionary["values"][0] == "in":
            self.ActionResult.insert("end", "Action ist kein Output.")
        else:
            try:
                status = GUI.connection.call_action(GUI.currentservice, GUI.currentaction)
                print(status[action])
                if not status[action]:
                    self.ActionResult.insert("end", "Error")
                if status[action] is None:
                    self.ActionResult.insert("end", "None")
                else:
                    self.ActionResult.insert("end", status[action])
            except KeyError as error:
                self.addstatusentry("Action Error " + str(error) + "\n")


def get_cli_arguments():
    parser = argparse.ArgumentParser(description='Fritzbox Display Services')
    parser.add_argument('-CP', '--CheckPrerequisites',
                        action='store_true',
                        help='Check if all software requirements are met to run the application'
                        )

    args = parser.parse_args()
    return args


# ----------------------------------------------------------
# Main program
# ----------------------------------------------------------

main = Tk()
main.title("tkFritzInfo")
main.resizable(width=False, height=False)
main.geometry('{}x{}'.format(1070, 530))
main.minsize(width=400, height=400)

program = GUI(main)

# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------

if __name__ == '__main__':
    args = get_cli_arguments()
    if args.CheckPrerequisites:
        print("Checking software prerequisites ...")
        dependencies = [
            'FritzConnection>=0.5.1',
            'lxml>=3.6.4',
            'requests>=2.11.1'
        ]
        print("-----------------------------------------------")
        print("lxml version                  :", pkg_resources.get_distribution("lxml").version)
        print("FritzConnection version       :", pkg_resources.get_distribution("FritzConnection").version)
        print("requests version              :", pkg_resources.get_distribution("requests").version)
        print("\nPython version                :", platform.python_version())
        print("Tkinter TCL version           :", tkinter.TclVersion)
        print("Tkinter TK version            :", tkinter.TkVersion)
        print("\nOperating system platform     :", platform.system())
        print("Operating system version      :", platform.release())
        print("-----------------------------------------------")
        try:
            modules = pkg_resources.require(dependencies)
        except pkg_resources.VersionConflict as Version_error:
            print("The following software dependency is not met:\n")
            print("Version installed :", Version_error.dist)
            print("Version required  :", Version_error.req)
            exit()
    main.mainloop()
