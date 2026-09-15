# Entrega MVP local — 2026-09-15

## Qué se entrega

Fashion CAD Studio queda listo para correr **localmente en este equipo Windows** y producir, para sus dos familias MVP, un flujo trazable desde brief hasta archivos técnicos:

- Camiseta unisex regular y bolso para laptop, con revisiones inmutables y operaciones acotadas.
- Análisis determinista de brief; el bolso exige ancho, alto y espesor físicos de la laptop antes de exportar.
- Mockup GLB técnico vinculado a su diseño/revisión, SVG, PDF A4 tiled, PDF A0 y Tech Pack PDF/XLSX.
- Biblioteca local TXT/Markdown/PDF textual con FTS y búsqueda semántica BGE-M3 en LanceDB.
- El índice semántico se reconstruye como trabajo cancelable. Cada rebuild usa una tabla nueva, conserva el índice anterior durante la ejecución y cambia el puntero sólo al finalizar; no acumula duplicados entre rebuilds.
- Studio web y MCP local con superficies limitadas; no exponen shell ni rutas arbitrarias.

## Preflight y verificación

Se requieren Python y Node ya instalados en el equipo. No se descarga ningún peso automáticamente.

```powershell
Set-Location 'D:\Digital Lab\FashionCAD'
Copy-Item .env.example .env -ErrorAction SilentlyContinue
.\scripts\setup-local.ps1
.\scripts\verify-mvp.ps1
```

`verify-mvp.ps1` revisa espacio disponible, ejecuta las pruebas API, compila MCP y Studio web, y ejecuta dos rebuilds reales con el BGE-M3 local en una ruta única bajo `cache\delivery-verification`. No escribe en `data\library` ni altera el índice del usuario. Para una comprobación rápida sin cargar el modelo se puede usar `-SkipModelVerification`, pero no es la validación de entrega completa.

## Arranque

En dos terminales:

```powershell
Set-Location 'D:\Digital Lab\FashionCAD'
.\scripts\run-api.ps1
```

```powershell
Set-Location 'D:\Digital Lab\FashionCAD'
.\scripts\run-web.ps1
```

Abrir `http://127.0.0.1:5173`. La documentación API queda en `http://127.0.0.1:8000/docs`.

## Aceptación manual mínima

1. Crear una camiseta o un bolso; para el bolso ingresar las tres medidas físicas requeridas.
2. Exportar mockup, patrón y Tech Pack, y comprobar que las descargas pertenecen a la misma revisión mostrada.
3. Importar un TXT/MD/PDF textual desde `data\library`, reconstruir el índice BGE-M3 desde el panel Knowledge y esperar el estado `completed`; comprobar una búsqueda semántica con fuente, página y fragmento.
4. Imprimir el patrón de prueba y medir el cuadrado de control: debe medir 100 ± 1 mm antes de cortar o coser.

## Límites que no se deben ocultar

- Esta entrega es local para el equipo configurado, no un instalador portable: Python/Node aún no están empaquetados bajo `runtime`.
- Los patrones y el Tech Pack son borradores técnicos; necesitan prueba física y corrección de patronista/taller antes de producción.
- Studio Operator permanece desactivado. Requiere una prueba Windows supervisada de foco, banner y `Ctrl+Alt+Pause` antes de habilitarlo con aplicaciones reales.
- Qwen-VL, SigLIP2, OCR, voz, Blender, proveedores cloud y túnel MCP no se incluyen: requieren runtimes/pesos/credenciales que no están instalados y no fueron simulados.
