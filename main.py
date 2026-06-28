#DISCO DE FABIANES - SIMULACIÓN DE ALMACENAMIENTO FÍSICO DE BASE DE DATOS
# - BUSTAMANTE TORRES, FABIAN
# - MEDINA GRADOS, FABIAN 
# - SALAS RAMOS, RODRIGO

import sys
import os
import csv
from PyQt6.QtWidgets import QApplication, QMessageBox
from basededatos.basededatos import BaseDeDatos
from util.estructura import leer_sql, parse_create_table, convertir_fila
from disco.disco import DISCO
from interfaz.interfaz import ConfigDialog, ArchivosDialog, VentanaPrincipal


def main():
    app = QApplication(sys.argv)

    # 1. Configuración del disco
    config = ConfigDialog()
    if not config.exec():
        return

    valores = config.get_valores()
    disco = DISCO(
        platos=valores["platos"],
        pistas=valores["pistas"],
        sectores_por_pista=valores["sectores"],
        tamano_sector=valores["tamano"]
    )

    # 2. Selección de archivos
    archivos = ArchivosDialog()
    if not archivos.exec():
        QMessageBox.warning(None, "Cancelado", "No se seleccionaron archivos.")
        return

    # 3. Cargar estructura y datos
    bd = BaseDeDatos(disco)

    try:
        sql = leer_sql(archivos.ruta_txt)
        nombre_tabla, estructura = parse_create_table(sql)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al procesar .txt:\n{e}")
        return

    try:
        filas = []
        with open(archivos.ruta_csv, encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo, delimiter=',', quotechar='"')
            for row in lector:
                fila = convertir_fila(estructura, row)
                filas.append(fila)

        bd.definir_tabla(nombre_tabla, estructura)

        try:
            bd.cargar_datos(nombre_tabla, filas)
        except MemoryError:
            QMessageBox.warning(None, "Advertencia",
                                "El disco se llenó durante la carga.\n"
                                "Se guardaron los registros que alcanzaron espacio.")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Error al cargar CSV:\n{e}")
        return

    # 4. Mostrar ventana principal
    ventana = VentanaPrincipal(disco, bd, nombre_tabla)
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
