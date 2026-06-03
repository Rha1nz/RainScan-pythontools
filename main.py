from colorama import Fore, Style, init

init(autoreset=True)  # Inicializa los colores

def mostrar_menu():
    print(Fore.CYAN + """
    =============================================
    |                RAINSCAN v1.0              |
    =============================================
    """)

def iniciar_consola():
    mostrar_menu()
    target = ""
    
    while True:
        # Si hay un target fijado, lo muestra en el prompt, si no, lo deja limpio (Estilo Metasploit)
        prompt_info = f"({Fore.RED}{target}{Fore.BLUE})" if target else ""
        comando = input(Fore.BLUE + f"rainscan{prompt_info} > " + Style.RESET_ALL).strip().lower()
        
        if not comando:
            continue
            
        if comando == "exit":
            print(Fore.RED + "Saliendo del framework...")
            break
            
        elif comando.startswith("set target"):
            try:
                # El .split() sin argumentos limpia CUALQUIER cantidad de espacios rebeldes
                target = comando.split()[-1]
                print(Fore.GREEN + f"[+] Objetivo fijado: {target}")
            except IndexError:
                print(Fore.RED + "[-] Error: Formato incorrecto. Usa 'set target [IP o Red]'")
                
        elif comando == "portscan":
            if not target:
                print(Fore.RED + "[-] Error: Primero debes fijar un objetivo con 'set target [IP]'")
            else:
                print(Fore.YELLOW + f"[*] Lanzando escaneo de puertos contra {target}...")
                from portscaner import escanear_puertos
                escanear_puertos(target)
                
        elif comando == "arpscan":
            if not target:
                print(Fore.RED + "[-] Error: Primero debes fijar una red objetivo con 'set target [Rango/CIDR]' (ej: 192.168.1.0/24)")
            else:
                print(Fore.YELLOW + f"[*] Lanzando escaneo ARP en la red: {target}...")
                from arpscaner import modulo_arp_scan
                modulo_arp_scan(target)
                
        elif comando == "help":
            print(Fore.WHITE + """
            Comandos disponibles:
            help        - Mostrar esta ayuda
            set target  - Configurar la IP o Red objetivo (ej: set target 192.168.1.1 o 192.168.1.0/24)
            portscan    - Ejecutar el escaneo de puertos sobre la IP fijada
            arpscan     - Ejecutar el escaneo ARP sobre el rango fijado
            exit        - Salir del programa
            """)
        else:
            print(Fore.RED + "[-] Comando desconocido. Escribe 'help' para ver las opciones.")

if __name__ == "__main__":
    iniciar_consola()