"""
Template para Contratos de Arrendamiento - Nivel Élite
======================================================
Refactorizado para replicar plantilla oficial Inmobiliaria Velar SAS.
Mapeo estricto de campos placeholders y cláusulas legales.

Fecha: 2026-01-25
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from num2words import num2words


from ..components.tables import AdvancedTable
from ..utils.validators import DataValidator
from .base_template import BaseDocumentTemplate


class ContratoArrendamientoElite(BaseDocumentTemplate):
    """
    Generador de contratos de arrendamiento Local Comercial que replica exactamente
    la plantilla PDF oficial de Inmobiliaria Velar.
    
    Características:
    - 25 Cláusulas exactas del formato legal.
    - Cabecera y Pie de página persistentes.
    - Mapeo dinámico de datos (Arrendatario, Inmueble, Codeudor).
    - Arrendador corporativo fijo.
    """

    # Información Fija del Arrendador
    ARRENDADOR_INFO = {
        "nombre": "INMOBILIARIA VELAR S.A.S.",
        "nit": "901703515-7",
        "representante": "CRISTIAN FERNANDO JAMIOY FONSECA",
        "documento_rep": "1.094.959.215",
        "direccion": "Calle 19 No. 16 – 44 Centro Comercial Manhatan Local 15 Armenia, Quindío",
        "telefono": "3011281684",
        "email": "inmobiliariavelarsasaxm@gmail.com"
    }

    # Cláusulas extraídas del PDF
    CLAUSULAS_TEXTO = [
        {
            "titulo": "PRIMERA. OBJETO DEL CONTRATO",
            "texto": "Mediante el presente contrato el ARRENDADOR concede al ARRENDATARIO el goce del inmueble que este tiene que más adelante será identificado con su respectiva dirección, linderos, descripción, matrícula inmobiliaria y ficha catastral, de acuerdo con el inventario que las partes firmaron, y que forma parte integral del contrato."
        },
        {
            "titulo": "SEGUNDA. DIRECCIÓN Y LINDEROS DEL INMUEBLE",
            "texto": "El inmueble objeto del presente contrato se encuentra en el [DIRECCION PREDIO] inmueble se identifica con el folio de matrícula inmobiliaria No. [MATRICULA INMOBILIARIA]."
        },
        {
            "titulo": "TERCERA. DESTINACIÓN",
            "texto": "El ARRENDATARIO se compromete a destinar el inmueble exclusivamente para <b>ESTABLECIMIENTO COMERCIAL</b>, y a no darle uso distinto, ni ceder o subarrendar el inmueble, ni ninguna porción de este sin que medie el consentimiento previo, expreso y escrito por parte del ARRENDADOR.<br/><br/><b>Parágrafo primero</b>: Como consecuencia de la enajenación del establecimiento de comercio, la cesión de este contrato implica para los arrendatarios el cumplimiento previo de los requisitos de los artículos 528 a 530 del Código de Comercio.<br/><br/><b>Parágrafo segundo</b>: Prohibido guardar sustancias explosivas o perjudiciales para la conservación, seguridad o higiene del inmueble."
        },
        {
            "titulo": "CUARTA. CANON DE ARRENDAMIENTO",
            "texto": "El valor acordado por las partes asciende a la suma de [VALOR CANON ARRENDAMIENTO] ([VALOR CANON ARRENDAMIENTO EN TEXTO]), la cual el ARRENDATARIO pagará en su totalidad, dentro de los cinco (5) primeros días calendario de cada período mensual (del 01 al 05 de cada mes), por anticipado, al ARRENDADOR o a su orden.<br/><br/><b>Parágrafo primero</b>: La mera tolerancia del arrendador en aceptar el pago del precio con posterioridad, no se entenderá como ánimo las condiciones del presente.<br/><br/><b>Parágrafo segundo</b>: El incremento para las nuevas vigencias del presente contrato será fijado de común acuerdo entre los contratantes, que el ARRENDATARIO se obliga a pagar dentro de los términos establecidos, sin necesidad de requerimientos privados o judiciales. El reajuste del precio en la cuantía antes señalada tendrá vigencia durante las prórrogas o renovaciones del presente.<br/><br/><b>Parágrafo tercero</b>: Queda a salvo el derecho de las partes contratantes para acordar un nuevo reajuste, acudiendo al procedimiento verbal de que trata el artículo 519 del Código de Comercio, por medio del cual se señala un nuevo valor de arrendamiento mensual, con base en el precio inicialmente pactado, más el precio en caso de renovación del contrato, y en ningún momento el reajuste establecido en el presente."
        },
        {
            "titulo": "QUINTA. TÉRMINO DEL CONTRATO",
            "texto": "El término inicial del presente contrato será de [DIFERENCIA DE MESES FECHA FIN - FECHA INICIO] meses, contados a partir del día [FECHA DE INICIO], hasta el día [FECHA DE FIN].<br/><br/><b>Parágrafo primero</b>: Los contratantes podrán renovarlo por mutuo acuerdo, por un período igual al inicialmente pactado, mediante comunicación escrita por lo menos con un (3) mes de anticipación.<br/><br/><b>Parágrafo segundo</b>: Lo anterior sin perjuicio de lo consagrado en el artículo 518 del Código de Comercio.<br/><br/><b>Parágrafo tercero</b>: En caso de que las partes no se pongan de acuerdo en el momento de la renovación del contrato, cualquiera de ellas podrá recurrir al procedimiento verbal de que trata el artículo 519 del Código de Comercio. Una vez ejecutoriada la sentencia que determine las nuevas condiciones del contrato, tendrán vigencia desde la fecha del vencimiento del preaviso contenido en el parágrafo primero de la presente cláusula. <br/><br/><b>Parágrafo cuarto</b>: Si EL ARRENDATARIO y CODEUDOR no se allanaran a suscribir el nuevo contrato de la forma prevista en el fallo, el ARRENDADOR podrá solicitar la restitución judicial del inmueble."
        },
        {
            "titulo": "SEXTA. LUGAR PARA EL PAGO",
            "texto": "El ARRENDATARIO depositará el canon de arrendamiento al ARRENDADOR en la cuenta del banco Caja social con el número de recaudo No. 15601928 a nombre de Inmobiliaria Velar SAS o través de la pasarela de pagos de PSE, o a través de la generación de un código QR que solicitará a su asesor o como última opción los pagará en la oficina ubicada en la Carrera 19 No. 16-44 Centro Comercial Manhatan Local 15 en Armenia, Quindío."
        },
        {
            "titulo": "SÉPTIMA. MORA",
            "texto": "En caso de mora en el pago del canon mensual, el ARRENDATARIO conocerá al ARRENDADOR un interés de mora equivalente al que a la fecha haya sido decretado por el Gobierno Nacional; interés que deberá ser cancelado al momento del respectivo pago, sin perjuicio de las condiciones del presente o las acciones legales a favor del arrendador."
        },
        {
            "titulo": "OCTAVA. SERVICIOS PÚBLICOS DOMICILIARIOS",
            "texto": "Los servicios públicos domiciliarios como: energía eléctrica, alumbrado público, acueducto, gas, aseo y alcantarillado no se encuentran incluidos en el valor del canon de arrendamiento, y estarán estrictamente a cargo del ARRENDATARIO. No obstante, al momento de entregar el inmueble en arriendo, el ARRENDATARIO le entrega al día el pago de dichos conceptos.<br/><br/><b>Parágrafo primero</b>: Si el ARRENDATARIO no cancelara dichos servicios, y como consecuencia, las respectivas liquidaciones producidas por las correspondientes Empresas los suspendieren y o retiraren los contadores correspondientes, este hecho se tendrá como incumplimiento del contrato, y el ARRENDADOR podrá exigir la restitución judicial del inmueble.<br/><br/><b>Parágrafo segundo</b>: El ARRENDATARIO renuncia expresamente a requerimientos privados o judiciales, y se declaran deudores de toda suma que pague el ARRENDADOR por causa de servicios a su cargo.<br/><br/><b>Parágrafo tercero</b>: El ARRENDADOR no le recibirá el inmueble al ARRENDATARIO, mientras este no le presente un Certificado de Paz y Salvo por concepto de servicios y pago de Impuesto de Industria y Comercio.<br/><br/><b>Parágrafo cuarto</b>: El valor de los derechos fiscales y demás gastos que cause el otorgamiento del presente contrato o de sus prórrogas, correrá por cuenta del ARRENDATARIO."
        },
        {
            "titulo": "NOVENA. MEJORAS",
            "texto": "El ARRENDATARIO declara haber recibido el inmueble a satisfacción. Así, ninguna mejora podrá ser realizada sin la venia del ARRENDADOR. Elaborada sin ella acrecerá inmueble, sin perjuicio de que el ARRENDADOR pueda exigir su retiro.<br/><br/><b>Parágrafo primero</b>: En ningún caso el ARRENDATARIO gozará de derecho de retención del inmueble por mejoras, ni derecho a ser indemnizado.<br/><br/><b>Parágrafo segundo</b>: Está obligado el ARRENDATARIO a efectuar en el inmueble las reparaciones locativas que por Ley le corresponden."
        },
        {
            "titulo": "DÉCIMA. ENDOSO DE DERECHOS",
            "texto": "Podrá el ARRENDADOR en cualquier tiempo transferir sus derechos a un tercero, obligándose los arrendatarios a cumplir sus obligaciones con el cesionario desde la fecha en que tal acto se les comunique por carta certificada o cablegráficamente."
        },
        {
            "titulo": "DÉCIMA PRIMERA. PREAVISOS PARA LA ENTREGA",
            "texto": "Por parte del ARRENDADOR, en los casos previstos en los numerales 2° y 3° del artículo 518 del Código de Comercio, se darán por carta certificada con no menos de seis (6) meses de anticipación, tal y como lo dispone el artículo 520. Por parte del ARRENDATARIO, con no menos de un (1) mes antes del vencimiento del término principal, o de cualquiera de las prórrogas o renovaciones."
        },
        {
            "titulo": "DÉCIMA SEGUNDA. REQUERIMIENTOS",
            "texto": "El ARRENDATARIO y el CODEUDOR manifiestan libre de todo apremio que renuncian a los requerimientos privados o judiciales."
        },
        {
            "titulo": "DÉCIMA TERCERA. ENTREGA / ABANDONO DEL INMUEBLE",
            "texto": "A la finalización del contrato de arrendamiento, las llaves deben ser entregadas al ARRENDADOR el mismo día; en caso de no ser así se da un plazo de diez (10) días. En el evento de que por cualquier causa el inmueble permanezca abandonado o deshabitado, y que la exposición al riesgo sea tal que amenace la integridad física del bien o la seguridad social, transcurridos los diez (10) días, el ARRENDADOR podrá hacer uso del local sin ninguna responsabilidad, y se autoriza el cambio de cerraduras en compañía de dos (2) testigos."
        },
        {
            "titulo": "DÉCIMA CUARTA. TRATAMIENTO DE DATOS PERSONALES Y AUTORIZACIÓN",
            "texto": "En cumplimiento de lo dispuesto en la Ley 1581 de 2012, le informamos que los datos de carácter personal que suministre en virtud del presente contrato de arrendamiento serán objeto de tratamiento por parte de <b>CRISTIAN FERNANDO JAMIOY FONSECA</b> con la finalidad de desarrollar el contrato durante todas las etapas de este y especialmente para: <br/>a) El desarrollo de la relación contractual entre el ARRENDADOR y el ARRENDATARIO.<br/>b) La actualización y consulta de datos personales.<br/>c) El reporte y la consulta de obligaciones ante las centrales de riesgo.<br/>d) La realización de ofertas de asesoría y servicios.<br/>e) La realización de campañas comerciales y de mercado sobre servicios afines al arrendamiento.<br/>f) La medición de niveles de satisfacción.<br/>g) La realización de investigaciones de mercadeo.<br/>h) La confirmación de referencias personales y comerciales de conformidad con la información por usted suministrada.<br/>i) El envío de mensajes en torno al contrato de arrendamiento por medio físico o electrónico (correo electrónico, SMS, FAX, o a cualquier otro medio electrónico o al celular)."
        },
        {
            "titulo": "DÉCIMA QUINTA. CENTRALES DE RIESGO",
            "texto": "El ARRENDATARIO autoriza al ARRENDADOR a reportarlo ante las centrales de riesgo (data-crédito) o (CIFIN), en caso de que exista mora en uno o más cánones de arrendamiento; también en el evento que el ARRENDATARIO se constituya deudor en favor del ARRENDADOR por cualquier concepto proveniente del presente contrato de arrendamiento."
        },
        {
            "titulo": "DÉCIMA SEXTA.  CLÁUSULA PENAL",
            "texto": "El incumplimiento por parte del ARRENDADOR o el ARRENDATARIO de cualquiera de las cláusulas derivadas del presente contrato, lo constituirá en deudor de la parte cumplida, en una suma equivalente a la suma de tres (3) salarios mínimos legales mensuales vigentes, exigibles ejecutivamente."
        },
        {
            "titulo": "DÉCIMA SÉPTIMA. NOTIFICACIONES",
            "texto": "Para todos los efectos judiciales o extrajudiciales, las partes se notificarán en las siguientes direcciones, así: EL ARRENDADOR en el Centro Comercial Manhatan local 15 en Armenia, Quindío; por medio del número de teléfono: 3011281684; y el correo electrónico: inmobiliariavelarsasaxm@gmail.com. EL ARRENDATARIO por medio del número de teléfono [TELEFONO ARRENDATARIO] y el correo electrónico [CORREO ARRENDATARIO], CODEUDOR: por medio del número de teléfono [TELEFONO CODEUDOR] y el correo electrónico [CORREO CODEUDOR] primero. <br/><br/><b>Parágrafo primero</b>: En caso de cambio de alguno de los datos descritos en la cláusula vigésima quinta del presente contrato, las partes se comprometen expresamente a informar por medio escrito para su debida actualización."
        },
    ]

    def __init__(self, output_dir: Path = None):
        super().__init__(output_dir)
        self.document_title = "CONTRATO DE ARRENDAMIENTO DE LOCAL COMERCIAL"
        self.margins = {'top': 60, 'bottom': 80, 'left': 60, 'right': 60}

    def _format_date_spanish(self, date_str: str) -> str:
        """Convierte fecha YYYY-MM-DD a formato 'DD de [MES] de YYYY'"""
        if not date_str:
            return ""
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                     "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            return f"{dt.day} de {meses[dt.month - 1]} de {dt.year}"
        except Exception:
            return date_str
        
    def _header_footer_with_features(self, canvas_obj, doc):
        """
        Override completo para evitar el header por defecto de la empresa (INMOBILIARIA VELAR SAS...)
        que se solapa con el título.
        """
        """
        Override completo para evitar el header por defecto de la empresa (INMOBILIARIA VELAR SAS...)
        que se solapa con el título.
        """
        # 0. Dibujar MEMBRETE (Fondo completo)
        current_dir = Path(__file__).parent
        membrete_path = current_dir / "VELAR INMOBILIARIA_membrete_modificada.png"
        
        try:
            if membrete_path.exists():
                # Dibujar imagen cubriendo toda la página
                page_width, page_height = doc.pagesize
                # mask='auto' maneja transparencias si es PNG
                canvas_obj.drawImage(str(membrete_path), 0, 0, width=page_width, height=page_height, mask='auto', preserveAspectRatio=False)
        except Exception as e:
            # Fallo silencioso o log mínimo para no romper generación
            print(f"Advertencia: No se pudo cargar fondo {membrete_path}: {e}")

        # 1. Agregar marca de agua si aplica (logic from Base)
        if self.watermark_text:
            from ..components.watermarks import Watermark
            Watermark.add_text_watermark(
                canvas_obj,
                text=self.watermark_text,
                opacity=self.watermark_opacity,
                position=self.watermark_style,
            )
            
        # 2. Footer simple (SOLO Página)
        canvas_obj.saveState()
        
        # Página y Timestamp
        page_num = canvas_obj.getPageNumber()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.gray)
        
        center_x = doc.pagesize[0] / 2
        
        # Centrado Página (más abajo que la dirección)
        canvas_obj.drawCentredString(center_x, 20, f"Página {page_num}")
        
        # 4. Textos Verticales en Márgenes
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.lightgrey) # Color tenue para no distraer
        
        from datetime import datetime
        dt_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Margen Izquierdo (Vertical)
        canvas_obj.saveState()
        canvas_obj.translate(30, 250) # Ajustar posición X,Y
        canvas_obj.rotate(90)
        canvas_obj.drawString(0, 0, "Impreso por Inmobiliaria Velar SAS - NIT 901.703.515 - Correo: inmobiliariavelarsasaxm@gmail.com")
        canvas_obj.restoreState()
        
        # Margen Derecho (Vertical)
        canvas_obj.saveState()
        canvas_obj.translate(doc.pagesize[0] - 30, 250)
        canvas_obj.rotate(90)
        canvas_obj.drawString(0, 0, f"Generado: {dt_str}")
        canvas_obj.restoreState()
        
        canvas_obj.restoreState()

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validación estricta para nueva plantilla"""
        # 1. Campos base
        required_base = ["contrato_id", "fecha", "inmueble", "condiciones", "arrendatario", "codeudor", "fecha_inicio", "fecha_fin"]
        
        is_valid, missing = DataValidator.validate_required_fields(data, required_base)
        if not is_valid:
            raise ValueError(f"Faltan campos principales: {', '.join(missing)}")
            
        # 2. Sub-estructuras
        self._require_fields(data["arrendatario"], "nombre", "documento", "telefono", "email")
        self._require_fields(data["codeudor"], "nombre", "documento", "direccion", "telefono", "email")
        
        # Inmueble exige matricula
        self._require_fields(data["inmueble"], "direccion", "matricula_inmobiliaria")
        
        # Validar montos
        if not DataValidator.validate_money_amount(data["condiciones"]["canon"]):
            raise ValueError("Canon inválido")
            
        return True

    def generate(self, data: Dict[str, Any]) -> Path:
        """Generación del contrato"""
        # Configurar template base
        # self.header_content_method ya no es necesario
        
        # Logo Logic - Store for use in header callback
        self.logo_data = data.get("logo_base64")
        
        if data.get("estado") == "borrador":
            self.set_watermark("BORRADOR VELAR SAS", opacity=0.1)
            
        filename = self._generate_filename("contrato_arrendamiento", data["contrato_id"])
        self.create_document(filename, self.document_title)
        
        # 1. Título y Ciudad
        self.add_title_main(self.document_title)
        self.add_paragraph(f"<b>FECHA DE SUSCRIPCIÓN DEL CONTRATO:</b> {self._format_date_spanish(data['fecha'])}", align='CENTER')
        self.add_paragraph("<b>CIUDAD DEL CONTRATO:</b><br/>ARMENIA, QUINDÍO", align='CENTER')
        self.add_spacer(0.4)
        
        # 2. Resumen de Partes (Tabla inicial del PDF)
        self._add_resumen_partes(data)
        
        # 3. Condiciones Generales (Header sección)
        self.add_section_divider("CONDICIONES GENERALES")
        self.story.append(Spacer(1, 10))
        
        # 4. Cláusulas
        self._add_clausulas_reales(data)
        
        # 5. Texto de Cierre Legal
        self.add_paragraph(
            "El presente contrato de arrendamiento se regirá por las normas establecidas en la Ley 820 de 2003... "
            "(ESTO SOLO SI SE TRATA DE PROPIEDAD HORIZONTAL).",
            style_name="Body"
        )
        self.add_spacer(0.2)
        self.add_paragraph(
            f"Para constancia de lo anterior se firma el día {self._format_date_spanish(data['fecha'])}, en dos ejemplares de un mismo tenor literal ordenado por la Ley."
        )
        self.add_spacer(0.5)
        
        # 6. Firmas
        self._add_firmas_tres_columnas(data)
        
        return self.build()

    def _add_resumen_partes(self, data: Dict[str, Any]):
        """Crea el bloque visual de resumen tipo ficha técnica"""
        arrendador = self.ARRENDADOR_INFO
        arrendatario = data['arrendatario']
        codeudor = data['codeudor']
        inmueble = data['inmueble']
        cond = data['condiciones']
        
        # Formato de moneda
        canon_fmt = f"${cond['canon']:,.0f}".replace(",", ".")
        
        # Estilos
        style_label = ParagraphStyle('Label', fontName='Helvetica-Bold', fontSize=9)
        style_val = ParagraphStyle('Val', fontName='Helvetica', fontSize=9)
        
        def p_kw(txt): return Paragraph(f"<b>{txt}</b>", style_label)
        def p_val(txt): return Paragraph(str(txt), style_val)

        # Construcción de filas simulando el layout visual
        # Fila 1: Arrendador bloque completo
        # Fila 1: Arrendador bloque completo
        row_arr = [
            [p_kw("ARRENDADOR:"), p_val(f"{arrendador['nombre']}<br/>NIT: {arrendador['nit']}<br/>REP: {arrendador['representante']}<br/>C.C: {arrendador['documento_rep']}")]
        ]
        
        # Dirección Inmueble
        # Se agrega Municipio y Departamento con salto de línea
        direccion_completa = f"{data['inmueble']['direccion']}<br/>{data['inmueble'].get('municipio', 'ARMENIA')}, {data['inmueble'].get('departamento', 'QUINDÍO')}"
        row_prop = [
            [p_kw("DIRECCIÓN DEL INMUEBLE:"), p_val(direccion_completa)]
        ]
        
        # Canon y Fechas
        row_eco = [
            [p_kw("CANON DE ARRENDAMIENTO:"), p_val(canon_fmt)],
            [p_kw("FECHA DE INICIO:"), p_val(self._format_date_spanish(data['fecha_inicio']))]
        ]
        
        # Duración (Nueva fila solicitada)
        duracion_meses = data.get('duracion', 12)
        row_duracion = [
             [p_kw("DURACIÓN DEL CONTRATO:"), p_val(f"{duracion_meses} Meses")]
        ]
        
        # Arrendatario
        row_user = [
            [p_kw("ARRENDATARIO:"), p_val(f"{arrendatario['nombre']}<br/>C.C. {arrendatario['documento']}")]
        ]
        
        # Codeudor y Fecha Fin
        row_cod = [
            [p_kw("CODEUDOR:"), p_val(f"{codeudor['nombre']}<br/>C.C. {codeudor['documento']}")]
        ]
        row_fin = [
            [p_kw("FECHA DE TERMINACIÓN:"), p_val(self._format_date_spanish(data['fecha_fin']))]
        ]

        # Renderizar cada bloque como mini tabla para control
        # Simplificación: Una tabla grande de 1 columna
        data_table = []
        # 1. DIRECCIÓN DEL INMUEBLE
        data_table.append(row_prop[0])
        # 2. ARRENDADOR
        data_table.append(row_arr[0])
        # 3. ARRENDATARIO
        data_table.append(row_user[0])
        # 4. CODEUDOR
        data_table.append(row_cod[0])
        # 5. CANON
        data_table.append([p_kw("CANON ARRENDAMIENTO:"), p_val(canon_fmt)])
        # 6. INICIO
        data_table.append([p_kw("FECHA DE INICIO DEL CONTRATO:"), p_val(self._format_date_spanish(data['fecha_inicio']))])
        # 7. FIN
        data_table.append([p_kw("FECHA DE TERMINACIÓN DEL CONTRATO:"), p_val(self._format_date_spanish(data['fecha_fin']))])
        # 8. DURACIÓN
        data_table.append(row_duracion[0]) # Agregado

        t = Table(data_table, colWidths=[150, 300])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        self.story.append(t)
        self.add_spacer(0.4)

    def _add_clausulas_reales(self, data: Dict[str, Any]):
        """Itera y reemplaza placeholders en las cláusulas"""
        mapeo = {
            "[DIRECCION PREDIO]": data['inmueble']['direccion'].upper(),
            "[MATRICULA INMOBILIARIA]": data['inmueble']['matricula_inmobiliaria'],
            "[FECHA ACTUAL DEL SISTEMA]": self._format_date_spanish(data['fecha']),
            "[VALOR CANON ARRENDAMIENTO]": f"${data['condiciones']['canon']:,.0f}".replace(",", "."),
            "[FECHA DE INICIO]": self._format_date_spanish(data['fecha_inicio']),
            "[FECHA DE FIN]": self._format_date_spanish(data['fecha_fin']),
            "[NOMBRE ARRENDATARIO]": data['arrendatario']['nombre'].upper(),
            "[NUMERO DE DOCUMENTO]": data['arrendatario']['documento'],
            "[DOCUMENTO ARRENDATARIO]": data['arrendatario']['documento'],
            "[DIRECCION ARRENDATARIO]": data['arrendatario'].get('direccion', 'N/A'),
            "[TELEFONO ARRENDATARIO]": data['arrendatario']['telefono'],
            "[CORREO ARRENDATARIO]": data['arrendatario']['email'],
            "[NOMBRE CODEUDOR]": data['codeudor']['nombre'].upper(),
            "[DOCUMENTO CODEUDOR]": data['codeudor']['documento'],
            "[DIRECCION CODEUDOR]": data['codeudor']['direccion'],
            "[TELEFONO CODEUDOR]": data['codeudor']['telefono'],
            "[CORREO CODEUDOR]": data['codeudor']['email'],
            "[CORREO CODEUDOR]": data['codeudor']['email'],
            "[DIFERENCIA DE MESES FECHA FIN - FECHA INICIO]": str(data['condiciones']['duracion_meses']), # Simplificado, asumimos viene calculado o data raw
            "[VALOR CANON ARRENDAMIENTO EN TEXTO]": num2words(data['condiciones']['canon'], lang='es').upper() + " PESOS M/CTE"
        }

        # Fix placeholder variations
        mapeo["[TELEFONO CODEUDOR]"] = data['codeudor']['telefono']
        mapeo["[CORREO CODEUDOR]"] = data['codeudor']['email']

        for clausula in self.CLAUSULAS_TEXTO:
            titulo = clausula["titulo"]
            texto = clausula["texto"]
            
            # Reemplazar con formato Negrita y Subrayado
            for k, v in mapeo.items():
                if k in texto:
                    replacement = f"<b><u>{v}</u></b>"
                    texto = texto.replace(k, replacement)
            
            # Render
            self.add_heading(titulo, level=2)
            self.add_paragraph(texto, style_name="Body", alignment="justify")
            self.add_spacer(0.15)

    def _add_firmas_tres_columnas(self, data: Dict[str, Any]):
        """Renderiza bloque de 3 firmas"""
        
        arr_info = self.ARRENDADOR_INFO
        arren = data['arrendatario']
        cod = data['codeudor']
        
        style_firma = ParagraphStyle('Firma', fontName='Helvetica', fontSize=8, leading=10, alignment=1) # Center
        
        def firma_bloque(titulo, nombre, doc, dir_contact="", tel=""):
            content = f"<br/><br/>_____________________________<br/><b>{titulo}</b><br/>{nombre}<br/>C.C. {doc}"
            if dir_contact: content += f"<br/>{dir_contact}"
            if tel: content += f"<br/>{tel}"
            return Paragraph(content, style_firma)
            
        # Arrendador
        bloque_1 = firma_bloque(
            "ARRENDADOR", 
            f"INMOBILIARIA VELAR S.A.S.<br/>Rep: {arr_info['representante']}", 
            arr_info['documento_rep'],
            arr_info['direccion'],
            arr_info['telefono']
        )
        
        # Arrendatario
        bloque_2 = firma_bloque(
            "ARRENDATARIO",
            arren['nombre'],
            arren['documento'],
            arren.get('direccion', ''),
            arren['telefono']
        )
        
        # Codeudor
        bloque_3 = firma_bloque(
            "CODEUDOR",
            cod['nombre'],
            cod['documento'],
            cod.get('direccion', ''),
            cod['telefono']
        )
        
        # Tabla de 3 columnas
        tabla_firmas = Table(
            [[bloque_1, bloque_2, bloque_3]], 
            colWidths=[170, 170, 170]
        )
        tabla_firmas.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        
        self.story.append(tabla_firmas)

__all__ = ["ContratoArrendamientoElite"]
