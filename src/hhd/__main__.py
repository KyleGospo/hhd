import argparse
import logging
import os
from multiprocessing import Process
from os.path import join
from threading import Condition, Lock
from typing import NamedTuple, Sequence

import pkg_resources
import yaml

from hhd.plugins import Config
from hhd.plugins.settings import Container, HHDSettings, Mode, Setting

from .logging import setup_logger
from .plugins import Config, Emitter, Event, HHDAutodetect, HHDPlugin
from .plugins.settings import merge_settings, parse_settings
from .utils import Context, expanduser, get_context

logger = logging.getLogger(__name__)

CONFIG_DIR = os.environ.get("HHD_CONFIG_DIR", "~/.config/hhd")

ERROR_DELAY = 5


def generate_desc(s: Setting | Container | Mode):
    desc = f"# {s['title']}"
    if h := s.get("hint", None):
        desc += f"\n{h}"

    match s["type"]:
        case "mode":
            desc += f"\nmodes: [{', '.join(map(str, s['modes']))}]"
        case "number":
            desc += f"\nnumerical: ["
            desc += f"{s['min'] if s.get('min', None) is not None else '-inf'}, "
            desc += f"{s['max'] if s.get('max', None) is not None else '+inf'}]"
        case "multiple" | "discrete":
            desc += f"\noptions: [{', '.join(map(str, s['options']))}]"

    if (d := s.get("default", None)) is not None:
        desc += f"\ndefault: {d}"
    return desc


def dump_setting(set: Setting | Container | Mode, prev: Sequence[str], conf: Config):
    out: dict = {"_": generate_desc(set)}

    match set["type"]:
        case "container":
            for child_name, child in set["children"].items():
                out[child_name] = dump_setting(child, [*prev, child_name], conf)
        case "mode":
            m = conf.get([*prev, "mode"], None)
            # Skip writing default values
            if set.get("default", None) == m:
                m = "default"
            out["mode"] = m
            for mode_name, mode in set["modes"].items():
                out[mode_name] = dump_setting(mode, [*prev, mode_name], conf)
        case _:
            m = conf.get(prev, None)
            # Skip writing default values
            if set.get("default", None) == m:
                m = "default"
            out["value"] = m

    return out


def dump_settings(set: HHDSettings, conf: Config):
    out: dict = {"version": 1}
    for sec_name, sec in set.items():
        out[sec_name] = {}
        for cont_name, cnt in sec.items():
            out[sec_name][cont_name] = dump_setting(cnt, [sec_name, cont_name], conf)
    return out


class EmitHolder(Emitter):
    def __init__(self) -> None:
        self._events = []
        self._lock = Lock()
        self._condition = Condition(self._lock)

    def __call__(self, event: Event | Sequence[Event]) -> None:
        with self._lock:
            if isinstance(event, Sequence):
                self._events.extend(event)
            else:
                self._events.append(event)
            self._condition.notify_all()

    def get_events(self, timeout: int = -1):
        with self._lock:
            if not self._events and timeout != -1:
                self._condition.wait()
            ev = self._events
            self._events = []
            return ev


def write_state(conf: Config, ctx: Context):
    state_fn = expanduser(join(CONFIG_DIR, "state.yml"), ctx)
    with open(state_fn, "w") as f:
        yaml.safe_dump(conf.state, f)
    os.chown(state_fn, ctx.euid, ctx.egid)


def read_state(ctx: Context):
    state_fn = expanduser(join(CONFIG_DIR, "state.yml"), ctx)
    try:
        with open(state_fn, "r") as f:
            return Config(yaml.safe_load(f))
    except FileNotFoundError:
        logger.info("State file not found, default settings will be used.")
        return Config({})


def main(user: str | None = None):
    # Setup temporary logger for permission retreival
    ctx = get_context(user)
    if not ctx:
        print(f"Could not get user information. Exiting...")
        return

    detectors: dict[str, HHDAutodetect] = {}
    plugins: dict[str, Sequence[HHDPlugin]] = {}
    try:
        setup_logger(join(CONFIG_DIR, "log"), ctx=ctx)

        for autodetect in pkg_resources.iter_entry_points("hhd.plugins"):
            detectors[autodetect.name] = autodetect.resolve()

        logger.info(f"Found plugin providers: {', '.join(list(detectors))}")

        logger.info(f"Running autodetection...")
        for name, autodetect in detectors.items():
            plugins[name] = autodetect([])

        plugin_str = "Loaded the following plugins:"
        for pkg_name, sub_plugins in plugins.items():
            plugin_str += (
                f"\n  - {pkg_name:>15s}: {', '.join(p.name for p in sub_plugins)}"
            )
        logger.info(plugin_str)

        # Get sorted plugins
        sorted_plugins: Sequence[HHDPlugin] = []
        for plugs in plugins.values():
            sorted_plugins.extend(plugs)
        sorted_plugins.sort(key=lambda x: x.priority)

        if not sorted_plugins:
            logger.error(f"No plugins started, exiting...")
            return

        # Open plugins
        emit = EmitHolder()
        for p in sorted_plugins:
            p.open(emit, ctx)

        # Compile initial configuration
        settings = merge_settings([p.settings() for p in sorted_plugins])
        defaults = parse_settings(settings)

        # FIll in default values
        conf = read_state(ctx)
        for k, v in defaults.items():
            if v is not None and k not in conf:
                conf[k] = v

        from rich import get_console

        get_console().print(conf.conf)
        get_console().print(defaults)
        get_console().print(settings)

        return settings, defaults, conf.conf

        # logger.info(f"Monitoring plugin status, and restarting if necessary.")
        # while True:
        #     exited = select.select(list(running_plugins), [], [])[0]
        #     for fd in exited:
        #         pkg_name, plugin, proc = running_plugins.pop(fd)
        #         if not proc.exitcode:
        #             # Plugin exited normally, not restarting
        #             logger.info(f"Plugin '{plugin['name']}' exited normally.")
        #             continue

        #         logger.error(
        #             f"Plugin '{plugin['name']}' crashed. Restarting in {ERROR_DELAY}s."
        #         )
        #         time.sleep(ERROR_DELAY)
        #         proc = launch_plugin(pkg_name, plugin, perms)
        #         if proc:
        #             running_plugins[proc.sentinel] = (pkg_name, plugin, proc)
        #     time.sleep(ERROR_DELAY)
    except KeyboardInterrupt:
        logger.info(
            f"HHD Daemon received KeyboardInterrupt, stopping plugins and exiting."
        )
    finally:
        for plugs in plugins.values():
            for plug in plugs:
                plug.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="HHD: Handheld Daemon main interface.",
        description="Handheld Daemon is a daemon for managing the quirks inherent in handheld devices.",
    )
    parser.add_argument(
        "-u",
        "--user",
        default=None,
        help="The user whose home directory will be used to store the files (~/.config/hhd).",
        dest="user",
    )
    args = parser.parse_args()
    user = args.user
    main(user)
