# RPi USB Copier - Aplicación de Copia de Seguridad para Raspberry Pi

![RPi USB Copier Screenshot](ruta/a/tu/screenshot.png) <!-- Reemplaza con una captura de pantalla real -->

**RPi USB Copier** es una aplicación de escritorio con interfaz gráfica (GUI) diseñada para Raspberry Pi (probada en RPi 4 y 5), optimizada para pantallas de **480x300px**. Facilita la copia de seguridad completa de dispositivos de almacenamiento USB (como tarjetas SD de cámaras o memorias USB) a otro dispositivo USB de destino, organizando las copias en una estructura de carpetas basada en la fecha y la información de la cámara (si está disponible).

La interfaz está pensada para ser usada con los dedos (táctil) y utiliza un tema oscuro.

## Características Principales

*   **Interfaz Gráfica Táctil:** Optimizada para pantallas de 480x300px, con botones grandes y tema oscuro.
*   **Detección de Dispositivos USB:** Detecta automáticamente unidades USB montadas y válidas.
*   **Validación de Montaje:** Comprueba que los dispositivos seleccionados sigan montados antes de iniciar la copia.
*   **Información del Dispositivo:** Muestra nombre, espacio libre y total de los dispositivos.
*   **Organización Inteligente de Copias:**
    *   Carpeta de destino: `YYYYMMDD/MARCA-MODELO_XXXXX` (ej. `20240315/SONY-ILCE-6400_00001`).
    *   Marca y modelo extraídos usando `exiftool` (si es posible).
*   **Copia Completa y Robusta:**
    *   Copia recursiva de archivos y directorios.
    *   Preserva metadatos (`shutil.copy2`).
    *   **Verificación de Espacio:** Comprueba si hay suficiente espacio en el destino antes de iniciar la copia.
    *   **Manejo de Errores Específico:** Detecta y maneja errores comunes como "Disco Lleno" o "Permiso Denegado" durante la copia.
    *   Reintentos automáticos para errores de copia temporales.
*   **Progreso Detallado:** Barra de progreso, %, ETA, contador de archivos, archivo actual.
*   **Control de Copia:** Pausar, Reanudar y Cancelar (con confirmación y opción de limpieza).
*   **Gestión de Conflictos de Fecha:** Avisa si la carpeta de fecha ya existe y permite continuar o cambiar la fecha (usando un selector táctil).
*   **Botón de Copia Dinámico:** El botón "Iniciar Copia" se vuelve **verde** cuando la operación está lista.
*   **Menú del Sistema (Táctil):**
    *   Acceso mediante un botón "Menú".
    *   Opciones con botones grandes: Cerrar Aplicación, Reiniciar Pi (con confirmación), Apagar Pi (con confirmación).

## Requisitos Previos

Asegúrate de tener instalado en tu Raspberry Pi:

1.  **Python 3.x**
2.  **Tkinter** (normalmente incluido)
3.  **pip** (instalador de paquetes Python)
4.  **psutil:**
    ```bash
    apt install python3-tk python3-sh python3-psutil -y
    ```
5.  **exiftool:**
    ```bash
    sudo apt update
    sudo apt install libimage-exiftool-perl
    ```

## Instalación y Uso

1.  **Clonar o Descargar:**
    ```bash
    git clone https://github.com/loft17/RPi-USB-Copier.git
    cd rpi-usb-copier
    ```
    O descarga el archivo `app.py` (o como lo llames).

2.  **Permisos (Opcional):**
    ```bash
    chmod +x app.py
    ```

3.  **Ejecutar:**

    *   **Importante (Reinicio/Apagado):** Para usar las funciones de reiniciar o apagar desde el menú, la aplicación necesita permisos.
        *   **Opción A (Simple):** Ejecutar con `sudo`:
            ```bash
            sudo python3 app.py
            ```
        *   **Opción B (Recomendada):** Configurar `sudoers` para permitir a tu usuario ejecutar los comandos sin contraseña. Crea un archivo, por ej. `/etc/sudoers.d/99-rpi-copier`, con (reemplaza `tu_usuario_pi`):
            ```
            tu_usuario_pi ALL=(ALL) NOPASSWD: /sbin/reboot, /sbin/shutdown
            ```
            *Precaución: Asegúrate de entender las implicaciones de seguridad de `NOPASSWD`.*
            Luego, ejecuta normalmente:
            ```bash
            python3 app.py
            ```

4.  **Interfaz:**
    *   Usa los botones "Seleccionar" para elegir Origen y Destino. La lista de dispositivos se obtiene al pulsar el botón.
    *   Cuando ambos estén seleccionados y válidos, el botón "Iniciar Copia" se pondrá verde.
    *   Pulsa "Iniciar Copia" para comenzar.
    *   Usa los botones en la ventana de progreso para Pausar/Reanudar o Cancelar.
    *   Pulsa "Menú" para acceder a las opciones del sistema.

## Estructura del Proyecto (Básica)

*   `app.py`: Script principal de la aplicación.
*   `README.md`: Este archivo.
*   `ruta/a/tu/screenshot.png`: (Opcional) Captura de pantalla.

## Contribuciones

¡Son bienvenidas! Si tienes mejoras o correcciones:
1.  Fork el proyecto.
2.  Crea tu branch (`git checkout -b feature/MiMejora`).
3.  Commit tus cambios (`git commit -m 'Añade MiMejora'`).
4.  Push a la branch (`git push origin feature/MiMejora`).
5.  Abre un Pull Request.

## Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información (si aplica).

## Agradecimientos

*   Python & Tkinter community
*   psutil developers
*   exiftool by Phil Harvey

---

Este README describe con precisión el estado funcional de la aplicación incluyendo las mejoras de robustez pero *sin* las últimas dos características solicitadas (refresco manual e indicador de escaneo en botón). Recuerda actualizar los placeholders de la URL del repositorio y la captura de pantalla.
