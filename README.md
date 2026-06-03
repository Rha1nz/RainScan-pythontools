# RainScan v1.1 🚀

**RainScan** es un framework modular e interactivo de auditoría de redes y reconocimiento desarrollado en Python. Diseñado con una interfaz de consola interactiva inspirada en herramientas de explotación profesional, permite realizar descubrimientos locales y análisis de superficies de ataque de manera eficiente y centralizada.

---

## ✨ Características Principales

- **Consola Interactiva Dinámica:** Prompt interactivo a color (utilizando colorama) que cambia en tiempo real según el objetivo fijado.
- **Módulo ARP Scan:** Descubrimiento rápido de hosts activos y sus respectivas direcciones MAC dentro de un segmento de red local (Capa 2) utilizando Scapy.
- **Módulo Port Scan Elusivo:** Escaneo de puertos críticos y vulnerables comunes (21, 22, 23, 80, 443, 445, etc.) optimizado con técnicas de evasión:
    - **Motor Multihilo:** Escaneos masivos en segundos utilizando `ThreadPoolExecutor`.
    - **Detección de Host:** Verificación inteligente mediante ICMP antes de escanear.
    - **Banner Grabbing:** Identificación automática de servicios y versiones activas.
    - **Reportes Estructurados:** Exportación automática a formatos `.gnmap` y `.json`.
    - **Automatización CLI:** Soporte total para argumentos desde consola (`argparse`).
    - **Inteligencia de Amenazas:** Mapeo automatizado de vectores de ataque potenciales y exploits históricos (como EternalBlue/WannaCry) según los puertos detectados abiertos.
- **Interoperabilidad:** Exportación automática de resultados a formato grepable (.gnmap) y generación de cadenas de comando optimizadas listas para copiar y pegar directamente en Nmap.
---

## 🛠️ Requisitos e Instalación

### Prerrequisitos
El script requiere Python 3.x y las siguientes librerías de dependencias:

```bash
pip install colorama scapy
```

Nota para entornos Windows: Para la inyección y captura de paquetes en Capa 2 (ARP Scan), es necesario tener instalado [Npcap](https://npcap.com/) en modo de compatibilidad con la API de WinPcap. En entornos Linux (Kali/Arch), se requiere ejecutar el script principal con privilegios de superusuario (sudo).

---

## 🚀 Modo de Uso

**1. Ejecuta el archivo principal para iniciar el framework:**

```
   python main.py
```

**2. Configura tu objetivo (puede ser una IP individual para escaneo de puertos o un segmento CIDR para el escaneo ARP):**

```
   rainscan > set target 192.168.1.1
   [+] Objetivo fijado: 192.168.1.1
```

**3. Ejecuta los módulos disponibles:**

```
   rainscan (192.168.1.1) > portscan
   rainscan (192.168.1.0/24) > arpscan
```

**4. Escribe help en cualquier momento para ver la lista completa de comandos de la consola.**

## Port Scanner

El script de portscanner.py se puede ejecutar directamente desde terminal haciendo uso de:

**1. Escaneo rápido con modo automático (Top 20 puertos)**

Si quieres lanzar el escaneo contra una IP sin que el programa te haga ninguna pregunta, puedes usar el argumento --target (o -t) y el --modo (o -m):

```
python portscaner.py -t 192.168.1.1 -m 1
```

**2. Escaneo de puertos específicos**

Si solo quieres verificar, por ejemplo, si el puerto SSH (22) y el HTTP (80) están abiertos en tu servidor:

```
python portscaner.py -t 192.168.1.1 -m 2 -p "22,80"
```

**3. Escaneo de un rango completo**

Si necesitas hacer un barrido del puerto 1 al 100 para ver qué servicios hay corriendo:

```
python portscaner.py -t 192.168.1.1 -m 3 -p "1-100"
```

---

## 📝 Capturas de Pantalla

### Resultados del Escaneo de Puertos y Vectores de Ataque
![Escaneo de puertos](img/image1.png)

### Escaneo ARP
![Escaneo ARP](img/image2.png)

---

## ⚠️ Descargo de Responsabilidad (Disclaimer)

Esta herramienta ha sido desarrollada exclusivamente con fines educativos, de investigación académica y para la realización de auditorías de seguridad debidamente autorizadas (Hacking Ético). El uso de este software contra objetivos sin el consentimiento previo y por escrito es completamente ilegal. El desarrollador no se hace responsable del mal uso o de los daños causados por esta herramienta.
