#!/usr/bin/env python3

from scapy.all import ARP, Ether, srp, conf
from colorama import Fore, Style, init
import argparse
import sys

init(autoreset=True)

def modulo_arp_scan(network):
    print(f"{Fore.GREEN}[*] Iniciando escaneo ARP en la red: {network}{Style.RESET_ALL}")
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)
    
    try:
        # verbose=False para que scapy no ensucie nuestra consola con sus propios mensajes
        ans, _ = srp(packet, timeout=2, verbose=False)
        
        print(f"{Fore.GREEN}\nIP\t\t\tMAC{Style.RESET_ALL}")
        print(f"{Fore.GREEN}" + "-" * 40 + f"{Style.RESET_ALL}")
        for snd, rcv in ans:
            print(f"{Fore.YELLOW}{rcv.psrc}\t\t{rcv.hwsrc}{Style.RESET_ALL}")
            
    except PermissionError:
        print(f"{Fore.RED}[-] Error crítico: Debes ejecutar RainScan con privilegios de administrador (sudo).{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[-] Ocurrió un error inesperado: {e}{Style.RESET_ALL}")

def print_devices(devices):
    print(f"{Fore.GREEN}IP\t\tMAC{Style.RESET_ALL}")
    print(f"{Fore.GREEN}-------------------------{Style.RESET_ALL}")
    for d in devices:
        print(f"{Fore.YELLOW}{d['ip']}\t\t{d['mac']}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="Escanea ips usando ARP con Scapy")
    parser.add_argument("network", help="Rango de IPs o dirección CIDR, por ejemplo 192.168.1.0/24")
    parser.add_argument("-i", "--iface", help="Interfaz de red a usar")
    parser.add_argument("-t", "--timeout", type=float, default=2, help="Timeout en segundos")
    args = parser.parse_args()

    try:
        modulo_arp_scan(args.network)
    except PermissionError:
        print(f"{Fore.RED}[-] Permiso denegado. Ejecuta el script con privilegios de administrador/root.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}[-] Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

