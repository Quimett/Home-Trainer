# Home Trainer 1.0 - Entrenamiento Postural con Visión por Computador

**Asignatura:** Interacción Persona-Máquina  
**Autor:** Joaquín Sigüenza Chilar 
**Fecha:** Noviembre 2025

## Descripción del Proyecto

Home Trainer 1.0 es un videojuego serio desarrollado para la rehabilitación física y el entrenamiento postural mediante visión por computador. Utiliza la librería MediaPipe de Google para detectar la postura corporal del usuario en tiempo real y evaluar la correcta ejecución de 11 ejercicios diferentes de fisioterapia y entrenamiento funcional.

El juego implementa un sistema progresivo de niveles con diferentes ejercicios posturales, desde movimientos básicos como levantar un brazo hasta posturas más complejas como la postura del guerrero de yoga. Incluye un sistema de puntuación con estrellas, feedback visual, guías en pantalla y múltiples niveles de dificultad.

## Requisitos del Sistema

- Python 3.12 recomendado
- Webcam funcional
- Sistema operativo: Windows, macOS o Linux
- Mínimo 4GB de RAM
- Espacio bien iluminado para la detección correcta de la postura

## Instalación

### 1. Clonar o descargar el proyecto

Descomprime el archivo .zip en la ubicación deseada.

### 2. Crear un entorno virtual (recomendado)
```bash
python -m venv venv
```

### 3. Activar el entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

## Estructura del Proyecto
```
home-trainer/
│
├── apli.py              # Archivo principal del juego
├── game_logic.py        # Lógica del juego, HUD y sistema de puntuación
├── gestures.py          # Detección de gestos y posturas
├── utils.py             # Funciones auxiliares (cálculo de ángulos)
├── .gitignore           # Archivos/directorios ignorados por Git  
└── README.md            # Este archivo
```

## Uso

### Ejecución del juego
```bash
python apli.py
```

### Controles

**En el menú principal:**
- `1, 2, 3` - Seleccionar dificultad (Fácil, Normal, Difícil)
- `ESPACIO` - Comenzar el juego

**Durante el juego:**
- `G` - Activar/desactivar guías visuales
- `F` - Pantalla completa
- `M` - Volver al menú (solo al finalizar)
- `R` - Reiniciar (solo al finalizar)
- `Q` o `ESC` - Salir

### Posicionamiento

Para un funcionamiento óptimo:
1. Colócate a 2-3 metros de la cámara
2. Asegúrate de que todo tu cuerpo sea visible en el encuadre
3. Usa iluminación frontal adecuada
4. Evita fondos con mucho movimiento

## Ejercicios Implementados

1. **Nivel 1:** Brazo derecho arriba
2. **Nivel 2:** Flexión de rodilla izquierda
3. **Nivel 3:** Equilibrio estable (mantener X segundos)
4. **Nivel 4:** Extensión de brazos hacia adelante
5. **Nivel 5:** Inclinación lateral
6. **Nivel 6:** Elevación alterna de rodillas
7. **Nivel 7:** Postura ergonómica/erguida (mantener X segundos)
8. **Nivel 8:** Sentadilla
9. **Nivel 9:** Brazos en cruz (T-Pose)
10. **Nivel 10:** Postura del guerrero (Warrior Pose)
11. **Nivel 11:** Salto

## Características Técnicas

### Detección de Poses
- Utiliza MediaPipe Pose para tracking del esqueleto en tiempo real
- Calcula ángulos entre articulaciones para validar posturas
- Detecta profundidad (eje Z) para ejercicios que requieren distancia

### Sistema de Juego
- 3 niveles de dificultad con diferentes duraciones y repeticiones
- Sistema de estrellas (1-3) según velocidad de completado
- Sistema de logros desbloqueables
- Racha de niveles consecutivos
- Feedback visual con partículas y animaciones

### Interfaz
- HUD con información de puntos, estrellas y racha
- Guías visuales animadas para cada ejercicio
- Esqueleto coloreado con efectos dinámicos
- Pantalla de menú y finalización con estadísticas

## Tecnologías Utilizadas

- **OpenCV (cv2):** Captura y procesamiento de vídeo
- **MediaPipe:** Detección de pose corporal en tiempo real
- **NumPy:** Cálculos matemáticos y de ángulos
- **Python:** Lenguaje de programación base
