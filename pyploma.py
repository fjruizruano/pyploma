#:wq!/usr/bin/env python
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
#

#
# Antes de ejecutar pyploma, debes crear una base de datos MySQL de esta forma:
# $ mysql -u root -p
# > CREATE DATABASE DBdeCrud;
# > GRANT ON ALL DBdeCrud.* TO "crud"@"localhost" IDENTIFIED BY "crudpass";
# > USE DBdeCrud
# > QUIT
#
# Introduce un fichero de texto plano como el ejemplo "listadip" con el nombre,
# apellidos, dni y letra del dni separados por tabulador. Seguidamente introduce
# una imagen y el resto de información. Al pulsar Run >> Crear, se crearán un
# fichero LaTeX para cada nombre del fichero y posteriormente se compilará en
# formato pdf. Finalmente, si pulsamos Run >> Unir, todos los pdfs creados se
# unirán en uno solo llamado "todos_diplomas.pdf"
#

import MySQLdb
import pygtk
import gtk as Gtk
from subprocess import call # para ejecutar comandos de consola

class pyploma_gui:

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("pyploma.glade")
        self.handlers = {"onDeleteWindow": Gtk.main_quit,
                        "onLoadActivate": self.onLoadActivate,
                        "onJoinActivate": self.onJoinActivate,
                        "onAboutDialog": self.onAboutDialog,
                        "onCloseAbout": self.onCloseAbout,}
        self.builder.connect_signals(self.handlers)
        self.window = self.builder.get_object("window1")
        self.window.show_all()

    # definimos módulo que se ejecutará
    def onLoadActivate(self, menuitem):
        self.load = menuitem.get_label()

        file1 = self.builder.get_object("filechooserbutton1") # entrada fichero con nombres y dni
        file2 = self.builder.get_object("filechooserbutton2") # entrada del logo
        entry1 = self.builder.get_object("entry1")  # entrada del nombre de la asociación
        entry2 = self.builder.get_object("entry2")  # entrada del nombre del curso
        entry3 = self.builder.get_object("entry3")  # entrada de información adicional del curso
        entry4 = self.builder.get_object("entry4")  # entrada del nombre y cargo del firmante

        # obtenemos la información anterior de la GUI
        f1 = file1.get_filename()
        f2 = file2.get_filename()
        ent1 = entry1.get_text()
        ent2 = entry2.get_text()
        ent3 = entry3.get_text()
        ent4 = entry4.get_text()
        
        lista = open(f1, "r").readlines() # abrimos fichero de nombre y dni
        Conexion = MySQLdb.connect(host="localhost", user="crud", passwd="crudpass", db="DBdeCrud") # conectamos a la base de datos
        micursor = Conexion.cursor() # creamos cursor
        try:
            micursor.execute("DROP TABLE New;") # Si existe tabla "New", la borramos
        except:
            pass
        micursor.execute("CREATE TABLE New (id INT, Nombre VARCHAR(100), Apellidos VARCHAR(100), Dni VARCHAR(10), Letra VARCHAR(1));") # creamos tabla
        Conexion.commit()
        counter = 0
        for line in lista: # para cada elemento de la lista
            
            Conexion.commit()
            counter += 1
            person = line[0:-1].split("\t") # para cada persona creamos una lista con el nombre, apellidos, dni y letra del dni
            print person
            micursor.execute("INSERT INTO New (id, Nombre, Apellidos, Dni, Letra) VALUES (\"%s\",\"%s\",\"%s\",%s,\"%s\");" % (counter, person[0], person[1], person[2], person[3])) # introducimos datos en la tabla
        Conexion.commit()
        micursor.execute("SELECT * FROM New;")
        num_reg = micursor.rowcount
        registros = micursor.fetchmany(num_reg) # recuperamos los registros de la base de datos
        a = 100
        for registro in registros: # para cada registro...
            print registro
            a += 1
            b = str(a)
            salida = open("output" + b + ".tex", "w") # creamos fichero LaTeX de salida
                
            text = open("certi.tex") # abrimos plantilla LaTeX
            text = text.read()
            text_list = list(text) # convertimos el texto en una lista

            # insertamos en la plantilla la información de la firma
            y_firma = text.find("%pointfirma")
            z_firma = len("%pointfirma")+1
            text_list[y_firma+z_firma:y_firma+z_firma] = list(ent4)
           
            # insertamos en la platilla la información adicional
            y_info = text.find("%pointinfo")
            z_info = len("%pointinfo")+1
            text_list[y_info+z_info:y_info+z_info] = list(ent3)
            
            # insertamos en la platilla el nombre del curso
            y_curso = text.find("%pointcurso")
            z_curso = len("%pointcurso")+1
            text_list[y_curso+z_curso:y_curso+z_curso] = list(ent2)

            # insertamos en la platilla el número y letra del dni
            y_dni = text.find("%pointdni")
            z_dni = len("%pointdni")+1
            text_list[y_dni+z_dni:y_dni+z_dni] = list(registro[3])+list(registro[4])

            # insertamos en la platilla el nombre y los apellidos 
            y_name = text.find("%pointname")
            z_name = len("%pointname")+1
            text_list[y_name+z_name:y_name+z_name] = list(registro[1])+list(" ")+list(registro[2])

            # insertamos en la platilla el nombre de la asociación 
            y_aso = text.find("%pointaso")
            z_aso = len("%pointaso")+1
            text_list[y_aso+z_aso:y_aso+z_aso] = list(ent1)

            # insertamos en la platilla el logotipo de la asociación 
            y_logo = text.find("%pointlogo")
            z_logo = len("%pointlogo")+1
            text_list[y_logo+z_logo:y_logo+z_logo] = list(f2)

            text_final = "".join(text_list) # convertimos la lista en cadena

            salida.write(text_final) # escribimos el fichero LaTeX de salida
            salida.close

            comp = "pdflatex output%s.tex &" % b 
            call(comp, shell=True) # ejecutamos comando para compilar LaTeX a pdf

        label7 = self.builder.get_object("label7")
        label7.set_label("DIPLOMAS CREADOS") # Creamos mensaje
    
    def onJoinActivate(self, menuitem):
        self.join = menuitem.get_label()
        call("pdftk output*.pdf cat output todos_diplomas.pdf", shell=True) # crea un pdf con todos los diplomas
        label7 = self.builder.get_object("label7")
        label7.set_label("DIPLOMAS UNIDOS") # Creamos mensaje

    # definimos ventana About
    def onAboutDialog(self, *args):
        self.about = self.builder.get_object("aboutdialog1")
        self.about.show_all()

    # definimos cierre de ventana About
    def onCloseAbout(self, *args):
        self.about = self.builder.get_object("aboutdialog1")
        self.about.hide()

def main():
    window = pyploma_gui()
    Gtk.main()
    return 0

if __name__ == "__main__":
    main()
