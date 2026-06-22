# Control de Temperatura con PIC16F887

---

#  1. Descripción General del Proyecto

El presente proyecto consiste en un sistema embebido de monitoreo y control de temperatura basado en un microcontrolador PIC16F887. El sistema adquiere la temperatura ambiente mediante un sensor LM35, procesa la información utilizando el conversor analógico-digital interno del microcontrolador y la presenta en tiempo real mediante dos displays de siete segmentos multiplexados.

Además, el sistema incorpora comunicación serie UART con una interfaz gráfica desarrollada en Python, permitiendo visualizar la temperatura desde una computadora y controlar actuadores externos como una lámpara calefactora y un cooler. El objetivo principal es implementar un sistema de regulación térmica simple con monitoreo local y remoto.

##  Alcances del Proyecto

### El sistema SÍ es capaz de:

- Medir temperatura mediante un sensor LM35.
- Convertir la señal analógica utilizando el ADC interno del PIC16F887.
- Mostrar la temperatura en displays de siete segmentos.
- Comunicar la temperatura a una PC mediante UART.
- Permitir el control de un cooler y una lámpara desde una interfaz gráfica.
- Implementar control automático mediante temperatura de referencia e histéresis.
- Utilizar Timer0 e interrupciones para multiplexado de displays.
- Controlar cargas externas de 12 V mediante MOSFETs.

### El sistema NO incluye:

- Almacenamiento local de datos históricos.
- Conectividad inalámbrica WiFi o Bluetooth.
- Alarmas sonoras o visuales.
- Medición simultánea de múltiples sensores.
- Interfaz web o aplicación móvil.

##  Posibles Etapas Siguientes

- Diseño de una PCB dedicada para el sistema.
- Incorporación de sensores adicionales.
- Registro histórico de temperatura.
- Comunicación inalámbrica mediante ESP32 o Bluetooth.
- Aplicación móvil para monitoreo remoto.
- Implementación de algoritmos avanzados de control térmico.

---

#  2. Arquitectura del Sistema

##  Hardware e Interconexión

### Diagrama de Bloques

```text
LM35
 │
 ▼
PIC16F887
 │
 ├── Displays 7 segmentos
 │
 ├── UART ↔ Interfaz Python
 │
 ├── Cooler 12V
 │
 └── Lámpara H7 12V
```

### Esquemático del Circuito

<img width="1004" height="500" alt="esquematico" src="https://github.com/user-attachments/assets/87a4428a-87ca-47f1-973e-cd5f850067a4" />

### Diagrama de bloques del Circuito

<img width="1536" height="1024" alt="diagrama_bloques" src="https://github.com/user-attachments/assets/c32f3960-69c3-474a-8780-2f4c9561e762" />


### Descripción del Circuito

El sensor LM35 se conecta a la entrada analógica AN0 (RA0) del microcontrolador. La temperatura es adquirida mediante el ADC interno del PIC16F887.

La visualización local se realiza mediante dos displays de siete segmentos ánodo común multiplexados utilizando transistores PNP BC327. Los segmentos están conectados al PORTD y la habilitación de cada display se realiza mediante RC0 y RC1.

La comunicación con la computadora se implementa mediante UART a 9600 bps utilizando un adaptador USB-UART.

El control de potencia para la lámpara calefactora y el cooler se realiza mediante MOSFETs canal N IRF1010N, alimentados desde una fuente externa de 12 V.

---

## 💻 Arquitectura de Software

### Flujo General

```text
Inicio

↓
Configuración de periféricos

↓
Lectura ADC

↓
Conversión de temperatura

↓
Actualización de patrones de display

↓
Envío UART

↓
Recepción de comandos

↓
Control de actuadores

↓
Repetir
```

### Arquitectura de Firmware

El firmware fue desarrollado en lenguaje ensamblador MPASM para el PIC16F887.

El programa principal realiza:

- Lectura del ADC.
- Conversión de la lectura a temperatura.
- Envío de temperatura mediante UART.
- Generación de los patrones de segmentos para los displays.
- Recepción de comandos provenientes de la interfaz.

El multiplexado de los displays se realiza mediante Timer0 e interrupciones. La rutina de interrupción únicamente alterna los displays y actualiza los segmentos, evitando realizar cálculos dentro de la ISR.

---

#  3. Especificaciones Eléctricas, Alimentación y Entorno

##  Parámetros de Alimentación

### Tensión de operación

- Lógica digital: 5 V
- Actuadores: 12 V

### Método de alimentación

- Fuente de 5 V para el PIC16F887.
- Fuente externa de 12 V para cooler y lámpara.

### Consumo estimado

**Modo normal:**

- PIC16F887 + displays + interfaz lógica: aproximadamente 80 mA.

**Modo máxima carga:**

- Cooler + lámpara H7: aproximadamente 5 A.

---


### Herramientas de Software

- MPLAB X IDE
- MPASM

### Hardware de Programación

- Bootloader AN1310 mediante adaptador USB-UART.

### Configuración de Bits (Fuses)

#### Oscilador

- XT
- Cristal externo de 4 MHz

#### Watchdog Timer

- OFF

#### Master Clear

- ON

### Periféricos Internos Utilizados

- ADC
- Timer0
- EUSART
- Interrupciones
- GPIO

### Gestión de Interrupciones

El sistema utiliza el vector único de interrupción del PIC16F887 ubicado en la dirección `0x04`.

La ISR está dedicada al multiplexado de los displays utilizando Timer0.

La secuencia de ejecución de la ISR es:

1. Guardar contexto (`W` y `STATUS`).
2. Verificar la bandera `T0IF`.
3. Recargar Timer0.
4. Apagar ambos displays.
5. Cargar el patrón correspondiente en PORTD.
6. Encender el display activo.
7. Alternar entre decenas y unidades.
8. Restaurar contexto.
9. Ejecutar `RETFIE`.

---

#  4. Proceso de Integración y Desarrollo

## Etapa 1 – Validación Inicial

Configuración del oscilador externo de 4 MHz y validación del entorno de programación mediante el bootloader AN1310.

## Etapa 2 – Comunicación UART

Implementación de la comunicación UART a 9600 bps y validación mediante terminal serie.

## Etapa 3 – Adquisición de Datos

Implementación del ADC interno y adquisición de temperatura desde el sensor LM35.

## Etapa 4 – Visualización Local

Implementación de displays de siete segmentos multiplexados para mostrar la temperatura medida.

## Etapa 5 – Interfaz Gráfica

Desarrollo de una interfaz gráfica en Python para visualizar temperatura y controlar actuadores.

## Etapa 6 – Control de Actuadores

Integración de MOSFETs para controlar un cooler y una lámpara calefactora de 12 V.

---

#  5. Ensayos, Pruebas y Resultados

## Pruebas Funcionales Realizadas

### Prueba de ADC

Se verificó la lectura del sensor LM35 comparando la tensión medida con multímetro y la temperatura reportada por el sistema.

### Prueba de UART

Se verificó la correcta transmisión y recepción de datos mediante terminal serie e interfaz Python.

### Prueba de Displays

Se comprobó el correcto funcionamiento del multiplexado mediante Timer0 y la visualización estable de la temperatura.

### Prueba de Actuadores

Se verificó:

- Encendido y apagado manual del cooler.
- Encendido y apagado manual de la lámpara.
- Recepción correcta de comandos UART.
- Activación de cargas de 12 V mediante MOSFETs.

### Prueba de Control Automático

Se verificó el funcionamiento del control mediante temperatura objetivo e histéresis configurable desde la interfaz gráfica.

## Evidencia Fotográfica y Gráficos

### Capturas de Instrumental

- Capturas de terminal serie.
<img width="913" height="964" alt="terminal_serie" src="https://github.com/user-attachments/assets/8ade62a2-443e-4852-8007-70de5ea736a4" />

Durante las etapas iniciales de validación se utilizó una terminal serie para verificar la correcta transmisión UART desde el PIC16F887. En esta etapa se enviaban mensajes de depuración que incluían el valor bruto del ADC y la temperatura calculada.
Esto permitió validar el funcionamiento del ADC, la conversión de temperatura y la comunicación serie antes de integrar la interfaz gráfica en Python.
  
- Capturas de la interfaz gráfica.

  <img width="254" height="502" alt="Interfaz_grafica" src="https://github.com/user-attachments/assets/0860a0be-aed8-416d-9e14-b0a0ac05c9dc" />


### Prototipo Real

*<img width="960" height="1280" alt="prototipo_final" src="https://github.com/user-attachments/assets/04b0a9b7-0b86-42ac-90f3-189e81a62295" />

---

# Consideraciones de Hardware

La etapa de potencia utiliza MOSFETs canal N IRF1010N para controlar cargas de 12 V.

Durante la integración se verificó la necesidad de compartir una referencia común de masa entre la fuente de 5 V del microcontrolador y la fuente de 12 V utilizada para los actuadores.

```text
GND PIC = GND Fuente 12V
```

Sin esta conexión común, los MOSFETs no pueden ser controlados correctamente desde las salidas digitales del microcontrolador.

La lámpara utilizada corresponde a una lámpara automotriz H7 de 12 V, la cual demanda corrientes elevadas y requiere cableado adecuado para evitar calentamientos excesivos.

```# TP_digitalII
