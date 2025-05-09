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
import errno # Para códigos de error específicos

# --- Constantes de Diseño y Configuración ---
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 300

BG_COLOR = "#2E2E2E"
FG_COLOR = "#E0E0E0"
ACCENT_COLOR = "#007ACC"
BUTTON_ACTIVE_BG = "#005C99"
ENABLED_COPY_COLOR = "#4CAF50"
ENABLED_COPY_ACTIVE_BG = "#388E3C"
BORDER_COLOR = "#4A4A4A"
LABEL_INFO_FG = "#B0B0B0"
DANGER_COLOR = "#D32F2F"
DANGER_ACTIVE_BG = "#B71C1C"

FONT_FAMILY = "DejaVu Sans"
FONT_SIZE_SMALL = 8
FONT_SIZE_NORMAL = 9
FONT_SIZE_LARGE = 11
FONT_SIZE_XLARGE = 13

# --- Clases CustomDialog, DatePickerDialog, DeviceSelectionDialog, SystemMenuDialog ---
class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title="", fixed_height_ratio=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG_COLOR)
        self.transient(parent)
        self.grab_set()
        parent_width = parent.winfo_width(); parent_height = parent.winfo_height()
        parent_x = parent.winfo_x(); parent_y = parent.winfo_y()
        effective_parent_width = parent_width if parent_width > 0 else SCREEN_WIDTH
        effective_parent_height = parent_height if parent_height > 0 else SCREEN_HEIGHT
        dialog_width = int(effective_parent_width * 0.90)
        if fixed_height_ratio: dialog_height = int(effective_parent_height * fixed_height_ratio)
        else: dialog_height = int(effective_parent_height * 0.80)
        dialog_width = min(dialog_width, SCREEN_WIDTH - 20)
        dialog_height = min(dialog_height, SCREEN_HEIGHT - 30)
        pos_x = parent_x + (effective_parent_width - dialog_width) // 2
        pos_y = parent_y + (effective_parent_height - dialog_height) // 2
        pos_x = max(5, min(pos_x, SCREEN_WIDTH - dialog_width - 5))
        pos_y = max(5, min(pos_y, SCREEN_HEIGHT - dialog_height - 5))
        self.geometry(f"{dialog_width}x{dialog_height}+{pos_x}+{pos_y}")
        self.resizable(False, False)
        self.result = None
        self.main_frame = ttk.Frame(self, style="CustomDialog.TFrame", padding=10)
        self.main_frame.pack(expand=True, fill=tk.BOTH)

    def _create_button_bar(self, buttons_config):
        button_frame = ttk.Frame(self.main_frame, style="CustomDialog.TFrame")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0))
        if not buttons_config:
            return button_frame

        button_frame.columnconfigure(list(range(len(buttons_config))), weight=1)
        for i, (text, command, style_name) in enumerate(buttons_config):
            btn = ttk.Button(button_frame, text=text, command=command, style=style_name, width=10)
            btn.grid(row=0, column=i, padx=5, pady=(0,5), sticky="ew")
        return button_frame

class DatePickerDialog(CustomDialog):
    def __init__(self, parent, title="Seleccionar Fecha", initial_date=None):
        self.current_date = initial_date if initial_date else datetime.date.today()
        super().__init__(parent, title, fixed_height_ratio=0.65)
        self._create_body()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.update_date_display()

    def _create_custom_spinbox(self, parent_frame, label_text, value_type):
        frame = ttk.Frame(parent_frame, style="CustomDialog.TFrame")
        ttk.Label(frame, text=label_text, style="Dialog.TLabel", width=4, anchor="w").pack(side=tk.LEFT, padx=(0,3))
        btn_down = ttk.Button(frame, text="-" , style="Arrow.Dialog.TButton", width=2, command=lambda vt=value_type: self.change_date_value(vt, -1)); btn_down.pack(side=tk.LEFT, padx=1)
        value_label = ttk.Label(frame, text="00", style="DateValue.Dialog.TLabel", width=4, anchor="center"); value_label.pack(side=tk.LEFT, padx=2)
        btn_up = ttk.Button(frame, text="+", style="Arrow.Dialog.TButton", width=2, command=lambda vt=value_type: self.change_date_value(vt, 1)); btn_up.pack(side=tk.LEFT, padx=1)
        return frame, value_label

    def _create_body(self):
        body_container = ttk.Frame(self.main_frame, style="CustomDialog.TFrame")
        body_container.pack(expand=True, fill=tk.BOTH, pady=5, padx=5)
        body_container.columnconfigure(0, weight=2); body_container.columnconfigure(1, weight=1)
        body_container.rowconfigure(0, weight=1)

        date_selectors_frame = ttk.Frame(body_container, style="CustomDialog.TFrame")
        date_selectors_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        date_selectors_frame.rowconfigure([0,4], weight=1); date_selectors_frame.rowconfigure([1,2,3], weight=0)
        date_selectors_frame.columnconfigure(0, weight=1)

        year_frame, self.year_label = self._create_custom_spinbox(date_selectors_frame, "Año:", "year")
        year_frame.grid(row=1, column=0, sticky="ew", pady=2)
        month_frame, self.month_label = self._create_custom_spinbox(date_selectors_frame, "Mes:", "month")
        month_frame.grid(row=2, column=0, sticky="ew", pady=2)
        day_frame, self.day_label = self._create_custom_spinbox(date_selectors_frame, "Día:", "day")
        day_frame.grid(row=3, column=0, sticky="ew", pady=2)

        buttons_frame = ttk.Frame(body_container, style="CustomDialog.TFrame")
        buttons_frame.grid(row=0, column=1, sticky="ns", padx=(5, 0))
        buttons_frame.rowconfigure([0,3], weight=1); buttons_frame.rowconfigure([1,2], weight=0)
        buttons_frame.columnconfigure(0, weight=1)

        accept_button = ttk.Button(buttons_frame, text="Aceptar", command=self.apply, style="Dialog.TButton", width=8)
        accept_button.grid(row=1, column=0, pady=(0, 4), sticky="ew")
        cancel_button = ttk.Button(buttons_frame, text="Cancelar", command=self.cancel, style="Dialog.TButton", width=8)
        cancel_button.grid(row=2, column=0, pady=(4, 0), sticky="ew")

    def update_date_display(self):
        self.year_label.config(text=f"{self.current_date.year:04d}")
        self.month_label.config(text=f"{self.current_date.month:02d}")
        self.day_label.config(text=f"{self.current_date.day:02d}")

    def change_date_value(self, value_type, delta):
        year, month, day = self.current_date.year, self.current_date.month, self.current_date.day
        if value_type == "year": year = max(2000, min(2100, year + delta))
        elif value_type == "month":
            month += delta;
            if month > 12: month = 1
            elif month < 1: month = 12
        elif value_type == "day":
            day += delta; max_days = calendar.monthrange(year, month)[1]
            if day > max_days: day = 1
            elif day < 1: day = max_days
        try: self.current_date = datetime.date(year, month, day)
        except ValueError:
            try: day = min(day, calendar.monthrange(year, month)[1]); self.current_date = datetime.date(year, month, day)
            except ValueError: pass
        self.update_date_display()

    def apply(self): self.result = self.current_date; self.destroy()
    def cancel(self): self.result = None; self.destroy()

class DeviceSelectionDialog(CustomDialog):
    def __init__(self, parent, title="Seleccionar Dispositivo", devices=None):
        self.devices = devices if devices else []
        super().__init__(parent, title, fixed_height_ratio=0.7)
        self._create_body()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def _create_body(self):
        ttk.Label(self.main_frame, text="Selecciona un dispositivo:", style="Dialog.TLabel").pack(pady=(5,10))
        body_content_frame = ttk.Frame(self.main_frame, style="CustomDialog.TFrame")
        body_content_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        if self.devices and len(self.devices) <= 2:
            for device in self.devices:
                btn_text = f"{device['label']}\n({device['free_space_gb']:.1f}G / {device['total_space_gb']:.1f}G)"
                btn = ttk.Button(body_content_frame, text=btn_text, style="LargeDevice.Dialog.TButton", command=lambda d=device: self.on_device_button_select(d))
                btn.pack(fill=tk.X, pady=5, ipady=8)
            self._create_button_bar([("Cancelar", self.on_cancel, "Dialog.TButton")])
        elif self.devices:
            self.listbox_frame = ttk.Frame(body_content_frame, style="CustomDialog.TFrame"); self.listbox_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
            self.listbox = tk.Listbox(self.listbox_frame, width=35, height=4, bg=BORDER_COLOR, fg=FG_COLOR, selectbackground=ACCENT_COLOR, selectforeground=FG_COLOR, font=(FONT_FAMILY, FONT_SIZE_NORMAL), borderwidth=0, highlightthickness=0, relief=tk.FLAT, activestyle="none")
            for dev in self.devices: self.listbox.insert(tk.END, f" {dev['label']} ({dev['free_space_gb']:.1f}G/{dev['total_space_gb']:.1f}G)")
            self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar = ttk.Scrollbar(self.listbox_frame, orient="vertical", command=self.listbox.yview, style="Custom.Vertical.TScrollbar"); scrollbar.pack(side=tk.RIGHT, fill="y")
            self.listbox.config(yscrollcommand=scrollbar.set)
            if self.devices: self.listbox.selection_set(0); self.listbox.activate(0)
            self._create_button_bar([("Aceptar", self.on_select_listbox, "Dialog.TButton"), ("Cancelar", self.on_cancel, "Dialog.TButton")])
        else:
            ttk.Label(body_content_frame, text="No se encontraron dispositivos.", style="Dialog.TLabel", anchor="center").pack(expand=True, fill=tk.BOTH, pady=20)
            self._create_button_bar([("Cerrar", self.on_cancel, "Dialog.TButton")])

    def on_device_button_select(self, device): self.result = device; self.destroy()
    def on_select_listbox(self):
        try: idx = self.listbox.curselection()[0]; self.result = self.devices[idx]; self.destroy()
        except IndexError: messagebox.showwarning("Advertencia", "Por favor, selecciona un dispositivo.", parent=self)
    def on_cancel(self): self.result = None; self.destroy()

class SystemMenuDialog(CustomDialog):
    def __init__(self, parent, app_instance):
        self.app = app_instance; super().__init__(parent, title="Menú del Sistema", fixed_height_ratio=0.8)
        self._create_menu_buttons(); self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _create_menu_buttons(self):
        menu_frame = ttk.Frame(self.main_frame, style="CustomDialog.TFrame"); menu_frame.pack(expand=True, fill=tk.BOTH, pady=10, padx=10)
        btn_close_app = ttk.Button(menu_frame, text="Cerrar Aplicación", command=self.close_application, style="Large.TButton"); btn_close_app.pack(fill=tk.X, pady=5, ipady=5)
        btn_reboot = ttk.Button(menu_frame, text="Reiniciar Pi", command=self.reboot_system, style="Danger.Large.TButton"); btn_reboot.pack(fill=tk.X, pady=5, ipady=5)
        btn_shutdown = ttk.Button(menu_frame, text="Apagar Pi", command=self.shutdown_system, style="Danger.Large.TButton"); btn_shutdown.pack(fill=tk.X, pady=5, ipady=5)

    def close_application(self): self.destroy(); self.app.root.destroy()
    def reboot_system(self):
        if messagebox.askyesno("Confirmar Reinicio", "¿Seguro que quieres reiniciar la Raspberry Pi?", icon='warning', parent=self):
            self.destroy()
            try: subprocess.run(["sudo", "reboot"], check=True)
            except Exception as e: messagebox.showerror("Error de Reinicio", f"No se pudo reiniciar el sistema:\n{e}", parent=self.app.root)
    def shutdown_system(self):
        if messagebox.askyesno("Confirmar Apagado", "¿Seguro que quieres apagar la Raspberry Pi?", icon='warning', parent=self):
            self.destroy()
            try: subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
            except Exception as e: messagebox.showerror("Error de Apagado", f"No se pudo apagar el sistema:\n{e}", parent=self.app.root)

class ModernCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RPi USB Copier")
        self.root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        self.root.configure(bg=BG_COLOR)

        self.current_user = getpass.getuser()
        self.USB_MOUNT_PREFIXES = (f"/media/{self.current_user}/", f"/run/media/{self.current_user}/", f"/mnt/{self.current_user}/", "/media/", "/mnt/")

        self.source_device_info = None
        self.destination_device_info = None
        self.camera_make = "UNTITLED"
        self.camera_model = "CAMERA"
        self.copy_date = datetime.date.today()

        self.copy_thread = None
        self.cancel_copy_flag = threading.Event()
        self.pause_copy_flag = threading.Event()
        
        self.is_sync_mode = tk.BooleanVar(value=False) # NUEVO: Variable para el modo sincronización

        self.style = ttk.Style()
        self.setup_styles()
        self.create_main_layout()
        self.update_status("Listo. Seleccione origen y destino.", "info")
        self.toggle_sync_mode_ui() # NUEVO: Llamar para establecer textos iniciales

    def setup_styles(self):
        self.style.theme_use('clam')
        self.style.configure("TFrame", background=BG_COLOR); self.style.configure("CustomDialog.TFrame", background=BG_COLOR)
        self.style.configure("Copy.TButton", font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"), padding=(8, 10), background=ACCENT_COLOR, foreground=FG_COLOR, borderwidth=1, relief="raised")
        self.style.map("Copy.TButton", background=[('active', BUTTON_ACTIVE_BG), ('disabled', BORDER_COLOR)], foreground=[('disabled', FG_COLOR)])
        self.style.configure("Enabled.Copy.TButton", font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"), padding=(8, 10), background=ENABLED_COPY_COLOR, foreground=FG_COLOR, borderwidth=1, relief="raised")
        self.style.map("Enabled.Copy.TButton", background=[('active', ENABLED_COPY_ACTIVE_BG)], foreground=[])
        self.style.configure("Danger.Large.TButton", font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"), padding=(8, 10), background=DANGER_COLOR, foreground=FG_COLOR, borderwidth=1, relief="raised")
        self.style.map("Danger.Large.TButton", background=[('active', DANGER_ACTIVE_BG), ('disabled', BORDER_COLOR)], foreground=[('disabled', FG_COLOR)])
        self.style.configure("Medium.TButton", font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"), padding=(6, 8), background=ACCENT_COLOR, foreground=FG_COLOR, borderwidth=1)
        self.style.map("Medium.TButton", background=[('active', BUTTON_ACTIVE_BG), ('disabled', BORDER_COLOR)], foreground=[('disabled', FG_COLOR)])
        self.style.configure("Dialog.TButton", font=(FONT_FAMILY, FONT_SIZE_NORMAL), padding=(6, 6), background=ACCENT_COLOR, foreground=FG_COLOR)
        self.style.map("Dialog.TButton", background=[('active', BUTTON_ACTIVE_BG)])
        self.style.configure("LargeDevice.Dialog.TButton", font=(FONT_FAMILY, FONT_SIZE_NORMAL), padding=(8, 8), background=ACCENT_COLOR, foreground=FG_COLOR, justify=tk.CENTER, anchor=tk.CENTER)
        self.style.map("LargeDevice.Dialog.TButton", background=[('active', BUTTON_ACTIVE_BG)])
        self.style.configure("Arrow.Dialog.TButton", font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"), padding=(4, 6), background=ACCENT_COLOR, foreground=FG_COLOR)
        self.style.map("Arrow.Dialog.TButton", background=[('active', BUTTON_ACTIVE_BG)])
        self.style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY, FONT_SIZE_NORMAL)); self.style.configure("Dialog.TLabel", background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.style.configure("DateValue.Dialog.TLabel", background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY, FONT_SIZE_XLARGE, "bold"), padding=(5,2))
        self.style.configure("Header.TLabelframe", background=BG_COLOR, foreground=ACCENT_COLOR, labelmargins=(5,0,0,0), font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"))
        self.style.configure("Header.TLabelframe.Label", background=BG_COLOR, foreground=ACCENT_COLOR, font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"))
        self.style.configure("Info.TLabel", font=(FONT_FAMILY, FONT_SIZE_SMALL), foreground=LABEL_INFO_FG, background=BG_COLOR)
        self.style.configure("Status.TLabel", font=(FONT_FAMILY, FONT_SIZE_SMALL), wraplength=SCREEN_WIDTH - 80, background=BG_COLOR)
        self.style.configure("Success.Status.TLabel", foreground="#4CAF50", background=BG_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL))
        self.style.configure("Error.Status.TLabel", foreground="#F44336", background=BG_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL))
        self.style.configure("Warning.Status.TLabel", foreground="#FFC107", background=BG_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL))
        self.style.configure("Info.Status.TLabel", foreground=LABEL_INFO_FG, background=BG_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL))
        self.style.configure("Custom.Horizontal.TProgressbar", thickness=15, background=ACCENT_COLOR, troughcolor=BORDER_COLOR, borderwidth=0)
        self.style.configure("Custom.Vertical.TScrollbar", gripcount=0, background=ACCENT_COLOR, darkcolor=BORDER_COLOR, lightcolor=BORDER_COLOR, troughcolor=BG_COLOR, bordercolor=BG_COLOR, arrowcolor=FG_COLOR)
        self.style.map("Custom.Vertical.TScrollbar", background=[('active', BUTTON_ACTIVE_BG)])
        self.style.configure("TCheckbutton", background=BG_COLOR, foreground=FG_COLOR, font=(FONT_FAMILY, FONT_SIZE_SMALL), indicatorcolor=BORDER_COLOR, padding=(5,2))
        self.style.map("TCheckbutton", indicatorcolor=[('selected', ACCENT_COLOR), ('active', BUTTON_ACTIVE_BG)])


    def create_main_layout(self):
        outer_container = ttk.Frame(self.root, style="TFrame"); outer_container.pack(expand=True, fill=tk.BOTH, padx=3, pady=3)
        
        # --- Sección de Selección ---
        selection_frame = ttk.Frame(outer_container, style="TFrame"); selection_frame.pack(fill=tk.BOTH, expand=True, pady=(0,5)) # Añadido pady para separar del checkbox
        
        self.source_labelframe = ttk.LabelFrame(selection_frame, text="ORIGEN", style="Header.TLabelframe"); self.source_labelframe.pack(fill=tk.X, pady=(0,3), padx=0)
        source_content_frame = ttk.Frame(self.source_labelframe, style="TFrame"); source_content_frame.pack(fill=tk.X, padx=3, pady=3)
        source_content_frame.columnconfigure(0, weight=1); source_content_frame.columnconfigure(1, weight=2)
        self.source_btn = ttk.Button(source_content_frame, text="Seleccionar", command=self.select_source, style="Medium.TButton"); self.source_btn.grid(row=0, column=0, sticky="ew", padx=(0,3))
        self.source_info_label = ttk.Label(source_content_frame, text="No seleccionado", style="Info.TLabel", justify=tk.LEFT, wraplength=int(SCREEN_WIDTH * 0.50)); self.source_info_label.grid(row=0, column=1, sticky="nsew")
        
        self.dest_labelframe = ttk.LabelFrame(selection_frame, text="DESTINO", style="Header.TLabelframe"); self.dest_labelframe.pack(fill=tk.X, pady=(3,3), padx=0)
        dest_content_frame = ttk.Frame(self.dest_labelframe, style="TFrame"); dest_content_frame.pack(fill=tk.X, padx=3, pady=3)
        dest_content_frame.columnconfigure(0, weight=1); dest_content_frame.columnconfigure(1, weight=2)
        self.dest_btn = ttk.Button(dest_content_frame, text="Seleccionar", command=self.select_destination, style="Medium.TButton"); self.dest_btn.grid(row=0, column=0, sticky="ew", padx=(0,3))
        self.dest_info_label = ttk.Label(dest_content_frame, text="No seleccionado", style="Info.TLabel", justify=tk.LEFT, wraplength=int(SCREEN_WIDTH * 0.50)); self.dest_info_label.grid(row=0, column=1, sticky="nsew")

        # --- Checkbox para Modo Sincronización ---
        self.sync_mode_checkbox = ttk.Checkbutton(
            outer_container, 
            text="Sincronizar disco de backup secundario", 
            variable=self.is_sync_mode, 
            command=self.toggle_sync_mode_ui, 
            style="TCheckbutton"
        )
        self.sync_mode_checkbox.pack(fill=tk.X, pady=(0, 5), padx=3)


        # --- Barra de Acción Inferior ---
        action_bar_height = 55
        action_bar_frame = ttk.Frame(outer_container, style="TFrame", height=action_bar_height)
        action_bar_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(3,0)); action_bar_frame.pack_propagate(False)
        action_bar_frame.columnconfigure(0, weight=3); action_bar_frame.columnconfigure(1, weight=1)
        self.copy_button = ttk.Button(action_bar_frame, text="INICIAR COPIA", command=self.start_copy, style="Copy.TButton", state=tk.DISABLED); self.copy_button.grid(row=0, column=0, sticky="nsew", padx=(3,1), pady=(1,1))
        self.system_menu_button = ttk.Button(action_bar_frame, text="Menú", command=self.open_system_menu, style="Medium.TButton"); self.system_menu_button.grid(row=0, column=1, sticky="nsew", padx=(1,3), pady=(1,1))
        self.status_label = ttk.Label(action_bar_frame, text="Listo", style="Status.TLabel", anchor="center"); self.status_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=3, pady=(0,1))

    # NUEVO: Función para actualizar la UI según el modo de sincronización
    def toggle_sync_mode_ui(self, *args):
        is_sync = self.is_sync_mode.get()
        if is_sync:
            self.source_labelframe.config(text="DISCO ORIGEN (Backup Principal)")
            self.dest_labelframe.config(text="DISCO DESTINO (Backup Secundario)")
            self.copy_button.config(text="SINCRONIZAR")
            self.update_status("Modo Sincronización: Seleccione discos.", "info")
        else:
            self.source_labelframe.config(text="ORIGEN (Tarjeta SD)")
            self.dest_labelframe.config(text="DESTINO (Disco Duro)")
            self.copy_button.config(text="INICIAR COPIA")
            self.update_status("Modo Copia SD: Seleccione origen y destino.", "info")
        
        # Resetear selecciones al cambiar de modo
        self.source_device_info = None
        self.destination_device_info = None
        self._display_device_info(self.source_info_label, None, "Origen")
        self._display_device_info(self.dest_info_label, None, "Destino")
        self.check_copy_readiness()


    def open_system_menu(self):
        if self.copy_thread and self.copy_thread.is_alive():
            messagebox.showinfo("Menú Bloqueado", "El menú no está disponible durante una copia.", parent=self.root); return
        SystemMenuDialog(self.root, self)

    def update_status(self, message, level="info"): self.status_label.config(text=message, style=f"{level.capitalize()}.Status.TLabel")

    def get_usb_devices(self):
        devices = []
        partitions = psutil.disk_partitions(all=False)
        for p in partitions:
            if any(p.mountpoint.startswith(prefix) for prefix in self.USB_MOUNT_PREFIXES) and os.path.exists(p.mountpoint) and os.path.ismount(p.mountpoint):
                try:
                    usage = psutil.disk_usage(p.mountpoint); label = os.path.basename(p.mountpoint)
                    devices.append({"path": p.mountpoint, "label": label if label else p.device, "free_space_gb": usage.free / (1024**3), "total_space_gb": usage.total / (1024**3), "device": p.device})
                except (FileNotFoundError, PermissionError) as e: print(f"Dispositivo {p.mountpoint} no accesible al listar: {e}")
                except Exception as e: print(f"Error al acceder a {p.mountpoint} (usuario: {self.current_user}): {e}")
        return devices

    def _display_device_info(self, label_widget, device_info, type_str=""):
        if device_info: label_widget.config(text=f"{device_info['label']}\n({device_info['free_space_gb']:.1f}G / {device_info['total_space_gb']:.1f}G)")
        else: label_widget.config(text=f"{type_str} no sel.")

    def select_source(self):
        devices = self.get_usb_devices()
        if not devices: messagebox.showinfo("Sin dispositivos", "No se detectaron dispositivos USB montados.", parent=self.root); return
        dialog = DeviceSelectionDialog(self.root, "Seleccionar Origen", devices); self.root.wait_window(dialog)
        selected_dev = dialog.result
        if selected_dev:
            if self.destination_device_info and selected_dev['path'] == self.destination_device_info['path']:
                messagebox.showwarning("Advertencia", "El origen no puede ser el mismo que el destino.", parent=self.root); return
            self.source_device_info = selected_dev
            self._display_device_info(self.source_info_label, self.source_device_info, "Origen")
            self.update_status(f"Origen: {self.source_device_info['label']}", "info")
            if not self.is_sync_mode.get(): # Solo extraer info de cámara si no es modo sync
                 threading.Thread(target=self.extract_camera_info_thread, daemon=True).start()
        self.check_copy_readiness()

    def select_destination(self):
        devices = self.get_usb_devices()
        if not devices: messagebox.showinfo("Sin dispositivos", "No se detectaron dispositivos USB montados.", parent=self.root); return
        dialog = DeviceSelectionDialog(self.root, "Seleccionar Destino", devices); self.root.wait_window(dialog)
        selected_dev = dialog.result
        if selected_dev:
            if self.source_device_info and selected_dev['path'] == self.source_device_info['path']:
                messagebox.showwarning("Advertencia", "El destino no puede ser el mismo que el origen.", parent=self.root); return
            self.destination_device_info = selected_dev
            self._display_device_info(self.dest_info_label, self.destination_device_info, "Destino")
            self.update_status(f"Destino: {self.destination_device_info['label']}", "info")
            if not self.is_sync_mode.get(): # Solo chequear conflicto de fecha si no es modo sync
                self.check_date_conflict()
        self.check_copy_readiness()

    def check_copy_readiness(self):
        source_ok = self.source_device_info and os.path.ismount(self.source_device_info['path'])
        dest_ok = self.destination_device_info and os.path.ismount(self.destination_device_info['path'])

        if source_ok and dest_ok:
            self.copy_button.config(state=tk.NORMAL, style="Enabled.Copy.TButton")
        else:
            self.copy_button.config(state=tk.DISABLED, style="Copy.TButton")
            if self.source_device_info and not os.path.ismount(self.source_device_info['path']):
                self.source_device_info = None; self._display_device_info(self.source_info_label, None, "Origen"); self.update_status("Origen desconectado.", "warning")
            if self.destination_device_info and not os.path.ismount(self.destination_device_info['path']):
                self.destination_device_info = None; self._display_device_info(self.dest_info_label, None, "Destino"); self.update_status("Destino desconectado.", "warning")

    def start_copy(self):
        if not self.source_device_info or not os.path.ismount(self.source_device_info['path']):
            messagebox.showerror("Error de Origen", "El dispositivo de origen no está montado o no es accesible.", parent=self.root); self.check_copy_readiness(); return
        if not self.destination_device_info or not os.path.ismount(self.destination_device_info['path']):
            messagebox.showerror("Error de Destino", "El dispositivo de destino no está montado o no es accesible.", parent=self.root); self.check_copy_readiness(); return

        self.copy_button.config(state=tk.DISABLED, style="Copy.TButton")
        self.source_btn.config(state=tk.DISABLED); self.dest_btn.config(state=tk.DISABLED)
        self.system_menu_button.config(state=tk.DISABLED)
        self.sync_mode_checkbox.config(state=tk.DISABLED) # NUEVO: Deshabilitar checkbox durante la operación

        self.cancel_copy_flag.clear(); self.pause_copy_flag.clear()
        self.create_progress_window()

        if self.is_sync_mode.get():
            self.update_status("Preparando sincronización...", "info")
            self.target_copy_folder_full_path = self.destination_device_info["path"] # En sync, el destino es la raíz del disco
            self.copy_thread = threading.Thread(target=self.perform_sync_operation, daemon=True)
        else:
            if not self.check_date_conflict(): self.check_copy_readiness(); self.finalize_copy_ui(success=False, message_override="Conflicto de fecha no resuelto."); return
            self.target_copy_folder_full_path = self.get_target_folder_name()
            if not self.target_copy_folder_full_path: self.finalize_copy_ui(success=False, message_override="Error al generar nombre de carpeta."); return
            self.update_status("Preparando copia SD...", "info")
            self.copy_thread = threading.Thread(target=self.perform_copy_operation, daemon=True)
        
        self.copy_thread.start()

    # NUEVA: Función para sincronizar discos (copia selectiva)
    def perform_sync_operation(self):
        source_root_path = self.source_device_info["path"]
        destination_root_path = self.destination_device_info["path"] # Ya es self.target_copy_folder_full_path
        
        self.root.after(0, lambda: self.current_file_label.config(text="Calculando archivos a sincronizar..."))
        
        items_to_copy = []
        total_items_to_copy_size = 0
        source_item_count_for_progress = 0 # Contará todos los items en origen para el progreso

        # Primera pasada: identificar qué copiar y calcular tamaño
        try:
            for root_dir, dirs, files in os.walk(source_root_path, topdown=True):
                if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return
                
                # Filtrar carpetas ocultas/sistema del origen
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['$RECYCLE.BIN', 'System Volume Information']]

                for dir_name in dirs:
                    source_item_count_for_progress +=1
                    src_dir = os.path.join(root_dir, dir_name)
                    relative_dir = os.path.relpath(src_dir, source_root_path)
                    dest_dir = os.path.join(destination_root_path, relative_dir)
                    if not os.path.exists(dest_dir):
                        items_to_copy.append({'type': 'dir', 'src': src_dir, 'dest': dest_dir})
                        # No sumamos tamaño para directorios, solo para el conteo
                
                for file_name in files:
                    if file_name.startswith("._") or file_name == ".DS_Store": continue
                    source_item_count_for_progress +=1
                    src_file = os.path.join(root_dir, file_name)
                    relative_file = os.path.relpath(src_file, source_root_path)
                    dest_file = os.path.join(destination_root_path, relative_file)
                    if not os.path.exists(dest_file):
                        try:
                            file_size = os.path.getsize(src_file)
                            items_to_copy.append({'type': 'file', 'src': src_file, 'dest': dest_file, 'size': file_size})
                            total_items_to_copy_size += file_size
                        except OSError: pass # Ignorar si no se puede obtener tamaño
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error al listar archivos en origen para sincronizar:\n{e}", parent=self.root))
            self.root.after(0, lambda: self.finalize_copy_ui(success=False, message_override="Error listando archivos (sync).")); return

        try:
            dest_usage = psutil.disk_usage(destination_root_path)
            if total_items_to_copy_size >= dest_usage.free:
                needed_gb = total_items_to_copy_size / (1024**3); free_gb = dest_usage.free / (1024**3)
                msg = (f"Espacio insuficiente en destino '{os.path.basename(destination_root_path)}' para sincronizar.\n"
                       f"Se necesitan: {needed_gb:.2f} GB\nDisponible: {free_gb:.2f} GB\n\nLa sincronización no puede continuar.")
                self.root.after(0, lambda m=msg: messagebox.showerror("Espacio Insuficiente", m, parent=self.root))
                self.root.after(0, lambda: self.finalize_copy_ui(success=False, message_override="Espacio insuficiente (sync).")); return
        except Exception as e:
            self.root.after(0, lambda: messagebox.showwarning("Advertencia Espacio", f"No se pudo verificar el espacio en destino (sync):\n{e}", parent=self.root))

        total_actual_items_to_copy = len(items_to_copy)
        self.root.after(0, lambda: self.progress_files_label.config(text=f"Items: 0/{total_actual_items_to_copy} (de {source_item_count_for_progress} en origen)"))
        
        if total_actual_items_to_copy == 0:
            parent_win = self.progress_window if hasattr(self, 'progress_window') and self.progress_window.winfo_exists() else self.root
            self.root.after(0, lambda: messagebox.showinfo("Info", "No hay nuevos archivos o carpetas para sincronizar.", parent=parent_win))
            self.root.after(0, lambda: self.finalize_copy_ui(success=True, files_copied=0, total_files_attempted=0, message_override="Sincronización: Nada nuevo que copiar.")); return

        copied_items_count = 0; start_time = time.time(); errors_occurred = []; stop_copy_due_to_disk_full = False
        
        for i, item_info in enumerate(items_to_copy):
            if stop_copy_due_to_disk_full: break
            while self.pause_copy_flag.is_set():
                if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return
                time.sleep(0.2)
            if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return

            src_path = item_info['src']
            dest_path = item_info['dest']
            item_type = item_info['type']
            
            self.root.after(0, lambda sp=src_path: self.current_file_label.config(text=f"{os.path.basename(sp)}"))
            
            copied_successfully = False; last_error = None
            try:
                if item_type == 'dir':
                    os.makedirs(dest_path, exist_ok=True)
                    copied_successfully = True
                elif item_type == 'file':
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True) # Asegurar que la carpeta contenedora exista
                    shutil.copy2(src_path, dest_path)
                    copied_successfully = True
            except OSError as e:
                last_error = e
                if e.errno == errno.ENOSPC:
                    self.root.after(0, lambda: self.current_file_label.config(text="¡DISCO LLENO en destino!"))
                    errors_occurred.append(f"Disco lleno al copiar {os.path.basename(src_path)}: {e}")
                    stop_copy_due_to_disk_full = True; copied_successfully = False
                elif e.errno == errno.EACCES:
                    self.root.after(0, lambda sp=src_path: self.current_file_label.config(text=f"Permiso denegado: {os.path.basename(sp)}"))
                    copied_successfully = False
                else:
                     self.root.after(0, lambda sp=src_path: self.current_file_label.config(text=f"Error OS {os.path.basename(sp)}"))
            except Exception as e:
                last_error = e
                self.root.after(0, lambda sp=src_path: self.current_file_label.config(text=f"Fallo {os.path.basename(sp)}"))
            
            if copied_successfully: copied_items_count += 1
            elif not stop_copy_due_to_disk_full: errors_occurred.append(f"Fallo {os.path.basename(src_path)}: {last_error}")

            progress_percent = ((i + 1) / total_actual_items_to_copy) * 100
            elapsed_time = time.time() - start_time; eta_seconds = 0
            if progress_percent > 0 and elapsed_time > 0.1: eta_seconds = (elapsed_time / progress_percent) * (100 - progress_percent)
            eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds)) if eta_seconds > 0 else "--:--";
            self.root.after(0, lambda p=progress_percent, cc=copied_items_count, tc=total_actual_items_to_copy, eta=eta_str: self.update_progress_display(p, cc, tc, eta))

        elapsed_total_time_str = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
        parent_win_msg = self.progress_window if hasattr(self, 'progress_window') and self.progress_window.winfo_exists() else self.root
        dest_label = os.path.basename(destination_root_path)

        if stop_copy_due_to_disk_full:
             msg = (f"SINCRONIZACIÓN INTERRUMPIDA: DISCO LLENO\nItems copiados: {copied_items_count}/{total_actual_items_to_copy}\nA: {dest_label}\nTiempo: {elapsed_total_time_str}")
             self.root.after(0, lambda m=msg: messagebox.showerror("Disco Lleno", m, parent=parent_win_msg))
             self.root.after(0, lambda: self.finalize_copy_ui(success=False, files_copied=copied_items_count, total_files_attempted=total_actual_items_to_copy, message_override="Interrumpido (sync): Disco lleno."))
        elif not errors_occurred:
            msg = (f"SINCRONIZACIÓN COMPLETA\n{copied_items_count}/{total_actual_items_to_copy} items nuevos a {dest_label}\nTiempo: {elapsed_total_time_str}")
            self.root.after(0, lambda m=msg: messagebox.showinfo("Éxito", m, parent=parent_win_msg))
            self.root.after(0, lambda: self.finalize_copy_ui(success=True, files_copied=copied_items_count, total_files_attempted=total_actual_items_to_copy))
        else:
            error_summary = "\n".join(errors_occurred[:2]);
            if len(errors_occurred) > 2: error_summary += f"\n... y {len(errors_occurred)-2} más."
            msg = (f"SINCRONIZACIÓN CON ERRORES\n{copied_items_count}/{total_actual_items_to_copy} a {dest_label}\nErrores:\n{error_summary}\nTiempo: {elapsed_total_time_str}")
            self.root.after(0, lambda m=msg: messagebox.showwarning("Errores", m, parent=parent_win_msg))
            self.root.after(0, lambda: self.finalize_copy_ui(success=False, files_copied=copied_items_count, total_files_attempted=total_actual_items_to_copy))


    def perform_copy_operation(self): # Copia de SD a HDD (original)
        source_path = self.source_device_info["path"]; destination_base_folder = self.target_copy_folder_full_path
        try: os.makedirs(destination_base_folder, exist_ok=True)
        except OSError as e: self.root.after(0, lambda: messagebox.showerror("Error", f"No se pudo crear la carpeta de destino principal:\n{destination_base_folder}\n{e}", parent=self.root)); self.root.after(0, lambda: self.finalize_copy_ui(success=False, message_override="Error creando carpeta destino.")); return

        self.root.after(0, lambda: self.current_file_label.config(text="Calculando tamaño..."))
        files_to_copy = []; total_source_size = 0
        try:
            for root_dir, dirs, files in os.walk(source_path, topdown=True):
                if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['$RECYCLE.BIN', 'System Volume Information']]
                relative_path = os.path.relpath(root_dir, source_path); current_dest_dir = os.path.join(destination_base_folder, relative_path)
                if relative_path != ".":
                    try: os.makedirs(current_dest_dir, exist_ok=True)
                    except OSError as e: print(f"No se pudo crear subdir {current_dest_dir}: {e}"); continue
                for file_name in files:
                    if file_name.startswith("._") or file_name == ".DS_Store": continue
                    src_file = os.path.join(root_dir, file_name); dest_file = os.path.join(current_dest_dir, file_name)
                    files_to_copy.append((src_file, dest_file))
                    try: total_source_size += os.path.getsize(src_file)
                    except OSError: pass
        except Exception as e: self.root.after(0, lambda: messagebox.showerror("Error", f"Error al listar archivos en origen:\n{e}", parent=self.root)); self.root.after(0, lambda: self.finalize_copy_ui(success=False, message_override="Error listando archivos.")); return

        try:
            dest_usage = psutil.disk_usage(self.destination_device_info["path"])
            if total_source_size >= dest_usage.free:
                needed_gb = total_source_size / (1024**3); free_gb = dest_usage.free / (1024**3)
                msg = (f"Espacio insuficiente en destino '{os.path.basename(self.destination_device_info['path'])}'.\nSe necesitan: {needed_gb:.2f} GB\nDisponible: {free_gb:.2f} GB\n\nLa copia no puede continuar.")
                self.root.after(0, lambda m=msg: messagebox.showerror("Espacio Insuficiente", m, parent=self.root))
                self.root.after(0, lambda: self.finalize_copy_ui(success=False, message_override="Espacio insuficiente en destino.")); return
        except Exception as e: self.root.after(0, lambda: messagebox.showwarning("Advertencia Espacio", f"No se pudo verificar el espacio en destino:\n{e}", parent=self.root))

        total_files = len(files_to_copy)
        self.root.after(0, lambda: self.progress_files_label.config(text=f"Archivos: 0/{total_files}"))
        if total_files == 0: parent_win = self.progress_window if hasattr(self, 'progress_window') and self.progress_window.winfo_exists() else self.root; self.root.after(0, lambda: messagebox.showinfo("Info", "No hay archivos para copiar.", parent=parent_win)); self.root.after(0, lambda: self.finalize_copy_ui(success=True, files_copied=0, total_files_attempted=0)); return

        copied_files = 0; start_time = time.time(); errors_occurred = []; stop_copy_due_to_disk_full = False
        for i, (src_file, dest_file) in enumerate(files_to_copy):
            if stop_copy_due_to_disk_full: break
            while self.pause_copy_flag.is_set():
                if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return
                time.sleep(0.2)
            if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return
            self.root.after(0, lambda sf=src_file: self.current_file_label.config(text=f"{os.path.basename(sf)}"))
            retries = 2; copied_successfully = False; last_error = None
            for attempt in range(retries + 1):
                if self.cancel_copy_flag.is_set(): self.root.after(0, self.handle_copy_cancelled); return
                try:
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True); shutil.copy2(src_file, dest_file); copied_successfully = True; break
                except OSError as e:
                    last_error = e
                    if e.errno == errno.ENOSPC: self.root.after(0, lambda: self.current_file_label.config(text=f"¡DISCO LLENO en destino!")); errors_occurred.append(f"Disco lleno al copiar {os.path.basename(src_file)}: {e}"); stop_copy_due_to_disk_full = True; copied_successfully = False; break
                    elif e.errno == errno.EACCES: self.root.after(0, lambda sf=src_file: self.current_file_label.config(text=f"Permiso denegado: {os.path.basename(sf)}")); copied_successfully = False; break
                    if attempt < retries: self.root.after(0, lambda sf=src_file, a=attempt+1: self.current_file_label.config(text=f"Error {os.path.basename(sf)}. Reint. {a+1}")); time.sleep(1)
                    else: self.root.after(0, lambda sf=src_file: self.current_file_label.config(text=f"Fallo {os.path.basename(sf)}"))
                except Exception as e:
                    last_error = e
                    if attempt < retries: self.root.after(0, lambda sf=src_file, a=attempt+1: self.current_file_label.config(text=f"Error {os.path.basename(sf)}. Reint. {a+1}")); time.sleep(1)
                    else: self.root.after(0, lambda sf=src_file: self.current_file_label.config(text=f"Fallo {os.path.basename(sf)}"))
            if copied_successfully: copied_files += 1
            elif not stop_copy_due_to_disk_full: errors_occurred.append(f"Fallo {os.path.basename(src_file)}: {last_error}")
            progress_percent = ((i + 1) / total_files) * 100; elapsed_time = time.time() - start_time; eta_seconds = 0
            if progress_percent > 0 and elapsed_time > 0.1: eta_seconds = (elapsed_time / progress_percent) * (100 - progress_percent)
            eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds)) if eta_seconds > 0 else "--:--"; self.root.after(0, lambda p=progress_percent, cf=copied_files, tf=total_files, eta=eta_str: self.update_progress_display(p, cf, tf, eta))

        elapsed_total_time_str = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)); parent_win_msg = self.progress_window if hasattr(self, 'progress_window') and self.progress_window.winfo_exists() else self.root
        dest_folder_short = f"...{os.path.basename(os.path.dirname(destination_base_folder))}/{os.path.basename(destination_base_folder)}"
        if stop_copy_due_to_disk_full:
             msg = (f"COPIA INTERRUMPIDA: DISCO LLENO\nArchivos copiados: {copied_files}/{total_files}\nDestino: {dest_folder_short}\nTiempo: {elapsed_total_time_str}\nRevise los errores para más detalles.")
             self.root.after(0, lambda m=msg: messagebox.showerror("Disco Lleno", m, parent=parent_win_msg)); self.root.after(0, lambda: self.finalize_copy_ui(success=False, files_copied=copied_files, total_files_attempted=total_files, message_override="Interrumpido: Disco lleno en destino."))
        elif not errors_occurred:
            msg = (f"COPIA COMPLETA\n{copied_files}/{total_files} archivos a {dest_folder_short}\nTiempo: {elapsed_total_time_str}"); self.root.after(0, lambda m=msg: messagebox.showinfo("Éxito", m, parent=parent_win_msg)); self.root.after(0, lambda: self.finalize_copy_ui(success=True, files_copied=copied_files, total_files_attempted=total_files))
        else:
            error_summary = "\n".join(errors_occurred[:2]);
            if len(errors_occurred) > 2: error_summary += f"\n... y {len(errors_occurred)-2} más."
            msg = (f"COPIA CON ERRORES\n{copied_files}/{total_files} a {dest_folder_short}\nErrores:\n{error_summary}\nTiempo: {elapsed_total_time_str}"); self.root.after(0, lambda m=msg: messagebox.showwarning("Errores", m, parent=parent_win_msg)); self.root.after(0, lambda: self.finalize_copy_ui(success=False, files_copied=copied_files, total_files_attempted=total_files))

    def update_progress_display(self, percent, copied_count, total_count, eta_str):
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_bar['value'] = percent
            self.progress_percent_label.config(text=f"{percent:.0f}% | ETA: {eta_str}")
            # Ajustar texto de "Archivos" o "Items" según el modo
            item_label = "Items" if self.is_sync_mode.get() else "Archivos"
            self.progress_files_label.config(text=f"{item_label}: {copied_count}/{total_count}")


    def handle_copy_cancelled(self):
        self.update_status("Operación cancelada.", "warning")
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists(): self.progress_window.destroy()
        
        # Solo intentar borrar destino parcial si NO estamos en modo sync
        if not self.is_sync_mode.get() and hasattr(self, 'target_copy_folder_full_path') and \
           self.target_copy_folder_full_path and os.path.exists(self.target_copy_folder_full_path):
            try:
                is_empty = not any(os.scandir(self.target_copy_folder_full_path)) # Python 3.5+
                if not is_empty:
                    if messagebox.askyesno("Cancelar", "Operación cancelada. ¿Eliminar destino parcial?", parent=self.root):
                        shutil.rmtree(self.target_copy_folder_full_path)
                        self.update_status("Cancelada. Destino parcial eliminado.", "warning")
                else: # Si está vacío, borrarlo sin preguntar
                    shutil.rmtree(self.target_copy_folder_full_path)
                    self.update_status("Cancelada. Destino vacío eliminado.", "warning")
            except Exception as e: self.update_status(f"Cancelada. Error limpiando destino: {e}", "error")
        
        self.finalize_copy_ui(success=False, message_override="Operación cancelada.")


    def finalize_copy_ui(self, success, files_copied=0, total_files_attempted=0, message_override=None):
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists(): self.progress_window.destroy()
        
        op_type = "Sincronización" if self.is_sync_mode.get() else "Copia"
        item_label = "items" if self.is_sync_mode.get() else "archivos"

        if message_override:
            status_level = "warning"
            if "cancelada" in message_override.lower() or "interrumpido" in message_override.lower(): status_level = "warning"
            elif not success and ("error" in message_override.lower() or "fallo" in message_override.lower()): status_level = "error"
            elif success: status_level = "info"
            self.update_status(message_override, status_level)
        elif success: self.update_status(f"{op_type} completada: {files_copied}/{total_files_attempted} {item_label}.", "success")
        else: self.update_status(f"{op_type} con errores: {files_copied}/{total_files_attempted} {item_label}.", "error")
        
        self.source_btn.config(state=tk.NORMAL); self.dest_btn.config(state=tk.NORMAL)
        self.system_menu_button.config(state=tk.NORMAL)
        self.sync_mode_checkbox.config(state=tk.NORMAL) # NUEVO: Reactivar checkbox

        if self.source_device_info and os.path.ismount(self.source_device_info['path']):
            try: usage = psutil.disk_usage(self.source_device_info['path']); self.source_device_info['free_space_gb'] = usage.free / (1024**3); self._display_device_info(self.source_info_label, self.source_device_info, "Origen")
            except: pass
        if self.destination_device_info and os.path.ismount(self.destination_device_info['path']):
            try: usage = psutil.disk_usage(self.destination_device_info['path']); self.destination_device_info['free_space_gb'] = usage.free / (1024**3); self._display_device_info(self.dest_info_label, self.destination_device_info, "Destino")
            except: pass

        if not self.is_sync_mode.get(): # Resetear info de cámara solo si no estamos en sync
            self.copy_date = datetime.date.today(); self.camera_make = "UNTITLED"; self.camera_model = "CAMERA"
        
        self.cancel_copy_flag.clear(); self.pause_copy_flag.clear(); self.copy_thread = None
        self.check_copy_readiness()
        self.toggle_sync_mode_ui() # Para asegurar que los labels estén correctos

    def check_date_conflict(self):
        if self.is_sync_mode.get() or not self.destination_device_info: return True # No hay conflicto de fecha en modo sync
        date_folder_name = self.copy_date.strftime("%Y%m%d")
        potential_date_folder = os.path.join(self.destination_device_info["path"], date_folder_name)
        if os.path.exists(potential_date_folder) and os.path.isdir(potential_date_folder):
            res = messagebox.askyesnocancel("Conflicto de Fecha", f"La carpeta '{date_folder_name}' ya existe.\n¿Continuar (Sí)?\n¿Cambiar fecha (No)?", parent=self.root, icon='warning')
            if res is True: self.update_status(f"Destino: {self.destination_device_info['label']}, Carpeta: {date_folder_name} (existente)", "info"); return True
            elif res is False:
                date_dialog = DatePickerDialog(self.root, "Nueva Fecha de Copia", self.copy_date); self.root.wait_window(date_dialog)
                if date_dialog.result: self.copy_date = date_dialog.result; self.update_status(f"Destino: {self.destination_device_info['label']}, Nueva fecha: {self.copy_date.strftime('%Y%m%d')}", "info"); return True
                else: self.destination_device_info = None; self._display_device_info(self.dest_info_label, None, "Destino"); self.update_status("Destino cancelado.", "warning"); return False
            else: self.destination_device_info = None; self._display_device_info(self.dest_info_label, None, "Destino"); self.update_status("Destino cancelado.", "warning"); return False
        return True

    def extract_camera_info_thread(self):
        if self.is_sync_mode.get() or not self.source_device_info: return # No extraer en modo sync
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

    def get_target_folder_name(self): # Solo para copia SD->HDD
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

    def create_progress_window(self):
        op_title = "Progreso de Sincronización" if self.is_sync_mode.get() else "Progreso de Copia"
        self.progress_window = CustomDialog(self.root, op_title, fixed_height_ratio=0.7)
        self.progress_window.protocol("WM_DELETE_WINDOW", self.confirm_cancel_copy)
        main_frame = self.progress_window.main_frame
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=SCREEN_WIDTH-100, mode="determinate", style="Custom.Horizontal.TProgressbar"); self.progress_bar.pack(pady=(10,5), padx=10, fill=tk.X)
        self.progress_percent_label = ttk.Label(main_frame, text="0% | ETA: --:--:--", style="Dialog.TLabel"); self.progress_percent_label.pack()
        item_label_text = "Items: 0/0" if self.is_sync_mode.get() else "Archivos: 0/0"
        self.progress_files_label = ttk.Label(main_frame, text=item_label_text, style="Dialog.TLabel"); self.progress_files_label.pack()
        current_item_label_text = "Item: N/A" if self.is_sync_mode.get() else "Archivo: N/A"
        self.current_file_label = ttk.Label(main_frame, text=current_item_label_text, style="Dialog.TLabel", wraplength=SCREEN_WIDTH-110); self.current_file_label.pack(pady=5)
        action_button_frame = ttk.Frame(main_frame, style="CustomDialog.TFrame"); action_button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0))
        action_button_frame.columnconfigure(0, weight=1); action_button_frame.columnconfigure(1, weight=1)
        self.pause_resume_button = ttk.Button(action_button_frame, text="Pausar", command=self.toggle_pause_resume, style="Dialog.TButton"); self.pause_resume_button.grid(row=0, column=0, padx=5, sticky="ew")
        cancel_button = ttk.Button(action_button_frame, text="Cancelar", command=self.confirm_cancel_copy, style="Dialog.TButton"); cancel_button.grid(row=0, column=1, padx=5, sticky="ew")

    def toggle_pause_resume(self):
        op_type_past = "Sincronización" if self.is_sync_mode.get() else "Copia"
        if self.pause_copy_flag.is_set():
            self.pause_copy_flag.clear()
            if hasattr(self, 'pause_resume_button') and self.pause_resume_button.winfo_exists(): self.pause_resume_button.config(text="Pausar")
            self.update_status(f"{op_type_past} reanudada.", "info")
        else:
            self.pause_copy_flag.set()
            if hasattr(self, 'pause_resume_button') and self.pause_resume_button.winfo_exists(): self.pause_resume_button.config(text="Reanudar")
            self.update_status(f"{op_type_past} pausada.", "warning")

    def confirm_cancel_copy(self):
        parent_window = self.progress_window if hasattr(self, 'progress_window') and self.progress_window.winfo_exists() else self.root
        op_type_present = "la sincronización" if self.is_sync_mode.get() else "la copia"
        if messagebox.askyesno(f"Cancelar {op_type_present.capitalize()}", f"¿Seguro que cancelas {op_type_present}?", parent=parent_window):
            self.cancel_copy_flag.set()
            if self.pause_copy_flag.is_set(): self.pause_copy_flag.clear()

if __name__ == "__main__":
    root = tk.Tk()
    # root.attributes('-fullscreen', True) # Descomentar para pantalla completa en RPi
    app = ModernCopierApp(root)
    root.mainloop()
