import socket
import time
import json
import subprocess
import platform
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from colorama import Fore, Style, init

# Inicializar colores
init(autoreset=True)

PUERTOS_CLAVE = {
    20: "FTP Data", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 111: "RPCBind", 135: "MSRPC",
    139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS",
    587: "SMTP Submission", 993: "IMAPS", 995: "POP3S", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-Proxy"
}

VECTORES_ATAQUE = {
    21: "FTP: Riesgo de inicio de sesión anónimo, exploits en versiones antiguas.",
    22: "SSH: Objetivo común para ataques de diccionario y fuerza bruta.",
    23: "Telnet: ¡Crítico! Tráfico en texto plano. Vulnerable a sniffing.",
    25: "SMTP: Enumeración de usuarios o Open Relay.",
    53: "DNS: Transferencias de zona no autorizadas (AXFR).",
    80: "HTTP: Superficie de ataque web. Fallos en el servidor web.",
    139: "NetBIOS: Divulgación de información sensible (usuarios, dominios).",
    443: "HTTPS: Uso de cifrados obsoletos o fallos web.",
    445: "SMB: Vector crítico. Ejecución remota de código (ej: EternalBlue).",
    3306: "MySQL: Bases de datos expuestas a fuerza bruta o inyecciones.",
    3389: "RDP: Riesgo de secuestro de sesión o exploits (BlueKeep)."
}

# Candado para que los hilos no se pisen al imprimir en consola a color
print_lock = threading.Lock()

def verificar_host_activo(ip):
    """
    Envía un paquete ICMP (Ping) para verificar si el host está encendido.
    """
    parametro = '-n' if platform.system().lower() == 'windows' else '-c'
    tiempo_espera = '1000' if platform.system().lower() == 'windows' else '1'
    comando = ['ping', parametro, '1', '-w', tiempo_espera, ip]
    
    try:
        # Ejecutamos el ping silenciosamente
        resultado = subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return resultado.returncode == 0
    except Exception:
        return False

def capturar_banner(ip, puerto):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2) 
        sock.connect((ip, puerto))
        
        try:
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            if banner:
                return banner
        except socket.timeout:
            pass 
        
        if puerto in [80, 443, 8080]:
            peticion = f"GET / HTTP/1.1\r\nHost: {ip}\r\n\r\n"
            sock.send(peticion.encode())
            respuesta = sock.recv(1024).decode('utf-8', errors='ignore')
            for linea in respuesta.split('\n'):
                if 'Server:' in linea:
                    return linea.strip()
            return "Servicio Web (Banner oculto)"
            
        return "Servicio silencioso"
    except Exception:
        return "No se pudo capturar el banner"
    finally:
        sock.close()

def trabajador_escaneo(ip, puerto, puertos_abiertos, banners_encontrados, total_puertos):
    """
    Función que ejecuta cada hilo (thread) de forma independiente.
    """
    servicio = PUERTOS_CLAVE.get(puerto, "Desconocido")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    resultado = sock.connect_ex((ip, puerto))
    sock.close()

    if resultado == 0:
        banner = capturar_banner(ip, puerto)
        # Usamos el lock para que el texto no se mezcle en pantalla
        with print_lock:
            print(Fore.GREEN + f"[+] Puerto {puerto} ({servicio}) -> ABIERTO")
            if banner and "No se pudo" not in banner and "silencioso" not in banner:
                print(Fore.LIGHTBLACK_EX + f"    └─ Banner: {banner}")
        
        puertos_abiertos.append(puerto)
        banners_encontrados[puerto] = banner
    else:
        with print_lock:
            if total_puertos <= 50:
                print(Fore.RED + f"[-] Puerto {puerto} ({servicio}) -> CERRADO")

def escanear_puertos(ip_objetivo, modo=None, parametro_puertos=None):
    print(Fore.YELLOW + f"\n[*] Preparando escaneo contra {ip_objetivo}...")
    
    # 1. VERIFICACIÓN DE HOST ACTIVO (Pre-check)
    print(Fore.LIGHTBLACK_EX + "[*] Realizando ping de descubrimiento (Host Discovery)...")
    if verificar_host_activo(ip_objetivo):
        print(Fore.GREEN + "[+] ¡El host está activo y responde a ICMP!")
    else:
        print(Fore.LIGHTRED_EX + "[-] El host parece inactivo o está bloqueando paquetes Ping (Firewall).")
        respuesta = input(Fore.YELLOW + "[?] ¿Deseas forzar el escaneo de todas formas? (s/n): " + Style.RESET_ALL).strip().lower()
        if respuesta != 's':
            print(Fore.RED + "[-] Escaneo abortado.")
            return

    # 2. MENÚ INTERACTIVO (Si no se pasaron argumentos)
    if not modo:
        print(Fore.CYAN + "\n[⚙️ CONFIGURACIÓN DE ESCANEO]")
        print("1. Top 20+ Puertos Comunes (Recomendado)")
        print("2. Puertos Específicos (ej: 22,80,443)")
        print("3. Rango de Puertos (ej: 1-1024)")
        modo = input(Fore.BLUE + "[?] Elige el modo de escaneo (1/2/3): " + Style.RESET_ALL).strip()
        
        if modo == "2":
            parametro_puertos = input(Fore.BLUE + "[?] Ingresa los puertos separados por coma: " + Style.RESET_ALL)
        elif modo == "3":
            parametro_puertos = input(Fore.BLUE + "[?] Ingresa el rango (ej: 1-100): " + Style.RESET_ALL)

    lista_puertos = []
    
    if modo == "2" and parametro_puertos:
        try:
            lista_puertos = [int(p.strip()) for p in parametro_puertos.split(",")]
        except ValueError:
            lista_puertos = list(PUERTOS_CLAVE.keys())
    elif modo == "3" and parametro_puertos:
        try:
            inicio, fin = map(int, parametro_puertos.split("-"))
            lista_puertos = list(range(inicio, fin + 1))
        except ValueError:
            lista_puertos = list(PUERTOS_CLAVE.keys())
    else:
        lista_puertos = list(PUERTOS_CLAVE.keys())

    print(Fore.YELLOW + f"\n[*] Iniciando motor multihilo...")
    print(Fore.YELLOW + f"[*] Total de puertos a analizar: {len(lista_puertos)}")
    print(Fore.CYAN + "-" * 65)

    puertos_abiertos = []
    banners_encontrados = {}

    # 3. CONCURRENCIA (Multi-threading)
    # Ajustamos la cantidad de hilos: un máximo de 50 a la vez para no saturar la red
    max_hilos = min(50, len(lista_puertos))
    
    tiempo_inicio = time.time()
    
    with ThreadPoolExecutor(max_workers=max_hilos) as ejecutor:
        for puerto in lista_puertos:
            ejecutor.submit(trabajador_escaneo, ip_objetivo, puerto, puertos_abiertos, banners_encontrados, len(lista_puertos))

    tiempo_fin = time.time()
    
    print(Fore.CYAN + "-" * 65)
    print(Fore.YELLOW + f"[*] Escaneo finalizado en {round(tiempo_fin - tiempo_inicio, 2)} segundos.")

    # 4. REPORTES Y EXPORTACIÓN JSON/GNMAP
    if puertos_abiertos:
        puertos_ordenados = sorted(puertos_abiertos)
        print(Fore.GREEN + "\n[+] ANÁLISIS POST-ESCANEO:")
        
        cadena_nmap = ",".join(map(str, puertos_ordenados))
        print(Fore.BLUE + f"[*] Cadena rápida para Nmap: -p {cadena_nmap}")
        
        # Exportación GNMAP
        nombre_gnmap = f"scan_{ip_objetivo.replace('.', '_')}.gnmap"
        try:
            with open(nombre_gnmap, "w") as f:
                detalles = ", ".join([f"{p}/open/tcp" for p in puertos_ordenados])
                f.write(f"Host: {ip_objetivo} | Ports: {detalles}\n")
        except Exception:
            pass
            
        # Exportación JSON Moderna
        nombre_json = f"reporte_{ip_objetivo.replace('.', '_')}.json"
        data_json = {
            "target": ip_objetivo,
            "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execution_time_seconds": round(tiempo_fin - tiempo_inicio, 2),
            "open_ports": []
        }
        
        for p in puertos_ordenados:
            data_json["open_ports"].append({
                "port": p,
                "service": PUERTOS_CLAVE.get(p, "Desconocido"),
                "banner": banners_encontrados.get(p, ""),
                "attack_vector": VECTORES_ATAQUE.get(p, "N/A")
            })
            
        try:
            with open(nombre_json, "w") as f:
                json.dump(data_json, f, indent=4)
            print(Fore.BLUE + f"[*] Reportes exportados con éxito: {nombre_gnmap} y {nombre_json}")
        except Exception as e:
            print(Fore.RED + f"[-] No se pudieron exportar los reportes: {e}")
            
        print(Fore.MAGENTA + "\n[!] INTELIGENCIA DE SUPERFICIE DE ATAQUE:")
        print(Fore.CYAN + "=" * 65)
        for puerto in puertos_ordenados:
            if puerto in VECTORES_ATAQUE:
                print(Fore.YELLOW + f"-> Puerto {puerto} ({PUERTOS_CLAVE.get(puerto, 'Desconocido')}): " + Fore.WHITE + VECTORES_ATAQUE[puerto])
            
            banner = banners_encontrados.get(puerto, "")
            if banner and "No se pudo" not in banner and "silencioso" not in banner:
                print(Fore.LIGHTGREEN_EX + f"   [!] Versión Detectada: {banner}")
        print(Fore.CYAN + "=" * 65)
        
    else:
        print(Fore.RED + "\n[-] No se detectaron puertos abiertos en este host.")

if __name__ == "__main__":
    # Uso de argparse para permitir ejecución directa desde la consola con parámetros
    parser = argparse.ArgumentParser(description="Escáner de Puertos Concurrente (RainScan)")
    parser.add_argument("-t", "--target", help="Dirección IP objetivo", required=False)
    parser.add_argument("-m", "--modo", help="Modo (1: Top, 2: Específicos, 3: Rango)", choices=["1", "2", "3"])
    parser.add_argument("-p", "--puertos", help="Puertos (ej: '22,80' para modo 2, o '1-100' para modo 3)")
    
    args = parser.parse_args()
    
    # Si se pasan parámetros, corre automático. Si no, pide la IP de forma manual.
    ip = args.target if args.target else input(Fore.BLUE + "[*] Ingrese la dirección IP del objetivo: " + Style.RESET_ALL).strip()
    
    escanear_puertos(ip, args.modo, args.puertos)