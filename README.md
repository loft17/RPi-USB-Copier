# RPi USB Copier - Aplicación de Copia de Seguridad para Raspberry Pi

![RPi USB Copier Screenshot](ruta/a/tu/screenshot.png) <!-- Reemplaza con una captura de pantalla real -->

**RPi USB Copier** es una aplicación de escritorio con interfaz gráfica (GUI) diseñada para Raspberry Pi (probada en RPi 4 y 5). Facilita la copia de seguridad completa de dispositivos de almacenamiento USB (como tarjetas SD de cámaras o memorias USB) a otro dispositivo USB de destino, organizando las copias en una estructura de carpetas basada en la fecha y la información de la cámara (si está disponible).

La interfaz está optimizada para pantallas pequeñas (480x300px) y uso táctil.

## Características Principales

*   **Interfaz Gráfica Táctil:** Diseñada para pantallas de 480x300px, con botones grandes y un tema oscuro minimalista.
*   **Detección de Dispositivos USB:** Detecta automáticamente unidades USB conectadas para seleccionar origen y destino.
*   **Información del Dispositivo:** Muestra el nombre, espacio libre y total de los dispositivos seleccionados.
*   **Organización Inteligente de Copias:**
    *   Las copias se guardan en una carpeta con la fecha actual (o seleccionada) en formato `YYYYMMDD`.
    *   Dentro, se crea una subcarpeta `MARCA-MODELO_XXXXX` (ej. `SONY-ILCE-6400_00001`).
    *   La marca y modelo se intentan extraer de metadatos EXIF usando `exiftool`.
*   **Copia Completa y Robusta:**
    *   Realiza una copia recursiva de todos los archivos y directorios.
    *   Preserva metadatos de los archivos.
    *   Reintentos automáticos para archivos individuales en caso de error.
*   **Progreso Detallado:** Muestra porcentaje, ETA, contador de archivos y archivo actual durante la copia.
*   **Control de Copia:** Permite pausar, reanudar y cancelar la operación de copia.
*   **Gestión de Conflictos de Fecha:** Avisa si la carpeta de fecha ya existe y permite continuar o cambiar la fecha de la copia.
*   **Menú del Sistema:**
    *   Cerrar la aplicación.
    *   Reiniciar la Raspberry Pi (con confirmación).
    *   Apagar la Raspberry Pi (con confirmación).

## Requisitos Previos

Antes de ejecutar la aplicación, asegúrate de tener lo siguiente instalado en tu Raspberry Pi:

1.  **Python 3.x**
2.  **Tkinter** (generalmente incluido con Python en Raspberry Pi OS)
3.  **pip** (instalador de paquetes de Python)
4.  **psutil:** Para obtener información de los discos.
    ```bash
    pip install psutil
    ```
5.  **exiftool:** Para leer metadatos de imágenes.
    ```bash
    sudo apt update
    sudo apt install libimage-exiftool-perl
    ```

## Instalación y Uso

1.  **Clonar el Repositorio (o descargar el script):**
    ```bash
    git clone https://github.com/tu_usuario/rpi-usb-copier.git
    cd rpi-usb-copier
    ```
    O descarga el archivo `app.py` (o como lo hayas llamado) directamente.

2.  **Permisos de Ejecución (Opcional):**
    ```bash
    chmod +x app.py
    ```

3.  **Ejecutar la Aplicación:**

    *   **Para las funciones de Reinicio/Apagado del Sistema:** La aplicación necesita privilegios de superusuario para ejecutar los comandos `reboot` y `shutdown`. Puedes:
        *   **Opción A (Más Simple):** Ejecutar la aplicación con `sudo`:
            ```bash
            sudo python3 app.py
            ```
        *   **Opción B (Más Segura, Recomendada):** Configurar `sudoers` para permitir que tu usuario ejecute los comandos específicos sin contraseña. Crea un archivo (ej. `/etc/sudoers.d/99-rpi-copier`) con el siguiente contenido (reemplaza `tu_usuario_pi` con tu nombre de usuario, usualmente `pi`):
            ```
            tu_usuario_pi ALL=(ALL) NOPASSWD: /sbin/reboot, /sbin/shutdown
            ```
            Luego, puedes ejecutar la aplicación normalmente:
            ```bash
            python3 app.py
            ```

4.  **Uso de la Interfaz:**
    *   **Seleccionar Origen:** Pulsa "Seleccionar" en la sección ORIGEN y elige tu dispositivo USB fuente.
    *   **Seleccionar Destino:** Pulsa "Seleccionar" en la sección DESTINO y elige tu dispositivo USB de respaldo.
    *   **Iniciar Copia:** Una vez seleccionados origen y destino, el botón "INICIAR COPIA" se volverá verde. Púlsalo para comenzar.
    *   **Menú:** Pulsa "Menú" para acceder a las opciones de cerrar aplicación, reiniciar o apagar el sistema.

## Estructura del Proyecto

*   `app.py`: El script principal de la aplicación Python.
*   `README.md`: Este archivo.
*   `ruta/a/tu/screenshot.png`: (Opcional) Una captura de pantalla de la aplicación.

## Contribuciones

Las contribuciones son bienvenidas. Si tienes ideas para mejorar la aplicación o encuentras algún error, por favor:
1.  Haz un Fork del proyecto.
2.  Crea tu Feature Branch (`git checkout -b feature/AmazingFeature`).
3.  Haz Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`).
4.  Haz Push a la Branch (`git push origin feature/AmazingFeature`).
5.  Abre un Pull Request.

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles (si decides añadir uno).

## Agradecimientos

*   A la comunidad de Python y Tkinter.
*   A los desarrolladores de `psutil` y `exiftool`.

---
