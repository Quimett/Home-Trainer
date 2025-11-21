import cv2
import time
import mediapipe as mp
import numpy as np

# Importar las funciones de gestos extendidas
from gestures import (
    brazo_derecho_arriba,
    rodilla_izquierda_flexionada,
    equilibrio_estable,
    extension_adelante,
    inclinacion_lateral,
    elevacion_rodilla,
    postura_ergonomica,
    sentadilla,
    brazos_en_cruz,
    postura_guerrero,
    postura_guerrero_3d,
    salto_detectado
)
from game_logic import Game


def dibujar_skeleton_mejorado(frame, landmarks, connections, mp_pose):
    """Dibuja el esqueleto con colores dinámicos y efectos."""
    tiempo_actual = time.time()
    # Color dinámico
    hue = int((tiempo_actual * 50) % 180)
    color_base = cv2.cvtColor(np.uint8([[[hue, 255, 200]]]), cv2.COLOR_HSV2BGR)[0][0]
    color_landmark = tuple(map(int, color_base))
    
    for connection in connections:
        start_idx = connection[0]
        end_idx = connection[1]
        
        start_point = landmarks[start_idx]
        end_point = landmarks[end_idx]
        
        if start_point.visibility > 0.5 and end_point.visibility > 0.5:
            h, w = frame.shape[:2]
            start = (int(start_point.x * w), int(start_point.y * h))
            end = (int(end_point.x * w), int(end_point.y * h))
            
                # Línea
            cv2.line(frame, start, end, (100, 255, 100), 3, cv2.LINE_AA)
    
            # Dibujar landmarks
    for idx, landmark in enumerate(landmarks):
        if landmark.visibility > 0.5:
            h, w = frame.shape[:2]
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            
            cv2.circle(frame, (cx, cy), 8, color_landmark, -1)
            # Círculo interior
            cv2.circle(frame, (cx, cy), 4, (255, 255, 255), -1)


def dibujar_guias_visuales(frame, game, landmarks, world_landmarks=None):
    """Dibuja guías visuales según el nivel actual."""
    h, w = frame.shape[:2]
    
    # Nivel 1: brazo derecho arriba
    if game.nivel == 1:
        hombro = landmarks[12]
        hombro_pos = (int(hombro.x * w), int(hombro.y * h))
        cv2.arrowedLine(frame, hombro_pos, (hombro_pos[0], hombro_pos[1] - 150), 
                       (0, 255, 255), 3, tipLength=0.3)
        cv2.putText(frame, "ARRIBA", (hombro_pos[0] - 40, hombro_pos[1] - 160), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    # Nivel 4: extensión adelante
    elif game.nivel == 4:
        hombro_i = landmarks[11]
        hombro_d = landmarks[12]
        centro_x = int((hombro_i.x + hombro_d.x) / 2 * w)
        centro_y = int((hombro_i.y + hombro_d.y) / 2 * h)
        
        cv2.circle(frame, (centro_x, centro_y), 60, (255, 200, 0), 3)
        cv2.putText(frame, "EXTIENDE", (centro_x - 60, centro_y - 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
    
    # Nivel 8: sentadilla
    elif game.nivel == 8:
        rodilla_i = landmarks[25]
        rodilla_d = landmarks[26]
        centro_x = int((rodilla_i.x + rodilla_d.x) / 2 * w)
        centro_y = int((rodilla_i.y + rodilla_d.y) / 2 * h)

        cv2.arrowedLine(frame, (centro_x, centro_y - 50), (centro_x, centro_y + 50), 
                       (100, 255, 255), 3, tipLength=0.3)
        cv2.putText(frame, "BAJA", (centro_x - 40, centro_y + 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 255, 255), 2)

    # Nivel 10: Postura del Guerrero
    elif game.nivel == 10:
        # Landmarks relevantes
        hombro_i = landmarks[11]
        hombro_d = landmarks[12]
        cadera_i = landmarks[23]
        cadera_d = landmarks[24]
        rodilla_i = landmarks[25]
        rodilla_d = landmarks[26]
        tobillo_i = landmarks[27]
        tobillo_d = landmarks[28]
        muneca_i = landmarks[15]
        muneca_d = landmarks[16]

        # Determinar qué pierna está delante (usar Z si está disponible)
        if world_landmarks is not None:
            try:
                frente_izq = world_landmarks[25].z < world_landmarks[26].z
            except Exception:
                frente_izq = rodilla_i.x < rodilla_d.x
        else:
            try:
                frente_izq = rodilla_i.z < rodilla_d.z
            except Exception:
                frente_izq = rodilla_i.x < rodilla_d.x

        # Resaltar la pierna adelante
        if frente_izq:
            hip = (int(cadera_i.x * w), int(cadera_i.y * h))
            knee = (int(rodilla_i.x * w), int(rodilla_i.y * h))
            ankle = (int(tobillo_i.x * w), int(tobillo_i.y * h))
        else:
            hip = (int(cadera_d.x * w), int(cadera_d.y * h))
            knee = (int(rodilla_d.x * w), int(rodilla_d.y * h))
            ankle = (int(tobillo_d.x * w), int(tobillo_d.y * h))

        # Pierna adelante: líneas resaltadas
        cv2.line(frame, hip, knee, (0, 200, 255), 4, cv2.LINE_AA)
        cv2.line(frame, knee, ankle, (0, 200, 255), 4, cv2.LINE_AA)
        cv2.circle(frame, ankle, 8, (0, 200, 255), -1)
        cv2.putText(frame, "Pierna adelante", (knee[0] - 60, knee[1] - 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

        # Brazos: guía horizontal a la altura de hombros
        left_sh = (int(hombro_i.x * w), int(hombro_i.y * h))
        right_sh = (int(hombro_d.x * w), int(hombro_d.y * h))
        cv2.line(frame, (left_sh[0] - 80, left_sh[1]), (right_sh[0] + 80, right_sh[1]), (200, 200, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, "Extiende los brazos", (left_sh[0] - 80, left_sh[1] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 0), 2)

        # Torso: recta guía cadera->hombro
        mid_hip = (int((cadera_i.x + cadera_d.x) / 2 * w), int((cadera_i.y + cadera_d.y) / 2 * h))
        mid_sh = (int((hombro_i.x + hombro_d.x) / 2 * w), int((hombro_i.y + hombro_d.y) / 2 * h))
        cv2.line(frame, mid_hip, mid_sh, (150, 255, 150), 2, cv2.LINE_AA)
        cv2.putText(frame, "Torso erguido", (mid_sh[0] - 40, mid_sh[1] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (150, 255, 150), 2)

        # Panel tutorial (izquierda, abajo)
        panel_w, panel_h = 340, 140
        panel_x, panel_y = 20, h - panel_h - 20
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (20, 30, 40), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (100, 200, 255), 2)

        pasos = [
            "1) Da un paso delantero con la pierna que elijas.",
            "2) Dobla la rodilla delantera ~90° (rodilla alineada).",
            "3) Mantén la pierna trasera recta y el talón apoyado.",
            "4) Extiende los brazos a la altura de los hombros.",
            "5) Mantén el torso erguido y mirada al frente."
        ]

        for i, texto in enumerate(pasos):
            y = panel_y + 25 + i * 22
            cv2.putText(frame, texto, (panel_x + 12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), 1)

        # Sugerencia adicional (si detecta profundidad prominente)
        depth_diff = None
        if world_landmarks is not None:
            try:
                depth_diff = abs(world_landmarks[25].z - world_landmarks[26].z)
            except Exception:
                depth_diff = abs(rodilla_i.z - rodilla_d.z)
        else:
            depth_diff = abs(rodilla_i.z - rodilla_d.z)

        if depth_diff > 0.18:
            hint = "Consejo: asegurate de que la rodilla delantera no sobrepase los dedos del pie."
            cv2.putText(frame, hint, (20, h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 120), 1)


def main():
    # === CONFIGURACIÓN ===
    modo_espejo = True
    pantalla_completa = False
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1
    )
    drawing = mp.solutions.drawing_utils
    game = Game()

    window_name = "Home trainer 1.0"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    print("=" * 50)
    print("     Home Trainer 1.0 - Entrenamiento Postural Avanzado")
    print("=" * 50)
    print("\nCONTROLES:")
    print("  ESPACIO    = Comenzar juego")
    print("  1, 2, 3    = Cambiar dificultad (en menú)")
    print("  F          = Pantalla completa")
    print("  R          = Reiniciar (cuando termines)")
    print("  M          = Volver al menú")
    print("  G          = Activar/desactivar guías visuales")
    print("  Q o ESC    = Salir")
    print("\nNUEVOS NIVELES:")
    print("  • 11 niveles de ejercicios variados")
    print("  • Sistema de estrellas (1-3 por nivel)")
    print("  • Múltiples dificultades")
    print("  • Logros desbloqueables")
    print("  • Efectos visuales mejorados")
    print("=" * 50)

    mostrar_guias = True
    altura_referencia_tobillo = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if modo_espejo:
            frame = cv2.flip(frame, 1)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(frame_rgb)
        tiempo = time.time()

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark

            # Dibujar esqueleto mejorado
            dibujar_skeleton_mejorado(frame, landmarks, mp_pose.POSE_CONNECTIONS, mp_pose)

            # Extraer world landmarks 3D si están disponibles
            world_landmarks = None
            if hasattr(result, 'pose_world_landmarks') and result.pose_world_landmarks:
                world_landmarks = result.pose_world_landmarks.landmark

            # Calcular altura de referencia para saltos (nivel 11)
            if game.nivel == 11 and altura_referencia_tobillo is None:
                altura_referencia_tobillo = (landmarks[27].y + landmarks[28].y) / 2

            gesto_ok = False
            nueva_pierna = game.ultima_pierna
            nuevo_lado = game.ultimo_lado

            # Solo detectar gestos si estamos jugando o mostrando instrucciones
            if game.estado in ["jugando", "mostrando_instruccion"]:
                # Dibujar guías visuales si están activadas
                if mostrar_guias:
                    dibujar_guias_visuales(frame, game, landmarks, world_landmarks)

                # === DETECCIÓN DE GESTOS POR NIVEL ===
                if game.nivel == 1:
                    gesto_ok = brazo_derecho_arriba(landmarks, espejo=modo_espejo)

                elif game.nivel == 2:
                    gesto_ok = rodilla_izquierda_flexionada(landmarks, espejo=modo_espejo)

                elif game.nivel == 3:
                    gesto_ok = equilibrio_estable(landmarks)

                elif game.nivel == 4:
                    gesto_ok = extension_adelante(landmarks)

                elif game.nivel == 5:
                    gesto_ok = inclinacion_lateral(landmarks)

                elif game.nivel == 6:
                    gesto_ok, nueva_pierna = elevacion_rodilla(landmarks, game.ultima_pierna)
                    if gesto_ok:
                        game.ultima_pierna = nueva_pierna

                elif game.nivel == 7:
                    gesto_ok = postura_ergonomica(landmarks)

                elif game.nivel == 8:
                    gesto_ok = sentadilla(landmarks)

                elif game.nivel == 9:
                    gesto_ok = brazos_en_cruz(landmarks)

                elif game.nivel == 10:
                    # Usar detección 3D si hay world_landmarks
                    if world_landmarks is not None:
                        gesto_ok, checks_debug = postura_guerrero_3d(world_landmarks, debug=True)
                        # Mostrar debug en pantalla
                        debug_y = 200
                        for check_name, (check_ok, check_val) in checks_debug.items():
                            color = (0, 255, 0) if check_ok else (0, 0, 255)
                            cv2.putText(frame, f"{check_name}: {check_val}", (20, debug_y), 
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                            debug_y += 20
                    else:
                        gesto_ok = postura_guerrero(landmarks)

                elif game.nivel == 11:
                    if altura_referencia_tobillo:
                        gesto_ok = salto_detectado(landmarks, altura_referencia_tobillo)

                # Actualizar el juego
                game.actualizar(gesto_ok, tiempo)
                
                # Resetear altura de referencia si cambiamos de nivel (fuera del nivel 11)
                if game.nivel != 11:
                    altura_referencia_tobillo = None

        # Mostrar interfaz del juego
        game.dibujar_hud(frame)
        game.mostrar_instrucciones(frame)

        # Indicador de guías visuales
        if game.estado == "jugando" and mostrar_guias:
            cv2.putText(frame, "Guias: ON", (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)

        # Ventana de cámara
        cv2.imshow(window_name, frame)

        # === CONTROLES ===
        key = cv2.waitKey(1) & 0xFF
        
        # Salir
        if key in [ord("q"), 27]:
            break
        
        # Comenzar juego desde menú
        if key == ord(" ") and game.estado == "menu":
            game.iniciar_juego()
        
        # Cambiar dificultad en menú
        if game.estado == "menu":
            if key == ord("1"):
                game.cambiar_dificultad("facil")
                print("Dificultad: FÁCIL")
            elif key == ord("2"):
                game.cambiar_dificultad("normal")
                print("Dificultad: NORMAL")
            elif key == ord("3"):
                game.cambiar_dificultad("dificil")
                print("Dificultad: DIFÍCIL")
        
        # Reiniciar juego
        if key == ord("r") and game.estado == "completado":
            game.reiniciar()
            altura_referencia_tobillo = None
        
        # Volver al menú
        if key == ord("m") and game.estado == "completado":
            game.__init__()
            altura_referencia_tobillo = None
        
        # Alternar pantalla completa
        if key in [ord("f"), ord("F")]:
            pantalla_completa = not pantalla_completa
            if pantalla_completa:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                print("Modo pantalla completa activado")
            else:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                print("Modo ventana normal activado")
        
        # Alternar guías visuales
        if key == ord("g") or key == ord("G"):
            mostrar_guias = not mostrar_guias
            print(f"Guías visuales: {'ON' if mostrar_guias else 'OFF'}")

    cap.release()
    cv2.destroyAllWindows()
    
    print("\n¡Gracias por jugar Home Trainer!")
    print(f"Puntuación final: {game.puntos}")
    print(f"Racha máxima: {game.racha_maxima}")
    print(f"Logros desbloqueados: {len(game.logros)}")


if __name__ == "__main__":
    main()
