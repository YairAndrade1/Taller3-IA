"""
cnf_transform.py — Transformaciones a Forma Normal Conjuntiva (CNF).
El pipeline completo to_cnf() llama a todas las transformaciones en orden.
"""

from __future__ import annotations

from src.logic_core import And, Atom, Formula, Not, Or, Implies, Iff


# --- FUNCION GUÍA SUMINISTRADA COMPLETA ---


def eliminate_double_negation(formula: Formula) -> Formula:
    """
    Elimina dobles negaciones recursivamente.

    Transformacion:
        Not(Not(a)) -> a

    Se aplica recursivamente hasta que no queden dobles negaciones.

    Ejemplo:
        >>> eliminate_double_negation(Not(Not(Atom('p'))))
        Atom('p')
        >>> eliminate_double_negation(Not(Not(Not(Atom('p')))))
        Not(Atom('p'))
    """
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        if isinstance(formula.operand, Not):
            return eliminate_double_negation(formula.operand.operand)
        return Not(eliminate_double_negation(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_double_negation(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_double_negation(d) for d in formula.disjuncts))
    return formula


# --- FUNCIONES QUE DEBEN IMPLEMENTAR ---


def eliminate_iff(formula: Formula) -> Formula:
    res = formula
    if isinstance(formula, Atom):
        res = formula
    elif isinstance(formula, Iff):
        arg1 = eliminate_iff(formula.left)
        arg2 = eliminate_iff(formula.right)
        imp1 = Implies(arg1, arg2)
        imp2 = Implies(arg2, arg1)
        res = And(imp1, imp2)
    elif isinstance(formula, Not):
        op = eliminate_iff(formula.operand)
        res = Not(op)
    elif isinstance(formula, And):
        new_args = []
        for c in formula.conjuncts:
            new_args.append(eliminate_iff(c))
        res = And(*new_args)
    elif isinstance(formula, Or):
        new_args = []
        for d in formula.disjuncts:
            new_args.append(eliminate_iff(d))
        res = Or(*new_args)
    elif isinstance(formula, Implies):
        a1 = eliminate_iff(formula.antecedent)
        a2 = eliminate_iff(formula.consequent)
        res = Implies(a1, a2)
    return res


def eliminate_implication(formula: Formula) -> Formula:
    ans = formula
    if isinstance(formula, Atom):
        ans = formula
    elif isinstance(formula, Implies):
        ant = eliminate_implication(formula.antecedent)
        cons = eliminate_implication(formula.consequent)
        not_ant = Not(ant)
        ans = Or(not_ant, cons)
    elif isinstance(formula, Not):
        val = eliminate_implication(formula.operand)
        ans = Not(val)
    elif isinstance(formula, And):
        lista = []
        for x in formula.conjuncts:
            lista.append(eliminate_implication(x))
        ans = And(*lista)
    elif isinstance(formula, Or):
        lista = []
        for x in formula.disjuncts:
            lista.append(eliminate_implication(x))
        ans = Or(*lista)
    return ans


def push_negation_inward(formula: Formula) -> Formula:
    final = formula
    if isinstance(formula, Atom):
        final = formula
    elif isinstance(formula, Not):
        op = formula.operand
        if isinstance(op, Atom):
            final = formula
        elif isinstance(op, Not):
            final = push_negation_inward(op.operand)
        elif isinstance(op, And):
            new_ops = []
            for c in op.conjuncts:
                neg = Not(c)
                new_ops.append(push_negation_inward(neg))
            final = Or(*new_ops)
        elif isinstance(op, Or):
            new_ops = []
            for d in op.disjuncts:
                neg = Not(d)
                new_ops.append(push_negation_inward(neg))
            final = And(*new_ops)
    elif isinstance(formula, And):
        recs = []
        for c in formula.conjuncts:
            recs.append(push_negation_inward(c))
        final = And(*recs)
    elif isinstance(formula, Or):
        recs = []
        for d in formula.disjuncts:
            recs.append(push_negation_inward(d))
        final = Or(*recs)
    return final


def distribute_or_over_and(formula: Formula) -> Formula:
    res = formula
    if isinstance(formula, Atom):
        res = formula
    elif isinstance(formula, Not):
        res = formula
    elif isinstance(formula, And):
        new_c = []
        for c in formula.conjuncts:
            new_c.append(distribute_or_over_and(c))
        res = And(*new_c)
    elif isinstance(formula, Or):
        new_d = []
        for d in formula.disjuncts:
            new_d.append(distribute_or_over_and(d))
        fixed_or = Or(*new_d)
        and_idx = -1
        for i in range(len(new_d)):
            if isinstance(new_d[i], And):
                and_idx = i
                break
        if and_idx != -1:
            target_and = new_d[and_idx]
            others = []
            for i in range(len(new_d)):
                if i != and_idx:
                    others.append(new_d[i])
            if len(others) == 1:
                A = others[0]
            else:
                A = Or(*others)
            new_conjs = []
            for arg_b in target_and.conjuncts:
                new_conjs.append(distribute_or_over_and(Or(A, arg_b)))
            res = And(*new_conjs)
        else:
            res = fixed_or
    return res


def flatten(formula: Formula) -> Formula:
    ret = formula
    if isinstance(formula, Atom):
        ret = formula
    elif isinstance(formula, Not):
        op = flatten(formula.operand)
        ret = Not(op)
    elif isinstance(formula, And):
        new_l = []
        for c in formula.conjuncts:
            f = flatten(c)
            if isinstance(f, And):
                for sub in f.conjuncts:
                    new_l.append(sub)
            else:
                new_l.append(f)
        if len(new_l) == 1:
            ret = new_l[0]
        else:
            ret = And(*new_l)
    elif isinstance(formula, Or):
        new_l = []
        for d in formula.disjuncts:
            f = flatten(d)
            if isinstance(f, Or):
                for sub in f.disjuncts:
                    new_l.append(sub)
            else:
                new_l.append(f)
        if len(new_l) == 1:
            ret = new_l[0]
        else:
            ret = Or(*new_l)
    return ret


# --- PIPELINE COMPLETO ---


def to_cnf(formula: Formula) -> Formula:
    """
    [DADO] Pipeline completo de conversion a CNF.

    Aplica todas las transformaciones en el orden correcto:
    1. Eliminar bicondicionales (Iff)
    2. Eliminar implicaciones (Implies)
    3. Mover negaciones hacia adentro (Not)
    4. Eliminar dobles negaciones (Not Not)
    5. Distribuir Or sobre And
    6. Aplanar conjunciones/disyunciones

    Ejemplo:
        >>> to_cnf(Implies(Atom('p'), And(Atom('q'), Atom('r'))))
        And(Or(Not(Atom('p')), Atom('q')), Or(Not(Atom('p')), Atom('r')))
    """
    formula = eliminate_iff(formula)
    formula = eliminate_implication(formula)
    formula = push_negation_inward(formula)
    formula = eliminate_double_negation(formula)
    formula = distribute_or_over_and(formula)
    formula = flatten(formula)
    return formula
