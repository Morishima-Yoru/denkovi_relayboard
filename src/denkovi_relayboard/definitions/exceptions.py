class DenkoviRelayBoardException(Exception):
    pass


class DenkoviRelayBoardTimeoutException(DenkoviRelayBoardException):
    pass


class DenkoviRelayBoardStateOverflowException(DenkoviRelayBoardException):
    def __init__(self, max_channel: int) -> None:
        super().__init__(f"State overflow: max channel is {max_channel}")
