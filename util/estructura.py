import struct
import re

def leer_sql(nombre_archivo):
    with open(nombre_archivo, 'r') as f:
        return f.read()

def parse_create_table(sql):
    estructura = []
    nombre_tabla = None

    for linea in sql.splitlines():
        linea = linea.strip().strip(',').strip(';')

        if not linea:
            continue

        if 'create table' in linea.lower():
            match = re.search(r'create table\s+([a-zA-Z_][a-zA-Z0-9_]*)', linea, re.IGNORECASE)
            if match:
                nombre_tabla = match.group(1).lower()
            continue

        if linea.startswith("(") or linea.startswith(")"):
            continue

        # Eliminar decoradores
        linea = linea.split('not null')[0].split('primary key')[0].strip().lower()

        match = re.match(r'^([a-z_][a-z0-9_]*)\s+([a-z]+)(?:\(([^)]+)\))?', linea)
        if not match:
            continue

        nombre, tipo, params = match.groups()

        if tipo == "varchar" and params:
            estructura.append((nombre, f"{int(params)}s"))
        elif tipo in ("int", "integer"):
            estructura.append((nombre, "i"))
        elif tipo == "decimal":
            estructura.append((nombre, "d"))

    return nombre_tabla, estructura  


def empaquetar(estructura, datos):
    formato = '=' + ''.join(tipo for _, tipo in estructura)
    valores = []
    for (_, tipo), val in zip(estructura, datos):
        if tipo.endswith('s'):
            tam = int(tipo[:-1])
            valores.append(val.encode('utf-8')[:tam].ljust(tam, b'\x00'))
        else:
            valores.append(val)
    return struct.pack(formato, *valores)

def desempaquetar(estructura, registro_bytes):
    formato = '=' + ''.join(tipo for _, tipo in estructura)
    valores = struct.unpack(formato, registro_bytes)
    resultado = []
    for (_, tipo), val in zip(estructura, valores):
        if tipo.endswith('s'):
            resultado.append(val.decode('utf-8').rstrip('\x00'))
        else:
            resultado.append(val)
    return resultado

def convertir_fila(estructura, fila_dict):
    fila_convertida = []
    for (col, tipo) in estructura:
        val = (
            fila_dict.get(col) or
            fila_dict.get(col.capitalize()) or
            fila_dict.get(col.upper()) or
            fila_dict.get(col.lower())
        )
        if val is None:
            raise KeyError(f"Columna '{col}' no encontrada en el CSV")

        if tipo == 'i':
            fila_convertida.append(int(val))
        elif tipo == 'd':
            fila_convertida.append(float(val))
        elif tipo.endswith('s'):
            fila_convertida.append(val.strip())
        else:
            fila_convertida.append(val)
    return fila_convertida
