import socket
import random
import time
from colorama import Fore, Style, init

# Inicializar colores
init(autoreset=True)

# Base de conocimiento: Vectores de ataque potenciales por puerto
VECTORES_ATAQUE = {
    21: "FTP: Riesgo de inicio de sesión anónimo, exploits de fuerza bruta o vulnerabilidades de ejecución de código en versiones antiguas (ej. vsftpd 2.3.4).",
    22: "SSH: Objetivo común para ataques de diccionario y fuerza bruta. Se recomienda auditar si permite autenticación por contraseña simple.",
    23: "Telnet: ¡Crítico! Todo el tráfico (incluyendo credenciales) viaja en texto plano. Vulnerable a interceptación de datos (sniffing).",
    25: "SMTP: Posible enumeración de usuarios válidos del sistema o retransmisión abierta de correo (Open Relay).",
    53: "DNS: Exposición a transferencias de zona no autorizadas (AXFR) o envenenamiento de caché.",
    80: "HTTP: Superficie de ataque web. Requiere inspección de directorios ocultos, inyecciones de código (SQLi, XSS) o fallos en CMS.",
    110: "POP3: Descarga de correos sin cifrar. Las credenciales pueden ser capturadas fácilmente en la red local.",
    139: "NetBIOS: Divulgación de información sensible (chismoso). Permite enumerar nombres de sistemas, dominios y usuarios activos.",
    443: "HTTPS: Auditoría requerida para comprobar el uso de cifrados SSL/TLS obsoletos (Heartbleed, Poodle) o fallos web.",
    445: "SMB: Vector de máxima prioridad. Exposición a exploits de ejecución remota de código críticos (EternalBlue MS17-010, WannaCry).",
    3389: "RDP: Riesgo de secuestro de sesión, ataques de fuerza bruta o exploits de ejecución remota de código (BlueKeep)."
}

def escanear_puertos(ip_objetivo):
    puertos_clave = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 
        53: "DNS", 80: "HTTP", 110: "POP3", 139: "NetBIOS", 
        443: "HTTPS", 445: "SMB", 3389: "RDP"
    }

    print(Fore.YELLOW + f"\n[*] Iniciando escaneo sigiloso y aleatorizado en: {ip_objetivo}")
    print(Fore.CYAN + "-" * 55)

    # MEJORA DE SIGILO 1: Convertir las llaves en lista y desordenar el orden de escaneo
    # Esto rompe el patrón secuencial que los sistemas de detección (IDS) identifican fácilmente
    lista_puertos = list(puertos_clave.keys())
    random.shuffle(lista_puertos)

    puertos_abiertos = []

    for puerto in lista_puertos:
        servicio = puertos_clave[puerto]
        
        # MEJORA DE SIGILO 2: Retraso de tiempo aleatorio entre puertos (Antispam / Delay)
        # Hace que el tráfico se mezcle y parezca comportamiento humano normal
        delay = random.uniform(0.5, 1.5)
        time.sleep(delay)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        
        resultado = sock.connect_ex((ip_objetivo, puerto))
        
        if resultado == 0:
            print(Fore.GREEN + f"[+] Puerto {puerto} ({servicio}) -> ABIERTO")
            puertos_abiertos.append(puerto)
        else:
            print(Fore.RED + f"[-] Puerto {puerto} ({servicio}) -> CERRADO")
            
        sock.close()

    print(Fore.CYAN + "-" * 55)
    print(Fore.YELLOW + "[*] Escaneo de puertos finalizado.")

    # MÓDULO DE REPORTE E INTELIGENCIA (Solo si se encontraron puertos abiertos)
    if puertos_abiertos:
        # Aseguramos ordenar los puertos numéricamente para los reportes finales
        puertos_ordenados = sorted(puertos_abiertos)
        
        print(Fore.GREEN + "\n[+] ANÁLISIS POST-ESCANEO:")
        
        # MEJORA 3: Generar cadena formateada para copiar directo a Nmap
        cadena_nmap = ",".join(map(str, puertos_ordenados))
        print(Fore.BLUE + f"[*] Cadena rápida para Nmap: -p {cadena_nmap}")
        
        # MEJORA 4: Exportación automática a formato Grepable (.gnmap)
        nombre_archivo = f"scan_{ip_objetivo.replace('.', '_')}.gnmap"
        try:
            with open(nombre_archivo, "w") as f:
                detalles = ", ".join([f"{p}/open/tcp" for p in puertos_ordenados])
                f.write(f"Host: {ip_objetivo} | Ports: {detalles}\n")
            print(Fore.BLUE + f"[*] Resultados exportados con éxito a: {nombre_archivo}")
        except Exception as e:
            print(Fore.RED + f"[-] No se pudo exportar el archivo: {e}")
            
        # MEJORA 5: Despliegue automatizado de vectores de ataque sugeridos
        print(Fore.MAGENTA + "\n[!] MAPEO DE SUPERFICIE DE ATAQUE (VECTORES SUGERIDOS):")
        print(Fore.CYAN + "=" * 55)
        for puerto in puertos_ordenados:
            if puerto in VECTORES_ATAQUE:
                print(Fore.YELLOW + f"-> Puerto {puerto}: " + Fore.WHITE + VECTORES_ATAQUE[puerto])
        print(Fore.CYAN + "=" * 55)
        
    else:
        print(Fore.RED + "\n[-] No se detectaron puertos objetivos abiertos en este host.")

if __name__ == "__main__":
    ip_objetivo = input("[*] Ingrese la dirección IP del objetivo: ")
    escanear_puertos(ip_objetivo)