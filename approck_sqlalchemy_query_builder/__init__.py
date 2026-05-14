import datetime
import time
from typing import Any, Dict, Iterable, List, cast

import sqlalchemy as sa
from dateutil.parser import parse
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.expression import Select

from approck_sqlalchemy_query_builder.types import Condition, Operator, Query, QueryRule


def build_rule_condition(
    map_columns: Dict[str, sa.Column], rule: QueryRule, skip_unknown_column: bool
) -> ColumnElement[bool] | None:
    column = map_columns.get(rule.id)

    if column is None:
        if skip_unknown_column:
            return None

        raise ValueError(f"Column for '{rule.id}' is not found")

    value = rule.value

    if "DATETIME" in str(column.type).upper():
        if isinstance(value, int):
            if value > time.time():
                value /= 1000.0

            value = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
        elif isinstance(value, (str, bytes)):
            value = parse(value).replace(tzinfo=datetime.timezone.utc)

    if rule.operator == Operator.OP_EQUAL:
        return column == value
    elif rule.operator == Operator.OP_GREATER_THAN:
        return column > value
    elif rule.operator == Operator.OP_LESS_THAN:
        return column < value
    elif rule.operator == Operator.OP_GREATER_THAN_OR_EQUAL:
        return column >= value
    elif rule.operator == Operator.OP_LESS_THAN_OR_EQUAL:
        return column <= value
    elif rule.operator == Operator.OP_NOT_EQUAL:
        return column != value
    elif rule.operator == Operator.OP_IN:
        return column.in_(cast(Iterable[Any], value))
    elif rule.operator == Operator.OP_NOT_IN:
        return column.not_in(cast(Iterable[Any], value))

    raise ValueError(f"Operator '{rule.operator}' is not supported")


def build_condition(
    map_columns: Dict[str, sa.Column], query: Query, skip_unknown_column: bool
) -> ColumnElement[bool] | None:
    clauses: List[ColumnElement[bool]] = []

    for rule in query.rules:
        condition = None

        if isinstance(rule, Query):
            condition = build_condition(map_columns=map_columns, query=rule, skip_unknown_column=skip_unknown_column)
        elif isinstance(rule, QueryRule):
            condition = build_rule_condition(
                map_columns=map_columns, rule=rule, skip_unknown_column=skip_unknown_column
            )

        if condition is not None:
            clauses.append(condition)

    if clauses:
        if query.condition == Condition.OR:
            return sa.or_(*clauses)
        elif query.condition == Condition.AND:
            return sa.and_(*clauses)

    return None


def query_filter(
    statement: Select, map_columns: Dict[str, sa.Column], query: Query, skip_unknown_column: bool = False
) -> Select:
    condition = build_condition(map_columns=map_columns, query=query, skip_unknown_column=skip_unknown_column)

    if condition is not None:
        statement = statement.where(condition)

    return statement
