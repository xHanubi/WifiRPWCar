import network
import socket
from time import sleep
import machine
from machine import Pin, I2C, PWM
import ssd1306
from ssd1306 import SSD1306_I2C

# Configuración de los pines OLED
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)  # GP15 (SCL) y GP14 (SDA)
oled_width = 128
oled_height = 32
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Configuración de los pines del motor
Motor_A_Adelante = PWM(Pin(18))  # Motor A adelante
Motor_A_Atras = PWM(Pin(19))     # Motor A atrás
Motor_B_Adelante = PWM(Pin(20))  # Motor B adelante
Motor_B_Atras = PWM(Pin(21))     # Motor B atrás

# Establecer la frecuencia para los motores
Motor_A_Adelante.freq(1000)
Motor_A_Atras.freq(1000)
Motor_B_Adelante.freq(1000)
Motor_B_Atras.freq(1000)

# Funciones de control del motor
def adelante(velocidad=65535):
    Motor_A_Adelante.duty_u16(velocidad)
    Motor_B_Adelante.duty_u16(velocidad)
    Motor_A_Atras.duty_u16(0)
    Motor_B_Atras.duty_u16(0)

def atras(velocidad=65535):
    Motor_A_Adelante.duty_u16(0)
    Motor_B_Adelante.duty_u16(0)
    Motor_A_Atras.duty_u16(velocidad)
    Motor_B_Atras.duty_u16(velocidad)

def detener():
    Motor_A_Adelante.duty_u16(0)
    Motor_B_Adelante.duty_u16(0)
    Motor_A_Atras.duty_u16(0)
    Motor_B_Atras.duty_u16(0)

def izquierda():
    Motor_A_Adelante.duty_u16(35000)  # Cambiar a avanzar motor A
    Motor_B_Adelante.duty_u16(65535)  # Detener motor B
    Motor_A_Atras.duty_u16(0)
    Motor_B_Atras.duty_u16(0)

def derecha():
    Motor_A_Adelante.duty_u16(65535)  # Detener motor A
    Motor_B_Adelante.duty_u16(35000)  # Cambiar a avanzar motor B
    Motor_A_Atras.duty_u16(0)
    Motor_B_Atras.duty_u16(0)

def izquierda_lenta(duracion=0.1):
    Motor_A_Adelante.duty_u16(0)
    Motor_B_Adelante.duty_u16(65535)
    Motor_A_Atras.duty_u16(0)
    Motor_B_Atras.duty_u16(0)
    sleep(duracion)
    detener()

def derecha_lenta(duracion=0.1):
    Motor_A_Adelante.duty_u16(65535)
    Motor_B_Adelante.duty_u16(0)
    Motor_A_Atras.duty_u16(0)
    Motor_B_Atras.duty_u16(0)
    sleep(duracion)
    detener()

detener()

# Crear el punto de acceso (AP)
def crear_ap():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid='PicoW_AP', password='12345678')  # Nombre y clave del AP
    ap.active(True)
    
    while not ap.active():
        pass
    
    ip = ap.ifconfig()[0]
    print(f'Punto de acceso activo con IP: {ip}')
    
    # Mostrar la IP en la pantalla OLED
    oled.fill(0)  # Limpiar pantalla
    oled.text("Conectado a IP", 0, 0)
    oled.text(f'{ip}', 0, 10)
    oled.show()
    
    return ip

# Abrir socket para conexión
def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

# Página web del control
def pagina_web(): 
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            </head>
            <body>
            <center>
            <form action="./adelante">
            <input type="submit" value="Adelante" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px" />
            </form>
            <form action="./adelante_lento">
            <input type="submit" value="Adelante Lento" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px" />
            </form>
            <table><tr>
            <td>
                <form action="./izquierda">
                    <input type="submit" value="Izquierda" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
                </form>
            </td>
            <td>
                <form action="./izquierda_lenta">
                    <input type="submit" value="Diagonal Izq" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
                </form>
            </td>
            <td>
                <form action="./detener">
                    <input type="submit" value="Detener" style="background-color: #FF0000; border-radius: 50px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px" />
                </form>
            </td>
            <td>
                <form action="./derecha_lenta">
                    <input type="submit" value="Diagonal Der" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
                </form>
            </td>
            <td>
                <form action="./derecha">
                    <input type="submit" value="Derecha" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
                </form>
            </td>
            </tr></table>
            <form action="./atras_lento">
            <input type="submit" value="Atras Lento" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
            </form>
            <form action="./atras">
            <input type="submit" value="Atras" style="background-color: #04AA6D; border-radius: 15px; height:120px; width:120px; border: none; color: white; padding: 16px 24px; margin: 4px 2px"/>
            </form>
            </center>
            </body>
            </html>
            """
    return str(html)

# Servidor que gestiona las solicitudes
def serve(connection):
    while True:
        cliente = connection.accept()[0]
        peticion = cliente.recv(1024)
        peticion = str(peticion)
        try:
            peticion = peticion.split()[1]
        except IndexError:
            pass
        if peticion == '/adelante?':
            adelante(65535)  # Velocidad normal
        elif peticion == '/adelante_lento?':
            adelante(40000)  # Velocidad reducida
        elif peticion == '/izquierda?':
            izquierda()
        elif peticion == '/izquierda_lenta?':
            izquierda_lenta(duracion=0.1)
        elif peticion == '/detener?':
            detener()
        elif peticion == '/derecha?':
            derecha()
        elif peticion == '/derecha_lenta?':
            derecha_lenta(duracion=0.1)
        elif peticion == '/atras?':
            atras(65535)
        elif peticion == '/atras_lento?':
            atras(40000)

        cliente.send('HTTP/1.1 200 OK\n')
        cliente.send('Content-Type: text/html\n')
        cliente.send('Connection: close\n\n')
        cliente.sendall(pagina_web())
        cliente.close()

# Función principal
def main():
    ip = crear_ap()  # Crear el punto de acceso
    connection = open_socket(ip)
    serve(connection)

# Ejecutar el código principal
main()

