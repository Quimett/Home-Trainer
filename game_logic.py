import cv2
import time
import numpy as np
import random

class Game:
    def __init__(self):
        self.puntos = 0
        self.nivel = 1
        self.estado = "menu"
        self.inicio_nivel = 0
        self.tiempo_gesto = 0
        self.objetivo_activo = False
        self.ultima_pierna = "ninguna"
        self.ultimo_lado = "ninguno"
        self.contador_alternos = 0
        self.juego_completado = False
        
        # Características del juego
        self.dificultad = "normal"  # facil, normal, dificil
        self.estrellas_nivel = []  # Estrellas por nivel (0-3)
        self.tiempo_inicio_nivel = 0
        self.mejor_tiempo = float('inf')
        self.racha_actual = 0
        self.racha_maxima = 0
        self.logros = set()
        self.particulas = []
        
        # Sistema de feedback visual
        self.feedback_texto = ""
        self.feedback_tiempo = 0
        self.feedback_color = (255, 255, 255)
        
        # Trail de movimiento
        self.trail_puntos = []
        self.max_trail = 15
        
        # Configuración según dificultad
        self.configurar_dificultad()

    def configurar_dificultad(self):
        """Ajusta los parámetros según la dificultad"""
        if self.dificultad == "facil":
            self.tiempo_nivel_3 = 2
            self.tiempo_nivel_7 = 3
            self.repeticiones_nivel_6 = 2
            self.repeticiones_nivel_9 = 2
        elif self.dificultad == "normal":
            self.tiempo_nivel_3 = 3
            self.tiempo_nivel_7 = 5
            self.repeticiones_nivel_6 = 3
            self.repeticiones_nivel_9 = 3
        else:  # dificil
            self.tiempo_nivel_3 = 5
            self.tiempo_nivel_7 = 8
            self.repeticiones_nivel_6 = 5
            self.repeticiones_nivel_9 = 4

    def mostrar_menu(self, frame):
        """Pantalla de inicio mejorada"""
        overlay = frame.copy()
        h, w = frame.shape[:2]
        
        # Fondo degradado
        for i in range(h):
            alpha = i / h
            color = (
                int(20 + alpha * 20),
                int(20 + alpha * 30),
                int(40 + alpha * 20)
            )
            cv2.line(overlay, (0, i), (w, i), color, 1)
        
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Título
        titulo = "Home Trainer 1.0"
        self._texto_con_sombra(frame, titulo, (w//2, 120), 
                               cv2.FONT_HERSHEY_DUPLEX, 2.5, (0, 255, 255), 5, centrado=True)
        
        subtitulo = "Entrenamiento Postural Avanzado"
        self._texto_con_sombra(frame, subtitulo, (w//2, 180), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2, centrado=True)
        
        # Selector de dificultad
        y_pos = 250
        self._texto_con_sombra(frame, "Selecciona Dificultad:", (w//2, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 100), 2, centrado=True)
        
        dificultades = [
            ("1 - FACIL", (100, 255, 100)),
            ("2 - NORMAL", (255, 200, 100)),
            ("3 - DIFICIL", (255, 100, 100))
        ]
        
        y_pos = 300
        for i, (texto, color) in enumerate(dificultades):
            if self.dificultad == ["facil", "normal", "dificil"][i]:
                self._texto_con_sombra(frame, f">>> {texto} <<<", (w//2, y_pos), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 3, centrado=True)
            else:
                self._texto_con_sombra(frame, texto, (w//2, y_pos), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2, centrado=True)
            y_pos += 40
        
        # Instrucciones
        y_pos = 460
        self._texto_parpadeante(frame, "Presiona ESPACIO para comenzar", (w//2, y_pos), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (100, 255, 100), 3, centrado=True)
        
        # Estadísticas si hay
        if self.racha_maxima > 0:
            y_pos = 520
            self._texto_con_sombra(frame, f"Racha Maxima: {self.racha_maxima} niveles", 
                                   (w//2, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                                   (180, 180, 255), 2, centrado=True)
        
        # Controles
        y_pos = 580
        self._texto_con_sombra(frame, "F = Pantalla completa  |  Q o ESC = Salir", 
                               (w//2, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                               (150, 150, 150), 2, centrado=True)

    def mostrar_pantalla_final(self, frame):
        """Pantalla de finalización mejorada con estadísticas"""
        overlay = frame.copy()
        h, w = frame.shape[:2]
        
        # Fondo con partículas
        for i in range(50):
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.randint(2, 6)
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            cv2.circle(overlay, (x, y), size, color, -1)
        
        cv2.rectangle(overlay, (0, 0), (w, h), (20, 40, 20), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Título
        titulo = "FELICIDADES"
        self._texto_con_sombra(frame, titulo, (w//2, 80), 
                               cv2.FONT_HERSHEY_DUPLEX, 2.8, (50, 255, 50), 6, centrado=True)
        
        # Puntuación
        puntos_texto = f"Puntuacion Final: {self.puntos}"
        self._texto_con_sombra(frame, puntos_texto, (w//2, 150), 
                               cv2.FONT_HERSHEY_DUPLEX, 1.6, (100, 200, 255), 4, centrado=True)
        
        # Estrellas totales
        estrellas_totales = sum(self.estrellas_nivel)
        estrellas_texto = f"Estrellas: {estrellas_totales}/33"
        self._texto_con_sombra(frame, estrellas_texto, (w//2, 200), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 215, 0), 3, centrado=True)
        
        # Dificultad completada
        dif_texto = f"Dificultad: {self.dificultad.upper()}"
        self._texto_con_sombra(frame, dif_texto, (w//2, 250), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 150, 100), 2, centrado=True)
        
        # Logros desbloqueados
        if len(self.logros) > 0:
            y_pos = 300
            self._texto_con_sombra(frame, "Logros Desbloqueados:", (w//2, y_pos), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 100), 2, centrado=True)
            y_pos = 330
            for logro in list(self.logros)[:3]:  # Mostrar máximo 3
                self._texto_con_sombra(frame, f"* {logro}", (w//2, y_pos), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 255, 180), 2, centrado=True)
                y_pos += 30
        
        # Opciones
        y_pos = h - 120
        self._texto_parpadeante(frame, "Presiona R para reiniciar", (w//2, y_pos), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 200, 100), 2, centrado=True)
        
        y_pos = h - 70
        self._texto_con_sombra(frame, "Presiona M para volver al menu", (w//2, y_pos), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 2, centrado=True)

    def mostrar_instrucciones(self, frame):
        """Instrucciones mejoradas con indicador visual"""
        if self.estado not in ["mostrando_instruccion", "jugando"]:
            return
            
        instrucciones = {
            1: "Levanta el brazo derecho",
            2: "Flexiona la rodilla izquierda",
            3: f"Manten el equilibrio {self.tiempo_nivel_3}s",
            4: "Extiende los brazos hacia adelante",
            5: "Inclinate lateralmente",
            6: f"Eleva las rodillas alternando ({self.repeticiones_nivel_6} veces)",
            7: f"Manten postura recta {self.tiempo_nivel_7}s",
            8: "Realiza una sentadilla",
            9: "Brazos en cruz (T-Pose) 3s",
            10: "Postura del guerrero 4s",
            11: "Salta"
        }
        
        texto = instrucciones.get(self.nivel, "")
        h, w = frame.shape[:2]
        
        # Panel de instrucciones
        altura_cuadro = 120
        overlay = frame.copy()
        
        # Color del borde animado
        tiempo_actual = time.time()
        color_borde = (
            int(100 + 155 * abs(np.sin(tiempo_actual * 2))),
            int(150 + 105 * abs(np.sin(tiempo_actual * 2 + 1))),
            255
        )
        
        cv2.rectangle(overlay, (0, 40), (w, 40 + altura_cuadro), (30, 30, 60), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        cv2.rectangle(frame, (5, 45), (w-5, 40 + altura_cuadro - 5), color_borde, 3)
        
        # Nivel y progreso
        nivel_texto = f"NIVEL {self.nivel}/11"
        self._texto_con_sombra(frame, nivel_texto, (w//2, 75), 
                               cv2.FONT_HERSHEY_DUPLEX, 1.3, (100, 200, 255), 3, centrado=True)
        
        # Barra de progreso de niveles
        barra_x = 50
        barra_y = 95
        barra_w = w - 100
        barra_h = 8
        progreso = self.nivel / 11.0
        
        cv2.rectangle(frame, (barra_x, barra_y), (barra_x + barra_w, barra_y + barra_h), 
                     (50, 50, 50), -1)
        cv2.rectangle(frame, (barra_x, barra_y), 
                     (barra_x + int(barra_w * progreso), barra_y + barra_h), 
                     (100, 255, 100), -1)
        
        # Instrucción
        self._texto_con_sombra(frame, texto, (w//2, 125), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 100), 2, centrado=True)

    def actualizar(self, gesto_detectado, tiempo):
        """Lógica actualizada con 11 niveles"""
        if self.estado in ["menu", "completado"]:
            return
            
        if self.estado == "mostrando_instruccion":
            self.estado = "jugando"
            self.inicio_nivel = tiempo
            self.tiempo_inicio_nivel = tiempo
            self.tiempo_gesto = 0
            self.objetivo_activo = False

        if self.estado == "jugando":
            # Niveles instantáneos
            if self.nivel in [1, 2, 4, 5, 8] and gesto_detectado:
                self._completar_nivel(tiempo, 100)

            # Nivel 6: elevación alterna de rodillas
            elif self.nivel == 6 and gesto_detectado:
                self.contador_alternos += 1
                self.mostrar_feedback("Bien", (100, 255, 100))
                if self.contador_alternos >= self.repeticiones_nivel_6:
                    self._completar_nivel(tiempo, 150)
                    self.contador_alternos = 0

            # Nivel 3: equilibrio
            elif self.nivel == 3:
                self._actualizar_temporizador(gesto_detectado, tiempo, self.tiempo_nivel_3, 150)

            # Nivel 7: postura erguida
            elif self.nivel == 7:
                self._actualizar_temporizador(gesto_detectado, tiempo, self.tiempo_nivel_7, 200)

            # Nivel 9: brazos en cruz
            elif self.nivel == 9:
                self._actualizar_temporizador(gesto_detectado, tiempo, 3, 150)

            # Nivel 10: postura guerrero
            elif self.nivel == 10:
                self._actualizar_temporizador(gesto_detectado, tiempo, 4, 200)

            # Nivel 11: Salto (detección instantánea)
            elif self.nivel == 11 and gesto_detectado:
                self._completar_nivel(tiempo, 150)

    def _actualizar_temporizador(self, gesto_detectado, tiempo, duracion, puntos):
        """Maneja niveles con temporizador"""
        if gesto_detectado:
            if not self.objetivo_activo:
                self.objetivo_activo = True
                self.tiempo_gesto = tiempo
            elif tiempo - self.tiempo_gesto >= duracion:
                self._completar_nivel(tiempo, puntos)
                self.objetivo_activo = False
        else:
            self.objetivo_activo = False

    def _completar_nivel(self, tiempo, puntos_base):
        """Completa un nivel y calcula estrellas"""
        tiempo_nivel = tiempo - self.tiempo_inicio_nivel
        
        # Calcular estrellas (1-3) según velocidad
        if tiempo_nivel < 3:
            estrellas = 3
            multiplicador = 1.5
            self.mostrar_feedback("PERFECTO ***", (255, 215, 0))
        elif tiempo_nivel < 6:
            estrellas = 2
            multiplicador = 1.2
            self.mostrar_feedback("MUY BIEN **", (200, 200, 50))
        else:
            estrellas = 1
            multiplicador = 1.0
            self.mostrar_feedback("COMPLETADO *", (150, 150, 50))
        
        self.estrellas_nivel.append(estrellas)
        puntos_ganados = int(puntos_base * multiplicador)
        self.puntos += puntos_ganados
        self.racha_actual += 1
        self.racha_maxima = max(self.racha_maxima, self.racha_actual)
        
        # Crear partículas de celebración
        self.crear_particulas_exito()
        
        # Logros especiales
        if estrellas == 3:
            self.desbloquear_logro(f"Estrella Nivel {self.nivel}")
        if self.racha_actual >= 5:
            self.desbloquear_logro("Racha de 5")
        
        self.nivel += 1
        if self.nivel > 11:
            self.juego_completado = True
            self.estado = "completado"
            if sum(self.estrellas_nivel) == 33:
                self.desbloquear_logro("PERFECCION TOTAL")
        else:
            self.estado = "mostrando_instruccion"

    def dibujar_hud(self, frame):
        """HUD mejorado con más información"""
        if self.estado == "menu":
            self.mostrar_menu(frame)
            return
            
        if self.estado == "completado":
            self.mostrar_pantalla_final(frame)
            return
        
        h, w = frame.shape[:2]
        
        # Panel superior - Puntos y estrellas
        self._dibujar_panel(frame, 5, 5, 250, 70, (40, 40, 40), (100, 200, 100))
        self._texto_con_sombra(frame, f"PUNTOS: {self.puntos}", (15, 30), 
                               cv2.FONT_HERSHEY_DUPLEX, 0.7, (100, 255, 100), 2)
        
        # Mostrar estrellas del nivel actual si hay
        if len(self.estrellas_nivel) > 0:
            estrellas_texto = "*" * sum(self.estrellas_nivel[-3:])  # Últimas 3
            self._texto_con_sombra(frame, estrellas_texto, (15, 55), 
                                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 215, 0), 2)
        
        # Contador para niveles con alternancia
        if self.nivel == 6:
            self._dibujar_panel(frame, 265, 5, 240, 40, (40, 40, 40), (255, 165, 0))
            self._texto_con_sombra(frame, f"Repeticiones: {self.contador_alternos}/{self.repeticiones_nivel_6}", 
                                   (275, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 200, 100), 2)
        
        # Racha actual
        if self.racha_actual > 0:
            self._dibujar_panel(frame, w - 205, 5, 200, 40, (40, 40, 40), (255, 100, 255))
            self._texto_con_sombra(frame, f"Racha: {self.racha_actual}", 
                                   (w - 195, 30), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 150, 255), 2)
        
        # Temporizador para niveles con duración
        if self.nivel in [3, 7, 9, 10] and self.objetivo_activo:
            duraciones = {3: self.tiempo_nivel_3, 7: self.tiempo_nivel_7, 
                         9: 3, 10: 4}
            self._dibujar_temporizador(frame, duraciones[self.nivel])
        
        # Feedback temporal
        if time.time() - self.feedback_tiempo < 1.5:
            self._mostrar_feedback_actual(frame)
        
        # Dibujar partículas
        self._actualizar_particulas(frame)

    def _dibujar_panel(self, frame, x, y, w, h, color_fondo, color_borde):
        """Dibuja un panel decorativo"""
        overlay = frame.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color_fondo, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color_borde, 2)

    def _dibujar_temporizador(self, frame, tiempo_objetivo):
        """Dibuja barra de progreso de temporizador"""
        h, w = frame.shape[:2]
        tiempo_transcurrido = min(int(time.time() - self.tiempo_gesto), tiempo_objetivo)
        progreso = tiempo_transcurrido / tiempo_objetivo
        
        x_inicio = w - 250
        y_pos = 10
        ancho_barra = 230
        alto_barra = 35
        
        self._dibujar_panel(frame, x_inicio, y_pos, ancho_barra, alto_barra, 
                           (40, 40, 40), (100, 100, 255))
        
        # Relleno de progreso con gradiente
        ancho_progreso = int((ancho_barra - 4) * progreso)
        if progreso < 0.33:
            color_progreso = (0, 100, 255)
        elif progreso < 0.66:
            color_progreso = (0, 200, 255)
        else:
            color_progreso = (0, 255, 150)
            
        cv2.rectangle(frame, (x_inicio + 2, y_pos + 2), 
                     (x_inicio + 2 + ancho_progreso, y_pos + alto_barra - 2), 
                     color_progreso, -1)
        
        # Texto del tiempo
        self._texto_con_sombra(frame, f"{tiempo_transcurrido}/{tiempo_objetivo}s", 
                               (x_inicio + ancho_barra//2 - 20, y_pos + 25), 
                               cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)

    def mostrar_feedback(self, texto, color):
        """Muestra feedback temporal"""
        self.feedback_texto = texto
        self.feedback_color = color
        self.feedback_tiempo = time.time()

    def _mostrar_feedback_actual(self, frame):
        """Renderiza el feedback actual"""
        h, w = frame.shape[:2]
        alpha = 1.0 - (time.time() - self.feedback_tiempo) / 1.5
        if alpha > 0:
            escala = 1.5 + (1 - alpha) * 0.5
            color = tuple(int(c * alpha) for c in self.feedback_color)
            self._texto_con_sombra(frame, self.feedback_texto, (w//2, h//2 - 100), 
                                   cv2.FONT_HERSHEY_DUPLEX, escala, color, 3, centrado=True)

    def crear_particulas_exito(self):
        """Crea partículas de celebración"""
        for _ in range(20):
            self.particulas.append({
                'x': random.randint(0, 640),
                'y': random.randint(0, 480),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-5, -1),
                'vida': 60,
                'color': (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            })

    def _actualizar_particulas(self, frame):
        """Actualiza y dibuja partículas"""
        particulas_activas = []
        for p in self.particulas:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.2  # Gravedad
            p['vida'] -= 1
            
            if p['vida'] > 0:
                alpha = p['vida'] / 60
                size = int(4 * alpha)
                if size > 0:
                    cv2.circle(frame, (int(p['x']), int(p['y'])), size, p['color'], -1)
                particulas_activas.append(p)
        
        self.particulas = particulas_activas

    def desbloquear_logro(self, nombre):
        """Desbloquea un logro"""
        if nombre not in self.logros:
            self.logros.add(nombre)
            self.mostrar_feedback(f"Logro: {nombre}", (255, 215, 0))

    def cambiar_dificultad(self, nueva_dif):
        """Cambia la dificultad"""
        self.dificultad = nueva_dif
        self.configurar_dificultad()

    def reiniciar(self):
        """Reinicia el juego manteniendo estadísticas"""
        racha_max = self.racha_maxima
        logros = self.logros.copy()
        dif = self.dificultad
        
        self.__init__()
        self.racha_maxima = racha_max
        self.logros = logros
        self.dificultad = dif
        self.configurar_dificultad()

    def iniciar_juego(self):
        """Inicia el juego desde el menú"""
        self.estado = "mostrando_instruccion"

    def _texto_con_sombra(self, frame, texto, pos, fuente, escala, color, grosor, centrado=False):
        """Dibuja texto con sombra"""
        x, y = pos
        if centrado:
            (ancho_texto, alto_texto), _ = cv2.getTextSize(texto, fuente, escala, grosor)
            x = x - ancho_texto // 2
        cv2.putText(frame, texto, (x + 2, y + 2), fuente, escala, (0, 0, 0), grosor + 1)
        cv2.putText(frame, texto, (x, y), fuente, escala, color, grosor)

    def _texto_parpadeante(self, frame, texto, pos, fuente, escala, color, grosor, centrado=False):
        """Dibuja texto parpadeante"""
        if int(time.time() * 2) % 2 == 0:
            self._texto_con_sombra(frame, texto, pos, fuente, escala, color, grosor, centrado)