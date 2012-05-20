#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       pyploma.py
#       
#       Copyright 2012 Francisco J. Ruiz-Ruano <fjruizruano@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import MySQLdb
import pygtk
import gtk as Gtk
from subprocess import call

class pyploma_gui:

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("pyploma.glade")
        self.handlers = {"onDeleteWindow": Gtk.main_quit,
                        "onLoadActivate": self.onLoadActivate,
                        "onAboutDialog": self.onAboutDialog,
                        "onCloseAbout": self.onCloseAbout,}
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("window1")
        self.window.show_all()

    def onLoadActivate(self, menuitem):
        self.load = menuitem.get_label()

        file1 = self.builder.get_object("filechooserbutton1")
        file2 = self.builder.get_object("filechooserbutton2")
        entry1 = self.builder.get_object("entry1")
        entry2 = self.builder.get_object("entry2")
        entry3 = self.builder.get_object("entry3")
        entry4 = self.builder.get_object("entry4")

        f1 = file1.get_filename()
        f2 = file2.get_filename()
        ent1 = entry1.get_text()
        ent2 = entry2.get_text()
        ent3 = entry3.get_text()
        ent4 = entry4.get_text()
        
        lista = open(f1, "r").readlines()
        Conexion = MySQLdb.connect(host="localhost", user="crud", passwd="crudpass", db="DBdeCrud")
        micursor = Conexion.cursor()
        try:
            micursor.execute("DROP TABLE New;")
        except:
            pass
        micursor.execute("CREATE TABLE New (id INT, Nombre VARCHAR(100), Apellidos VARCHAR(100), Dni VARCHAR(8), Letra VARCHAR(1));")
        Conexion.commit()
        counter = 0
        for line in lista:
            
            Conexion.commit()
            counter += 1
            person = line[0:-1].split("\t")
            print person
            micursor.execute("INSERT INTO New (id, Nombre, Apellidos, Dni, Letra) VALUES (\"%s\",\"%s\",\"%s\",%s,\"%s\");" % (counter, person[0], person[1], person[2], person[3]))
        Conexion.commit()
        micursor.execute("SELECT * FROM New;")
        num_reg = micursor.rowcount
        registros = micursor.fetchmany(num_reg)
        a = 100
        for registro in registros:
            print registro
            a += 1
            b = str(a)
            salida = open("output" + b + ".tex", "w")
                
            text = open("certi.tex")
            text = text.read()
            text_list = list(text)

            y_firma = text.find("%pointfirma")
            z_firma = len("%pointfirma")+1
            text_list[y_firma+z_firma:y_firma+z_firma] = list(ent4)
            
            y_info = text.find("%pointinfo")
            z_info = len("%pointinfo")+1
            text_list[y_info+z_info:y_info+z_info] = list(ent3)
            
            y_curso = text.find("%pointcurso")
            z_curso = len("%pointcurso")+1
            text_list[y_curso+z_curso:y_curso+z_curso] = list(ent2)

            y_dni = text.find("%pointdni")
            z_dni = len("%pointdni")+1
            text_list[y_dni+z_dni:y_dni+z_dni] = list(registro[3])+list(registro[4])

            y_name = text.find("%pointname")
            z_name = len("%pointname")+1
            text_list[y_name+z_name:y_name+z_name] = list(registro[1])+list(" ")+list(registro[2])

            y_aso = text.find("%pointaso")
            z_aso = len("%pointaso")+1
            text_list[y_aso+z_aso:y_aso+z_aso] = list(ent1)

            y_logo = text.find("%pointlogo")
            z_logo = len("%pointlogo")+1
            text_list[y_logo+z_logo:y_logo+z_logo] = list(f2)

            text_final = "".join(text_list)

            salida.write(text_final)
            salida.close

            comp = "pdflatex output%s.tex &" % b
            call(comp, shell=True)

    def onAboutDialog(self, *args):
        self.about = self.builder.get_object("aboutdialog1")
        self.about.show_all()

    def onCloseAbout(self, *args):
        self.about = self.builder.get_object("aboutdialog1")
        self.about.hide()

def main():
    window = pyploma_gui()
    Gtk.main()
    return 0

if __name__ == "__main__":
    main()
