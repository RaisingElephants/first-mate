"""
server/util.py

Utility code
"""
import pyhtml as p


def list_to_checkboxes(
    values: list[str],
    input_name: str,
) -> p.Tag:
    """
    Given a list of possible values, return a collections of
    checkboxes that allows users to select them.
    """

    html_values = [
        p.p(
            p.input(type="checkbox", name=input_name, id=value, value=value),
            p.label(for_=value)(value),
        )
        for value in values
    ]

    return p.div(html_values)
