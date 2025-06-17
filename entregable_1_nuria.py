

from enum import Enum
import time
import pytest


class CapacidadExcedidaError(Exception): pass

class PedidoInvalidoError(Exception): pass


class EnumCanal(Enum):
    INGRESO = 1
    TELEFONO = 2
    FAX = 3


class Vehiculo:
    def __init__(self, capacidad_maxima, tipo):
        if capacidad_maxima <= 0:
            raise ValueError("La capacidad debe ser positiva")
        self.capacidad_maxima = capacidad_maxima
        self.tipo = tipo
        self.en_uso = False

    def esta_disponible(self):
        return not self.en_uso

    def asignar(self):
        if self.en_uso:
            raise Exception("Vehículo ya en uso")
        self.en_uso = True

    def liberar(self):
        self.en_uso = False

class VehiculoMotorizado(Vehiculo): pass
class VehiculoEcologico(Vehiculo): pass

class Furgoneta(VehiculoMotorizado):
    def __init__(self, capacidad): super().__init__(capacidad, "Furgoneta")
class Camion(VehiculoMotorizado):
    def __init__(self, capacidad): super().__init__(capacidad, "Camion")
class Bicicleta(VehiculoEcologico):
    def __init__(self, capacidad): super().__init__(capacidad, "Bicicleta")
class BicicletaElectrica(VehiculoMotorizado, VehiculoEcologico):
    def __init__(self, capacidad): Vehiculo.__init__(self, capacidad, "Bicicleta Electrica")

# --- TRABAJADORES ---
class Trabajador:
    def __init__(self, nombre): self.nombre = nombre
class Conductor(Trabajador): pass
class Ayudante(Trabajador): pass

# --- CLIENTES Y PAQUETES ---
class Cliente:
    def __init__(self, id, nombre, contacto):
        self.id = id
        self.nombre = nombre
        self.contacto = contacto
        self.facturas = []

    def agregar_factura(self, factura):
        self.facturas.append(factura)

class Paquete:
    def __init__(self, id, peso, destino):
        if peso <= 0:
            raise ValueError("Peso del paquete debe ser positivo")
        self.id = id
        self.peso = peso
        self.destino = destino

# --- PEDIDOS ---
class Pedido:
    def __init__(self, cliente, canal, recogida, numpedido, vehiculo):
        self.cliente = cliente
        self.canal = canal
        self.recogida = recogida
        self.numpedido = numpedido
        self.vehiculo = vehiculo
        self.paquetes = []

    def agregar_paquete(self, paquete):
        if self.peso_total() + paquete.peso > self.vehiculo.capacidad_maxima:
            raise CapacidadExcedidaError("Capacidad del vehiculo superada")
        self.paquetes.append(paquete)

    def peso_total(self):
        return sum(p.peso for p in self.paquetes)

# --- VIAJE Y PARTE ---
class ParteViaje:
    def __init__(self, viaje): self.viaje = viaje

    def generar(self):
        print(f"--- PARTE DE VIAJE ---\nVehiculo: {self.viaje.vehiculo.tipo}\nConductores: {self.viaje.conductor.nombre}" +
              (f" y {self.viaje.ayudante.nombre}" if self.viaje.ayudante else "") +
              f"\nPedidos: {len(self.viaje.pedidos)}\nDistancia: {self.viaje.distancia}km\nDuracion: {self.viaje.duracion}s\n---")

class Viaje:
    def __init__(self, pedidos, distancia, duracion, conductor, ayudante=None):
        self.pedidos = pedidos
        self.distancia = distancia
        self.duracion = duracion
        self.conductor = conductor
        self.ayudante = ayudante
        self.vehiculo = pedidos[0].vehiculo
        self.parte = ParteViaje(self)
        self.vehiculo.asignar()

    def iniciar(self):
        print(f"Iniciando viaje con {self.vehiculo.tipo}...")
        time.sleep(self.duracion)
        self.finalizar()

    def finalizar(self):
        self.vehiculo.liberar()
        self.parte.generar()

# --- FACTURACION ---
class Factura:
    def __init__(self, cliente, total):
        self.cliente = cliente
        self.total = total
        self.pagada = False

    def pagar(self):
        self.pagada = True
        print(f"Factura de {self.total}€ pagada por {self.cliente.nombre}.")

# --- SISTEMA DE LOGISTICA ---
class SistemaLogistica:
    def __init__(self):
        self.clientes = {}
        self.vehiculos = []
        self.trabajadores = []
        self.pedidos = []
        self.viajes = []
        self.facturas = []

    def registrar_cliente(self, id, nombre, contacto):
        c = Cliente(id, nombre, contacto)
        self.clientes[id] = c
        return c

    def registrar_vehiculo(self, tipo, capacidad):
        tipos = {
            "Furgoneta": Furgoneta,
            "Camion": Camion,
            "Bicicleta": Bicicleta,
            "BicicletaElectrica": BicicletaElectrica
        }
        v = tipos[tipo](capacidad)
        self.vehiculos.append(v)
        return v

    def registrar_trabajador(self, tipo, nombre):
        t = Conductor(nombre) if tipo == "Conductor" else Ayudante(nombre)
        self.trabajadores.append(t)
        return t

    def crear_pedido(self, cliente_id, canal, recogida, numpedido, vehiculo, paquetes):
        cliente = self.clientes[cliente_id]
        pedido = Pedido(cliente, canal, recogida, numpedido, vehiculo)
        for p in paquetes:
            pedido.agregar_paquete(p)
        self.pedidos.append(pedido)
        return pedido

    def planificar_viaje(self, pedidos, distancia, duracion, conductor, ayudante=None):
        viaje = Viaje(pedidos, distancia, duracion, conductor, ayudante)
        self.viajes.append(viaje)
        viaje.iniciar()

    def generar_factura(self, cliente_id, total):
        cliente = self.clientes[cliente_id]
        factura = Factura(cliente, total)
        cliente.agregar_factura(factura)
        self.facturas.append(factura)
        factura.pagar()

# --- EJEMPLO DE USO ---
if __name__ == "__main__":
    sistema = SistemaLogistica()

    cliente1 = sistema.registrar_cliente(1, "Caridad", "caridad@gmail.com")
    conductor = sistema.registrar_trabajador("Conductor", "Barbara")
    ayudante = sistema.registrar_trabajador("Ayudante", "Ana")
    furgoneta = sistema.registrar_vehiculo("Furgoneta", 1000)

    paquetes = [Paquete(1, 300, "Murcia"), Paquete(2, 400, "Yecla")]
    pedido = sistema.crear_pedido(1, EnumCanal.TELEFONO, True, 101, furgoneta, paquetes)

    sistema.planificar_viaje([pedido], 60, 2, conductor, ayudante)
    sistema.generar_factura(1, 80)
