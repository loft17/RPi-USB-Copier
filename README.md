RPi USB Copier

RPi USB Copier es una aplicación de escritorio con interfaz gráfica (Tkinter) diseñada para Raspberry Pi (o cualquier sistema Linux) que permite copiar de manera sencilla y segura todos los archivos desde un dispositivo de almacenamiento USB o tarjeta SD de origen a un dispositivo de destino, organizando las copias por fecha y nombre de cámara.

📝 Descripción

Detecta automáticamente dispositivos USB/Tarjetas montadas.

Extrae información EXIF (Make y Model) de la cámara usando exiftool.

Organiza las copias en carpetas con formato YYYYMMDD/CAMERA-MODEL_#####.

Permite pausar, reanudar y cancelar la copia en cualquier momento.

Muestra un progreso detallado con porcentaje, ETA y cuenta de archivos.

Tema oscuro minimalista con Tkinter y ttk.

⚙️ Características

Selección interactiva de dispositivo de origen y destino.

Validación de fecha: evita sobrescribir carpetas existentes, permite cambiar la fecha.

Hilos para operaciones de copia sin bloquear la interfaz.

Reintentos automáticos al copiar archivos en caso de errores.

Estilos personalizados con ttk.Style para una UX consistente.

📦 Requisitos

Python 3.6 o superior

Tkinter (incluido en la mayoría de distribuciones Python)

Módulos Python:

psutil (pip install psutil)

getpass (incluido en la librería estándar)

Herramientas del sistema:

exiftool instalado y accesible en el PATH para extraer metadata de imágenes.

🛠 Instalación

Clona este repositorio:

git clone https://github.com/<TU_USUARIO>/rpi-usb-copier.git
cd rpi-usb-copier

Crea un entorno virtual (opcional pero recomendado):

python3 -m venv venv
source venv/bin/activate

Instala dependencias Python:

pip install psutil

Asegúrate de tener exiftool instalado:

# En Debian/Ubuntu:
sudo apt-get update
sudo apt-get install libimage-exiftool-perl

🚀 Uso

Ejecuta la aplicación:

python app.py

Selecciona el dispositivo de origen (USB/Tarjeta) desde el que deseas copiar.

Selecciona el dispositivo de destino donde se almacenará la copia.

Si existe ya una carpeta con la fecha actual, decide si usarla o cambiar la fecha.

Haz clic en INICIAR COPIA.

Monitorea el progreso, pausa/reanuda o cancela la operación según necesites.

🖥️ Capturas

(Coloca aquí capturas de pantalla de la interfaz si lo deseas.)

🤝 Contribuciones

¡Las contribuciones son bienvenidas! Puedes:

Abrir issues para reportar bugs o sugerir mejoras.

Enviar pull requests con nuevas funcionalidades o correcciones.

Por favor sigue las guías de estilo y asegúrate de probar tus cambios.

📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

