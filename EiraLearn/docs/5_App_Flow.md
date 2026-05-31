# EiraLearn: App Flow & State Management

```mermaid
graph TD
    A[Landing / Login Supabase Auth] --> B[Dashboard Main]
    
    B --> C(Input Híbrido: Pega texto o imagen)
    
    C --> D{Selección de Modo}
    
    D -->|Modo MacGyver| E[Se extraen conceptos, se asigna palabra comodín]
    E --> E1[Usuario redacta síntesis conectando TODO]
    E1 --> E2[Eira Puntúa Nivel de Coherencia y Creatividad]
    
    D -->|Modo Colisión| F[IA analiza texto/imagen]
    F --> F1[Devuelve 2 conceptos aislados + Timer arranca]
    F1 --> F2[Usuario escribe Oración/Solución Híbrida]
    F2 --> F3[Eira valida la lógica inter-disciplinaria]
    
    D -->|Modo Socrático| G[Usuario postula idea inicial]
    G --> G1[Eira devuelve contra-pregunta 1]
    G1 --> G2[Usuario defiende/elabora]
    G2 --> G3{¿Se rinde o llega al núcleo?}
    G3 -->|Más dudas| G1
    G3 -->|Núcleo 100%| G4[Eira cierra con Resumen Magistral]
```

## 🔄 State Management
- **Local State (Zustand o Context):** Para manejar el estado de las sesiones / chats actuales sin estar llamando constantemente a la base de datos y ahorrar ancho de banda.
- **Gestión de Imágenes:** Un estado global pre-almacena el `base64` de la imagen en cliente para renderizar el preview instantáneo antes de la confirmación de subida.
