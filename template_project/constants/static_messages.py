"""User-facing strings, kept out of the code that emits them."""


class StaticMessages:
    """Messages returned to callers or written to logs.

    Attributes
    ----------
    HEALTH_OK : str
        Body of a successful health probe.
    MISSING_CURRENT_USER : str
        Raised when a request reaches a use case without an identified caller.
    INVALID_API_KEY : str
        Returned when the bearer token does not match the configured key.
    EMPTY_PROMPT : str
        Returned when the caller submits a blank prompt.
    COMPLETION_FAILED : str
        Returned when the language model could not produce an answer.
    """

    HEALTH_OK: str = "OK"
    MISSING_CURRENT_USER: str = "No authenticated user is bound to this request."
    INVALID_API_KEY: str = "The supplied API key is not valid."
    EMPTY_PROMPT: str = "The prompt must not be empty."
    COMPLETION_FAILED: str = "The language model did not return an answer."
