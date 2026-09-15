# Operación local

Antes de descargar modelos, ejecutar `scripts\setup-local.ps1 -BenchmarkOnly`. El script verifica espacio libre, rutas de caché y dependencias. No descargar modelos si el cálculo deja menos de 30 GB libres en `D:`.

El Studio Operator necesita su extra aislado: `python -m pip install -e "apps\api[operator]"`. Instalarlo solo cuando se vaya a probar automatización de ventana con el usuario presente.

Los originales se conservan bajo `data\incoming`; las exportaciones se versionan bajo `artifacts`. Hacer copias de seguridad solo de `data`, `artifacts`, `.env` y `models\manifest.json`; nunca copiar cachés o `node_modules` como respaldo principal.
