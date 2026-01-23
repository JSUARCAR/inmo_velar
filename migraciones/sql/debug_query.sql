
        SELECT 
            m.ID_CONTRATO_M,
            p.ID_PROPIEDAD,
            p.DIRECCION_PROPIEDAD, 
            p.MATRICULA_INMOBILIARIA,
            m.ID_PROPIETARIO,
            per_prop.NOMBRE_COMPLETO as NOMBRE_PROPIETARIO,
            m.ID_ASESOR,
            per_ases.NOMBRE_COMPLETO as NOMBRE_ASESOR,
            m.FECHA_INICIO_CONTRATO_M,
            m.FECHA_FIN_CONTRATO_M,
            m.DURACION_CONTRATO_M,
            m.CANON_MANDATO,
            m.COMISION_PORCENTAJE_CONTRATO_M,
            m.ESTADO_CONTRATO_M,
            m.CREATED_AT,
            m.CREATED_BY
        FROM CONTRATOS_MANDATOS m
        JOIN PROPIEDADES p ON m.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS rp ON m.ID_PROPIETARIO = rp.ID_PROPIEDARIO
        JOIN PERSONAS per_prop ON rp.ID_PERSONA = per_prop.ID_PERSONA
        JOIN ASESORES ra ON m.ID_ASESOR = ra.ID_ASESOR
        JOIN PERSONAS per_ases ON ra.ID_PERSONA = per_ases.ID_PERSONA
        WHERE m.ID_CONTRATO_M = 1
        