import tkinter as tk
from tkinter import messagebox
import serial

INTERVALO_MS = 300
TEMP_LIMITE_DEFAULT = 22.0
HISTERESIS_DEFAULT = 2.0

CMD_COOLER_OFF = bytes([0x00])
CMD_COOLER_ON = bytes([0x01])
CMD_LAMPARA_ON = bytes([0x02])
CMD_LAMPARA_OFF = bytes([0x03])


class AppTemperatura:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Temperatura")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.ser = None
        self.temp_actual = None
        self.temp_limite = TEMP_LIMITE_DEFAULT
        self.histeresis = HISTERESIS_DEFAULT
        self.foco_encendido = False
        self.cooler_encendido = False

        self._build_ui()
        self._actualizar()

    def _build_ui(self):
        PAD = dict(padx=20, pady=10)

        tk.Label(
            self.root,
            text="🌡 Monitor de Temperatura",
            font=("Helvetica", 16, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4"
        ).pack(pady=(20, 0))

        frame_temp = tk.Frame(self.root, bg="#313244")
        frame_temp.pack(fill="x", **PAD)

        tk.Label(
            frame_temp,
            text="Temperatura actual",
            font=("Helvetica", 11),
            bg="#313244",
            fg="#a6adc8"
        ).pack(pady=(12, 0))

        self.lbl_temp = tk.Label(
            frame_temp,
            text="--.- °C",
            font=("Helvetica", 48, "bold"),
            bg="#313244",
            fg="#89dceb"
        )
        self.lbl_temp.pack()

        self.lbl_zona = tk.Label(
            frame_temp,
            text="Esperando conexión...",
            font=("Helvetica", 9),
            bg="#313244",
            fg="#6c7086"
        )
        self.lbl_zona.pack(pady=(0, 12))

        frame_estados = tk.Frame(self.root, bg="#1e1e2e")
        frame_estados.pack(fill="x", padx=20, pady=0)

        frame_foco = tk.Frame(frame_estados, bg="#313244")
        frame_foco.pack(side="left", expand=True, fill="both", padx=(0, 8))

        tk.Label(
            frame_foco,
            text="Lámpara",
            font=("Helvetica", 11),
            bg="#313244",
            fg="#a6adc8"
        ).pack(pady=(12, 0))

        self.lbl_foco = tk.Label(
            frame_foco,
            text="● APAGADA",
            font=("Helvetica", 16, "bold"),
            bg="#313244",
            fg="#6c7086"
        )
        self.lbl_foco.pack(pady=(0, 12))

        frame_cooler = tk.Frame(frame_estados, bg="#313244")
        frame_cooler.pack(side="left", expand=True, fill="both", padx=(8, 0))

        tk.Label(
            frame_cooler,
            text="Cooler",
            font=("Helvetica", 11),
            bg="#313244",
            fg="#a6adc8"
        ).pack(pady=(12, 0))

        self.lbl_cooler = tk.Label(
            frame_cooler,
            text="● APAGADO",
            font=("Helvetica", 16, "bold"),
            bg="#313244",
            fg="#6c7086"
        )
        self.lbl_cooler.pack()

        self.btn_cooler = tk.Button(
            frame_cooler,
            text="ENCENDER",
            font=("Helvetica", 11, "bold"),
            bg="#89b4fa",
            fg="#1e1e2e",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            command=self._toggle_cooler
        )
        self.btn_cooler.pack(pady=(6, 12))

        frame_cfg = tk.Frame(self.root, bg="#1e1e2e")
        frame_cfg.pack(fill="x", **PAD)

        tk.Label(
            frame_cfg,
            text="Configuración de la lámpara",
            font=("Helvetica", 11, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4"
        ).pack(anchor="w", pady=(0, 6))

        fila1 = tk.Frame(frame_cfg, bg="#1e1e2e")
        fila1.pack(fill="x", pady=4)

        tk.Label(
            fila1,
            text="Límite (°C):",
            font=("Helvetica", 11),
            bg="#1e1e2e",
            fg="#a6adc8",
            width=14,
            anchor="w"
        ).pack(side="left")

        self.entry_limite = tk.Entry(
            fila1,
            font=("Helvetica", 12),
            width=6,
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat",
            bd=6
        )
        self.entry_limite.insert(0, str(TEMP_LIMITE_DEFAULT))
        self.entry_limite.pack(side="left")

        fila2 = tk.Frame(frame_cfg, bg="#1e1e2e")
        fila2.pack(fill="x", pady=4)

        tk.Label(
            fila2,
            text="Histéresis (°C):",
            font=("Helvetica", 11),
            bg="#1e1e2e",
            fg="#a6adc8",
            width=14,
            anchor="w"
        ).pack(side="left")

        self.entry_histeresis = tk.Entry(
            fila2,
            font=("Helvetica", 12),
            width=6,
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat",
            bd=6
        )
        self.entry_histeresis.insert(0, str(HISTERESIS_DEFAULT))
        self.entry_histeresis.pack(side="left")

        tk.Button(
            frame_cfg,
            text="Aplicar configuración",
            font=("Helvetica", 11, "bold"),
            bg="#89b4fa",
            fg="#1e1e2e",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            command=self._aplicar_config
        ).pack(anchor="w", pady=(10, 0))

        self.lbl_resumen = tk.Label(
            frame_cfg,
            text=self._texto_resumen(),
            font=("Helvetica", 9),
            bg="#1e1e2e",
            fg="#6c7086"
        )
        self.lbl_resumen.pack(anchor="w", pady=(6, 0))

        frame_puerto = tk.Frame(self.root, bg="#1e1e2e")
        frame_puerto.pack(fill="x", **PAD)

        tk.Label(
            frame_puerto,
            text="Puerto serie",
            font=("Helvetica", 11, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4"
        ).pack(anchor="w", pady=(0, 6))

        fila3 = tk.Frame(frame_puerto, bg="#1e1e2e")
        fila3.pack(fill="x")

        self.entry_puerto = tk.Entry(
            fila3,
            font=("Helvetica", 12),
            width=10,
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief="flat",
            bd=6
        )
        self.entry_puerto.insert(0, "COM3")
        self.entry_puerto.pack(side="left", padx=(0, 10))

        self.btn_conectar = tk.Button(
            fila3,
            text="Conectar",
            font=("Helvetica", 11, "bold"),
            bg="#89b4fa",
            fg="#1e1e2e",
            relief="flat",
            bd=0,
            padx=14,
            pady=6,
            command=self._conectar_puerto
        )
        self.btn_conectar.pack(side="left")

        self.lbl_estado = tk.Label(
            self.root,
            text="● Desconectado",
            font=("Helvetica", 9),
            bg="#1e1e2e",
            fg="#f38ba8",
            anchor="w"
        )
        self.lbl_estado.pack(fill="x", padx=20, pady=(10, 16))

    def _texto_resumen(self):
        apaga_en = self.temp_limite + self.histeresis
        return f"Enciende si temp < {self.temp_limite}°C | Apaga si temp > {apaga_en}°C"

    def _conectar_puerto(self):
        puerto = self.entry_puerto.get().strip()

        try:
            self.ser = serial.Serial(
                port=puerto,
                baudrate=9600,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=0
            )

            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

            self.lbl_estado.config(text=f"● Conectado a {puerto}", fg="#a6e3a1")
            self.btn_conectar.config(text="Conectado", state="disabled", bg="#45475a")
            self.entry_puerto.config(state="disabled")

        except serial.SerialException as e:
            self.ser = None
            messagebox.showerror("Error de conexión", f"No se pudo abrir {puerto}\n\n{e}")

    def _leer_temperatura_uart(self):
        if self.ser is None or not self.ser.is_open:
            return None

        try:
            if self.ser.in_waiting <= 0:
                return None

            datos = self.ser.read(self.ser.in_waiting)
            texto = datos.decode(errors="ignore")

            print("RAW:", datos, "HEX:", datos.hex(), "TXT:", repr(texto))

            if not hasattr(self, "buffer_rx"):
                self.buffer_rx = ""

            self.buffer_rx += texto

            while "\n" in self.buffer_rx:
                linea, self.buffer_rx = self.buffer_rx.split("\n", 1)
                linea = linea.strip()

                if linea.isdigit():
                    temp = float(linea)
                    if 0 <= temp <= 99:
                        return temp

            return None

        except Exception as e:
            print("ERROR UART:", e)
            self.lbl_estado.config(text="● Error UART", fg="#f38ba8")
            return None

    def _enviar_comando(self, comando):
        if self.ser is None or not self.ser.is_open:
            return

        try:
            print("ENVIANDO COMANDO:", comando.hex())
            for _ in range(5):
                self.ser.write(comando)
                self.ser.flush()
            
        except serial.SerialException:
            self.lbl_estado.config(text="● Error enviando comando", fg="#f38ba8")

    def _toggle_cooler(self):
        self.cooler_encendido = not self.cooler_encendido

        if self.cooler_encendido:
            self.lbl_cooler.config(text="● ENCENDIDO", fg="#89dceb")
            self.btn_cooler.config(text="APAGAR", bg="#f38ba8", fg="#1e1e2e")
            self._enviar_comando(CMD_COOLER_ON)
        else:
            self.lbl_cooler.config(text="● APAGADO", fg="#6c7086")
            self.btn_cooler.config(text="ENCENDER", bg="#89b4fa", fg="#1e1e2e")
            self._enviar_comando(CMD_COOLER_OFF)

    def _aplicar_config(self):
        try:
            limite = float(self.entry_limite.get())
            histeresis = float(self.entry_histeresis.get())

            if not (0 <= limite <= 99):
                raise ValueError("límite fuera de rango")
            if not (0 <= histeresis <= 10):
                raise ValueError("histéresis fuera de rango")

            self.temp_limite = limite
            self.histeresis = histeresis
            self.lbl_resumen.config(text=self._texto_resumen(), fg="#a6e3a1")

        except ValueError as e:
            messagebox.showerror("Error", f"Valor inválido: {e}")

    def _actualizar(self):
        nueva_temp = self._leer_temperatura_uart()

        if nueva_temp is not None:
            self.temp_actual = nueva_temp

        if self.temp_actual is None:
            self.lbl_temp.config(text="--.- °C", fg="#6c7086")
            self.lbl_zona.config(text="Esperando datos del PIC...")
            self.root.after(INTERVALO_MS, self._actualizar)
            return

        apaga_en = self.temp_limite + self.histeresis

        if self.temp_actual < self.temp_limite:
            color = "#89dceb"
            zona = f"↓ Por debajo del límite ({self.temp_limite}°C) — lámpara encendida"
        elif self.temp_actual <= apaga_en:
            color = "#fab387"
            zona = f"↔ Zona muerta ({self.temp_limite}°C – {apaga_en}°C) — mantiene estado"
        else:
            color = "#a6e3a1"
            zona = f"↑ Por encima de {apaga_en}°C — lámpara apagada"

        self.lbl_temp.config(
            text=f"{self.temp_actual:.1f} °C",
            fg=color
        )
        self.lbl_zona.config(text=zona)

        if self.temp_actual < self.temp_limite:
            self._enviar_comando(CMD_LAMPARA_ON)
            self.foco_encendido = True

        elif self.temp_actual > apaga_en:
            self._enviar_comando(CMD_LAMPARA_OFF)
            self.foco_encendido = False

        self.lbl_foco.config(
            text="● ENCENDIDA" if self.foco_encendido else "● APAGADA",
            fg="#f9e2af" if self.foco_encendido else "#6c7086"
        )

        self.lbl_resumen.config(text=self._texto_resumen())
        self.root.after(INTERVALO_MS, self._actualizar)


if __name__ == "__main__":
    root = tk.Tk()
    app = AppTemperatura(root)
    root.mainloop()