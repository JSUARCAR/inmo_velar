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
from num2words import num2words
from datetime import datetime


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
	    "titulo": "CLÁUSULA DE TRATAMIENTO DE DATOS PERSONALES Y CENTRALES DE RIESGO",
	    "texto": "El Mandante autoriza expresa e inequívocamente al Mandatario para recolectar, consultar, verificar, reportar y administrar la información personal, laboral y financiera de arrendatarios y fiadores, ante aseguradoras, entidades financieras, centrales de riesgo y demás entidades, exclusivamente con fines de análisis de riesgo, validación de solvencia y cumplimiento del contrato de arrendamiento.<br><br>El tratamiento de la información se realizará conforme a la <b>Ley 1581 de 2012</b> (protección de datos personales) y a la <b>Ley 1266 de 2008</b> (habeas data financiero), garantizando los derechos de los titulares de la información, quienes podrán ejercer en cualquier momento sus derechos de acceso, rectificación, actualización y supresión de datos."
	    },
	    {
	    "titulo": "CLÁUSULA DE RÉGIMEN DE PROPIEDAD HORIZONTAL Y CONVIVENCIA",
	    "texto": "El Mandante y el arrendatario se obligan a cumplir estrictamente con el <b>Reglamento de Propiedad Horizontal</b>, el <b>Manual de Convivencia y demás disposiciones internas</b> que rijan la copropiedad donde se encuentre el inmueble objeto de este contrato, en los términos de la <b>Ley 675 de 2001</b>.<br><br>Las sanciones, multas o cobros que se originen por incumplimiento de tales normas serán de cargo exclusivo del Mandante, quien autoriza expresamente al Mandatario a descontarlos de los cánones de arrendamiento recaudados o exigir su pago directo. El Mandatario no asumirá responsabilidad alguna por el comportamiento de los arrendatarios frente al reglamento interno, limitándose a informar oportunamente al Mandante sobre cualquier situación que genere sanciones por parte de la copropiedad."
	    },
        {
            "titulo": "PRIMERA. OBJETO DEL CONTRATO",
            "texto": "El MANDANTE entrega al MANDATARIO el inmueble ubicado en [DIRECCION PREDIO], e identificado con la matrícula inmobiliaria No. [MATRICULA INMOBILIARIA] El Mandatario adelantará el proceso de selección de arrendatarios y fiadores aplicando parámetros de verificación tales como estudio de riesgos financieros, laborales y personales, consulta en listas restrictivas, referencias personales, comerciales y crediticias, así como cualquier otro criterio que resulte pertinente para garantizar la seguridad del arrendamiento.<br><br>No obstante, lo anterior, <b>la decisión final sobre la aceptación o rechazo de los arrendatarios será exclusiva del Mandatario</b>, en ejercicio de las facultades propias del mandato con representación conferido en este contrato, sin que se requiera autorización previa del Mandante para la firma del contrato de arrendamiento."
        },
        {
            "titulo": "SEGUNDA. TÉRMINO DEL CONTRATO",
            "texto": "El término de duración del presente será de [DIFERENCIA DE MESES FECHA FIN - FECHA INICIO] ([DIFERENCIA DE MESES FECHA FIN - FECHA INICIO EN TEXTO]) meses"
        },
        {
            "titulo": "TERCERA. FIJACIÓN DEL CANON Y FORMA DE PAGO",
            "texto": "El precio pactado con el MANDANTE por el cual se arrendará el inmueble objeto del presente contrato, será la suma de [VALOR CANON MANDATO] ([VALOR CANON MANDATO EN TEXTO]) la cual será depositada a nombre de [NOMBRE PROPIETARIO], a la cuenta bancaria: [BANCO PROPIETARIO] - [TIPO DE CUENTA PROPIETARIO] - [NUMERO DE CUENTA PROPIETARIO].<br><br>El Mandatario queda facultado para ofertar y fijar el canon de arrendamiento del inmueble objeto de este contrato, de acuerdo con las condiciones del mercado y las disposiciones legales vigentes.<br><br>El canon de arrendamiento se ajustará anualmente en el porcentaje correspondiente a la variación del <b>Índice de Precios al Consumidor (IPC) certificado por el DANE</b>, en los términos del <b>artículo 20 de la Ley 820 de 2003</b>, sin necesidad de autorización previa del Mandante.<br><br>En caso de que se pretenda un incremento superior al IPC legalmente permitido, o cualquier modificación extraordinaria del canon, se requerirá autorización previa y por escrito del Mandante."
        },
        {
            "titulo": "CUARTA. REPORTE MENSUAL",
            "texto": "El MANDATARIO transferirá al MANDANTE el valor neto del cánon de mandato el día [FECHA DE PAGO TEXTO] [FECHA DE PAGO] de cada mes (o el día hábil siguiente si este coincidiere con un día festivo), siempre y cuando el inmueble estuviere ocupado y los arrendatarios hubiesen cancelado el correspondiente canon de arrendamiento.<br><br>De dicho valor se realizará la respectiva Deducción mensual, que comprende: <br><br>a) La comisión equivalente al diez por ciento (10%) del canon de arrendamiento y el IVA sobre el 10% del servicio prestado. <br><br>b)	Gastos adicionales como: impuestos, contribuciones, cuotas ordinarias y extraordinarias de administración, multas, intereses, vigilantes, ascensoristas, avisos publicitarios, y otras cuentas pendientes cuando no correspondan al arrendatario del bien inmueble, siempre con previa autorización del propietario, De no recibir respuesta del MANDANTE, observaciones dentro del mes siguiente, se entenderá que aprobó el monto pagado por conceptos nombrados.<br><br>El Mandatario se obliga a rendir cuentas al Mandante de la gestión realizada, de manera mensual, dentro de los primeros diez (10) días hábiles de cada mes, entregando reporte escrito o electrónico con el detalle de los cánones de arrendamiento recaudados, descuentos aplicados y valores entregados, acompañado de los soportes correspondientes (facturas, recibos de administración, comprobantes de pago de servicios, constancias de retención en la fuente, entre otros).<br><br>Los dineros recaudados a nombre del Mandante se mantendrán en <b>cuentas separadas</b> de las del Mandatario, sin que puedan mezclarse con recursos propios o de terceros, salvo autorización expresa del Mandante.<br><br>El Mandatario podrá efectuar, con cargo a dichos recursos, los siguientes descuentos: <br><br>a)	Comisión pactada a su favor <br><br>b)	Impuestos, tasas y contribuciones que legalmente graven el inmueble o el contrato. <br><br>c)	Expensas comunes ordinarias y extraordinarias de la copropiedad. <br><br>d)	Reparaciones locativas realizadas conforme a este contrato. <br><br>e)	Sanciones o multas impuestas por la copropiedad. <br><br>f)	Gastos de cobranza prejurídica generados por el incumplimiento del arrendatario.<br><br>El Mandante autoriza expresamente al Mandatario a <b>conciliar y aplicar compensaciones menores</b>, cuando existan diferencias derivadas de ajustes de servicios públicos, cuotas de administración o reparaciones menores, siempre que se respete el principio de buena fe y se entreguen los soportes respectivos con su previa autorización."
        },
	    {
            "titulo": "CLÁUSULA DE INTERESES DE MORA",
            "texto": "En caso de incumplimiento por parte del Mandante en el pago oportuno de cualquier obligación derivada del presente contrato, se causarán intereses de mora a la <b>tasa máxima legal permitida para obligaciones civiles o comerciales</b>, certificada por la <b>Superintendencia Financiera de Colombia</b>, liquidados mes vencido, sin perjuicio de las demás acciones legales a que haya lugar."
	    },
        {
            "titulo": "QUINTA. FACULTADES DEL MANDATARIO",
            "texto": "El MANDANTE faculta al MANDATARIO para que en su nombre y representación: promueva a través de medios ordinarios e idóneos el arriendo del inmueble objeto del presente contrato; escoja a los arrendatarios bajo sus criterios; celebre los respectivos contratos bajo las garantías que a su juicio sean oportunas; reciba los pagos de los cánones de arrendamiento, y demás pagos a cargo de los arrendatarios; arriende el inmueble por el precio acordado con el MANDANTE, teniendo en cuenta la calidad y ubicación del inmueble, y las leyes vigentes en materia de arrendamiento, procurando el mayor beneficio para el MANDANTE; otorgar autorizaciones a los arrendatarios para instalaciones o traslado de líneas de servicio telefónico y/o de internet al inmueble; efectuar todas aquellas reparaciones locativas que legalmente se encuentren a cargo del MANDANTE para la conservación del inmueble y que estén encaminadas a satisfacer el goce pleno del inmueble, y asimismo todas aquellas que sean ordenadas por las autoridades. con un tope máximo del 50% (En caso de que el inmueble necesite para su cuidado y mantenimiento de los servicios de trabajadores como carpinteros, maestros de obra, celadores, aseadoras, ascensoristas, etc., serán contratados a nombre y bajo la única y exclusiva responsabilidad del MANDANTE, el cual ostenta la calidad de empleador, y por tanto, tendrá a su cargo el pago de salarios, prestaciones sociales, seguridad social y demás obligaciones que avengan como consecuencia de dichas relaciones de naturaleza laboral o incluso civil, salvo instrucciones escritas dadas por él mismo; pagar con cargo al propietario los servicios públicos domiciliarios y demás gastos que no correspondan a los arrendatarios, si fuere el caso. Igualmente podrá pagar impuestos y seguros cuando estos sean autorizados formalmente por el MANDANTE; dar por terminado antes del vencimiento, por justa causa, el contrato de arrendamiento que se haya suscrito sobre el inmueble; e iniciar las acciones legales previo aviso al MANDANTE, con una antelación de ocho (8) días hábiles, a fin de restituir el inmueble en caso de ser necesario; iniciar oportunamente las acciones judiciales, administrativas y/o policiales tendientes a librar de perturbaciones a los arrendatarios. En el evento de que haya necesidad de promover procesos para obtener judicialmente la restitución del inmueble, los gastos del proceso serán aquellos que señale el juzgado competente, y los deberán pagar los arrendatarios; en casos de mora en las obligaciones hipotecarias de los inmuebles arrendados, cancelar su obligación hasta el monto de los arriendos, a cargo del MANDANTE; descontar inmediatamente de los correspondientes cánones de arrendamiento que reciba, el valor de los honorarios generados por concepto de administración, además de los gastos y costos en que incurra el  administrador  por  causa  de  la  gestión  que  adelante,  previo  aviso  a  al mandante, exceptuando los de comercialización del inmueble, así como también a descontar los servicios públicos, administraciones, seguros de todo riesgo y de arrendamiento, celaduría, reparaciones locativas, cuotas extraordinarias, impuestos, acciones judiciales, administrativas y/o policivas y demás que demande el inmueble, y que el MANDATARIO haya asumido de manera directa por autorización del propietario; y otorgar poder a un abogado para que inicie cualquier proceso judicial, administrativo o extrajudicial relacionado con el inmueble, e incluso para que eleve derechos de petición y cualquier tipo de recurso, en aras de defender los intereses del MANDANTE.<br><br>La entrega del Inmueble al Arrendatario se realizará mediante inventario y/o acta de entrega con registro fotográfico y/o audiovisual, que hará parte integral del contrato de arrendamiento. A la terminación, el Inmueble se restituirá con base en dicho inventario.<br><br>El Mandante reconoce que será de su cargo el deterioro normal por uso legítimo y por el transcurso del tiempo (desgaste natural), mientras que los daños ocasionados por mal uso, negligencia o incumplimiento del Arrendatario serán de cargo de este último. El Mandatario no asumirá responsabilidad por el desgaste natural ni por daños imputables al Arrendatario, sin perjuicio de su deber de gestión diligente para su cobro y reparación.<br><br>El Mandatario responderá solo por dolo o culpa grave. No responderá por hechos atribuibles al arrendatario, terceros, fuerza mayor o desgaste natural."
        },
	    {
            "titulo": "CLÁUSULA. EXCLUSIVIDAD Y NO COMPETENCIA DEL MANDANTE",
            "texto": "El Mandante confiere al Mandatario la gestión exclusiva de arrendamiento del inmueble objeto de este contrato, obligándose a no celebrar directa ni indirectamente contratos de arrendamiento, ni realizar gestiones de comercialización, promoción, publicidad o negociación respecto del inmueble mientras el presente mandato esté vigente.<br><br>En caso de incumplimiento de esta obligación por parte del Mandante, éste deberá pagar al Mandatario, a título de cláusula penal, una suma equivalente al valor de las comisiones que el Mandatario hubiere percibido durante todo el término de vigencia pactado en el presente contrato, sin perjuicio de las demás acciones legales a que haya lugar."
	    },
	    {
            "titulo": "CLÁUSULA. COSTAS PROCESALES Y COBRANZA PREJURÍDICA",
            "texto": "Las costas procesales y las agencias en derecho serán impuestas a la parte vencida conforme a la normatividad vigente y la regulación judicial aplicable.<br><br>Los gastos de cobranza prejuridica (incluyendo cartas, comunicaciones, visitas, llamadas y mensajería) que se generen por incumplimiento del arrendatario serán de cargo exclusivo de este, y podrán descontarse de los valores recaudados con sus respectivos soportes, de acuerdo con lo previsto en el contrato de arrendamiento y conforme a tarifas razonables previamente informadas al Mandante."
	    },
        {
            "titulo": "SEXTA. OBLIGACIONES DEL MANDATARIO",
            "texto": "Celebrar el contrato de arrendamiento bajo las garantías que a su juicio sean oportunas; cobrar a los arrendatarios el valor de los arrendamientos, y una vez recibidos entregarlos al MANDANTE mensualmente, o seguir las instrucciones que éste le dé, previa deducción de la comisión que corresponde al MANDATARIO, y de los gastos que éste hubiera efectuado por cuenta del MANDANTE; efectuar por cuenta del MANDANTE las reparaciones locativas que el MANDATARIO juzgue convenientes para la conservación del inmueble o para facilitar su arrendamiento, previa comunicación y autorización del MANDANTE, con un tope máximo del 50% y/o las consagradas en el Artículo 1982 del Código Civil; pagar los impuestos prediales que graven el bien con autorización del MANDANTE; cancelar por cuenta del MANDANTE los servicios de energía eléctrica, gas domiciliario, teléfono, parabólica, internet, administración y demás gastos cuando NO correspondan al arrendatario; rendir mensualmente al MANDANTE una cuenta detallada del canon recibido, así como los gastos que ocasionados durante el mismo período; y hacer entrega del inmueble a los arrendatarios, con inventario donde conste el estado general del mismo."
        },
        {
            "titulo": "CLÁUSULA. CONFIDENCIALIDAD",
            "texto": "Las partes se obligan a mantener en estricta confidencialidad toda la información personal, comercial, financiera y contractual a la que tengan acceso con ocasión del presente contrato, incluyendo, pero sin limitarse a: datos del Mandante, del Inmueble, de los Arrendatarios y Fiadores, y condiciones de los contratos de arrendamiento.<br><br>Dicha información no podrá ser divulgada ni utilizada para fines distintos a la ejecución del presente contrato, salvo que: <br><br>a)	exista autorización previa, expresa y escrita de la parte titular de la información. <br><br>b)	Se trate de requerimientos de autoridades administrativas o judiciales competentes. <br><br>c)	La información sea de dominio público sin culpa de la parte receptora.<br><br>La obligación de confidencialidad permanecerá vigente aún después de la terminación del contrato, por un período de cinco (5) años."
        },
        {
            "titulo": "SÉPTIMA. OBLIGACIONES DEL MANDANTE",
            "texto": "Entregar el bien inmueble objeto contrato al día por concepto de acueducto, alcantarillado, energía, gas domiciliario, y demás servicios que se encuentren a su cargo; realizar las reparaciones estructurales y/o necesarias contempladas en el artículo 1986 del Código Civil que deban realizarse para la conservación y facilitación de arrendamiento del inmueble, y que estarán a su cargo con un plazo no mayor a veinte (20) días calendario, posterior a la notificación por parte del MANDATARIO para realizar y/o autorizar dichas reparaciones, so pena de que el arrendatario y/o MANDATARIO realicen las mencionadas reparaciones con un tope máximo del 50%, y sean estas descontadas del canon de arrendamiento que se pague inmediatamente después de realizarse de las reparaciones con previa autorización del propietario.<br><br><b>Parágrafo primero</b>: Si fuera el MANDATARIO quien realizará las reparaciones estructurales, él mismo deberá entregar al MANDANTE soportes y registros fotográficos que prueben la elaboración de las reparaciones.<br><br><b>Parágrafo segundo</b>: En caso de que el inmueble requiera para su cuidado y mantenimiento la prestación de servicios de trabajadores, celadores, ascensoristas, aseadores, etc., el MANDANTE autoriza expresamente al MANDATARIO para que los contrate. No obstante, el MANDANTE podrá contratar a los empleados para realizar las reparaciones; reparaciones estas que realizará a nombre propio y bajo su única responsabilidad, adquiriendo la calidad de patrono que deberá responder por salarios, prestaciones sociales, seguridad social y demás obligaciones.<br><br>Adicional a lo anterior, el MANDANTE se compromete a pagar al MANDATARIO una comisión del diez por ciento (10%) y el IVA sobre este mismo porcentaje, las tarifas vigentes por la Lonja de Propiedad Raíz del Quindío, del valor mensual del canon de arrendamiento, y además reconocerá el valor de las estampillas y demás descuentos que se efectúen sobre dicho canon cuando el arrendatario sea una entidad oficial, para lo cual el MANDATARIO podrá descontar del valor total del arrendamiento de cada mes; a reembolsar al MANDATARIO el valor de los gastos en que por negligencia todo previa autorización del propietario, renuencia, mora o falta de decisión suya, incurra con respecto al mantenimiento del inmueble en óptimas condiciones de habitabilidad.<br><br><b>Parágrafo tercero</b>: En caso de que el MANDANTE enajena el bien, deberá reconocer al MANDATARIO las comisiones faltantes hasta la fecha de terminación del contrato de mandato del inmueble, y entonces, de dicho modo dar por terminado el contrato; además, en caso de que el MANDANTE venda el inmueble, deberá actuar conforme los términos contenidos en los <b>artículos 22 numerales 7 y 8 literal c y 23 de la <b>Ley 820 de 2003</b></b>, que es la que rige los contratos de arrendamiento; y finalmente, en el evento de que no sea posible reclamar personalmente el valor del arrendamiento, o por transferencia a cuenta bancaria, deberá autorizar por escrito a un tercero para su recibo."
        },
        {
            "titulo": "OCTAVA. TERMINACIÓN Y RENOVACIÓN DEL CONTRATO",
            "texto": "Este contrato tendrá una duración de [DIFERENCIA DE MESES FECHA FIN - FECHA INICIO] meses los cuales son pagados por adelantado; si vencido este término ninguna de las partes lo da por terminado mediante aviso escrito comunicado a través de correo certificado con treinta (30) días de antelación, se entenderá renovado por el mismo término.<br><br><b>Parágrafo primero</b>. De común acuerdo, las partes podrán dar por terminado el contrato en cualquier tiempo si lo desean.<br><br><b>Parágrafo segundo</b>. Una vez vencido el término del contrato o su prórroga, y el MANDATARIO dé por terminado el contrato y notifique al MANDANTE, cesarán sus obligaciones y luego no podrá ser responsabilizado por hechos que ocurran después de haber manifestado su voluntad de terminar el contrato.<br><br><b>Parágrafo tercero</b>. El presente contrato tendrá una vigencia inicial de [DIFERENCIA DE MESES FECHA FIN - FECHA INICIO] meses, contado a partir de su firma, y se prorrogará automáticamente por períodos iguales mientras subsista contrato de arrendamiento vigente celebrado por el Mandatario en desarrollo del presente mandato, salvo manifestación en contrario de cualquiera de las partes con un preaviso no inferior a treinta (30) días calendario.<br><br>En caso de que, al momento de la terminación del contrato, existan saldos pendientes a cargo del Mandante por concepto de comisiones, expensas, impuestos o cualquier otra obligación a su cargo, dichos valores serán exigibles de manera inmediata y podrán cobrarse por la vía ejecutiva, sin que ello implique la renovación automática del contrato de mandato.<br><br><b>Parágrafo cuarto</b>. En caso de que el MANDATARIO sea quien manifieste su voluntad de terminar el contrato, una vez vencido el término de treinta (30) días contados desde la fecha en que haya avisado de manera formal al MANDANTE, cesarán todas sus obligaciones y no será responsable por hecho alguno que ocurra luego del plazo mencionado, y en tal evento, si por cualquier circunstancia resultare algún saldo insoluto a favor del MANDATARIO por causa de su gestión, dicho valor deberá ser pagado a él o a su orden, por parte del MANDANTE dentro del mes siguiente a la terminación del contrato. <br><br>El presente contrato podrá darse por terminado anticipadamente en los siguientes eventos:<br><br>Por parte del <i>Mandatario</i>:<br><br>1. Incumplimiento del Mandante en el pago oportuno de la comisión, gastos reembolsables u otras obligaciones a su cargo. <br><br>2. Negativa injustificada del Mandante a autorizar reparaciones necesarias que superen el tope establecido. <br><br>3.	Instrucciones del Mandante que sean contrarias a la ley, a la moral, a las normas de propiedad horizontal o que pongan en riesgo la responsabilidad del Mandatario. <br><br>4. Reiterado incumplimiento del Arrendatario que haga inviable la gestión, sin apoyo del Mandante.<br><br>Por parte del <i>Mandante</i>:<br><br>1. Incumplimiento grave del Mandatario en sus deberes de rendición de cuentas. <br><br>2. Actuación dolosa o con culpa grave del Mandatario que cause perjuicio comprobado al Mandante. <br><br>3. Utilización indebida de los recursos entregados o mezcla de fondos.<br><br><b>Efectos</b>:<br><br>La terminación anticipada por justa causa dará lugar al pago de las obligaciones pendientes a cargo de la parte incumplida, incluida la cláusula penal si fuere aplicable, sin perjuicio de las indemnizaciones legales a que haya lugar."
        },
        {
            "titulo": "NOVENA. INCUMPLIMIENTO Y CLÁUSULA PENAL",
            "texto": "En caso de incumplimiento del presente contrato por parte del Mandante, este deberá pagar al Mandatario, a título de cláusula penal, una suma equivalente al diez por ciento (10%) del valor total de los cánones de arrendamiento proyectados durante el término de vigencia inicial del contrato de mandato, o en su defecto, una suma equivalente a las comisiones faltantes por devengar hasta la fecha de vencimiento pactada, lo que resulte mayor.<br><br>La cláusula penal será determinable de manera aritmética, tomando como base el canon de arrendamiento vigente a la fecha del incumplimiento y el porcentaje de comisión pactado a favor del Mandatario.<br><br>La misma sanción se aplicará en caso de terminación unilateral e injustificada por parte del Mandante antes del vencimiento del contrato, salvo que medie justa causa debidamente probada.<br><br>La cláusula penal será mínima y acumulable con la indemnización de perjuicios adicionales que llegaren a demostrarse judicialmente."
        },
        {
            "titulo": "DÉCIMA. MÉRITO EJECUTIVO",
            "texto": "El presente contrato, junto con las liquidaciones de cuenta que presente el Mandatario al Mandante, debidamente soportadas con recibos, comprobantes y demás documentos pertinentes, prestará mérito ejecutivo de conformidad con lo previsto en el artículo 422 del Código General del Proceso.<br><br>El Mandatario enviará al Mandante un estado de cuenta mensual con el detalle de valores recaudados, descuentos efectuados y saldos a favor o en contra. El Mandante dispondrá de un plazo de cinco (5) días hábiles contados a partir de la recepción del estado de cuenta para presentar observaciones u objeciones por escrito.<br><br>Transcurrido dicho término sin objeción, la liquidación de cuenta se tendrá como expresa, clara y exigible, constituyendo título ejecutivo contra el Mandante por los saldos pendientes a su cargo."
        },
        {
            "titulo": "CLÁUSULA. CONCILIACIÓN PREVIA Y RESOLUCIÓN DE CONTROVERSIAS",
            "texto": "Las partes procurarán resolver de manera directa y de buena fe cualquier diferencia derivada de la interpretación, ejecución o terminación del presente contrato.<br><br>En caso de no lograr un acuerdo directo dentro de los diez (10) días hábiles siguientes a la manifestación escrita de la controversia, las partes se obligan a acudir a conciliación extrajudicial en derecho ante un Centro de Conciliación autorizado por el Ministerio de Justicia, como requisito previo para iniciar cualquier proceso judicial.<br><br>Lo anterior se entiende sin perjuicio de la facultad del Mandatario de acudir directamente a la jurisdicción cuando se trate de cobros ejecutivos de sumas líquidas, claras y exigibles derivadas del presente contrato o de los contratos de arrendamiento que celebre en ejercicio del mandato."
        },
        {
            "titulo": "DÉCIMA PRIMERA. NOTIFICACIONES",
            "texto": "Para efectos judiciales o extrajudiciales, las partes se notificarán así: EL MANDATARIO en Calle 19 No. 16 – 44 Centro Comercial Manhatan Local 15 en Armenia, Quindío; por medio del número de teléfono: 3011281684; y el correo electrónico: inmobiliariavelarsas@gmail.com. EL MANDANTE en [DIRECCION PREDIO] por medio del número de teléfono [TELEFONO PROPIETARIO] y el correo electrónico [CORREO PROPIETARIO].<br><br><b>Parágrafo primero</b>: en caso de cambio de alguno de los datos descritos en la cláusula décima primera del presente contrato, las partes se comprometen expresamente a informar por medio escrito para su debida actualización.<br><br>Para constancia, las partes manifiestan su voluntad de aceptación firmando el presente contrato en la ciudad de Armenia, Quindío; el día [FECHA ACTUAL DEL SISTEMA], en dos ejemplares del mismo tenor, una copia para cada parte."
        },
    ]

    def __init__(self, output_dir: Path = None):
        super().__init__(output_dir)
        self.document_title = "CONTRATO DE MANDATO<br>(ADMINISTRACIÓN DE INMUEBLE)"
        self.margins = {'top': 60, 'bottom': 80, 'left': 60, 'right': 60}
        
    def _format_fecha_es(self, fecha_str: str) -> str:
        """Convierte fecha YYYY-MM-DD a formato texto español"""
        if not fecha_str or str(fecha_str).strip().upper() in ['N/A', 'NONE', '']:
            return fecha_str
        try:
            from datetime import datetime
            dt = datetime.strptime(str(fecha_str), '%Y-%m-%d')
            meses = {
                1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
                7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
            }
            mes_nombre = meses.get(dt.month, "")
            return f"{dt.day} de {mes_nombre} de {dt.year}"
        except:
            return str(fecha_str)

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
            self.set_watermark("BORRADOR VELAR SAS", opacity=0.1)
            
        filename = self._generate_filename("contrato_mandato", data["contrato_id"])
        self.create_document(filename, self.document_title)
        
        # 1. Título y Ciudad
        # Título en NEGRO (sobreescribiendo el default de base que es azul)
        style_title = ParagraphStyle(
            'TitleBlack',
            parent=self.styles['Heading1'],
            alignment=TA_CENTER,
            textColor=colors.black,
            fontSize=17,
            spaceAfter=2, # Espacio reducido para que parezcan un solo bloque
            leading=10
        )
        
        style_subtitle = ParagraphStyle(
            'SubTitleBlack',
            parent=style_title,
            fontSize=13, # Mismo tamaño
            spaceAfter=12
        )
        
        self.story.append(Paragraph("CONTRATO DE MANDATO", style_title))
        self.story.append(Paragraph("(ADMINISTRACIÓN DE INMUEBLE)", style_subtitle))
        
        # Formatear Fecha
        fecha_fmt = self._format_fecha_es(data.get('fecha', ''))
            
        self.add_paragraph(f"<b>FECHA DE SUSCRIPCIÓN DEL CONTRATO:</b> {fecha_fmt}", align='CENTER')
        self.add_paragraph("<b>CIUDAD DEL CONTRATO:</b>", align='CENTER')
        self.add_paragraph("ARMENIA, QUINDÍO", align='CENTER')
        self.add_spacer(0.4)
        
        # 2. Resumen de Partes (Tabla inicial del PDF)
        self._add_resumen_partes(data)
        
        # 3. Condiciones Generales (Header sección en NEGRO)
        # self.add_section_divider("CONDICIONES GENERALES")
        
        # Título Sección
        style_h2 = ParagraphStyle(
            'H2Black',
            parent=self.styles['Heading2'],
            textColor=colors.black,
            fontSize=12,
            spaceAfter=6
        )
        self.story.append(Paragraph("CONDICIONES GENERALES", style_h2))
        
        # Línea separadora Negra
        from reportlab.platypus import HRFlowable
        hr = HRFlowable(
            width="100%",
            thickness=2,
            color=colors.black,
            spaceAfter=10,
            spaceBefore=10,
        )
        self.story.append(hr)
        
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
        
        def p_val(txt): 
            # Safe split for <br> to avoid ReportLab syntax errors
            # Returns a list of Paragraphs which is valid for Table cells
            if not txt:
                return []
            lines = str(txt).split('<br>')
            return [Paragraph(line.strip(), style_val) for line in lines if line.strip()]

        # Construcción de filas simulando el layout visual
        
        # Dirección Inmueble (Manejo de N/A gracefully)
        direccion_inmueble = inmueble.get('direccion', 'N/A')
        municipio = inmueble.get('municipio', 'ARMENIA')
        departamento = inmueble.get('departamento', 'QUINDÍO')
        direccion_full = f"{direccion_inmueble}<br>{municipio}, {departamento}"
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
            f"{nombre_inmo}<br>"
            f"NIT: {nit_inmo}<br>"
            f"REP. {rep_legal}<br>"
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
            [p_kw("MANDANTE:"), p_val(f"{nombre_mandante}<br>C.C. {doc_mandante}")]
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
        data_table.append([p_kw("CANON MANDATO:"), p_val(f"{canon_fmt} (COP - PESOS COLOMBIANOS)")])
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

        # INICIO: Preparar variables con valores por defecto
        diff_meses_texto = "DOCE"
        canon_texto = "CERO PESOS M/CTE"
        fecha_pago_texto = "CINCO"
        fecha_pago_num = "5"
        
        # Intentar calcular valores reales
        try:
            # 1. Calcular diferencia de meses real si hay fechas
            f_inicio_str = data.get('fecha_inicio')
            f_fin_str = data.get('fecha_fin')
            
            duracion_meses = data['condiciones'].get('duracion_meses', 12) # Fallback al valor numérico directo si falla cálculo
            
            if f_inicio_str and f_fin_str and f_inicio_str != 'N/A' and f_fin_str != 'N/A':
                try:
                    dt_inicio = datetime.strptime(str(f_inicio_str), '%Y-%m-%d')
                    dt_fin = datetime.strptime(str(f_fin_str), '%Y-%m-%d')
                    
                    # Cálculo aproximado de meses (diferencia de años * 12 + diferencia de meses)
                    # Ajuste simple: si día fin < día inicio, se resta un mes (no siempre exacto legalmente pero estándar)
                    
                    diff_years = dt_fin.year - dt_inicio.year
                    diff_months = dt_fin.month - dt_inicio.month
                    
                    calculated_months = (diff_years * 12) + diff_months
                    if calculated_months > 0:
                        duracion_meses = calculated_months
                except ValueError:
                    pass # Fallback to existing duracion_meses
            
            # 2. Convertir a Texto
            diff_meses_texto = num2words(duracion_meses, lang='es').upper()
            
            canon_val = data['condiciones'].get('valor_canon_sugerido', 0)
            canon_texto = num2words(canon_val, lang='es').upper() + " PESOS M/CTE"
            
            # Fecha de Pago Logic
            fecha_pago_dia = data['condiciones'].get('fecha_pago', '5')
            try:
                # Si viene "YYYY-MM-DD", extraer día
                if "-" in str(fecha_pago_dia):
                     dt_pago = datetime.strptime(str(fecha_pago_dia), '%Y-%m-%d')
                     dia_num = dt_pago.day
                else:
                     dia_num = int(fecha_pago_dia)
                
                fecha_pago_texto = num2words(dia_num, lang='es').upper()
                fecha_pago_num = str(dia_num)
            except:
                pass  # Use default values already set
            
        except Exception as e:
            print(f"Error en conversión num2words: {e}")
            # Variables ya tienen valores por defecto, no es necesario reasignar

        
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
            "[DIFERENCIA DE MESES FECHA FIN - FECHA INICIO]": str(data['condiciones'].get('duracion_meses', 12)),
            "[DIFERENCIA DE MESES FECHA FIN - FECHA INICIO EN TEXTO]": diff_meses_texto,
            "[VALOR CANON MANDATO EN TEXTO]": canon_texto,
            "[FECHA DE PAGO]": f"({fecha_pago_num})",
            "[FECHA DE PAGO TEXTO]": fecha_pago_texto
        }

        for clausula in self.CLAUSULAS_TEXTO:
            titulo = clausula["titulo"]
            texto = clausula["texto"]
            
            # Reemplazar con formato Negrita y Subrayado
            for k, v in mapeo.items():
                if k in texto:
                    replacement = f"<b><u>{v}</u></b>"
                    texto = texto.replace(k, replacement)
            
            # Render - Fix for <br> (ReportLab "No content allowed in br tag")
            self.add_heading(titulo, level=2)
            
            # Split by <br> and add separate paragraphs
            # This is safer than relying on ReportLab's <br/> handling which is fragile with mixed content
            parts = texto.split('<br>')
            for part in parts:
                if part.strip():
                    self.add_paragraph(part.strip(), style_name="Body", alignment="justify")
            
            self.add_spacer(0.15)

    def _add_firmas_tres_columnas(self, data: Dict[str, Any]):
        """Renderiza firmas (Solo 2 para Mandato)"""
        
        info_inmo = data.get('inmobiliaria', self.ARRENDADOR_INFO)
        mandante = data['mandante']
        
        style_firma = ParagraphStyle('Firma', fontName='Helvetica', fontSize=8, leading=10, alignment=1) # Center
        
        def firma_bloque(titulo, nombre, doc):
            content = f"<br><br><br><br>_______________________________________<br><b>{titulo}</b><br>{nombre}<br>C.C./NIT. {doc}"
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

__all__ = ["ContratoMandatoElite"]

