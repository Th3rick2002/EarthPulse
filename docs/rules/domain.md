# Reglas de dominio

- El MVP usa variables de ciencias de la Tierra con fuente, producto de datos, unidad y definición rastreables.
- Una región se expresa como bbox con orden explícito: `lat_min`, `lat_max`, `lon_min`, `lon_max`; validar rangos y cruces del antimeridiano.
- La serie se agrega a frecuencia mensual para la experiencia MVP. Cada registro conserva fecha, valor y unidad/identidad de origen.
- Para emitir una tendencia válida se requiere al menos un año de cobertura y suficientes observaciones válidas; una consulta no puede superar cincuenta años. Una ausencia no se convierte en cero.
- La significancia MVP usa Mann-Kendall con umbral `p < 0.05`; comunicar que significancia no implica causalidad.
- El resultado incluye pendiente, unidad/periodo de la pendiente, p-value, intervalo temporal, método y una interpretación comprensible.
- La calidad distingue valores observados, interpolados y faltantes. No interpolar silenciosamente ni incluir faltantes en el análisis.
- Diferentes productos/fuentes pueden tener unidades, cobertura y resolución distintas. No mezclarlos sin una transformación documentada.
- Variables y regiones iniciales son catálogo limitado; las regiones personalizadas no deben exceder validaciones de área/cobertura establecidas por el backend.
