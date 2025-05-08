def refresh_device_list_and_select(self, device_type):
    self.update_status(f"Refrescando lista de dispositivos...", "info")
    devices = self.get_usb_devices() # get_usb_devices ya tiene validación de montaje
    if not devices:
        messagebox.showinfo("Sin dispositivos", "No se detectaron dispositivos USB montados.", parent=self.root)
        self.update_status(f"No se encontraron dispositivos.", "warning")
        return

    current_selection = None
    if device_type == 'source':
        current_selection = self.source_device_info
        title = "Refrescar y Seleccionar Origen"
    else: # 'destination'
        current_selection = self.destination_device_info
        title = "Refrescar y Seleccionar Destino"

    dialog = DeviceSelectionDialog(self.root, title, devices)
    # Preseleccionar el dispositivo actual si aún está en la lista
    if current_selection:
        try:
            idx = [d['path'] for d in devices].index(current_selection['path'])
            dialog.listbox.selection_set(idx)
            dialog.listbox.activate(idx)
        except ValueError:
            pass # El dispositivo anterior ya no está

    self.root.wait_window(dialog)
    selected_dev = dialog.result

    if selected_dev:
        if device_type == 'source':
            if self.destination_device_info and selected_dev['path'] == self.destination_device_info['path']:
                messagebox.showwarning("Advertencia", "Origen y destino no pueden ser iguales.", parent=self.root)
                return
            self.source_device_info = selected_dev
            self._display_device_info(self.source_info_label, self.source_device_info, "Origen")
            self.update_status(f"Origen: {self.source_device_info['label']}", "info")
            threading.Thread(target=self.extract_camera_info_thread, daemon=True).start()
        else: # 'destination'
            if self.source_device_info and selected_dev['path'] == self.source_device_info['path']:
                messagebox.showwarning("Advertencia", "Origen y destino не pueden ser iguales.", parent=self.root)
                return
            self.destination_device_info = selected_dev
            self._display_device_info(self.dest_info_label, self.destination_device_info, "Destino")
            self.update_status(f"Destino: {self.destination_device_info['label']}", "info")
            self.check_date_conflict()
    
    self.check_copy_readiness()
    if not selected_dev: # Si el usuario canceló el diálogo de refresco
         self.update_status(f"Selección de {device_type} no cambiada.", "info")
