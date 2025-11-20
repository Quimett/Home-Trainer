from utils import calcular_angulo
import numpy as np

UMBRAL_VISIBILIDAD = 0.5

def landmarks_visibles(landmarks, indices):
    """Comprueba visibilidad mínima de los landmarks requeridos."""
    for idx in indices:
        if landmarks[idx].visibility < UMBRAL_VISIBILIDAD:
            return False
    return True


def brazo_derecho_arriba(landmarks, espejo=False):
    """Nivel 1: brazo levantado (ángulo en codo)."""
    indices = [11, 13, 15] if espejo else [12, 14, 16]
    if not landmarks_visibles(landmarks, indices):
        return False
    hombro, codo, muñeca = [landmarks[i] for i in indices]
    ang = calcular_angulo((hombro.x, hombro.y), (codo.x, codo.y), (muñeca.x, muñeca.y))
    return ang < 45


def rodilla_izquierda_flexionada(landmarks, espejo=False):
    """NIVEL 2: Flexión de rodilla izquierda"""
    if espejo:
        indices = [24, 26, 28]
    else:
        indices = [23, 25, 27]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    cadera, rodilla, tobillo = [landmarks[i] for i in indices]
    ang = calcular_angulo((cadera.x, cadera.y), (rodilla.x, rodilla.y), (tobillo.x, tobillo.y))
    return ang < 100


def equilibrio_estable(landmarks):
    """NIVEL 3: Equilibrio en una pierna"""
    indices = [27, 28]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    tobillo_d = landmarks[28]
    tobillo_i = landmarks[27]
    
    return tobillo_d.y < tobillo_i.y - 0.1 or tobillo_i.y < tobillo_d.y - 0.1


def extension_adelante(landmarks):
    """NIVEL 4: Extensión de brazos hacia adelante"""
    indices = [11, 13, 15, 12, 14, 16]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    hombro_i, codo_i, muñeca_i = [landmarks[i] for i in [11, 13, 15]]
    hombro_d, codo_d, muñeca_d = [landmarks[i] for i in [12, 14, 16]]

    ang_i = calcular_angulo((hombro_i.x, hombro_i.y), (codo_i.x, codo_i.y), (muñeca_i.x, muñeca_i.y))
    ang_d = calcular_angulo((hombro_d.x, hombro_d.y), (codo_d.x, codo_d.y), (muñeca_d.x, muñeca_d.y))
    brazos_rectos = ang_i > 140 and ang_d > 140

    manos_adelante = muñeca_i.z < hombro_i.z - 0.1 and muñeca_d.z < hombro_d.z - 0.1
    alturas_similares = abs(muñeca_i.y - muñeca_d.y) < 0.1

    return brazos_rectos and manos_adelante and alturas_similares


def inclinacion_lateral(landmarks):
    """NIVEL 5: Inclinación lateral del torso"""
    indices = [11, 12, 23, 24]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    hombro_i = landmarks[11]
    hombro_d = landmarks[12]
    cadera_i = landmarks[23]
    cadera_d = landmarks[24]

    diff_hombros = abs(hombro_i.y - hombro_d.y)
    diff_caderas = abs(cadera_i.y - cadera_d.y)
    
    return diff_hombros > 0.08 and diff_caderas < 0.06


def elevacion_rodilla(landmarks, ultima_pierna="ninguna"):
    """NIVEL 6: Elevación alterna de rodillas"""
    indices = [23, 25, 27, 24, 26, 28]
    
    if not landmarks_visibles(landmarks, indices):
        return False, ultima_pierna
    
    cadera_i, rodilla_i, tobillo_i = [landmarks[i] for i in [23, 25, 27]]
    cadera_d, rodilla_d, tobillo_d = [landmarks[i] for i in [24, 26, 28]]

    elev_i = rodilla_i.y < cadera_i.y - 0.05
    elev_d = rodilla_d.y < cadera_d.y - 0.05

    if ultima_pierna == "ninguna":
        if elev_i:
            return True, "izquierda"
        elif elev_d:
            return True, "derecha"
    elif ultima_pierna == "izquierda" and elev_d and not elev_i:
        return True, "derecha"
    elif ultima_pierna == "derecha" and elev_i and not elev_d:
        return True, "izquierda"
    
    return False, ultima_pierna


def postura_ergonomica(landmarks):
    """NIVEL 7: Postura erguida y alineada"""
    indices = [11, 23, 25, 27]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    hombro = landmarks[11]
    cadera = landmarks[23]
    rodilla = landmarks[25]
    tobillo = landmarks[27]

    difx1 = abs(hombro.x - cadera.x)
    difx2 = abs(cadera.x - rodilla.x)
    difx3 = abs(rodilla.x - tobillo.x)

    return difx1 < 0.1 and difx2 < 0.1 and difx3 < 0.1


def sentadilla(landmarks):
    """NIVEL 8: Sentadilla (Squat)
    Detecta cuando ambas rodillas están flexionadas y las caderas bajadas.
    """
    indices = [23, 25, 27, 24, 26, 28, 11, 12]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    cadera_i, rodilla_i, tobillo_i = [landmarks[i] for i in [23, 25, 27]]
    cadera_d, rodilla_d, tobillo_d = [landmarks[i] for i in [24, 26, 28]]
    hombro_i, hombro_d = landmarks[11], landmarks[12]
    
    # Ángulos de ambas rodillas
    ang_i = calcular_angulo((cadera_i.x, cadera_i.y), (rodilla_i.x, rodilla_i.y), (tobillo_i.x, tobillo_i.y))
    ang_d = calcular_angulo((cadera_d.x, cadera_d.y), (rodilla_d.x, rodilla_d.y), (tobillo_d.x, tobillo_d.y))
    
    # Ambas rodillas flexionadas (entre 70 y 120 grados)
    rodillas_flexionadas = 70 < ang_i < 120 and 70 < ang_d < 120
    
    # Caderas descendidas (altura de cadera cercana a altura de rodillas)
    cadera_media_y = (cadera_i.y + cadera_d.y) / 2
    rodilla_media_y = (rodilla_i.y + rodilla_d.y) / 2
    hombro_medio_y = (hombro_i.y + hombro_d.y) / 2
    
    caderas_bajas = cadera_media_y > rodilla_media_y - 0.15
    
    return rodillas_flexionadas and caderas_bajas


def estocada(landmarks, ultima_pierna="ninguna"):
    """NIVEL 9: Estocadas alternas (Lunges)
    Detecta cuando una pierna está adelante flexionada y la otra atrás.
    """
    indices = [23, 25, 27, 24, 26, 28]
    
    if not landmarks_visibles(landmarks, indices):
        return False, ultima_pierna
    
    cadera_i, rodilla_i, tobillo_i = [landmarks[i] for i in [23, 25, 27]]
    cadera_d, rodilla_d, tobillo_d = [landmarks[i] for i in [24, 26, 28]]
    
    # Ángulos de rodillas
    ang_i = calcular_angulo((cadera_i.x, cadera_i.y), (rodilla_i.x, rodilla_i.y), (tobillo_i.x, tobillo_i.y))
    ang_d = calcular_angulo((cadera_d.x, cadera_d.y), (rodilla_d.x, rodilla_d.y), (tobillo_d.x, tobillo_d.y))
    
    # Detectar estocada: una rodilla flexionada (60-110°) y diferencia de profundidad
    estocada_i = 60 < ang_i < 110 and rodilla_i.z > rodilla_d.z + 0.1
    estocada_d = 60 < ang_d < 110 and rodilla_d.z > rodilla_i.z + 0.1
    
    # Sistema de alternancia
    if ultima_pierna == "ninguna":
        if estocada_i:
            return True, "izquierda"
        elif estocada_d:
            return True, "derecha"
    elif ultima_pierna == "izquierda" and estocada_d:
        return True, "derecha"
    elif ultima_pierna == "derecha" and estocada_i:
        return True, "izquierda"
    
    return False, ultima_pierna


def brazos_en_cruz(landmarks):
    """NIVEL 10: Brazos en cruz (T-Pose)
    Ambos brazos extendidos horizontalmente a los lados.
    """
    indices = [11, 13, 15, 12, 14, 16]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    hombro_i, codo_i, muñeca_i = [landmarks[i] for i in [11, 13, 15]]
    hombro_d, codo_d, muñeca_d = [landmarks[i] for i in [12, 14, 16]]
    
    # Brazos rectos
    ang_i = calcular_angulo((hombro_i.x, hombro_i.y), (codo_i.x, codo_i.y), (muñeca_i.x, muñeca_i.y))
    ang_d = calcular_angulo((hombro_d.x, hombro_d.y), (codo_d.x, codo_d.y), (muñeca_d.x, muñeca_d.y))
    brazos_rectos = ang_i > 160 and ang_d > 160
    
    # Muñecas a la altura de hombros
    altura_similar_i = abs(muñeca_i.y - hombro_i.y) < 0.1
    altura_similar_d = abs(muñeca_d.y - hombro_d.y) < 0.1
    
    # Brazos extendidos lateralmente (no hacia adelante)
    lateral_i = abs(muñeca_i.z - hombro_i.z) < 0.15
    lateral_d = abs(muñeca_d.z - hombro_d.z) < 0.15
    
    return brazos_rectos and altura_similar_i and altura_similar_d and lateral_i and lateral_d


def elevacion_talones(landmarks):
    """NIVEL 10: Elevación de talones (Calf Raises)
    Detecta cuando la persona se pone de puntillas.
    """
    indices = [23, 25, 27, 24, 26, 28, 29, 30, 31, 32]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    cadera_i, rodilla_i, tobillo_i = [landmarks[i] for i in [23, 25, 27]]
    cadera_d, rodilla_d, tobillo_d = [landmarks[i] for i in [24, 26, 28]]
    
    # Índices de los dedos de los pies y talones
    talon_i, talon_d = landmarks[29], landmarks[30]
    dedo_i, dedo_d = landmarks[31], landmarks[32]
    
    # Piernas rectas (más tolerante)
    ang_i = calcular_angulo((cadera_i.x, cadera_i.y), (rodilla_i.x, rodilla_i.y), (tobillo_i.x, tobillo_i.y))
    ang_d = calcular_angulo((cadera_d.x, cadera_d.y), (rodilla_d.x, rodilla_d.y), (tobillo_d.x, tobillo_d.y))
    piernas_rectas = ang_i > 150 and ang_d > 150
    
    # Método mejorado: comparar talones con dedos de los pies
    # Cuando te pones de puntillas, los talones suben más que los dedos
    altura_talones = (talon_i.y + talon_d.y) / 2
    altura_dedos = (dedo_i.y + dedo_d.y) / 2
    
    # Los talones deben estar MÁS ARRIBA (menor Y) que los dedos
    talones_elevados = altura_talones < altura_dedos - 0.03
    
    # Alternativa: Los tobillos más altos de lo normal
    tobillo_medio_y = (tobillo_i.y + tobillo_d.y) / 2
    cadera_media_y = (cadera_i.y + cadera_d.y) / 2
    
    # Si el tobillo está muy cerca de la cadera (estirado), está de puntillas
    cuerpo_estirado = (cadera_media_y - tobillo_medio_y) > 0.35
    
    return piernas_rectas and (talones_elevados or cuerpo_estirado)


def rotacion_torso(landmarks, ultimo_lado="ninguno"):
    """NIVEL 12: Rotación de torso alterna
    Detecta cuando los hombros rotan respecto a las caderas.
    """
    indices = [11, 12, 23, 24]
    
    if not landmarks_visibles(landmarks, indices):
        return False, ultimo_lado
    
    hombro_i, hombro_d = landmarks[11], landmarks[12]
    cadera_i, cadera_d = landmarks[23], landmarks[24]
    
    # Calcular diferencia de profundidad (eje Z) entre hombros
    diff_z_hombros = hombro_d.z - hombro_i.z
    
    # Rotación hacia la derecha: hombro derecho más adelante
    rotacion_derecha = diff_z_hombros < -0.1
    
    # Rotación hacia la izquierda: hombro izquierdo más adelante
    rotacion_izquierda = diff_z_hombros > 0.1
    
    # Sistema de alternancia
    if ultimo_lado == "ninguno":
        if rotacion_derecha:
            return True, "derecha"
        elif rotacion_izquierda:
            return True, "izquierda"
    elif ultimo_lado == "derecha" and rotacion_izquierda:
        return True, "izquierda"
    elif ultimo_lado == "izquierda" and rotacion_derecha:
        return True, "derecha"
    
    return False, ultimo_lado


def tocar_dedos_pies(landmarks):
    """NIVEL 13: Tocar los dedos de los pies
    Detecta flexión hacia adelante para tocar los pies.
    """
    indices = [11, 12, 15, 16, 23, 24, 27, 28]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    hombro_i, hombro_d = landmarks[11], landmarks[12]
    muñeca_i, muñeca_d = landmarks[15], landmarks[16]
    cadera_i, cadera_d = landmarks[23], landmarks[24]
    tobillo_i, tobillo_d = landmarks[27], landmarks[28]
    
    # Manos cerca de los pies (altura similar)
    altura_manos = (muñeca_i.y + muñeca_d.y) / 2
    altura_pies = (tobillo_i.y + tobillo_d.y) / 2
    
    manos_cerca_pies = altura_manos > altura_pies - 0.2
    
    # Torso inclinado (hombros más abajo que caderas)
    altura_hombros = (hombro_i.y + hombro_d.y) / 2
    altura_caderas = (cadera_i.y + cadera_d.y) / 2
    
    torso_inclinado = altura_hombros > altura_caderas
    
    return manos_cerca_pies and torso_inclinado


def postura_guerrero(landmarks):
    """NIVEL 14: Postura del Guerrero (Yoga Warrior Pose)
    Una pierna adelante flexionada, brazos extendidos, torso erguido.
    """
    indices = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    hombro_i, hombro_d = landmarks[11], landmarks[12]
    codo_i, codo_d = landmarks[13], landmarks[14]
    muñeca_i, muñeca_d = landmarks[15], landmarks[16]
    cadera_i, cadera_d = landmarks[23], landmarks[24]
    rodilla_i, rodilla_d = landmarks[25], landmarks[26]
    
    # Brazos extendidos
    ang_brazo_i = calcular_angulo((hombro_i.x, hombro_i.y), (codo_i.x, codo_i.y), (muñeca_i.x, muñeca_i.y))
    ang_brazo_d = calcular_angulo((hombro_d.x, hombro_d.y), (codo_d.x, codo_d.y), (muñeca_d.x, muñeca_d.y))
    brazos_extendidos = ang_brazo_i > 140 and ang_brazo_d > 140
    
    # Una pierna flexionada
    ang_pierna_i = calcular_angulo((cadera_i.x, cadera_i.y), (rodilla_i.x, rodilla_i.y), (cadera_i.x, rodilla_i.y))
    ang_pierna_d = calcular_angulo((cadera_d.x, cadera_d.y), (rodilla_d.x, rodilla_d.y), (cadera_d.x, rodilla_d.y))
    
    una_pierna_flexionada = (ang_pierna_i < 120) or (ang_pierna_d < 120)
    
    # Diferencia de profundidad entre pies (una adelante, otra atrás)
    diferencia_profundidad = abs(rodilla_i.z - rodilla_d.z) > 0.15
    
    return brazos_extendidos and una_pierna_flexionada and diferencia_profundidad


def postura_guerrero_3d(world_landmarks, debug=False):
    """Detección mejorada 3D de la Postura del Guerrero usando `pose_world_landmarks`.
    Versión SIMPLIFICADA: solo checks esenciales basados en profundidad y altura.
    
    debug: si es True, devuelve (resultado, estado_checks) para diagnosticar
    """
    # Asegurarse de que haya suficientes landmarks
    try:
        hombro_i = world_landmarks[11]
        hombro_d = world_landmarks[12]
        cadera_i = world_landmarks[23]
        cadera_d = world_landmarks[24]
        rodilla_i = world_landmarks[25]
        rodilla_d = world_landmarks[26]
        tobillo_i = world_landmarks[27]
        tobillo_d = world_landmarks[28]
        muneca_i = world_landmarks[15]
        muneca_d = world_landmarks[16]
    except Exception:
        return (False, {}) if debug else False

    # Estado de checks para diagnóstico
    checks = {}

    # CHECK 1: Brazos levantados (altura de muñecas > altura de hombros)
    munecas_levantadas = (muneca_i.y < hombro_i.y) and (muneca_d.y < hombro_d.y)
    checks['brazos_arriba'] = (munecas_levantadas, "✓" if munecas_levantadas else "✗")

    # CHECK 2: Una pierna flexionada (diferencia en Y entre cadera-rodilla-tobillo)
    # Si el tobillo está más abajo que la cadera, la pierna está flexionada
    pierna_i_flex = tobillo_i.y > rodilla_i.y > cadera_i.y
    pierna_d_flex = tobillo_d.y > rodilla_d.y > cadera_d.y
    una_pierna_flexionada = pierna_i_flex or pierna_d_flex
    checks['pierna_flex'] = (una_pierna_flexionada, "✓" if una_pierna_flexionada else "✗")

    # CHECK 3: Diferencia de profundidad significativa (una pierna adelante, otra atrás)
    depth_diff = abs(rodilla_i.z - rodilla_d.z)
    diferencia_profundidad = depth_diff > 0.05  # 5 cm de diferencia
    checks['profundidad'] = (diferencia_profundidad, f"{depth_diff:.3f} m")

    # CHECK 4: Postura separada (cadera ancha)
    cadera_ancho = abs(cadera_i.x - cadera_d.x) > 0.15  # 15 cm entre caderas
    checks['caderas_sep'] = (cadera_ancho, f"{abs(cadera_i.x - cadera_d.x):.3f} m")

    resultado = munecas_levantadas and una_pierna_flexionada and diferencia_profundidad and cadera_ancho
    
    if debug:
        return resultado, checks
    return resultado


def salto_detectado(landmarks, altura_referencia):
    """NIVEL 11: Salto
    Detecta cuando ambos pies se elevan del suelo.
    altura_referencia debe ser la altura media de los tobillos cuando está de pie.
    """
    indices = [27, 28, 25, 26]
    
    if not landmarks_visibles(landmarks, indices):
        return False
    
    tobillo_i, tobillo_d = landmarks[27], landmarks[28]
    rodilla_i, rodilla_d = landmarks[25], landmarks[26]
    
    # Altura actual de los tobillos
    altura_actual = (tobillo_i.y + tobillo_d.y) / 2
    
    # Altura actual de las rodillas
    altura_rodillas = (rodilla_i.y + rodilla_d.y) / 2
    
    # Detección mejorada: 
    # 1. Los tobillos deben estar significativamente más arriba (< 0.06m = 6cm)
    # 2. Las rodillas también deben estar levantadas (flexión para saltar)
    # 3. Umbral más relajado: 0.06 en lugar de 0.08
    
    tobillos_levantados = altura_actual < altura_referencia - 0.06
    rodillas_flexionadas = altura_rodillas < altura_referencia - 0.04
    
    return tobillos_levantados or rodillas_flexionadas