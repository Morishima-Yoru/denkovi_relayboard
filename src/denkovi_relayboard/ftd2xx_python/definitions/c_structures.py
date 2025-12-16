import ctypes as ct


class FT_DEVICE_LIST_INFO_NODE(ct.Structure):
    _fields_ = [
        ("Flags", ct.c_uint32),
        ("Type", ct.c_uint32),
        ("ID", ct.c_uint32),
        ("LocId", ct.c_uint32),
        ("SerialNumber", ct.c_char * 16),
        ("Description", ct.c_char * 64),
        ("ftHandle", ct.c_void_p),
    ]
