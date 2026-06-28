from disco.sector import Sector
class DISCO:
    def __init__(self, platos=2, pistas=20, sectores_por_pista=20, tamano_sector=16):
        self.platos = platos
        self.pistas_por_superficie = pistas
        self.sectores_por_pista = sectores_por_pista
        self.superficies_por_plato = 2
        self.tamano_sector = tamano_sector

        self.total_sectores = platos * self.superficies_por_plato * pistas * sectores_por_pista
        self.sectores = [None] * self.total_sectores
        self.mapa_ubicacion_fisica = {}  

    def _chs_a_lba(self, plato, superficie, pista, sector):
        spp = self.sectores_por_pista
        pps = self.pistas_por_superficie
        spf = self.superficies_por_plato
        sectores_por_plato = spf * pps * spp
        sectores_por_superficie = pps * spp
        return (plato * sectores_por_plato) + (superficie * sectores_por_superficie) + (pista * spp) + sector

    def _lba_a_chs(self, lba):
        if lba >= self.total_sectores:
            raise ValueError("fuera de rango")
        spp = self.sectores_por_pista
        pps = self.pistas_por_superficie
        spf = self.superficies_por_plato
        sectores_por_plato = spf * pps * spp
        sectores_por_superficie = pps * spp
        plato = lba // sectores_por_plato
        resto_plato = lba % sectores_por_plato
        superficie = resto_plato // sectores_por_superficie
        resto_sup = resto_plato % sectores_por_superficie
        pista = resto_sup // spp
        sector = resto_sup % spp
        return (plato, superficie, pista, sector)

    def guardar_dato(self, registro_bytes, id_registro):
        
        offset = 0
        total = len(registro_bytes)
        ubicaciones = []

        while offset < total:
            fragmento_restante = registro_bytes[offset:]

            for lba in range(len(self.sectores)):
                sector = self.sectores[lba]
                if sector is None:
                    sector = Sector(self.tamano_sector)
                    self.sectores[lba] = sector

                guardado = sector.agregar_fragmento(id_registro, fragmento_restante)
                if guardado > 0:
                    frag = sector.fragmentos[-1]
                    ubicaciones.append((lba, frag['inicio'], frag['fin']))
                    offset += guardado
                    break  
            else:
                raise MemoryError("¡Disco lleno!")
        self.mapa_ubicacion_fisica[id_registro] = ubicaciones

    def recuperar_dato(self, id_registro):
        if id_registro not in self.mapa_ubicacion_fisica:
            return None

        fragmentos = []
        for lba, _, _ in self.mapa_ubicacion_fisica[id_registro]:
            sector = self.sectores[lba]
            if sector:
                fragmentos.extend(sector.obtener_fragmentos(id_registro))

        return b''.join(fragmentos)

    def obtener_ubicacion(self, id_registro):
        return self.mapa_ubicacion_fisica.get(id_registro, None)
