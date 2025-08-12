# Pharma Plant Condition Monitoring (Raspberry Pi + Cumulocity IoT)

This demo shows how a Raspberry Pi 4 monitors **temperature, humidity, and light exposure** and streams data to **Cumulocity IoT**. A Cumulocity dashboard displays **live measurements, alarms, and events**.


## Highlights
- **VS Code Remote–SSH**: edit and run code directly on the Pi.
- **Sensors**: DHT11 (GPIO4) and digital light sensor (GPIO17).
- **Cumulocity**: REST API for measurements and events; Smart Rules for alarms.
- **Secrets hygiene**: credentials live in `config.ini` locally; only `config.ini.template` is committed.

## Hardware
- Raspberry Pi 4 Model B
- DHT11 temp/humidity sensor → DATA on **GPIO4 (BCM)**
- Digital photo/light sensor → OUT on **GPIO17 (BCM)**
- 3.3V and GND to power both sensors

> Power the modules from **3.3V** to keep the Pi’s GPIO safe.

## Wiring (BCM numbering)
| Function     | Pi Pin (physical) | BCM GPIO |
|--------------|--------------------|---------|
| DHT11 DATA   | Pin 7              | GPIO4   |
| Light OUT    | Pin 11             | GPIO17  |
| 3.3V         | Pin 1              | —       |
| GND          | Pin 6              | —       |


## YouTube Link
https://youtu.be/dQKUQWXk84U
