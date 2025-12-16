from dataclasses import dataclass
from typing_extensions import Self

from .namespace import FTDeviceListInfoNodeFlags, FTDeviceType
from .c_structures import FT_DEVICE_LIST_INFO_NODE


@dataclass
class FTDeviceListInfoNodeStruct:
    flags: FTDeviceListInfoNodeFlags
    type: FTDeviceType
    id: int
    loc_id: int
    serial_number: str
    description: str

    @classmethod
    def from_structure(cls, structure: FT_DEVICE_LIST_INFO_NODE) -> Self:
        return cls(
            flags=FTDeviceListInfoNodeFlags(structure.Flags),
            type=FTDeviceType(structure.Type),
            id=structure.ID,
            loc_id=structure.LocId,
            serial_number=structure.SerialNumber.decode(),
            description=structure.Description.decode(),
        )

    def to_structure(self) -> FT_DEVICE_LIST_INFO_NODE:
        return FT_DEVICE_LIST_INFO_NODE(
            Flags=self.flags.value,
            Type=self.type.value,
            ID=self.id,
            LocId=self.loc_id,
            SerialNumber=self.serial_number.encode(),
            Description=self.description.encode(),
        )
