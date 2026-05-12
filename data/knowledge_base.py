# Base de conocimiento hardcodeada con documentos LangChain
# Contiene fragmentos sobre próceres de la independencia latinoamericana

from langchain_core.documents import Document

DOCUMENTS = [
    # ── Simón Bolívar ────────────────────────────────────────────────────────
    Document(
        page_content=(
            "Simón Bolívar nació el 24 de julio de 1783 en Caracas, Venezuela. "
            "Fue hijo de Juan Vicente Bolívar y María de la Concepción Palacios. "
            "Quedó huérfano a los nueve años y fue educado por tutores privados, "
            "entre ellos el ilustrado Simón Rodríguez, quien le inculcó los ideales "
            "de la Ilustración y de Rousseau."
        ),
        metadata={"personaje": "Simón Bolívar", "tema": "nacimiento y juventud"},
    ),
    Document(
        page_content=(
            "Simón Bolívar lideró la Batalla de Boyacá el 7 de agosto de 1819, "
            "victoria decisiva que selló la independencia de la Nueva Granada "
            "(actual Colombia). Tres días después entró triunfante a Bogotá. "
            "Esta batalla es considerada uno de los hitos más importantes de las "
            "guerras de independencia hispanoamericanas."
        ),
        metadata={"personaje": "Simón Bolívar", "tema": "batallas"},
    ),
    Document(
        page_content=(
            "En la Batalla de Carabobo (24 de junio de 1821) Bolívar derrotó "
            "definitivamente al ejército realista español en Venezuela, consolidando "
            "la independencia venezolana. La Batalla de Pichincha (24 de mayo de 1822), "
            "dirigida por su lugarteniente Antonio José de Sucre, liberó Ecuador. "
            "Bolívar también fue protagonista de la Batalla de Junín (1824) en Perú."
        ),
        metadata={"personaje": "Simón Bolívar", "tema": "batallas"},
    ),
    Document(
        page_content=(
            "Bolívar proclamó la independencia de Venezuela en 1811 y fue el "
            "artífice de la liberación de Venezuela, Colombia, Ecuador, Perú y Bolivia. "
            "En 1819 fundó la República de Gran Colombia, que unía a Venezuela, "
            "Colombia y Ecuador bajo un mismo gobierno, con él como presidente. "
            "Su visión era una gran confederación de naciones latinoamericanas."
        ),
        metadata={"personaje": "Simón Bolívar", "tema": "independencia y política"},
    ),
    Document(
        page_content=(
            "El legado de Simón Bolívar es inmenso: liberó seis naciones, abolió "
            "la esclavitud en los territorios que controló, promovió constituciones "
            "republicanas y convocó el Congreso Anfictiónico de Panamá (1826) para "
            "unir a los pueblos hispanoamericanos. Es conocido como 'El Libertador' "
            "y su figura es símbolo de libertad e integración en América Latina."
        ),
        metadata={"personaje": "Simón Bolívar", "tema": "legado"},
    ),
    Document(
        page_content=(
            "Simón Bolívar murió el 17 de diciembre de 1830 en Santa Marta, "
            "Colombia, aquejado de tuberculosis. Sus últimos años estuvieron marcados "
            "por la desintegración de la Gran Colombia, los conflictos políticos y "
            "su renuncia a la presidencia. Sus últimas palabras reflejaron su "
            "desilusión: 'He arado en el mar'. Tenía 47 años."
        ),
        metadata={"personaje": "Simón Bolívar", "tema": "muerte"},
    ),
    # ── José de San Martín ───────────────────────────────────────────────────
    Document(
        page_content=(
            "José de San Martín nació el 25 de febrero de 1778 en Yapeyú, en el "
            "Virreinato del Río de la Plata (actual Argentina). Fue militar y "
            "estadista, conocido como el 'Libertador del Sur'. Lideró la independencia "
            "de Argentina, Chile y Perú. Su cruce de los Andes en 1817 junto al "
            "Ejército de los Andes es una de las gestas militares más notables de "
            "la historia americana."
        ),
        metadata={"personaje": "José de San Martín", "tema": "vida y logros"},
    ),
    Document(
        page_content=(
            "San Martín y Bolívar se reunieron en la Entrevista de Guayaquil "
            "en julio de 1822, encuentro cuyo contenido exacto permanece en el misterio. "
            "Tras esa reunión, San Martín renunció al mando del ejército libertador "
            "del Perú y se retiró a Europa, donde vivió en el exilio hasta su muerte "
            "en Boulogne-sur-Mer, Francia, el 17 de agosto de 1850."
        ),
        metadata={"personaje": "José de San Martín", "tema": "retiro y muerte"},
    ),
    # ── Antonio José de Sucre ────────────────────────────────────────────────
    Document(
        page_content=(
            "Antonio José de Sucre nació el 3 de febrero de 1795 en Cumaná, "
            "Venezuela. Fue el lugarteniente más destacado de Simón Bolívar y uno "
            "de los generales más brillantes de la independencia suramericana. "
            "Dirigió la Batalla de Ayacucho (9 de diciembre de 1824), que puso fin "
            "al dominio español en América del Sur, siendo considerada la batalla "
            "definitiva de las guerras de independencia."
        ),
        metadata={"personaje": "Antonio José de Sucre", "tema": "vida y batallas"},
    ),
    Document(
        page_content=(
            "Antonio José de Sucre fue el primer presidente de Bolivia (1825-1828), "
            "país que lleva el nombre de Bolívar. Sucre fundó instituciones, promovió "
            "la educación y fue reconocido por su honestidad y capacidad de gobierno. "
            "Fue asesinado el 4 de junio de 1830 en la montaña de Berruecos, Colombia, "
            "a los 35 años. Bolívar lo llamó 'el hombre mejor de América'."
        ),
        metadata={"personaje": "Antonio José de Sucre", "tema": "presidencia y muerte"},
    ),
    # ── Francisco de Paula Santander ────────────────────────────────────────
    Document(
        page_content=(
            "Francisco de Paula Santander nació el 2 de abril de 1792 en Villa del "
            "Rosario de Cúcuta, Nueva Granada (actual Colombia). Fue un destacado "
            "militar y político que participó en la independencia de Colombia. "
            "Colaboró estrechamente con Bolívar durante las guerras de independencia "
            "y fue vicepresidente de la Gran Colombia entre 1821 y 1827, gestionando "
            "el país mientras Bolívar lideraba campañas militares."
        ),
        metadata={"personaje": "Francisco de Paula Santander", "tema": "vida y política"},
    ),
    Document(
        page_content=(
            "Santander fue conocido como 'El Hombre de las Leyes' por su defensa del "
            "estado de derecho y las instituciones republicanas. Tuvo fuertes "
            "discrepancias con Bolívar sobre el modelo de gobierno: Santander "
            "defendía el federalismo y el poder del Congreso, mientras Bolívar "
            "prefería un gobierno centralizado. Fue presidente de Colombia entre "
            "1833 y 1837 y murió en Bogotá el 6 de mayo de 1840."
        ),
        metadata={"personaje": "Francisco de Paula Santander", "tema": "legado y presidencia"},
    ),
]
