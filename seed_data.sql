-- Semillas de datos para MuniSmart Cholchol
-- Ejecutar en Supabase SQL Editor

INSERT INTO tickets (created_at, title, description, category, subcategory, status, priority, assigned_department_id, user_id, metadata, location_lat, location_lon, is_indap, requires_social_report)
VALUES
(NOW() - INTERVAL '2 days', 'Solicitud Apoyo Siembra', 'Requiero sacos de semilla de trigo para temporada.', 'Mundo Rural / Agro', 'Apoyo Siembra', 'RECIBIDO', 'MEDIA', 'UDEL (Fomento Productivo)', auth.uid(), '{"sentiment": "Neutro"}', -38.605, -72.855, true, false),
(NOW() - INTERVAL '5 days', 'Camino Intransitable', 'El camino principal de Malalche está cortado por lluvia.', 'Caminos y Obras', 'Reparación Camino', 'EN_PROCESO', 'URGENTE', 'Dirección de Obras', auth.uid(), '{"sentiment": "Negativo"}', -38.610, -72.840, false, false),
(NOW() - INTERVAL '1 hour', 'Basura en sector puente', 'Acumulación de residuos en la entrada del puente.', 'Medio Ambiente', 'Denuncia Ambiental', 'RECIBIDO', 'ALTA', 'Medio Ambiente', auth.uid(), '{"sentiment": "Negativo"}', -38.595, -72.860, false, false),
(NOW() - INTERVAL '10 days', 'Ayuda Social Alimentos', 'Solicito caja de alimentos, adulto mayor sin ingresos.', 'Ayuda Social', 'Asistencia Familiar', 'FINALIZADO', 'ALTA', 'DIDECO (Social)', auth.uid(), '{"sentiment": "Neutro"}', -38.600, -72.850, true, true),
(NOW() - INTERVAL '3 days', 'Ruidos Molestos', 'Vecinos con música alta toda la noche.', 'Seguridad', 'Denuncia Ruidos', 'RECIBIDO', 'BAJA', 'Seguridad Pública', auth.uid(), '{"sentiment": "Negativo"}', -38.602, -72.852, false, false),
(NOW() - INTERVAL '15 days', 'Maquinaria Agrícola', 'Solicitud de tractor para preparar tierra.', 'Mundo Rural / Agro', 'Solicitud Maquinaria', 'FINALIZADO', 'MEDIA', 'UDEL (Fomento Productivo)', auth.uid(), '{"sentiment": "Positivo"}', -38.620, -72.830, true, false),
(NOW() - INTERVAL '1 day', 'Luminaria Quemada', 'Poste fuera de mi casa no enciende.', 'Caminos y Obras', 'Alumbrado Público', 'RECIBIDO', 'MEDIA', 'Dirección de Obras', auth.uid(), '{"sentiment": "Neutro"}', -38.601, -72.848, false, false),
(NOW() - INTERVAL '8 days', 'Microbasural Clanileo', 'Se está formando un basural en cruce Clanileo.', 'Medio Ambiente', 'Denuncia Ambiental', 'EN_PROCESO', 'URGENTE', 'Medio Ambiente', auth.uid(), '{"sentiment": "Negativo"}', -38.590, -72.870, false, false),
(NOW() - INTERVAL '20 days', 'Subsidio Agua Potable', 'Consulta por estado de subsidio.', 'Ayuda Social', 'Subsidio Agua', 'FINALIZADO', 'BAJA', 'DIDECO (Social)', auth.uid(), '{"sentiment": "Neutro"}', -38.615, -72.845, true, true),
(NOW() - INTERVAL '4 days', 'Ronda Policial', 'Robos en el sector rural la semana pasada.', 'Seguridad', 'Ronda Policial', 'EN_PROCESO', 'ALTA', 'Seguridad Pública', auth.uid(), '{"sentiment": "Negativo"}', -38.580, -72.820, false, false),
(NOW() - INTERVAL '6 days', 'Apoyo Fertilizante', 'Solicitud de urea para praderas.', 'Mundo Rural / Agro', 'Apoyo Siembra', 'RECIBIDO', 'MEDIA', 'UDEL (Fomento Productivo)', auth.uid(), '{"sentiment": "Neutro"}', -38.625, -72.835, true, false),
(NOW() - INTERVAL '7 days', 'Árbol Caído', 'Árbol bloquea ruta secundaria.', 'Caminos y Obras', 'Emergencias', 'FINALIZADO', 'ALTA', 'Dirección de Obras', auth.uid(), '{"sentiment": "Negativo"}', -38.608, -72.842, false, false);
