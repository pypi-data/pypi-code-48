from ..constants import FORMULA_OPERATIONS_GLOBAL, FORMULA_OPERATIONS_VIEWPORT
from ..widget import Widget


def formula_widget(value, operation=None, title=None, description=None, footer=None, is_global=False):
    """Helper function for quickly creating a formula widget.

    Formula widgets calculate aggregated values ('avg', 'max', 'min', 'sum') from numeric columns
    or counts of features ('count') in a dataset.

    A formula widget's aggregations can be calculated on 'global' or 'viewport' based values.
    If you want the values in a formula widget to update on zoom and/or pan, use viewport based aggregations.

    Args:
        value (str): Column name of the numeric value.
        operation (str): attribute for widget's aggregated value ('count', 'avg', 'max', 'min', 'sum').
        title (str, optional): Title of widget.
        description (str, optional): Description text widget placed under widget title.
        footer (str, optional): Footer text placed on the widget bottom.
        is_global (boolean, optional): Account for calculations based on the entire dataset ('global') vs.
            the default of 'viewport' features.

    Returns:
        cartoframes.viz.widget.Widget

    Example:
        >>> formula_widget(
        ...     'column_name',
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer')

        >>> formula_widget(
        ...     'column_name',
        ...     operation='sum',
        ...     title='Widget title',
        ...     description='Widget description',
        ...     footer='Widget footer')

    """
    if isinstance(operation, str):
        operation = operation.lower()
    value = _get_value_expression(operation, value, is_global)
    return Widget('formula', value, title, description, footer)


def _get_value_expression(operation, value, is_global):
    if value == 'count':
        formula_operation = _get_formula_operation(value, is_global)
        return formula_operation + '()'
    elif operation in ['avg', 'max', 'min', 'sum']:
        formula_operation = _get_formula_operation(operation, is_global)
        return formula_operation + '($' + value + ')'
    else:
        return '$' + value


def _get_formula_operation(operation, is_global):
    if is_global:
        return FORMULA_OPERATIONS_GLOBAL.get(operation)
    else:
        return FORMULA_OPERATIONS_VIEWPORT.get(operation)
