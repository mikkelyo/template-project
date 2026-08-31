"""Keys used to store request-scoped values in the context registry."""


class ContextKeys:
    """Frozen key names for :class:`template_project.context.Context`.

    Attributes
    ----------
    CURRENT_USER : str
        Slot holding the :class:`CurrentUser` of the in-flight request.
    REQUEST_ID : str
        Slot holding the correlation id of the in-flight request.
    """

    CURRENT_USER: str = "current_user"
    REQUEST_ID: str = "request_id"
