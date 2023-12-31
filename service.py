import dbus
import dbus.service
import os
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

def get_xdg_data_home() -> str:
    """Returns the XDG_DATA_HOME environment variable. Fallbacks to
    .local/share if there's none assigned.

    Returns:
        str: Envvar XDG_DATA_HOME value
    """
    return os.getenv("XDG_DATA_HOME") if os.getenv("XDG_DATA_HOME") \
        else f"{os.getenv('HOME')}/.local/share"

# Service declarations
SERVICE_NAME = "WindowRestore"
SERVICE_PATH = "WindowRestore"
# KWin constants
BUS_KWIN = "org.kde.KWin"
BUS_KWIN_SCRIPT = f"{BUS_KWIN}.Script"
INTERFACE_KWIN = BUS_KWIN.lower()
INTERFACE_SCRIPT = f"{INTERFACE_KWIN}.Script"
# JS constants
JS_DIR = os.path.dirname(os.path.abspath(__file__))
JS_SAVE = f"{JS_DIR}/kwin_save.js"
JS_RESTORE = f"{JS_DIR}/kwin_restore.js"
PERSISTENCE_PATH = f"{get_xdg_data_home()}/kwindowrestore.json"


def get_kwin_scripting() -> dbus.Interface:
    """Returns the interface for calling KwinScripting methods.

    Returns:
        Interface: KWinScripting interface
    """
    return dbus_send(
        service=BUS_KWIN,
        path="/Scripting",
        interface=f"{INTERFACE_KWIN}.Scripting"
    )

def load_and_run_kwinjs(script: str) -> None:
    """Loads and runs a given Kwin JS script, assigning it to our service.
    It must call an unload call by itself.

    Args:
        script (str): Path to the JS script
    """
    script_id = get_kwin_scripting().loadScript(
        script,
        SERVICE_NAME,
        signature="ss"
    )
    dbus_send(
        service=BUS_KWIN,
        path=f"/{str(script_id)}",
        interface=INTERFACE_SCRIPT
    ).run()

def dbus_send(service: str, path: str, interface: str):
    """Sends a DBus call to the path of specified service using the given
    interface.

    Args:
        service (str): Service qualifier (org.example.Service)
        path (str): Path of the method (/Method)
        interface (str): Interface to be called (org.example.Service.Call)

    Returns:
        dbus.Interface: Wrapper interface for the remote retrieved object
    """
    obj = bus.get_object(service, path)
    return dbus.Interface(obj, interface)


class WindowRestoreService(dbus.service.Object):
    def __init__(self):
        """DBus boilerplate for requesting the service namespace.
        """
        self.loop = loop
        bus = dbus.SessionBus()
        bus.request_name(f"{BUS_KWIN_SCRIPT}.{SERVICE_NAME}")
        bus_name = dbus.service.BusName(f"{BUS_KWIN}.Scripting", bus=bus)
        dbus.service.Object.__init__(self, bus_name, f"/{SERVICE_PATH}")

    @dbus.service.method(dbus_interface="org.kde.kwin.Script",
                            in_signature="", out_signature="")
    def TriggerRestore(self):
        """Restores saved window data. by executing the loading script.
        User should trigger this function.
        """
        load_and_run_kwinjs(JS_RESTORE)

    @dbus.service.method(dbus_interface="org.kde.kwin.Script",
                            in_signature="", out_signature="s")
    def Restore(self):
        """Loads and returns the stored window data.
        This should always be called from KWin scripts.

        Returns:
            str: Window data stored as JSON
        """
        with open(PERSISTENCE_PATH, 'r') as file:
            return file.read()

    @dbus.service.method(dbus_interface="org.kde.kwin.Script",
                            in_signature="", out_signature="")
    def TriggerSave(self):
        """Stores opened window data by executing the save script.
        User should trigger this function.
        """
        load_and_run_kwinjs(JS_SAVE)

    @dbus.service.method(dbus_interface="org.kde.kwin.Script",
                            in_signature="s", out_signature="")
    def Save(self, data: str):
        """Receives a JSON data string and writes it to JSON_FILE.
        This should always be called from KWin scripts.

        Args:
            data (str): JSON window data string
        """
        with open(PERSISTENCE_PATH, 'w') as file:
            file.write(data)

    @dbus.service.method(dbus_interface="org.kde.kwin.Script",
                            in_signature="", out_signature="")
    def UnloadServiceScript(self):
        """Unloads a KWin JS script associated with this service. As our
        scripts run only once, this should be called after finishing their
        execution.
        """
        get_kwin_scripting().unloadScript(SERVICE_NAME)

    @dbus.service.method(dbus_interface="org.kde.kwin.Script",
                            in_signature="", out_signature="")
    def Teardown(self):
        """Undeploys our service gracefully from the DBus.
        """
        self.UnloadServiceScript()
        self.loop.quit()


if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()
    bus = dbus.SessionBus()

    try:
        service = WindowRestoreService()
        loop.run()
    except (BaseException) as exc:
        service.Teardown()
