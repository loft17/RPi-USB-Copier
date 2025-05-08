import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import shutil
import subprocess
import threading
import time
import datetime
import psutil # pip install psutil
import getpass # Para obtener el usuario actual
import calendar # Para DatePickerDialog

# --- Constantes de Diseño y Configuración ---
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 300 # <--- CAMBIO AQUÍ

# Colores para un tema oscuro minimalista (ajustar al gusto)
BG_COLOR = "#2E2E2E"
FG_COLOR = "#E0E0E0"
ACCENT_COLOR = "#007ACC"     # Azul para acentos (botones normales)
BUTTON_ACTIVE_BG = "#005C99"
ENABLED_COPY_COLOR = "#4CAF50" # Verde para botón de copia habilitado
ENABLED_COPY_ACTIVE_BG = "#388E3C" # Verde más oscuro para activo
BORDER_COLOR = "#4A4A4A"
LABEL_INFO_FG = "#B0B0B0"
DANGER_COLOR = "#D32F2F"
DANGER_ACTIVE_BG = "#B71C1C"

FONT_FAMILY = "DejaVu Sans"
FONT_SIZE_SMALL = 8 # Reducido un poco para más compacidad
FONT_SIZE_NORMAL = 9 # Reducido
FONT_SIZE_LARGE = 11 # Reducido
FONT_SIZE_XLARGE = 13 # Reducido

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title="", fixed_height_ratio=None): # Nuevo parámetro
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG_COLOR)
        self.transient(parent)
        self.grab_set()
        
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        
        # Usar valores predeterminados si parent.winfo_width/height es 0 (inicio de app)
        effective_parent_width = parent_width if parent_width > 0 else SCREEN_WIDTH
        effective_parent_height = parent_height if parent_height > 0 else SCREEN_HEIGHT

        dialog_width = int(effective_parent_width * 0.90)
        
        if fixed_height_ratio: # Para diálogos con altura más controlada
            dialog_height = int(effective_parent_height * fixed_height_ratio)
        else: # Altura más flexible
            dialog_height = int(effective_parent_height * 0.80) # Ratio general
        
        dialog_width = min(dialog_width, SCREEN_WIDTH - 20)
        dialog_height = min(dialog_height, SCREEN_HEIGHT - 30) # Más margen vertical

        pos_x = parent_x + (effective_parent_width - dialog_width) // 2
        pos_y = parent_y + (effective_parent_height - dialog_height) // 2

        pos_x = max(5, min(pos_x, SCREEN_WIDTH - dialog_width - 5)) # Márgenes mínimos
        pos_y = max(5, min(pos_y, SCREEN_HEIGHT - dialog_height - 5))

        self.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")
        self.resizable(False, False)

        self.result = None 

        self.main_frame = ttk.Frame(self, style="CustomDialog.TFrame", padding=10)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

    def _create_button_bar(self, buttons_config):
        button_frame = ttk.Frame(self.main_frame, style="CustomDialog.TFrame")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0))
        if len(buttons_config) > 0:
            button_frame.columnconfigure(list(range(len(buttons_config))), weight=1)

        for i, (text, command, style_name) in enumerate(buttons_config):
            btn = ttk.Button(button_frame, text=text, command=command, style=style_name, width=10)
            btn.grid(row=0, column=i, padx=5, pady=(0,5), sticky="ew") # Añadido pady inferior
        return button_frame


class DatePickerDialog(CustomDialog):
    def __init__(self, parent, title="Seleccionar Fecha", initial_date=None):
        self.current_date = initial_date if initial_date else datetime.date.today()
        super().__init__(parent, title, fixed_height_ratio=0.75) # Un poco más de altura para los controles de fecha

        self._create_body()
        self._create_button_bar([
            ("Aceptar", self.apply, "Dialog.TButton"), 
            ("Cancelar", self.cancel, "Dialog.TButton")
        ])
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_date_display()

    def _create_custom_spinbox(self, parent_frame, label_text, value_type):
        frame = ttk.Frame(parent_frame, style="CustomDialog.TFrame")
        
        ttk.Label(frame, text=label_text, style="Dialog.TLabel", width=5, anchor="w").pack(side=tk.LEFT, padx=(0,5))

        btn_down = ttk.Button(frame, text="-" , style="Arrow.Dialog.TButton", width=2,
                              command=lambda vt=value_type: self.change_date_value(vt, -1))
        btn_down.pack(side=tk.LEFT, padx=1)

        value_label = ttk.Label(frame, text="00", style="DateValue.Dialog.TLabel", width=4, anchor="center")
        value_label.pack(side=tk.LEFT, padx=3)

        btn_up = ttk.Button(frame, text="+", style="Arrow.Dialog.TButton", width=2,
                            command=lambda vt=value_type: self.change_date_value(vt, 1))
        btn_up.pack(side=tk.LEFT, padx=1)
        
        return frame, value_label

    def _create_body(self):
        body_frame = ttk.Frame(self.main_frame, style="CustomDialog.TFrame")
        body_frame.pack(expand=True, fill=tk.BOTH, pady=10, padx=5) # Reducido pady

        year_frame, self.year_label = self._create_custom_spinbox(body_frame, "Año:", "year")
        year_frame.pack(fill=tk.X, pady=3) # Reducido pady
        
        month_frame, self.month_label = self._create_custom_spinbox(body_frame, "Mes:", "month")
        month_frame.pack(fill=tk.X, pady=3)

        day_frame, self.day_label = self._create_custom_spinbox(body_frame, "Día:", "day")
        day_frame.pack(fill=tk.X, pady=3)

    def update_date_display(self):
        self.year_label.config(text=f"{self.current_date.year:04d}")
        self.month_label.config(text=f"{self.current_date.month:02d}")
        self.day_label.config(text=f"{self.current_date.day:02d}")

    def change_date_value(self, value_type, delta):
        year, month, day = self.current_date.year, self.current_date.month, self.current_date.day

        if value_type == "year":
            year += delta
            year = max(2000, min(2100, year))
        elif value_type == "month":
            month += delta
            if month > 12: month = 1
            if month < 1: month = 12
        elif value_type == "day":
            day += delta
            max_days = calendar.monthrange(year, month)[1]
            if day > max_days: day = 1
            if day < 1: day = max_days
        
        try:
            self.current_date = datetime.date(year, month, day)
        except ValueError:
            try:
                last_day_of_month = calendar.monthrange(year, month)[1]
                day = min(day, last_day_of_month)
                self.current_date = datetime.date(year, month, day)
            except ValueError: 
                pass 
        self.update_date_display()

    def apply(self):
        self.result = self.current_date
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class DeviceSelectionDialog(CustomDialog):
    def __init__(self, parent, title="Seleccionar Dispositivo", devices=None):
        self.devices = devices if devices else []
        super().__init__(parent, title, fixed_height_ratio=0.7) # Un poco menos de altura

        self._create_body()
        self._create_button_bar([
            ("Aceptar", self.on_select, "Dialog.TButton"), 
            ("Cancelar", self.on_cancel, "Dialog.TButton")
        ])
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def _create_body(self):
        ttk.Label(self.main_frame, text="Selecciona un dispositivo:", style="Dialog.TLabel").pack(pady=(0,5))
        
        self.listbox_frame = ttk.Frame(self.main_frame, style="CustomDialog.TFrame")
        self.listbox_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(self.listbox_frame, 
                                  width=35, height=4,  # Reducida altura de listbox
                                  bg=BORDER_COLOR, fg=FG_COLOR, 
                                  selectbackground=ACCENT_COLOR, selectforeground=FG_COLOR,
                                  font=(FONT_FAMILY, FONT_SIZE_SMALL),
                                  borderwidth=0, highlightthickness=0, relief=tk.FLAT,
                                  activestyle="none") 
        
        for dev in self.devices:
            item_text = f" {dev['label']} ({dev['free_space_gb']:.1f}G/{dev['total_space_gb']:.1f}G)"
            self.listbox.insert(tk.END, item_text)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.listbox_frame, orient="vertical", command=self.listbox.yview, style="Custom.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        if self.devices:
            self.listbox.selection_set(0)
            self.listbox.activate(0)

    def on_select(self):
        try:
            idx = self.listbox.curselection()[0]
            self.result = self.devices[idx]
            self.destroy()
        except IndexError:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un dispositivo.", parent=self)
    
    def on_cancel(self):
        self.result = None
        self.destroy()


class SystemMenuDialog(CustomDialog):
    def __init__(self, parent, app_instance):
        self.app = app_instance 
        # Para el menú del sistema, usar una altura un poco mayor, pero que quepa bien
        super().__init__(parent, title="Menú del Sistema", fixed_height_ratio=0.8) # <--- AJUSTE ALTURA

        self._create_menu_buttons()
        self._create_button_bar([("Volver", self.destroy, "Dialog.TButton")]) 
        self.protocol("WM_DELETE_WINDOW", self.destroy)


    def _create_menu_buttons(self):
        menu_frame = ttk.Frame(self.main_frame, style="CustomDialog.TFrame")
        menu_frame.pack(expand=True, fill=tk.BOTH, pady=5, padx=10)

        btn_close_app = ttk.Button(menu_frame, text="Cerrar Aplicación", 
                                   command=self.close_application, style="Large.TButton")
        btn_close_app.pack(fill=tk.X, pady=3, ipady=3) # Reducido pady

        btn_reboot = ttk.Button(menu_frame, text="Reiniciar Pi", 
                                command=self.reboot_system, style="Danger.Large.TButton")
        btn_reboot.pack(fill=tk.X, pady=3, ipady=3)

        btn_shutdown = ttk.Button(menu_frame, text="Apagar Pi", 
                                  command=self.shutdown_system, style="Danger.Large.TButton")
        btn_shutdown.pack(fill=tk.X, pady=3, ipady=3)

    def close_application(self):
        self.destroy() 
        self.app.root.destroy()

    def reboot_system(self):
        if messagebox.askyesno("Confirmar Reinicio", 
                               "¿Seguro que quieres reiniciar la Raspberry Pi?", 
                               icon='warning', parent=self):
            self.destroy() 
            try:
                subprocess.run(["sudo", "reboot"], check=True)
            except Exception as e:
                messagebox.showerror("Error de Reinicio", f"No se pudo reiniciar el sistema:\n{e}", parent=self.app.root)

    def shutdown_system(self):
        if messagebox.askyesno("Confirmar Apagado", 
                               "¿Seguro que quieres apagar la Raspberry Pi?", 
                               icon='warning', parent=self):
            self.destroy() 
            try:
                subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
            except Exception as e:
                messagebox.showerror("Error de Apagado", f"No se pudo apagar el sistema:\n{e}", parent=self.app.root)


class ModernCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RPi USB Copier")
        self.root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}") # Usando constantes actualizadas
        self.root.configure(bg=BG_COLOR)
        # self.root.resizable(False, False) # Mantener esto para evitar redimensionamiento
        
        self.current_user = getpass.getuser()
        self.USB_MOUNT_PREFIXES = (
            f"/media/{self.current_user}/",
            f"/run/media/{self.current_user}/", 
            f"/mnt/{self.current_user}/",
            "/media/", 
            "/mnt/"    
        )

        self.source_device_info = None
        self.destination_device_info = None
        self.camera_make = "UNTITLED"
        self.camera_model = "CAMERA"
        self.copy_date = datetime.date.today()

        self.copy_thread = None
        self.cancel_copy_flag = threading.Event()
        self.pause_copy_flag = threading.Event() 

        self.style = ttk.Style()
        self.setup_styles()
        self.create_main_layout()
        self.update_status("Listo. Seleccione origen y destino.", "info")

    def setup_styles(self):
        self.style.theme_use('clam') 

        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("CustomDialog.TFrame", background=BG_COLOR)

        # Estilo base para botón de copia (cuando está deshabilitado o por defecto)
        self.style.configure("Copy.TButton",
                        font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"),
                        padding=(8, 10), # Reducido padding vertical
                        background=ACCENT_COLOR, # Azul por defecto
                        foreground=FG_COLOR,
                        borderwidth=1,
                        relief="raised")
        self.style.map("Copy.TButton",
                  background=[('active', BUTTON_ACTIVE_BG), ('disabled', BORDER_COLOR)],
                  foreground=[('disabled', FG_COLOR)])

        # Estilo para botón de copia cuando está HABILITADO (Verde)
        self.style.configure("Enabled.Copy.TButton",
                        font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"),
                        padding=(8, 10),
                        background=ENABLED_COPY_COLOR, # Verde
                        foreground=FG_COLOR,
                        borderwidth=1,
                        relief="raised")
        self.style.map("Enabled.Copy.TButton",
                  background=[('active', ENABLED_COPY_ACTIVE_BG)], # No necesita 'disabled' aquí
                  foreground=[])


        self.style.configure("Danger.Large.TButton",
                        font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"),
                        padding=(8, 10), 
                        background=DANGER_COLOR, 
                        foreground=FG_COLOR,
                        borderwidth=1,
                        relief="raised")
        self.style.map("Danger.Large.TButton",
                  background=[('active', DANGER_ACTIVE_BG), ('disabled', BORDER_COLOR)],
                  foreground=[('disabled', FG_COLOR)])


        self.style.configure("Medium.TButton",
                        font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                        padding=(6, 8), # Reducido padding
                        background=ACCENT_COLOR,
                        foreground=FG_COLOR,
                        borderwidth=1)
        self.style.map("Medium.TButton",
                  background=[('active', BUTTON_ACTIVE_BG), ('disabled', BORDER_COLOR)],
                  foreground=[('disabled', FG_COLOR)])

        self.style.configure("Dialog.TButton",
                        font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                        padding=(6, 6), # Reducido
                        background=ACCENT_COLOR,
                        foreground=FG_COLOR)
        self.style.map("Dialog.TButton",
                  background=[('active', BUTTON_ACTIVE_BG)])
        
        self.style.configure("Arrow.Dialog.TButton",
                        font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"), 
                        padding=(4, 6), # Reducido
                        background=ACCENT_COLOR,
                        foreground=FG_COLOR)
        self.style.map("Arrow.Dialog.TButton",
                  background=[('active', BUTTON_ACTIVE_BG)])
        
        self.style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.style.configure("Dialog.TLabel", background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        
        self.style.configure("DateValue.Dialog.TLabel", 
                             background=BG_COLOR, 
                             foreground=FG_COLOR, 
                             font=(FONT_FAMILY, FONT_SIZE_XLARGE, "bold"),
                             padding=(5,2))

        self.style.configure("Header.TLabelframe", 
                             background=BG_COLOR, 
                             foreground=ACCENT_COLOR, 
                             labelmargins=(5,0,0,0),
                             font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold")) # Reducido título de Labelframe
        self.style.configure("Header.TLabelframe.Label", 
                             background=BG_COLOR, 
                             foreground=ACCENT_COLOR,
                             font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"))

        self.style.configure("Info.TLabel", font=(FONT_FAMILY, FONT_SIZE_SMALL), foreground=LABEL_INFO_FG, background=BG_COLOR)
        
        self.style.configure("Status.TLabel", font=(FONT_FAMILY, FONT_SIZE_SMALL), wraplength=SCREEN_WIDTH - 80, background=BG_COLOR)
        self.style.configure("Success.Status.TLabel", foreground="#4CAF50", background=BG_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL)) 
        self.style.configure("Error.Status.TLabel", foreground="#F44336", background=BG_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL))   
        self.style.configure("Warning.Status.TLabel", foreground="#FFC107", background=BG_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL)) 
        self.style.configure("Info.Status.TLabel", foreground=LABEL_INFO_FG, background=BG_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL))   

        self.style.configure("Custom.Horizontal.TProgressbar",
                        thickness=15,  # Reducido
                        background=ACCENT_COLOR,
                        troughcolor=BORDER_COLOR,
                        borderwidth=0)
        
        self.style.configure("Custom.Vertical.TScrollbar",
                        gripcount=0,
                        background=ACCENT_COLOR,
                        darkcolor=BORDER_COLOR,
                        lightcolor=BORDER_COLOR,
                        troughcolor=BG_COLOR,
                        bordercolor=BG_COLOR,
                        arrowcolor=FG_COLOR)
        self.style.map("Custom.Vertical.TScrollbar",
                  background=[('active', BUTTON_ACTIVE_BG)])

    def create_main_layout(self):
        outer_container = ttk.Frame(self.root, style="TFrame")
        outer_container.pack(expand=True, fill=tk.BOTH, padx=3, pady=3) # Reducido padding global

        selection_frame = ttk.Frame(outer_container, style="TFrame")
        selection_frame.pack(fill=tk.BOTH, expand=True) 

        source_labelframe = ttk.LabelFrame(selection_frame, text="ORIGEN", style="Header.TLabelframe")
        source_labelframe.pack(fill=tk.X, pady=(0,3), padx=0) # Reducido pady
        
        source_content_frame = ttk.Frame(source_labelframe, style="TFrame")
        source_content_frame.pack(fill=tk.X, padx=3, pady=3)
        source_content_frame.columnconfigure(0, weight=1) # Ajustar pesos si es necesario
        source_content_frame.columnconfigure(1, weight=2) 

        self.source_btn = ttk.Button(source_content_frame, text="Seleccionar", command=self.select_source, style="Medium.TButton")
        self.source_btn.grid(row=0, column=0, sticky="ew", padx=(0,3))
        self.source_info_label = ttk.Label(source_content_frame, text="No seleccionado", style="Info.TLabel", justify=tk.LEFT, wraplength=int(SCREEN_WIDTH * 0.50)) 
        self.source_info_label.grid(row=0, column=1, sticky="nsew")


        dest_labelframe = ttk.LabelFrame(selection_frame, text="DESTINO", style="Header.TLabelframe")
        dest_labelframe.pack(fill=tk.X, pady=(3,3), padx=0)

        dest_content_frame = ttk.Frame(dest_labelframe, style="TFrame")
        dest_content_frame.pack(fill=tk.X, padx=3, pady=3)
        dest_content_frame.columnconfigure(0, weight=1)
        dest_content_frame.columnconfigure(1, weight=2)

        self.dest_btn = ttk.Button(dest_content_frame, text="Seleccionar", command=self.select_destination, style="Medium.TButton")
        self.dest_btn.grid(row=0, column=0, sticky="ew", padx=(0,3))
        self.dest_info_label = ttk.Label(dest_content_frame, text="No seleccionado", style="Info.TLabel", justify=tk.LEFT, wraplength=int(SCREEN_WIDTH * 0.50))
        self.dest_info_label.grid(row=0, column=1, sticky="nsew")

        # --- Barra de Acciones Inferior ---
        action_bar_height = 60 # Altura ajustada
        action_bar_frame = ttk.Frame(outer_container, style="TFrame", height=action_bar_height) 
        action_bar_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(3,0))
        action_bar_frame.pack_propagate(False) 

        action_bar_frame.columnconfigure(0, weight=3) 
        action_bar_frame.columnconfigure(1, weight=1) 

        self.copy_button = ttk.Button(action_bar_frame, text="INICIAR COPIA", command=self.start_copy, style="Copy.TButton", state=tk.DISABLED) # Estilo base
        self.copy_button.grid(row=0, column=0, sticky="nsew", padx=(3,1), pady=(1,1)) # nsew para que tome altura

        self.system_menu_button = ttk.Button(action_bar_frame, text="Menú", 
                                             command=self.open_system_menu, style="Medium.TButton") 
        self.system_menu_button.grid(row=0, column=1, sticky="nsew", padx=(1,3), pady=(1,1)) # nsew


        self.status_label = ttk.Label(action_bar_frame, text="Listo", style="Status.TLabel", anchor="center")
        # Colocar status_label debajo de los botones, tomando todo el ancho de la action_bar_frame
        # Para esto, es mejor que action_bar_frame use pack para sus hijos principales y grid para el estado,
        # o usar grid consistentemente. Por simplicidad, lo dejamos así, pero podría necesitar ajuste si el texto es largo.
        # Una forma es ponerlo en una nueva fila que abarque ambas columnas:
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=3, pady=(0,1))

    def open_system_menu(self):
        # Solo abrir si no hay una copia en curso
        if self.copy_thread and self.copy_thread.is_alive():
            messagebox.showinfo("Menú Bloqueado", "El menú del sistema no está disponible durante una copia.", parent=self.root)
            return
        SystemMenuDialog(self.root, self)

    def check_copy_readiness(self):
        if self.source_device_info and self.destination_device_info:
            self.copy_button.config(state=tk.NORMAL, style="Enabled.Copy.TButton") # Estilo verde
        else:
            self.copy_button.config(state=tk.DISABLED, style="Copy.TButton") # Estilo por defecto (azul/gris)
    
    def start_copy(self):
        if not self.source_device_info or not self.destination_device_info:
            messagebox.showerror("Error", "Selecciona origen y destino.", parent=self.root)
            return

        if not self.check_date_conflict(): 
            self.check_copy_readiness() # Asegurar que el botón refleje el estado correcto
            return

        self.target_copy_folder_full_path = self.get_target_folder_name()
        if not self.target_copy_folder_full_path:
            return

        self.copy_button.config(state=tk.DISABLED, style="Copy.TButton") # Volver al estilo por defecto al deshabilitar
        self.source_btn.config(state=tk.DISABLED)
        self.dest_btn.config(state=tk.DISABLED)
        self.system_menu_button.config(state=tk.DISABLED)
        self.update_status("Preparando copia...", "info")
        self.cancel_copy_flag.clear()
        self.pause_copy_flag.clear()

        self.create_progress_window()

        self.copy_thread = threading.Thread(target=self.perform_copy_operation, daemon=True)
        self.copy_thread.start()

    def finalize_copy_ui(self, success, files_copied=0, total_files_attempted=0, message_override=None):
        # ... (contenido igual, solo asegurar que check_copy_readiness se llama al final) ...
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_window.destroy()
        
        if message_override:
            status_level = "warning"
            if "cancelada" in message_override.lower(): status_level = "warning"
            elif not success and "error" in message_override.lower() : status_level = "error"
            elif success: status_level = "info"
            self.update_status(message_override, status_level)

        elif success:
            self.update_status(f"Completada: {files_copied}/{total_files_attempted} archivos.", "success")
        else:
            self.update_status(f"Errores: {files_copied}/{total_files_attempted} archivos.", "error")

        self.source_btn.config(state=tk.NORMAL)
        self.dest_btn.config(state=tk.NORMAL)
        self.system_menu_button.config(state=tk.NORMAL)
        # self.copy_button.config(state=tk.DISABLED, style="Copy.TButton") # El estado se gestiona en check_copy_readiness

        self.source_device_info = None
        self.destination_device_info = None
        self._display_device_info(self.source_info_label, None, "Origen")
        self._display_device_info(self.dest_info_label, None, "Destino")
        self.copy_date = datetime.date.today()
        self.camera_make = "UNTITLED"
        self.camera_model = "CAMERA"
        self.cancel_copy_flag.clear()
        self.pause_copy_flag.clear()
        self.copy_thread = None 
        self.check_copy_readiness() # Esto establecerá el estilo y estado correctos del botón de copia
        
    # --- Resto de los métodos sin cambios relevantes para esta solicitud ---
    # (update_status, get_usb_devices, _display_device_info, select_source, select_destination, 
    #  check_date_conflict, extract_camera_info_thread, get_target_folder_name, 
    #  create_progress_window, toggle_pause_resume, confirm_cancel_copy, perform_copy_operation,
    #  update_progress_display, handle_copy_cancelled)

    # Asegúrate de que estos métodos estén presentes de la versión anterior si los borré por brevedad
    def update_status(self, message, level="info"): 
        self.status_label.config(text=message, style=f"{level.capitalize()}.Status.TLabel")

    def get_usb_devices(self):
        devices = []
        partitions = psutil.disk_partitions(all=False)
        for p in partitions:
            if any(p.mountpoint.startswith(prefix) for prefix in self.USB_MOUNT_PREFIXES) and os.path.ismount(p.mountpoint):
                try:
                    usage = psutil.disk_usage(p.mountpoint)
                    label = os.path.basename(p.mountpoint) 
                    
                    devices.append({
                        "path": p.mountpoint,
                        "label": label if label else p.device,
                        "free_space_gb": usage.free / (1024**3),
                        "total_space_gb": usage.total / (1024**3),
                        "device": p.device
                    })
                except Exception as e:
                    print(f"Error al acceder a {p.mountpoint} (usuario: {self.current_user}): {e}")
        return devices
    
    def _display_device_info(self, label_widget, device_info, type_str=""):
        if device_info:
            text = f"{device_info['label']}\n({device_info['free_space_gb']:.1f}G / {device_info['total_space_gb']:.1f}G)"
            label_widget.config(text=text)
        else:
            label_widget.config(text=f"{type_str} no sel.")

    def select_source(self):
        devices = self.get_usb_devices()
        if not devices:
            messagebox.showinfo("Sin dispositivos", "No se detectaron dispositivos USB montados.", parent=self.root)
            return

        dialog = DeviceSelectionDialog(self.root, "Seleccionar Origen", devices)
        self.root.wait_window(dialog) 
        
        selected_dev = dialog.result
        if selected_dev:
            if self.destination_device_info and selected_dev['path'] == self.destination_device_info['path']:
                messagebox.showwarning("Advertencia", "El origen no puede ser el mismo que el destino.", parent=self.root)
                return

            self.source_device_info = selected_dev
            self._display_device_info(self.source_info_label, self.source_device_info, "Origen")
            self.update_status(f"Origen: {self.source_device_info['label']}", "info")
            threading.Thread(target=self.extract_camera_info_thread, daemon=True).start()
        self.check_copy_readiness()

    def select_destination(self):
        devices = self.get_usb_devices()
        if not devices:
            messagebox.showinfo("Sin dispositivos", "No se detectaron dispositivos USB montados.", parent=self.root)
            return

        dialog = DeviceSelectionDialog(self.root, "Seleccionar Destino", devices)
        self.root.wait_window(dialog)

        selected_dev = dialog.result
        if selected_dev:
            if self.source_device_info and selected_dev['path'] == self.source_device_info['path']:
                messagebox.showwarning("Advertencia", "El destino no puede ser el mismo que el origen.", parent=self.root)
                return

            self.destination_device_info = selected_dev
            self._display_device_info(self.dest_info_label, self.destination_device_info, "Destino")
            self.update_status(f"Destino: {self.destination_device_info['label']}", "info")
            self.check_date_conflict()
        self.check_copy_readiness()

    def check_date_conflict(self): # Sin cambios, solo por completitud
        if not self.destination_device_info:
            return True 
        date_folder_name = self.copy_date.strftime("%Y%m%d")
        potential_date_folder = os.path.join(self.destination_device_info["path"], date_folder_name)
        if os.path.exists(potential_date_folder) and os.path.isdir(potential_date_folder):
            res = messagebox.askyesnocancel("Conflicto de Fecha",
                                           f"La carpeta '{date_folder_name}' ya existe.\n"
                                           "¿Continuar (Sí)?\n¿Cambiar fecha (No)?",
                                           parent=self.root, icon='warning')
            if res is True: 
                self.update_status(f"Destino: {self.destination_device_info['label']}, Carpeta: {date_folder_name} (existente)", "info")
                return True
            elif res is False: 
                date_dialog = DatePickerDialog(self.root, "Nueva Fecha de Copia", self.copy_date)
                self.root.wait_window(date_dialog)
                if date_dialog.result:
                    self.copy_date = date_dialog.result
                    self.update_status(f"Destino: {self.destination_device_info['label']}, Nueva fecha: {self.copy_date.strftime('%Y%m%d')}", "info")
                    return True 
                else: 
                    self.destination_device_info = None
                    self._display_device_info(self.dest_info_label, None, "Destino")
                    self.update_status("Destino cancelado.", "warning")
                    return False
            else: 
                self.destination_device_info = None
                self._display_device_info(self.dest_info_label, None, "Destino")
                self.update_status("Destino cancelado.", "warning")
                return False
        return True

    def extract_camera_info_thread(self): # Sin cambios, solo por completitud
        if not self.source_device_info:
            return
        self.root.after(0, lambda: self.update_status("Info cámara...", "info"))
        self.camera_make = "UNTITLED"; self.camera_model = "CAMERA"
        image_extensions = ('.arw', '.dng', '.nef', '.jpg', '.jpeg', '.cr2', '.cr3', '.raf', '.rw2', '.orf')
        found_info = False
        try:
            for root_dir, _, files in os.walk(self.source_device_info["path"]):
                if self.cancel_copy_flag.is_set() and self.copy_thread: return
                for file in files:
                    if file.lower().endswith(image_extensions):
                        filepath = os.path.join(root_dir, file)
                        try:
                            process_verbose = subprocess.run(["exiftool", "-Model", "-Make", filepath], capture_output=True, text=True, timeout=3, check=False, encoding='utf-8', errors='ignore')
                            temp_model, temp_make = None, None
                            if process_verbose.returncode == 0 and process_verbose.stdout:
                                for line_verbose in process_verbose.stdout.splitlines():
                                    if ":" in line_verbose:
                                        tag, value = line_verbose.split(":", 1); tag = tag.strip(); value = value.strip()
                                        if tag == "Make": temp_make = value
                                        elif tag == "Camera Model Name" or tag == "Model": temp_model = value
                            if temp_make and temp_model: self.camera_make = temp_make.replace(" ", "-").upper(); self.camera_model = temp_model.replace(" ", "-"); found_info = True; break 
                            elif temp_model : self.camera_make = "UNKNOWN_MAKE"; self.camera_model = temp_model.replace(" ", "-"); found_info = True; break
                        except FileNotFoundError: self.root.after(0, lambda: self.update_status("Error: exiftool no hallado.", "error")); self.root.after(0, lambda: messagebox.showwarning("Exiftool", "exiftool no está instalado.", parent=self.root)); return 
                        except subprocess.TimeoutExpired: continue
                        except Exception as e: print(f"Error exiftool {filepath}: {e}"); continue
                if found_info: break 
        except Exception as e: print(f"Error escaneo cámara: {e}"); self.root.after(0, lambda: self.update_status("Error info cámara.", "error"))
        if found_info: self.root.after(0, lambda: self.update_status(f"{self.camera_make} {self.camera_model}", "info"))
        else: self.root.after(0, lambda: self.update_status("Info cámara no hallada.", "warning"))
        self.root.after(0, self.check_copy_readiness)

    def get_target_folder_name(self): # Sin cambios, solo por completitud
        base_folder_name = f"{self.camera_make}-{self.camera_model}"; date_str = self.copy_date.strftime("%Y%m%d")
        final_dest_path_base = os.path.join(self.destination_device_info["path"], date_str)
        try: os.makedirs(final_dest_path_base, exist_ok=True)
        except OSError as e: messagebox.showerror("Error Destino", f"No se pudo crear carpeta de fecha:\n{os.path.basename(final_dest_path_base)}\n{e}", parent=self.root); return None
        counter = 1
        while True:
            target_subfolder = f"{base_folder_name}_{counter:05d}"; full_target_path = os.path.join(final_dest_path_base, target_subfolder)
            if not os.path.exists(full_target_path): return full_target_path
            counter += 1
            if counter > 99999: messagebox.showerror("Error", "Demasiadas carpetas con nombre base.", parent=self.root); return None

    def create_progress_window(self): # Sin cambios, solo por completitud
        self.progress_window = CustomDialog(self.root, "Progreso de Copia", fixed_height_ratio=0.7)
        self.progress_window.protocol("WM_DELETE_WINDOW", self.confirm_cancel_copy) 
        main_frame = self.progress_window.main_frame
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=SCREEN_WIDTH-100, mode="determinate", style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(pady=(10,5), padx=10, fill=tk.X)
        self.progress_percent_label = ttk.Label(main_frame, text="0% | ETA: --:--:--", style="Dialog.TLabel"); self.progress_percent_label.pack()
        self.progress_files_label = ttk.Label(main_frame, text="Archivos: 0/0", style="Dialog.TLabel"); self.progress_files_label.pack()
        self.current_file_label = ttk.Label(main_frame, text="Archivo: N/A", style="Dialog.TLabel", wraplength=SCREEN_WIDTH-110); self.current_file_label.pack(pady=5)
        action_button_frame = ttk.Frame(main_frame, style="CustomDialog.TFrame"); action_button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0))
        action_button_frame.columnconfigure(0, weight=1); action_button_frame.columnconfigure(1, weight=1)
        self.pause_resume_button = ttk.Button(action_button_frame, text="Pausar", command=self.toggle_pause_resume, style="Dialog.TButton"); self.pause_resume_button.grid(row=0, column=0, padx=5, sticky="ew")
        cancel_button = ttk.Button(action_button_frame, text="Cancelar", command=self.confirm_cancel_copy, style="Dialog.TButton"); cancel_button.grid(row=0, column=1, padx=5, sticky="ew")

    def toggle_pause_resume(self): # Sin cambios, solo por completitud
        if self.pause_copy_flag.is_set(): 
            self.pause_copy_flag.clear()
            if hasattr(self, 'pause_resume_button') and self.pause_resume_button.winfo_exists(): self.pause_resume_button.config(text="Pausar")
            self.update_status("Copia reanudada.", "info")
        else: 
            self.pause_copy_flag.set()
            if hasattr(self, 'pause_resume_button') and self.pause_resume_button.winfo_exists(): self.pause_resume_button.config(text="Reanudar")
            self.update_status("Copia pausada.", "warning")

    def confirm_cancel_copy(self): # Sin cambios, solo por completitud
        parent_window = self.progress_window if hasattr(self, 'progress_window') and self.progress_window.winfo_exists() else self.root
        if messagebox.askyesno("Cancelar Copia", "¿Seguro que cancelas la copia?", parent=parent_window):
            self.cancel_copy_flag.set()
            if self.pause_copy_flag.is_set(): self.pause_copy_flag.clear() 

    def perform_copy_operation(self): # Sin cambios, solo por completitud
        source_path = self.source_device_info["path"]; destination_base_folder = self.target_copy_folder_full_path
        try: os.makedirs(destination_base_folder, exist_ok=True)
        except OSError as e: self.root.after(0, lambda: messagebox.showerror("Error", f"Error al crear destino:\n{os.path.basename(destination_base_folder)}\n{e}", parent=self.root)); self.root.after(0, lambda: self.finalize_copy_ui(success=False, message_override="Error creando destino.")); return
        self.root.after(0, lambda: self.current_file_label.config(text="Calculando..."))
        files_to_copy = []
        try:
            for root_dir, dirs, files in os.walk(source_path, topdown=True):
                if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return
                relative_path = os.path.relpath(root_dir, source_path); current_dest_dir = os.path.join(destination_base_folder, relative_path)
                if relative_path != ".": os.makedirs(current_dest_dir, exist_ok=True)
                for file_name in files: src_file = os.path.join(root_dir, file_name); dest_file = os.path.join(current_dest_dir, file_name); files_to_copy.append((src_file, dest_file))
        except Exception as e: self.root.after(0, lambda: messagebox.showerror("Error", f"Error listando archivos:\n{e}", parent=self.root)); self.root.after(0, lambda: self.finalize_copy_ui(success=False, message_override="Error listando archivos.")); return
        total_files = len(files_to_copy)
        self.root.after(0, lambda: self.progress_files_label.config(text=f"Archivos: 0/{total_files}"))
        if total_files == 0: parent_win = self.progress_window if hasattr(self, 'progress_window') and self.progress_window.winfo_exists() else self.root; self.root.after(0, lambda: messagebox.showinfo("Info", "No hay archivos para copiar.", parent=parent_win)); self.root.after(0, lambda: self.finalize_copy_ui(success=True, files_copied=0, total_files_attempted=0)); return
        copied_files = 0; start_time = time.time(); errors_occurred = []
        for i, (src_file, dest_file) in enumerate(files_to_copy):
            while self.pause_copy_flag.is_set(): 
                if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return
                time.sleep(0.2) 
            if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return
            self.root.after(0, lambda sf=src_file: self.current_file_label.config(text=f"{os.path.basename(sf)}"))
            retries = 2; copied_successfully = False; last_error = None
            for attempt in range(retries + 1):
                if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return
                try: os.makedirs(os.path.dirname(dest_file), exist_ok=True); shutil.copy2(src_file, dest_file); copied_successfully = True; break 
                except Exception as e:
                    last_error = e
                    if attempt < retries: self.root.after(0, lambda sf=src_file, a=attempt+1: self.current_file_label.config(text=f"Error {os.path.basename(sf)}. Reint. {a+1}")); time.sleep(1)
                    else: self.root.after(0, lambda sf=src_file: self.current_file_label.config(text=f"Fallo {os.path.basename(sf)}"))
            if copied_successfully: copied_files += 1
            else: errors_occurred.append(f"Fallo {os.path.basename(src_file)}: {last_error}")
            progress_percent = ((i + 1) / total_files) * 100; elapsed_time = time.time() - start_time; eta_seconds = 0
            if progress_percent > 0 and elapsed_time > 0.1: eta_seconds = (elapsed_time / progress_percent) * (100 - progress_percent)
            eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds)) if eta_seconds > 0 else "--:--"; self.root.after(0, lambda p=progress_percent, cf=copied_files, tf=total_files, eta=eta_str: self.update_progress_display(p, cf, tf, eta))
        elapsed_total_time_str = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)); parent_win_msg = self.progress_window if hasattr(self, 'progress_window') and self.progress_window.winfo_exists() else self.root
        dest_folder_short = f"...{os.path.basename(os.path.dirname(destination_base_folder))}/{os.path.basename(destination_base_folder)}"
        if not errors_occurred:
            msg = (f"COPIA COMPLETA\n{copied_files}/{total_files} archivos a {dest_folder_short}\nTiempo: {elapsed_total_time_str}"); self.root.after(0, lambda m=msg: messagebox.showinfo("Éxito", m, parent=parent_win_msg)); self.root.after(0, lambda: self.finalize_copy_ui(success=True, files_copied=copied_files, total_files_attempted=total_files))
        else:
            error_summary = "\n".join(errors_occurred[:2]); 
            if len(errors_occurred) > 2: error_summary += f"\n... y {len(errors_occurred)-2} más."
            msg = (f"COPIA CON ERRORES\n{copied_files}/{total_files} a {dest_folder_short}\nErrores:\n{error_summary}\nTiempo: {elapsed_total_time_str}"); self.root.after(0, lambda m=msg: messagebox.showwarning("Errores", m, parent=parent_win_msg)); self.root.after(0, lambda: self.finalize_copy_ui(success=False, files_copied=copied_files, total_files_attempted=total_files))

    def update_progress_display(self, percent, copied_count, total_count, eta_str): # Sin cambios, solo por completitud
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_bar['value'] = percent; self.progress_percent_label.config(text=f"{percent:.0f}% | ETA: {eta_str}"); self.progress_files_label.config(text=f"Archivos: {copied_count}/{total_count}")

    def handle_copy_cancelled(self): # Sin cambios, solo por completitud
        self.update_status("Copia cancelada.", "warning")
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists(): self.progress_window.destroy()
        if hasattr(self, 'target_copy_folder_full_path') and self.target_copy_folder_full_path and os.path.exists(self.target_copy_folder_full_path):
            try:
                is_empty = not any(os.scandir(self.target_copy_folder_full_path))
                if not is_empty:
                    if messagebox.askyesno("Cancelar", "Copia cancelada. ¿Eliminar destino parcial?", parent=self.root): shutil.rmtree(self.target_copy_folder_full_path); self.update_status("Cancelada. Destino parcial eliminado.", "warning")
                else: shutil.rmtree(self.target_copy_folder_full_path); self.update_status("Cancelada. Destino vacío eliminado.", "warning")
            except Exception as e: self.update_status(f"Cancelada. Error limpiando destino: {e}", "error")
        self.finalize_copy_ui(success=False, message_override="Copia cancelada.")


if __name__ == "__main__":
    root = tk.Tk()
    # root.attributes('-fullscreen', True) 
    app = ModernCopierApp(root)
    root.mainloop()
