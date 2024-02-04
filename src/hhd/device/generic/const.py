from hhd.controller import Axis, Button, Configuration
from hhd.controller.physical.evdev import B, to_map

DEFAULT_MAPPINGS: dict[str, tuple[Axis, str | None, float, float | None]] = {
    "accel_x": ("accel_z", "accel", 1, 3),
    "accel_y": ("accel_x", "accel", 1, 3),
    "accel_z": ("accel_y", "accel", 1, 3),
    "anglvel_x": ("gyro_z", "anglvel", -1, None),
    "anglvel_y": ("gyro_x", "anglvel", -1, None),
    "anglvel_z": ("gyro_y", "anglvel", -1, None),
    "timestamp": ("gyro_ts", None, 1, None),
}

BTN_MAPPINGS: dict[int, str] = {
    # Volume buttons come from the same keyboard
    B("KEY_VOLUMEUP"): "key_volumeup",
    B("KEY_VOLUMEDOWN"): "key_volumedown",
    #
    # AOKZOE A1 mappings And onexplayer mini pro mappings
    #
    # Turbo Button [29, 56, 125] KEY_LEFTCTRL + KEY_LEFTALT + KEY_LEFTMETA
    B("KEY_LEFTALT"): "share",
    # Short press orange [32, 125] KEY_D + KEY_LEFTMETA
    B("KEY_D"): "mode",
    # KB Button [24, 97, 125]  KEY_O + KEY_RIGHTCTRL + KEY_LEFTMETA
    B("KEY_O"): "extra_l1",
    #
    # Loki Max
    #
    B("KEY_T"): "share",  # T + LCTRL + LSHFT + LALT
}

AYANEO_DEFAULT_MAPPINGS: dict[str, tuple[Axis, str | None, float, float | None]] = {
    "accel_x": ("accel_z", "accel", 1, 3),
    "accel_y": ("accel_x", "accel", 1, 3),
    "accel_z": ("accel_y", "accel", 1, 3),
    "anglvel_x": ("gyro_z", "anglvel", -1, None),
    "anglvel_y": ("gyro_x", "anglvel", -1, None),
    "anglvel_z": ("gyro_y", "anglvel", -1, None),
    "timestamp": ("gyro_ts", None, 1, None),
}

AYANEO_AIR_PLUS_MAPPINGS: dict[str, tuple[Axis, str | None, float, float | None]] = {
    "accel_x": ("accel_z", "accel", 1, 3),
    "accel_y": ("accel_x", "accel", 1, 3),
    "accel_z": ("accel_y", "accel", 1, 3),
    "anglvel_x": ("gyro_z", "anglvel", 1, None),
    "anglvel_y": ("gyro_x", "anglvel", -1, None),
    "anglvel_z": ("gyro_y", "anglvel", 1, None),
    "timestamp": ("gyro_ts", None, 1, None),
}

AYANEO_BTN_MAPPINGS: dict[int, str] = {
    # Volume buttons come from the same keyboard
    B("KEY_VOLUMEUP"): "key_volumeup",
    B("KEY_VOLUMEDOWN"): "key_volumedown",
    # Air Plus mappings
    B("KEY_F17"): "mode",  # Big Button
    B("KEY_D"): "share",  # Small Button
    B("KEY_F15"): "extra_l1",  # LC Button
    B("KEY_F16"): "extra_r1",  # RC Button
    # NEXT mappings
    B("KEY_F12"): "mode",  # Big Button [[96, 105, 133], [88, 97, 125]]
    # B("KEY_D"): "share", # Small Button [[40, 133], [32, 125]]
    # 2021 Mappings
    B("KEY_DELETE"): "share",  # TM Button [97,100,111]
    B("KEY_ESC"): "extra_l1",  # ESC Button [1]
    B("KEY_O"): "extra_l2",  # KB Button [97, 24, 125]
    # B("KEY_LEFTMETA"): "extra_r1", # Win Button [125], Conflict with KB Button
}

AYA_DEFAULT_CONF = {
    "hrtimer": True,
    "btn_mapping": AYANEO_BTN_MAPPINGS,
    "mapping": AYANEO_DEFAULT_MAPPINGS,
}

CONFS = {
    # Aokzoe
    "AOKZOE A1 AR07": {"name": "AOKZOE A1", "hrtimer": True},
    "AOKZOE A1 Pro": {"name": "AOKZOE A1 Pro", "hrtimer": True},
    # Onexplayer
    "ONEXPLAYER Mini Pro": {"name": "ONEXPLAYER Mini Pro", "hrtimer": True},
    # Ayn
    "Loki Max": {"name": "Loki Max", "hrtimer": True},
    # Ayaneo
    "AIR Plus": {
        "name": "AYANEO AIR Plus",
        **AYA_DEFAULT_CONF,
        "mapping": AYANEO_AIR_PLUS_MAPPINGS,
    },
    "AYANEO 2": {"name": "AYANEO 2", **AYA_DEFAULT_CONF},
    "AYANEO 2S": {"name": "AYANEO S2", **AYA_DEFAULT_CONF},
    "GEEK": {"name": "AYANEO GEEK", **AYA_DEFAULT_CONF},
    "GEEK 1S": {"name": "AYANEO GEEK 1S", **AYA_DEFAULT_CONF},
}


def get_default_config(product_name: str, manufacturer: str):
    out = {
        "name": product_name,
        "manufacturer": manufacturer,
        "hrtimer": True,
        "untested": True,
    }

    if manufacturer == "AYA":
        out["btn_mapping"] = AYANEO_BTN_MAPPINGS
        out["mapping"] = AYANEO_DEFAULT_MAPPINGS

    return out
