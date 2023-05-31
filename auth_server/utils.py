
def raise_on_empty(**kwargs):
    """Raises ValueError exception if at least one value of the
    key in kwargs dictionary is None
    """
    for key, value in kwargs.items():
        if value is None:
            raise ValueError(
                 f"{key} is expected to be non-empty"
            )
