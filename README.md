### Modularizacion 1/3/26

#### ✅ Fase 1 — Modularización

- Separar core / ui / state / config.

#### ✅ Fase 2 — Corrección de imports

- Arreglar estructura de módulos y ejecución.

#### ✅ Fase 3 — Reconstrucción del layout

- Eliminar duplicaciones, estabilizar canvas y panel.

#### ✅ Fase 4 — Reconectar controles

- Botones, guardado, notificaciones, panel MATCH.

### Siguientes Fases

#### 🔶 Fase 5 — Estabilidad profesional

- Objetivo: que no se rompa nunca.
- Manejo robusto de errores al cargar imagen
- Validación si carpeta no tiene imágenes
- Protección contra doble guardado
- Protección contra estado vacío
- Logging interno (archivo .log)
- Esto es “modo herramienta confiable”.

#### 🔶 Fase 6 — Rendimiento

- Aquí entramos en lo que tú realmente querías mejorar:
- Optimizar render del canvas
- Evitar recalcular thumbnails innecesarios
- Cargar imágenes lazy
- Cachear imágenes en memoria
- Evitar freeze cuando hay muchas imágenes
- Esto convierte el visor en algo rápido de verdad.

#### 🔶 Fase 7 — UX avanzada

- Zoom con rueda
- Arrastrar imagen
- Crop con proporción fija opcional
- Mostrar dimensiones del crop
- Historial de crops
- Atajos de teclado configurables
- Esto lo vuelve herramienta seria.

#### 🔶 Fase 8 — Arquitectura 2.0

- Aquí es donde se vuelve profesional de verdad:
- Separar completamente lógica UI de lógica de imagen
- EventBus interno
- Sistema de plugins
- Tests automáticos
- Build como .exe limpio
- Esto es cuando deja de ser MVP y se vuelve producto.

#### 🔶 Fase 9 — Monetización / Producto

- Aquí entramos en visión estratégica (lo que realmente importa):
- Versión gratuita limitada
- Versión Pro con funciones extra
- Marca propia
- Página web de descarga
- Telemetría opcional
- Licenciamiento


---

### 1️⃣ Problema que Resuelve

#### 📌 Problema Principal: Tiempo

El flujo manual actual para generar portadas implica:

- Entrar a carpeta madre  
- Entrar a subcarpeta  
- Elegir una imagen  
- Abrirla en el visor  
- Usar herramienta de recorte de Windows  
- Guardar manualmente  
- Escribir número manual (1,2,3,4…500)  
- Repetir proceso  

Este flujo toma entre **15 y 25 segundos por imagen**.

#### Escenarios reales

- 500 imágenes = 2–3 horas  
- 100 carpetas madre = días completos de trabajo repetitivo  

El problema no es técnico, es de flujo ineficiente.

---

### 2️⃣ Problema de Flujo que Sustituye

El proceso manual actual tiene:

- Cambio constante de ventanas  
- Escritura manual de nombres  
- Uso de herramienta externa  
- Movimiento repetitivo innecesario  
- Carga cognitiva por repetición  

#### VISOR CROP MVP reemplaza todo eso por:

Nuevo flujo:

1. Seleccionar carpeta madre (una vez)  
2. Click en subcarpeta  
3. Click en imagen  
4. Ajustar rectángulo con mouse  
5. Presionar `S`  
6. Se guarda automáticamente  
7. Avanza a siguiente imagen  

Sin escribir nombres.  
Sin usar herramienta de recorte externa.  
Sin cambiar de ventana.  
Sin renombrar manualmente.

---

### 3️⃣ Arquitectura del Programa

#### Lenguaje

- Python

#### Librerías

- Tkinter → Interfaz gráfica  
- Pillow → Manipulación de imágenes  
- PyInstaller → Generación de ejecutable `.exe`  

---

### 4️⃣ Arquitectura Visual

Interfaz dividida en dos niveles:

#### Nivel Superior

**VISOR (50% pantalla)**

- Muestra imagen seleccionada  
- Aplica overlay oscuro  
- Muestra rectángulo RP claro  
- Permite arrastrar verticalmente el rectángulo  

#### Nivel Inferior

Panel izquierdo → **CM**  
Panel derecho → **IMG**

##### CM:
Lista de subcarpetas dentro de la carpeta madre

##### IMG:
Lista de imágenes dentro de la subcarpeta seleccionada

---

### 5️⃣ Lógica del Rectángulo (RP)

#### Características

- Proporción 16:9  
- 80% del ancho de la imagen  
- Centrado horizontalmente  
- Posición vertical arrastrable con mouse  
- Limitado a no salir de la imagen  

#### Efecto visual

- Imagen completa oscurecida  
- Área del rectángulo en color natural  
- Borde rojo visible  

Esto genera una guía visual clara para el recorte.

---

### 6️⃣ Sistema de Guardado Automático

Al presionar la tecla `S`:

- Se recorta exactamente la zona del RP  
- Se guarda en formato JPG  
- Se numera automáticamente:
  - `1.jpg`
  - `2.jpg`
  - `3.jpg`

- Avanza automáticamente a la siguiente imagen  

---

### 7️⃣ Organización de Salida

Dentro de cada carpeta madre se crea automáticamente:

CarpetaMadre/
├─ Subcarpeta1/
├─ Subcarpeta2/
├─ [AAA/
├─ 1.jpg
├─ 2.jpg
├─ 3.jpg


El símbolo `[` garantiza que la carpeta quede en la primera posición.

#### El contador:

- Se reinicia automáticamente por cada carpeta madre  

---

### 8️⃣ Qué Hace Actualmente la Versión MVP

✔ Selección de carpeta madre  
✔ Listado automático de subcarpetas  
✔ Listado automático de imágenes  
✔ Visualización con overlay oscuro  
✔ Rectángulo 16:9 automático  
✔ Arrastre vertical con mouse  
✔ Guardado con tecla `S`  
✔ Numeración automática  
✔ Avance automático de imagen  
✔ Creación automática de carpeta `[AAA`  
✔ Reinicio de contador por carpeta madre  
✔ Ejecutable Windows (`.exe`)  

---

### 9️⃣ Impacto en Productividad

#### Antes

15–25 segundos por imagen  

#### Ahora

2–4 segundos por imagen  

#### Ahorro estimado

70% – 85% del tiempo total  

En escenarios grandes:

Días de trabajo → Horas  

---

### 🔟 Tipo de Herramienta

Esta no es una aplicación comercial.  
Es una herramienta interna de automatización de flujo.  
Diseñada para eliminar fricción operativa repetitiva.

---

### 1️⃣1️⃣ Posibles Mejoras Futuras

- Zoom con rueda del mouse  
- Mostrar contador actual en pantalla  
- Barra de progreso  
- Ajuste de opacidad del overlay  
- Soporte para múltiples proporciones  
- Guardado por subcarpeta  
- Vista previa tamaño final WordPress  

---

### 1️⃣2️⃣ Estado Actual

- Versión: MVP funcional  
- Enfoque: Productividad inmediata  
- Objetivo: Reducción drástica de tiempo manual  

---
