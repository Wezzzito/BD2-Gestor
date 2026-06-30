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

    # ──────────────────────────────────────────────────────────────────
    #  ALMACENAMIENTO ATÓMICO
    #  Un registro ocupa SIEMPRE un único sector completo.
    #  Si no cabe entero, se rechaza (no se fragmenta).
    # ──────────────────────────────────────────────────────────────────
    def guardar_dato(self, registro_bytes, id_registro):
        tamano = len(registro_bytes)

        # 1) El registro debe caber COMPLETO en un sector
        if tamano > self.tamano_sector:
            raise ValueError(
                f"El registro '{id_registro}' pesa {tamano} bytes y el sector "
                f"solo tiene {self.tamano_sector} bytes. El registro no se "
                f"fragmenta: debe caber completo o se descarta."
            )

        # 2) Buscar un sector con espacio suficiente para el registro completo
        for lba in range(self.total_sectores):
            sector = self.sectores[lba]
            if sector is None:
                sector = Sector(self.tamano_sector)
                self.sectores[lba] = sector

            if sector.espacio_disponible() >= tamano:
                guardado = sector.agregar_fragmento(id_registro, registro_bytes)
                frag = sector.fragmentos[-1]
                # Un solo sector, una sola entrada en el directorio
                self.mapa_ubicacion_fisica[id_registro] = [(lba, frag['inicio'], frag['fin'])]
                return

        # 3) No hay ningún sector con espacio suficiente
        raise MemoryError(
            f"Disco lleno: no hay un sector con {tamano} bytes disponibles "
            f"para el registro '{id_registro}'."
        )

    def recuperar_dato(self, id_registro):
        if id_registro not in self.mapa_ubicacion_fisica:
            return None

        lba, _, _ = self.mapa_ubicacion_fisica[id_registro][0]
        sector = self.sectores[lba]
        if not sector:
            return None

        fragmentos = sector.obtener_fragmentos(id_registro)
        return fragmentos[0] if fragmentos else None

    def obtener_ubicacion(self, id_registro):
        return self.mapa_ubicacion_fisica.get(id_registro, None)