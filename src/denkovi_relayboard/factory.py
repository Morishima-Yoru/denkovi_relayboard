from typing import Dict, List, Optional, Tuple, Type, Union
from typing_extensions import Literal
import logging

from .definitions.interfaces import IDenkoviRelayBoard
from .definitions.structures import DiscoveredDevice
from .backends import FTD2XXBackend, VCPBackend, MCP2200Backend, PyFtdiBackend
from .implements.denkovi_16ch import DenkoviRelayBoard16Ch
from .implements.denkovi_4ch import (
    DenkoviRelayBoard4ChFT422,
    DenkoviRelayBoard4ChMCP2200,
)
from .implements.denkovi_8ch import DenkoviRelayBoard8Ch

_logger = logging.getLogger(__name__)

PossibleBackendT = Literal["ftd2xx", "vcp", "mcp2200", "pyftdi"]
PossibleBackendClassT = Union[
    Type[FTD2XXBackend], Type[VCPBackend], Type[MCP2200Backend], Type[PyFtdiBackend]
]
PossibleRelayBoardT = Literal[
    "denkovi_16ch", "denkovi_8ch", "denkovi_4ch_ftd2xx", "denkovi_4ch_mcp2200"
]
PossibleRelayBoardClassT = Union[
    Type[DenkoviRelayBoard16Ch],
    Type[DenkoviRelayBoard8Ch],
    Type[DenkoviRelayBoard4ChFT422],
    Type[DenkoviRelayBoard4ChMCP2200],
]


class RelayBoardFactory:
    ACCEPTABLE_BACKEND_MAP: Dict[PossibleRelayBoardClassT, Tuple[PossibleBackendClassT, ...]] = {
        DenkoviRelayBoard16Ch: (FTD2XXBackend, VCPBackend, PyFtdiBackend),
        DenkoviRelayBoard8Ch: (FTD2XXBackend, PyFtdiBackend),
        DenkoviRelayBoard4ChFT422: (FTD2XXBackend,),
        DenkoviRelayBoard4ChMCP2200: (MCP2200Backend,),
    }
    BACKEND_REGISTRY: Dict[PossibleBackendT, PossibleBackendClassT] = {
        "ftd2xx": FTD2XXBackend,
        "vcp": VCPBackend,
        "mcp2200": MCP2200Backend,
        "pyftdi": PyFtdiBackend,
    }

    BOARD_REGISTRY: Dict[PossibleRelayBoardT, PossibleRelayBoardClassT] = {
        "denkovi_16ch": DenkoviRelayBoard16Ch,
        "denkovi_8ch": DenkoviRelayBoard8Ch,
        "denkovi_4ch_ftd2xx": DenkoviRelayBoard4ChFT422,
        "denkovi_4ch_mcp2200": DenkoviRelayBoard4ChMCP2200,
    }

    def create_relay_board(
        self,
        backend_type: PossibleBackendT,
        board_type: PossibleRelayBoardT,
        device_address: Optional[str] = None,
        serial_number: Optional[str] = None,
        timeout: int = 5000,
    ) -> IDenkoviRelayBoard:
        """
        Create a relay board instance.

        Args:
            backend_type (PossibleBackendT): The type of the backend.
            board_type (PossibleRelayBoardT): The type of the board.
            device_address (str | None): The address of the device.
            serial_number (str | None): The serial number of the device.
            timeout (int): The timeout of the device.

        Returns:
            IDenkoviRelayBoard: A relay board instance.

        Raises:
            ValueError: If the backend type or board type is not supported.
        """
        # Checking backend type
        if backend_type not in self.BACKEND_REGISTRY:
            raise ValueError(
                f"Unsupported backend type: {backend_type}. "
                f"Supported types: {list(self.BACKEND_REGISTRY.keys())}"
            )

        # Checking board type
        if board_type not in self.BOARD_REGISTRY:
            raise ValueError(
                f"Unsupported board type: {board_type}. "
                f"Supported types: {list(self.BOARD_REGISTRY.keys())}"
            )

        # Creating backend instance
        backend_clazz = self.BACKEND_REGISTRY[backend_type]
        backend = backend_clazz()

        # Creating board instance
        board_clazz = self.BOARD_REGISTRY[board_type]

        # Checking if the backend type is supported by the board type
        if backend_clazz not in self.ACCEPTABLE_BACKEND_MAP[board_clazz]:
            backend_class_to_name = {v: k for k, v in self.BACKEND_REGISTRY.items()}
            supported_backend_names = [
                backend_class_to_name[backend_class]
                for backend_class in self.ACCEPTABLE_BACKEND_MAP[board_clazz]
            ]
            raise ValueError(
                f"Unsupported backend type: {backend_type} for board type: {board_type}. "
                f"Supported types: {supported_backend_names}"
            )

        # Creating board instance
        board = board_clazz(
            backend=backend,  # type: ignore
            device_address=device_address,
            serial_number=serial_number,
            timeout=timeout,
        )

        return board

    def list_potential_boards(self) -> List[DiscoveredDevice]:
        """
        List all available relay boards from all backends.

        Returns:
            list[DiscoveredDevice]: A list of available devices.
        """
        result: List[DiscoveredDevice] = []
        for backend_type, backend_clazz in self.BACKEND_REGISTRY.items():
            try:
                devices = backend_clazz.list_potential_devices()
                result.extend(devices)
            except Exception as e:
                _logger.warning(
                    f"Failed to list devices for backend {backend_type}: {e}"
                )
                result.extend([])
        return result


create_relay_board = RelayBoardFactory().create_relay_board
list_potential_boards = RelayBoardFactory().list_potential_boards
