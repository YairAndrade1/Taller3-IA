"""
collar_maria_antonieta.py — El Collar de María Antonieta: Robo en el Louvre

El icónico collar de María Antonieta, valuado en 15 millones de dólares, desapareció
del Museo del Louvre durante una subasta de gala. Las cámaras de seguridad captaron a
un "portero" que nunca figuró en la nómina del museo. El verdadero portero, Benoît,
registró su salida antes de que ocurriera el robo. Juliette, hija del millonario
Pellegrini, asistió a la gala pero tiene coartada verificada por múltiples testigos.
Pellegrini mismo reclamaba el collar como propiedad familiar, pero no pudo probar su
inocencia. Assane, un misterioso asistente a la subasta, conocía el plano interno del
museo y no tiene coartada verificada.

Las reglas del caso son las siguientes: quien tiene registro oficial de salida está
descartado como culpable; quien tiene coartada verificada por testigos independientes
también está descartado. El testimonio de un sospechoso descartado es confiable.
Quien usa un disfraz que le otorga acceso a áreas restringidas tiene capacidad operativa
para cometer el robo. Finalmente, quien combina capacidad operativa, motivo personal y
ausencia de coartada verificada es culpable del robo.
"""

from src.crime_case import CrimeCase, QuerySpec
from src.predicate_logic import ExistsGoal, KnowledgeBase, Predicate, Rule, Term


def crear_kb() -> KnowledgeBase:
    """Construye la KB según la narrativa del módulo."""
    kb = KnowledgeBase()

    # Constantes del caso
    assane = Term("assane")
    pellegrini = Term("pellegrini")
    juliette = Term("juliette")
    benoit = Term("benoit")
    identidad_benoit = Term("identidad_benoit")

    # Hechos base
    kb.add_fact(Predicate("uso_disfraz", (assane, identidad_benoit)))
    kb.add_fact(Predicate("acceso_restringido", (identidad_benoit,)))
    kb.add_fact(Predicate("motivo_personal", (assane,)))
    kb.add_fact(Predicate("alibi_registro", (benoit,)))
    kb.add_fact(Predicate("alibi_verificado", (juliette,)))
    kb.add_fact(Predicate("sin_coartada", (assane,)))
    kb.add_fact(Predicate("acusa", (benoit, assane)))

    # Reglas
    kb.add_rule(
        Rule(
            head=Predicate("descartado", (Term("$X"),)),
            body=(Predicate("alibi_registro", (Term("$X"),)),),
        )
    )
    kb.add_rule(
        Rule(
            head=Predicate("descartado", (Term("$X"),)),
            body=(Predicate("alibi_verificado", (Term("$X"),)),),
        )
    )
    kb.add_rule(
        Rule(
            head=Predicate("capacidad_operativa", (Term("$X"),)),
            body=(
                Predicate("uso_disfraz", (Term("$X"), Term("$Y"))),
                Predicate("acceso_restringido", (Term("$Y"),)),
            ),
        )
    )
    kb.add_rule(
        Rule(
            head=Predicate("testimonio_confiable", (Term("$X"), Term("$Y"))),
            body=(
                Predicate("descartado", (Term("$X"),)),
                Predicate("acusa", (Term("$X"), Term("$Y"))),
            ),
        )
    )
    kb.add_rule(
        Rule(
            head=Predicate("culpable", (Term("$X"),)),
            body=(
                Predicate("capacidad_operativa", (Term("$X"),)),
                Predicate("motivo_personal", (Term("$X"),)),
                Predicate("sin_coartada", (Term("$X"),)),
            ),
        )
    )

    return kb


CASE = CrimeCase(
    id="collar_maria_antonieta",
    title="El Collar de María Antonieta: Robo en el Louvre",
    suspects=("assane", "pellegrini", "juliette", "benoit"),
    narrative=__doc__,
    description=(
        "El collar de María Antonieta desapareció del Louvre durante una subasta de gala. "
        "Un falso portero accedió a la bóveda usando el disfraz de Benoît. "
        "Razona sobre coartadas, capacidad operativa y el testimonio del portero real "
        "para descubrir al ladrón inspirado en Arsène Lupin."
    ),
    create_kb=crear_kb,
    queries=(
        QuerySpec(
            description="¿Benoît está descartado como culpable?",
            goal=Predicate("descartado", (Term("benoit"),)),
        ),
        QuerySpec(
            description="¿Juliette está descartada como culpable?",
            goal=Predicate("descartado", (Term("juliette"),)),
        ),
        QuerySpec(
            description="¿Assane tiene capacidad operativa para el robo?",
            goal=Predicate("capacidad_operativa", (Term("assane"),)),
        ),
        QuerySpec(
            description="¿El testimonio de Benoît contra Assane es confiable?",
            goal=Predicate("testimonio_confiable", (Term("benoit"), Term("assane"))),
        ),
        QuerySpec(
            description="¿Assane es culpable del robo?",
            goal=Predicate("culpable", (Term("assane"),)),
        ),
        QuerySpec(
            description="¿Existe algún sospechoso descartado?",
            goal=ExistsGoal(
                "$X", Predicate("descartado", (Term("$X"),))
            ),
        ),
    ),
)
