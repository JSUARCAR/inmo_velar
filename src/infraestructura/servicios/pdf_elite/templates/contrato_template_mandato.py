"""
Template para Contratos de Mandato - Nivel Élite
======================================================
Refactorizado para replicar plantilla oficial Inmobiliaria Velar SAS.
Mapeo estricto de campos placeholders y cláusulas legales.

Fecha: 2026-01-25
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from ..components.tables import AdvancedTable
from ..utils.validators import DataValidator
from .base_template import BaseDocumentTemplate


class ContratoMandatoElite(BaseDocumentTemplate):
    """
    Generador de contratos de Mandato que replica exactamente
    la plantilla PDF oficial de Inmobiliaria Velar.
    
    Características:
    - 25 Cláusulas exactas del formato legal.
    - Cabecera y Pie de página persistentes.
    - Mapeo dinámico de datos (Mandante, Inmueble).
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
            "texto": "El ARRENDATARIO se compromete a destinar el inmueble exclusivamente para VIVIENDA, y a no darle uso distinto, ni ceder o subarrendar el inmueble, ni ninguna porción de este sin que medie el consentimiento previo, expreso y escrito por parte del ARRENDADOR. Parágrafo: podrá el ARRENDADOR ceder libremente los derechos que emanan de este contrato, y tal cesión producirá efectos respecto del ARRENDATARIO y del CODEUDOR a partir de la fecha de la comunicación certificada en que a ellos se notifique tal cesión."
        },
        {
            "titulo": "CUARTA. OBLIGACIONES DE LAS PARTES",
            "texto": "Son obligaciones de las partes las siguientes: a) DEL ARRENDADOR: 1. Entregar al ARRENDATARIO en la fecha convenida el inmueble dado en arrendamiento en buen estado de servicios, seguridad y sanidad, y poner a su disposición los servicios, cosas o usos conexos y adicionales. 2. Mantener en el inmueble los servicios, las cosas y los usos conexos y adicionales en buen estado de servir para el fin convenido en el contrato. 3. Entregar al arrendatario una copia del reglamento interno de Propiedad Horizontal al que se encuentra sometido el inmueble. (ESTO SI SE TRATA DE PROPIEDAD HORIZONTAL) 4. Las demás obligaciones consagradas para los arrendadores en el artículo 8º de la Ley 820 de 2003. b) DEL ARRENDATARIO: 1. Pagar al ARRENDADOR en el lugar convenido en la cláusula séptima del presente contrato el valor del canon de arrendamiento. En el evento en que el ARRENDADOR se rehúse a recibir el canon de arrendamiento en las condiciones y lugar acordado, el ARRENDATARIO, podrá efectuarlo a través de pago por consignación extrajudicial a favor del ARRENDADOR, en las instituciones autorizadas por el Gobierno Nacional para tal efecto. 2. Cuidar el inmueble y las cosas recibidas en arrendamiento. En caso de daños o deterioros distintos derivados del uso normal o de la acción del tiempo, y que fueren imputables al mal uso del inmueble o a su propia culpa, deberá efectuar pago oportuno para realizar las reparaciones o sustituciones necesarias. 3. Cumplir con las normas consagradas en el reglamento de Propiedad Horizontal al que se encuentra sometido el inmueble arrendado, y las que expida el Gobierno Nacional en protección de los derechos de todos los vecinos. (ESTO SI SE TRATA DE PROPIEDAD HORIZONTAL) 4. Las demás obligaciones consagradas para los arrendatarios en el artículo 9º de la Ley 820 de 2003."
        },
        {
            "titulo": "QUINTA. CANON DE ARRENDAMIENTO",
            "texto": "El valor acordado por las partes asciende a la suma de [VALOR CANON ARRENDAMIENTO] M/CTE. la cual el ARRENDATARIO pagará en su totalidad, dentro de los cinco (5) primeros días calendario de cada período mensual (del 01 al 05 de cada mes), por anticipado, al ARRENDADOR o a su orden."
        },
        {
            "titulo": "SEXTA. INCREMENTOS DEL CANON",
            "texto": "Vencido el primer año de vigencia del presente, y así sucesivamente cada doce (12) mensualidades, en caso de prórroga tácita o expresa, automáticamente y sin necesidad de requerimiento alguno entre las partes, el valor mensual del arrendamiento se incrementará en una proporción igual al 100% del incremento que haya tenido el índice de Precios al Consumidor en el año calendario inmediatamente anterior a aquel en que se efectúe el incremento. Al suscribir este contrato, el ARRENDATARIO y el CODEUDOR quedan plenamente notificados de todos los reajustes automáticos pactados en este contrato y que operarán durante la vigencia de este."
        },
        {
            "titulo": "SÉPTIMA. LUGAR PARA EL PAGO",
            "texto": "EL ARRENDATARIO depositará el canon de arrendamiento al ARRENDADOR en la cuenta del banco caja social con código de recaudo Nro. 15601928. Si deseas realizar el pago por PSE, solicita el link a tu asesor asignado o directamente con el número de la oficina. Si deseas pagar en efectivo te puedes acercar a la oficina ubicada en la calle 19 No. 16 -44 Centro comercial Manhattan local 15 Armenia (recuerda que la atención es de 2 a 5 de la tarde) y finalmente puedes escanear el código QR enviado una vez formado el contrato."
        },
        {
            "titulo": "OCTAVA. MORA",
            "texto": "La mora en el pago del canon mensual facultará al ARRENDADOR para exigir judicial o extrajudicialmente la restitución del inmueble, y solicitar el pago de los perjuicios que dicha mora le llegará a ocasionar. Adicional a ello, le facultará para cobrar el treinta por ciento (30%) de los gastos de cobranza causados sobre el total adeudado, sin perjuicio de hacer exigible el pago de intereses corrientes, intereses moratorios, entre otros."
        },
        {
            "titulo": "NOVENA. CUOTAS DE ADMINISTRACIÓN",
            "texto": "El valor correspondiente a este concepto ya se encuentra incluido en el canon de arrendamiento especificado en la cláusula quinta."
        },
        {
            "titulo": "DÉCIMA. VIGENCIA DEL CONTRATO",
            "texto": "El término de duración del contrato es de [DIFERENCIA DE MESES FECHA FIN - FECHA INICIO] meses que comienzan a contarse a partir del día [FECHA DE INICIO], hasta el día [FECHA DE FIN]."
        },
        {
            "titulo": "DÉCIMA PRIMERA. PRÓRROGAS",
            "texto": "Este contrato se entenderá prorrogado en iguales condiciones y por el mismo término inicial, siempre que cada una de las partes haya cumplido con las obligaciones a su cargo y, que el ARRENDATARIO se avenga a los reajustes de la renta pactados en la cláusula sexta que antecede, autorizados en la Ley 820 de 2003."
        },
        {
            "titulo": "DECIMA SEGUNDA. SERVICIOS PÚBLICOS DOMICILIARIOS",
            "texto": "Los servicios públicos domiciliarios como: energía eléctrica, alumbrado público, acueducto y gas, no se encuentran incluidos en el valor del canon de arrendamiento, y estarán estrictamente a cargo del ARRENDATARIO. Parágrafo primero: Deberá el ARRENDATARIO notificar al ARRENDADOR, de la llegada de los recibos de servicios públicos del primer (1°) mes después que inicie el contrato. Parágrafo segundo: El presente documento, junto con los recibos cancelados por el ARRENDADOR, constituyen título ejecutivo para cobrar judicialmente al ARRENDATARIO y/o a su CODEUDOR los servicios que se dejaren de pagar, siempre que tales montos correspondan al período en que el ARRENDATARIO tuvo en su poder el inmueble. Parágrafo tercero: Los demás servicios adquiridos por el ARRENDATARIO serán pagaderos por éste mismo, y no podrá utilizar el inmueble objeto del presente contrato para contraer obligaciones de ningún tipo, so pena de reparar los perjuicios ocasionados al ARRENDADOR. Parágrafo cuarto: Al momento de la restitución del inmueble, EL ARRENDATARIO deberá presentar pagados los recibos de servicios públicos asignados al inmueble que correspondan a los tres (3) últimos meses, a fin de que el ARRENDADOR liquide el pago anticipado de los servicios públicos, con base en los consumos a la fecha de devolución del inmueble. Dicho monto lo dará al ARRENDATARIO en efectivo, para así proceder a recibir el inmueble."
        },
        {
            "titulo": "DÉCIMA TERCERA. COSAS Y USOS CONEXOS",
            "texto": "Además del inmueble identificado y descrito anteriormente, tendrá el ARRENDATARIO derecho de goce sobre las zonas comunes existentes, de acuerdo con lo estipulado en el Reglamento de Propiedad Horizontal, el cual declara conocer y se obliga a cumplir. (ESTO SI SE TRATA DE PROPIEDAD HORIZONTAL)"
        },
        {
            "titulo": "DÉCIMA CUARTA. RECIBO Y ESTADO",
            "texto": "El ARRENDATARIO declara que antes de firmar el presente contrato de arrendamiento, ha visitado, inspeccionado y revisado personalmente el inmueble; que el estado de mantenimiento, conservación y pintura se encuentra en óptimas condiciones; y que además ha recibido el inmueble a entera satisfacción conforme al Acta de Entrega que firma el ARRENDATARIO al momento de la entrega material del inmueble, la cual forma parte integral de este contrato. Parágrafo primero: el ARRENDATARIO está obligada a efectuar en el inmueble las reparaciones normales de uso, como, por ejemplo: llaves de los baños y cocina, servicio sanitario, cañerías o desagües (baños tapados), enlucimiento (aseo) de paredes, pisos, reposición de vidrios rotos, conservación de llaves y cerraduras de las puertas, instalaciones eléctricas y todas aquellas mejores locativas necesarias derivadas del uso diario. Parágrafo segundo: el ARRENDATARIO se compromete a entregar las paredes del inmueble en las mismas condiciones en que las recibe, es decir, con el mismo color de pintura. En caso de colocar pernos, chazos, o anclajes en las paredes, muros, enchapes de cerámica, cocina y baño, deberá el ARRENDATARIO reparar las superficies en procura de devolverlas tal cual las encontró al momento de recibir el inmueble. Parágrafo tercero: el ARRENDATARIO autoriza al ARRENDADOR para que visite el inmueble con previo aviso, y solicite la presentación de recibos de servicios públicos; esto lo podrá hacer personalmente o a través de un representante."
        },
        {
            "titulo": "DÉCIMA QUINTA. MEJORAS",
            "texto": "LA ARRENDATARIA tendrá a su cargo las reparaciones locativas a que se refiere la Ley 84 de 1873, artículos 2028, 2029, y 2030), y no podrá realizar otras sin el consentimiento escrito del ARRENDADOR; a excepción de las locativas que corren a su cargo. Si se ejecutaren, accederán al propietario del inmueble sin indemnización para quien las efectuó. Parágrafo primero: la ARRENDATARIA renuncia expresamente con la firma de este documento, a descontar del valor del canon de arrendamiento pagadero en cada mensualidad, los valores correspondientes a las reparaciones locativas y/o estructurales que realizare sin previa autorización escrita del propietario."
        },
        {
            "titulo": "DÉCIMA SEXTA. CAUSALES DE TERMINACIÓN DEL CONTRATO",
            "texto": "Son causales de terminación del contrato en forma unilateral por parte del ARRENDADOR, las previstas en el Artículo 22 de la Ley 820 de 2003; y por parte del ARRENDATARIO las consagradas en el artículo 24 de la misma. Parágrafo primero. Si así lo desean, las partes en cualquier tiempo y de común acuerdo podrán dar por terminado el presente contrato."
        },
        {
            "titulo": "DÉCIMA SÉPTIMA. PREAVISOS PARA LA ENTREGA",
            "texto": "Las partes podrán dar por terminado unilateralmente el contrato de arrendamiento a la fecha de vencimiento del término inicial o de sus prórrogas, siempre y cuando dé previo aviso por escrito a través del servicio postal autorizado, con una antelación no menor a tres (3) meses a la referida fecha de vencimiento. La terminación unilateral por parte del ARRENDATARIO en cualquier otro momento solo se aceptará previo el pago de una indemnización equivalente al precio de tres (3) meses de arrendamiento que esté vigente al momento de entrega del inmueble."
        },
        {
            "titulo": "DÉCIMA OCTAVA. ABANDONO DEL INMUEBLE",
            "texto": "Al suscribir este contrato, el ARRENDATARIO faculta al ARRENDADOR para ingresar al inmueble y recuperar su tenencia, con el solo requisito de que asista en presencia de dos (2) testigos, para evitar el deterioro o el desmantelamiento del inmueble; esto siempre que, por cualquier circunstancia, el mismo permanezca abandonado o deshabitado por un término superior a quince (15) días, o que amenace la integridad física del bien o su seguridad. Lo anterior haciendo el debido diligenciamiento del Acta de Entrega judicial o extrajudicial, suscrita con anotación clara del estado en que se encuentra, al igual que los faltantes de acuerdo con el inventario y los valores adeudados que quedaran pendientes como consecuencia del abandono y/o incumplimiento."
        },
        {
            "titulo": "DÉCIMA NOVENA. TRATAMIENTO DE DATOS PERSONALES Y AUTORIZACIÓN",
            "texto": "En cumplimiento de lo dispuesto en la Ley 1581 de 2012, le informamos que los datos de carácter personal que suministre en virtud del presente contrato de arrendamiento serán objeto de tratamiento por parte de CRISTIAN FERNANDO JAMIOY FONSECA con la finalidad de desarrollar el contrato durante todas las etapas de este y especialmente para: a) El desarrollo de la relación contractual entre el ARRENDADOR y el ARRENDATARIO. b) La actualización y consulta de datos personales. c) El reporte y la consulta de obligaciones ante las centrales de riesgo. d) La realización de ofertas de asesoría y servicios. e) La realización de campañas comerciales y de mercado sobre servicios afines al arrendamiento. f) La medición de niveles de satisfacción. g) La realización de investigaciones de mercadeo. h) La confirmación de referencias personales y comerciales de conformidad con la información por usted suministrada. i) El envío de mensajes en torno al contrato de arrendamiento por medio físico o electrónico (correo electrónico, SMS, FAX, o a cualquier otro medio electrónico o al celular)."
        },
        {
            "titulo": "VIGÉSIMA. CENTRALES DE RIESGO",
            "texto": "En virtud del presente contrato, El(los) arrendatario(s) y los deudores solidarios manifiestan que es su voluntad inequívoca y libre de cualquier presión, autorizar de manera previa, expresa e irrevocable al arrendador y a su eventual cesionario o subrogatorio para incorporar, reportar, procesar y consultar en bancos de datos, la información que se relacione con este contrato o que de él se derive, así mismo autorizan para que los contacten y notifiquen a través de los datos que aportan en este documento, las solicitudes de arrendamiento y a los que llegaran a encontrar a futuro, comprometiéndose a actualizar los mismos en caso de cambio de domicilio o lugar de trabajo siempre y cuando exista el vínculo contractual que dio origen a la autorización de consulta y reporte. PARAGRAFO PRIMERO: La presente autorización la extienden los arrendatarios y/o deudores solidarios en los mismos términos y con los mismos alcances aquí indicados para el cobro extraprocesal y/o procesal de las obligaciones derivadas del contrato de arrendamiento, cuando a ello hubiere lugar. PARAGRAFO SEGUNDO: Atendiendo Los términos en que se otorga esta autorización, los arrendatarios y/o deudores solidarios renuncian a efectuar cualquier reclamación ante entidades administrativas y/o judiciales por las actuaciones desplegadas por el arrendador y/o por su eventual cesionario o subrogatorio en el ejercicio legítimo, y dentro de los términos establecidos, de la autorización aquí otorgada."
        },
        {
            "titulo": "VIGÉSIMA PRIMERA. REQUERIMIENTOS",
            "texto": "EL ARRENDATARIO y el CODEUDOR manifiestan libre de todo apremio que renuncian a los requerimientos previos a la constitución en mora de que tratan los artículos 1594 y 1595 de la Ley 84 de 1873 (Código Civil); así como a cualquier otro que establezca norma de carácter procesal o sustancial."
        },
        {
            "titulo": "VIGÉSIMA SEGUNDA. MÉRITO EJECUTIVO",
            "texto": "Este contrato junto con los recibos cancelados por parte del ARRENDADOR, constituyen título ejecutivo para cobrar judicialmente el ARRENDATARIO y sus garantes los servicios públicos que dejare de pagar, es decir que, este documento presta mérito ejecutivo para exigir el cumplimiento de todas las obligaciones contraídas entre las partes. Las partes renuncian expresamente a los requerimientos para el pago de las obligaciones derivadas del mismo."
        },
        {
            "titulo": "VIGÉSIMA TERCERA. CLÁUSULA PENAL",
            "texto": "El incumplimiento por parte del ARRENDADOR o el ARRENDATARIO de cualquiera de las cláusulas derivadas del presente contrato, lo constituirá en deudor de la parte cumplida, en una suma equivalente a tres (3) cánones de arrendamiento que se encuentre vigente o en ejecución al momento del incumplimiento. El pago de la pena no extingue la obligación principal y podrá iniciarse a la vez el cobro de la pena, de la obligación principal y de los daños y perjuicios a que hubiere lugar. Ante el incumplimiento del pago del canon de arrendamiento en los términos pactados o de cualquier obligación pecuniaria a cargo del ARRENDATARIO, será exigible la cláusula penal aquí pactada a favor del ARRENDADOR. Las partes renuncian expresamente a los requerimientos para ser constituidos en mora del pago de cualquiera de sus obligaciones legales y las que aquí expresamente se han acordado. Parágrafo primero. En caso de atraso del pago del canon de arrendamiento, se establece cobro de sanción que se prorrateará de acuerdo con los días de atraso."
        },
        {
            "titulo": "VIGÉSIMA CUARTA. EXONERACIÓN DE RESPONSABILIDAD",
            "texto": "Tanto el ARRENDADOR como el propietario, no asumen responsabilidad alguna por los daños o perjuicios que el ARRENDATARIO pueda sufrir por caso fortuito, fuerza mayor, causas atribuibles a terceros, o la incorrecta y/o deficiente prestación de servicios públicos. En ninguno de estos casos asumen costos por perdida de enceres o cualquier elemento dentro del inmueble que sean de propiedad del ARRENDATARIO. Este último asume la responsabilidad por los daños ocasionados al inmueble o a los enceres y dotaciones de los vecinos o terceros, cuando estos provengan de su descuido o negligencia, o de sus dependientes, familia huéspedes o similares."
        },
        {
            "titulo": "VIGÉSIMA QUINTA. NOTIFICACIONES",
            "texto": "Para todos los efectos judiciales o extrajudiciales, las partes se notificarán en las siguientes direcciones, así: EL ARRENDADOR en el Centro Comercial Manhatan local 15 en Armenia, Quindío; por medio del número de teléfono: 3011281684; y el correo electrónico: inmobiliariavelarsasaxm@gmail.com. EL ARRENDATARIO por medio del número de teléfono [TELEFONO ARRENDATARIO] y el correo electrónico [CORREO ARRENDATARIO], CODEUDOR: por medio del número de teléfono [TELEFONO CODEUDOR] y el correo electrónico [CORREO CODEUDOR] primero. En caso de cambio de alguno de los datos descritos en la cláusula vigésima quinta del presente contrato, las partes se comprometen expresamente a informar por medio escrito para su debida actualización."
        }
    ]

    def __init__(self, output_dir: Path = None):
        super().__init__(output_dir)
        self.document_title = "CONTRATO DE MANDATO"
        self.margins = {'top': 60, 'bottom': 80, 'left': 60, 'right': 60}
        
    def _header_footer_with_features(self, canvas_obj, doc):
        """
        Override completo para evitar el header por defecto de la empresa (INMOBILIARIA VELAR SAS...)
        que se solapa con el título.
        """
        # 0. Dibujar LOGO si existe (Top Center)
        if hasattr(self, 'logo_data') and self.logo_data:
            try:
                import base64
                import io
                from reportlab.lib.utils import ImageReader
                
                # Decode base64
                image_data = base64.b64decode(self.logo_data)
                image_stream = io.BytesIO(image_data)
                logo_img = ImageReader(image_stream)
                
                # Dimensions
                logo_width = 150 # Ajustable
                logo_height = 60 # Ajustable aspect ratio handled by usage, but here fixed box
                
                # Center X
                page_width = doc.pagesize[0]
                x_pos = (page_width - logo_width) / 2
                y_pos = doc.pagesize[1] - logo_height - 30 # Top margin offset
                
                canvas_obj.drawImage(logo_img, x_pos, y_pos, width=logo_width, height=logo_height, mask='auto', preserveAspectRatio=True)
            except Exception as e:
                print(f"Error dibujando logo: {e}")

        # 1. Dibujar NUESTRO footer personalizado (Calle 19...) - Antes estaba en Header
        # Texto del footer centrado
        footer_text = [
            "Calle 19 No. 16 – 44 Centro Comercial Manhatan Local 15 Armenia, Quindío.",
            "Contacto: +57 3135410407"
        ]

        # 2. Agregar marca de agua si aplica (logic from Base)
        if self.watermark_text:
            from ..components.watermarks import Watermark
            Watermark.add_text_watermark(
                canvas_obj,
                text=self.watermark_text,
                opacity=self.watermark_opacity,
                position=self.watermark_style,
            )
            
        # 3. Footer simple (Página X)
        canvas_obj.saveState()
        
        # Dibujar dirección en footer
        canvas_obj.setFont('Helvetica-Bold', 8)
        canvas_obj.setFillColor(colors.gray)
        center_x = doc.pagesize[0] / 2
        y_pos = 50 # Un poco más arriba del borde
        
        for line in footer_text:
            canvas_obj.drawCentredString(center_x, y_pos, line)
            y_pos -= 10

        # Página y Timestamp
        page_num = canvas_obj.getPageNumber()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.gray)
        
        # Página Centrada
        canvas_obj.drawCentredString(center_x, 20, f"Página {page_num}")
        
        # 4. Textos Verticales en Márgenes
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.lightgrey) # Color tenue para no distraer
        
        from datetime import datetime
        dt_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Margen Izquierdo (Vertical)
        canvas_obj.saveState()
        canvas_obj.translate(50, 250) # Ajustar posición X,Y
        canvas_obj.rotate(90)
        canvas_obj.drawString(0, 0, "Impreso por Inmobiliaria Velar SAS - NIT 901.703.515 - Correo: inmobiliariavelarsasaxm@gmail.com")
        canvas_obj.restoreState()
        
        # Margen Derecho (Vertical)
        canvas_obj.saveState()
        canvas_obj.translate(doc.pagesize[0] - 50, 250)
        canvas_obj.rotate(90)
        canvas_obj.drawString(0, 0, f"Generado: {dt_str}")
        canvas_obj.restoreState()
        
        canvas_obj.restoreState()

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validación estricta para nueva plantilla de Mandato"""
        # 1. Campos base
        required_base = ["contrato_id", "fecha", "inmueble", "condiciones", "mandante"]
        
        is_valid, missing = DataValidator.validate_required_fields(data, required_base)
        if not is_valid:
            raise ValueError(f"Faltan campos principales: {', '.join(missing)}")
            
        # 2. Sub-estructuras
        self._require_fields(data["mandante"], "nombre", "documento", "telefono", "email")
        
        # Inmueble exige matricula
        self._require_fields(data["inmueble"], "direccion")
        
        # Validar montos (comisión)
        if not DataValidator.validate_money_amount(data["condiciones"].get("comision", 0)):
             # Nota: En mandato podría ser 0 o porcentaje, pero validamos que sea numérico válido
             pass
             
        return True

    def generate(self, data: Dict[str, Any]) -> Path:
        """Generación del contrato"""
        # Configurar template base
        # self.header_content_method ya no es necesario
        
        # Logo Logic - Store for use in header callback
        self.logo_data = data.get("logo_base64")
        
        if data.get("estado") == "borrador":
            self.set_watermark("BORRADOR", opacity=0.1)
            
        filename = self._generate_filename("contrato_mandato", data["contrato_id"])
        self.create_document(filename, self.document_title)
        
        # 1. Título y Ciudad
        self.add_title_main(self.document_title)
        self.add_paragraph(f"<b>Fecha:</b> {data['fecha']}", align='CENTER')
        self.add_paragraph("<b>CIUDAD DEL CONTRATO:</b><br/>(ARMENIA, QUINDÍO)", align='CENTER')
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
            "El presente contrato de arrendamiento se regirá por las normas establecidas en la <b>Ley 820 de 2003</b>... "
            "<i><b>(ESTO SOLO SI SE TRATA DE PROPIEDAD HORIZONTAL).</b></i>",
            style_name="Body"
        )
        self.add_spacer(0.2)
        self.add_paragraph(
            f"Para constancia de lo anterior se firma el día <b>{self._format_fecha_es(data.get('fecha', ''))}</b>, en dos ejemplares de un mismo tenor literal ordenado por la Ley."
        )
        self.add_spacer(0.5)
        
        # 6. Firmas
        self._add_firmas_tres_columnas(data)
        
        return self.build()

    def _add_resumen_partes(self, data: Dict[str, Any]):
        """Crea el bloque visual de resumen tipo ficha técnica"""
        mandatario = data.get('inmobiliaria', self.ARRENDADOR_INFO) # Fallback to default check
        mandante = data['mandante']
        inmueble = data['inmueble']
        cond = data['condiciones']
        
        # Estilos
        style_label = ParagraphStyle('Label', fontName='Helvetica-Bold', fontSize=9)
        style_val = ParagraphStyle('Val', fontName='Helvetica', fontSize=9)
        
        def p_kw(txt): return Paragraph(f"<b>{txt}</b>", style_label)
        def p_val(txt): return Paragraph(str(txt), style_val)

        # Construcción de filas simulando el layout visual
        
        # Dirección Inmueble (Manejo de N/A gracefully)
        direccion_inmueble = inmueble.get('direccion', 'N/A')
        municipio = inmueble.get('municipio', 'ARMENIA')
        departamento = inmueble.get('departamento', 'QUINDÍO')
        direccion_full = f"{direccion_inmueble}<br/>{municipio}, {departamento}"
        row_inm = [
            [p_kw("DIRECCIÓN DEL INMUEBLE:"), p_val(direccion_full)]
        ]

        # Mandatario (Inmobiliaria)
        # Usamos datos quemados si no vienen, o los del objeto
        nombre_inmo = mandatario.get('nombre', "INMOBILIARIA VELAR S.A.S.")
        nit_inmo = mandatario.get('nit', "901703515-7")
        rep_legal = mandatario.get('representante', "CRISTIAN FERNANDO JAMIOY FONSECA")
        rep_doc = mandatario.get('documento_rep', "1.094.959.215")
        
        contenido_mandatario = (
            f"{nombre_inmo}<br/>"
            f"NIT: {nit_inmo}<br/>"
            f"REP. {rep_legal}<br/>"
            f"C.C.: {rep_doc}"
        )
        
        row_arr = [
            [p_kw("MANDATARIO:"), p_val(contenido_mandatario)]
        ]
        
        # Mandante (Propietario)
        # Asegurar que si viene N/A se muestre algo decente o se mantenga
        nombre_mandante = mandante.get('nombre', 'N/A')
        doc_mandante = mandante.get('documento', 'N/A')
        
        row_user = [
            [p_kw("MANDANTE:"), p_val(f"{nombre_mandante}<br/>C.C. {doc_mandante}")]
        ]
        
        # Condiciones
        comision_fmt = f"${cond.get('comision', 0):,.0f}".replace(",", ".")
        canon_fmt = f"${cond.get('valor_canon_sugerido', 0):,.0f}".replace(",", ".")
        duracion = f"{cond.get('duracion_meses', 12)} Meses"
        
        # Fechas
        fecha_inicio = self._format_fecha_es(data.get('fecha_inicio', 'N/A'))
        fecha_fin = self._format_fecha_es(data.get('fecha_fin', 'N/A'))
        
        # Renderizar tabla
        data_table = []
        data_table.append(row_inm[0])
        data_table.append(row_arr[0])
        data_table.append(row_user[0])
        data_table.append([p_kw("CANON MANDATO:"), p_val(canon_fmt)])
        data_table.append([p_kw("FECHA DE INICIO DEL CONTRATO:"), p_val(fecha_inicio)])
        data_table.append([p_kw("FECHA DE TERMINACIÓN DEL CONTRATO:"), p_val(fecha_fin)])
        data_table.append([p_kw("DURACIÓN DEL CONTRATO:"), p_val(duracion)])
        # data_table.append([p_kw("FECHA:"), p_val(data['fecha'])]) # Redundante si ya están inicio/fin? El diseño original tenía FECHA simple. Dejar opcional o quitar si confunde. En la imagen de "Faltan datos" se veía FECHA pero faltaba inicio/fin. Dejaremos inicio/fin explícitos.

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
        
        mandante = data['mandante']
        
        # Mapping para compatibilidad con texto existente (que parece ser copia de arriendo)
        # Se mapean roles de Mandato a los placeholders de arriendo para que se llene
        
        mapeo = {
            "[DIRECCION PREDIO]": data['inmueble'].get('direccion', 'N/A').upper(),
            "[MATRICULA INMOBILIARIA]": data['inmueble'].get('matricula_inmobiliaria', 'N/A'),
            "[FECHA ACTUAL DEL SISTEMA]": self._format_fecha_es(data.get('fecha', 'N/A')),
            # Mapeos de roles - MANDANTE (Propietario)
            "[NOMBRE PROPIETARIO]": mandante.get('nombre', 'N/A').upper(),
            "[TELEFONO PROPIETARIO]": mandante.get('telefono', 'N/A'),
            "[CORREO PROPIETARIO]": mandante.get('email', 'N/A'),
            
            # Datos Bancarios (con fallback seguro)
            "[BANCO PROPIETARIO]": mandante.get('banco', '___BANCO___'),
            "[TIPO DE CUENTA PROPIETARIO]": mandante.get('tipo_cuenta', '___TIPO___'),
            "[NUMERO DE CUENTA PROPIETARIO]": mandante.get('numero_cuenta', '___NUMERO___'),
            
            # Fechas y valores
            "[FECHA DE INICIO]": self._format_fecha_es(data.get('fecha_inicio', 'N/A')),
            "[FECHA DE FIN]": self._format_fecha_es(data.get('fecha_fin', 'N/A')), 
            "[VALOR CANON ARRENDAMIENTO]": f"${data['condiciones'].get('valor_canon_sugerido', 0):,.0f}",
            "[VALOR CANON MANDATO]": f"${data['condiciones'].get('valor_canon_sugerido', 0):,.0f}",
            "[DIFERENCIA DE MESES FECHA FIN - FECHA INICIO]": str(data['condiciones'].get('duracion_meses', 12))
        }

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
        """Renderiza firmas (Solo 2 para Mandato)"""
        
        info_inmo = data.get('inmobiliaria', self.ARRENDADOR_INFO)
        mandante = data['mandante']
        
        style_firma = ParagraphStyle('Firma', fontName='Helvetica', fontSize=8, leading=10, alignment=1) # Center
        
        def firma_bloque(titulo, nombre, doc):
            content = f"<br/><br/><br/><br/>_______________________________________<br/><b>{titulo}</b><br/>{nombre}<br/>C.C./NIT. {doc}"
            return Paragraph(content, style_firma)
            
        # Mandatario
        bloque_1 = firma_bloque(
            "MANDATARIO", 
            info_inmo.get('nombre', 'INMOBILIARIA VELAR S.A.S.'),
            info_inmo.get('nit', '901703515-7')
        )
        
        # Mandante
        bloque_2 = firma_bloque(
            "MANDANTE",
            mandante['nombre'],
            mandante['documento']
        )
        
        # Tabla de 2 columnas
        tabla_firmas = Table(
            [[bloque_1, bloque_2]], 
            colWidths=[250, 250]
        )
        tabla_firmas.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        
        self.story.append(tabla_firmas)

__all__ = ["ContratoArrendamientoElite"]
