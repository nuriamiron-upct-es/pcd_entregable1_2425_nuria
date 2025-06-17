from enum import Enum
from datetime import datetime
import random

# --- Enumeraciones y excepciones personalizadas ---
class MedioEntrada(Enum):
    FORMULARIO = 1
    LLAMADA = 2
    FAX = 3

class ErrorVehiculo(Exception): pass
class ErrorCargaExcesiva(Exception): pass
class ErrorEmpleadoOcupado(Exception): pass

# --- Modelos principales ---
class Usuario:
    def __init__(self, dni, nombre, direccion):
        self.dni = dni
        self.nombre = nombre
        self.direccion = direccion
        self.pedidos_previos = []

    def resumen_mensual(self, mes):
        total = 0
        kms = 0
        for pedido in self.pedidos_previos:
            if pedido.fecha.month == mes:
                total += pedido.coste_total
                kms += pedido.destino.distancia
        return f"Resumen {mes}: {total}€ y {kms}km"

class CiudadDestino:
    def __init__(self, nombre, distancia):
        self.nombre = nombre
        self.distancia = distancia

class TipoEntrega:
    def __init__(self, destino):
        self.destino = destino

class Domicilio(TipoEntrega):
    def __init__(self, destino):
        super().__init__(destino)
        self.tipo = 1

    def coste_extra(self): return 10

class OficinaCentral(TipoEntrega):
    def __init__(self, destino):
        super().__init__(destino)
        self.tipo = 2

class Envio:
    def __init__(self, id_envio, canal, destino, entrega, usuario):
        self.id_envio = id_envio
        self.canal = canal
        self.destino = destino
        self.entrega = entrega
        self.usuario = usuario
        self.fecha = datetime.now()
        self.bultos = []
        self.generar_bultos()
        self.coste_total = self.calcular_coste()

    def generar_bultos(self):
        cantidad = random.randint(1, 5)
        for i in range(cantidad):
            peso = round(random.uniform(1, 15), 2)
            self.bultos.append(Bulto(f"{self.id_envio}-{i}", peso, self.destino))

    def calcular_coste(self):
        peso_total = sum(p.peso for p in self.bultos)
        tarifa = (self.destino.distancia * 0.03) + peso_total * 0.5
        if isinstance(self.entrega, Domicilio):
            tarifa += self.entrega.coste_extra()
        return round(tarifa, 2)

    def mostrar_detalle(self):
        return f"Envio {self.id_envio}: {[f'{b.peso}kg a {b.destino.nombre}' for b in self.bultos]}"

class Bulto:
    def __init__(self, codigo, peso, destino):
        self.codigo = codigo
        self.peso = peso
        self.destino = destino

class Empleado:
    def __init__(self, id_emp, nombre):
        self.id = id_emp
        self.nombre = nombre
        self.ocupacion = {}

    def esta_disponible(self, fecha):
        return fecha not in self.ocupacion

    def asignar_tarea(self, tarea):
        fecha = tarea.fecha
        if not self.esta_disponible(fecha):
            raise ErrorEmpleadoOcupado("Empleado ya ocupado ese día")
        self.ocupacion[fecha] = tarea

class Transportista(Empleado):
    def __init__(self, id_emp, nombre, vehiculo):
        super().__init__(id_emp, nombre)
        self.vehiculo_autorizado = vehiculo

class Auxiliar(Empleado):
    def redactar_informe(self, viaje, detalle):
        viaje.informe = detalle

class UnidadMovil:
    def __init__(self, id_unidad, capacidad):
        self.id_unidad = id_unidad
        self.capacidad = capacidad
        self.historial = []

    def cargar_envios(self, envio):
        carga = sum(p.peso for p in envio.bultos)
        if carga > self.capacidad:
            raise ErrorCargaExcesiva("Carga excede capacidad")
        self.historial.append(envio)

class RutaServicio:
    def __init__(self, id_ruta, fecha):
        self.id = id_ruta
        self.fecha = fecha
        self.paquetes = []
        self.equipo = []
        self.informe = None

    def agregar_paquete(self, paquete):
        self.paquetes.append(paquete)

# --- Simulación de operación logística ---
def main():
    cliente = Usuario("11223344Z", "Ana López", "Gran Vía 10")
    destino = CiudadDestino("Sevilla", 120)
    entrega = Domicilio(destino)

    envio = Envio(1, MedioEntrada.LLAMADA, destino, entrega, cliente)
    cliente.pedidos_previos.append(envio)

    ruta = RutaServicio("RUTA01", datetime.now().date())
    for p in envio.bultos:
        ruta.agregar_paquete(p)

    vehiculo = UnidadMovil("ABC123", 500)
    try:
        vehiculo.cargar_envios(envio)
    except ErrorCargaExcesiva as error:
        print("Error en carga del vehículo:", error)

    conductor = Transportista("EMP001", "José García", "Furgoneta")
    asistente = Auxiliar("EMP002", "María Ruiz")

    try:
        conductor.asignar_tarea(ruta)
        asistente.asignar_tarea(ruta)
        ruta.equipo.append(conductor)
        ruta.equipo.append(asistente)
    except ErrorEmpleadoOcupado as error:
        print("Error al asignar personal:", error)

    asistente.redactar_informe(ruta, "Entrega retrasada por tráfico.")

    print(envio.mostrar_detalle())
    print(f"Vehículo asignado: {vehiculo.id_unidad}")
    print(f"ID Conductor: {conductor.id}, ID Ayudante: {asistente.id}")
    print("Informe del viaje:", ruta.informe)
    print(cliente.resumen_mensual(datetime.now().month))

if __name__ == "__main__":
    main()