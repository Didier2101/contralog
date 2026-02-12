# app/core/errors.py

class ContraLogError(Exception):
    """Base para todos los errores de la aplicación"""
    pass

class RegistroNoEncontrado(ContraLogError):
    def __init__(self, entidad: str, id_valor: any):
        self.mensaje = f"{entidad} con identificador '{id_valor}' no existe."
        super().__init__(self.mensaje)

class DatosDuplicados(ContraLogError):
    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(self.mensaje)

class ErrorOperacion(ContraLogError):
    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(self.mensaje)

class CredencialesInvalidas(ContraLogError):
    def __init__(self, mensaje: str = "Email o contraseña incorrectos"):
        self.mensaje = mensaje
        super().__init__(self.mensaje)