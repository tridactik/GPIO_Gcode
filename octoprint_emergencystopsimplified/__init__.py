# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import re
from octoprint.events import Events
from time import sleep
import RPi.GPIO as GPIO


class GPIO_Gcode_Plugin(octoprint.plugin.StartupPlugin,
                                       octoprint.plugin.EventHandlerPlugin,
                                       octoprint.plugin.TemplatePlugin,
                                       octoprint.plugin.SettingsPlugin,
                                       octoprint.plugin.AssetPlugin):

    def initialize(self):
        GPIO.setwarnings(False)  # Disable GPIO warnings
        self.estop_sent = False
        self.pin_initialized = False

    @property
    def pin(self):
        return int(self._settings.get(["pin"]))

    @property
    def switch(self):
        return int(self._settings.get(["switch"]))

    @property
    def gcode(self):
        return int(self._settings.get(["gcode"]))

    # AssetPlugin hook
    def get_assets(self):
        return dict(js=["js/emergencystopsimplified.js"], css=["css/emergencystopsimplified.css"])

    # Template hooks
    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=False)]

    # Settings hook
    def get_settings_defaults(self):
        return dict(
            pin=-1,  # Default is -1
            switch=0
	    gcode="M112" # Default is M112, if using TP-Link use M81 [IP Address} 
        )

    def on_after_startup(self):
        self._logger.info("GPIO Gcode started")
        self._setup_button()

    def on_settings_save(self, data):
        if self.sensor_enabled() and self.pin_initialized:
            GPIO.remove_event_detect(self.pin)
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self._setup_button()

    def _setup_button(self):
        if self.sensor_enabled():
            self._logger.info("Setting up button.")
            self._logger.info("Using Board Mode")
            GPIO.setmode(GPIO.BCM)
            self._logger.info("Emergency Stop button active on GPIO Pin [%s]" % self.pin)
            if self.switch is 0:
                GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            else:
                GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            GPIO.remove_event_detect(self.pin)
            GPIO.add_event_detect(
                self.pin, GPIO.BOTH,
                callback=self.button_callback,
                bouncetime=1
            )
            self.pin_initialized = True
        else:
            self._logger.info("Pin not configured, won't work unless configured!")

    def sending_gcode(self, comm_instance, phase, cmd, cmd_type, gcode, subcode=None, tags=None, *args, **kwargs):
        if self.emergency_stop_triggered():
            self.send_emergency_stop()

    def sensor_enabled(self):
        return self.pin != -1

    def emergency_stop_triggered(self):
        return self.pin_initialized and self.sensor_enabled() and GPIO.input(self.pin) != self.switch

    def on_event(self, event, payload):
        if event is Events.CONNECTED:
            self.estop_sent = False
        elif event is Events.DISCONNECTED:
            self.estop_sent = True

        if not self.sensor_enabled():
            if event is Events.USER_LOGGED_IN:
                self._plugin_manager.send_plugin_message(self._identifier, dict(type="info", autoClose=True, msg="Don' forget to configure this plugin."))
            elif event is Events.PRINT_STARTED:
                self._plugin_manager.send_plugin_message(self._identifier, dict(type="info", autoClose=True, msg="You may have forgotten to configure this plugin."))

    def button_callback(self, _):
        self._logger.info("Emergency stop was triggered")
        if self.emergency_stop_triggered():
            self.send_emergency_stop()
        else:
            self.estop_sent = False

    def send_emergency_stop(self):
        if self.estop_sent:
            return

        self._logger.info("Sending emergency stop GCODE")
        self._printer.commands(gcode)
        self.estop_sent = True


    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            filamentsensorsimplified=dict(
                displayName="Emergency stop simplified",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="tridactik",
                repo="GPIO_Gcode",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/tridactick/GPIO_Gcode/archive/{target_version}.zip"
            )
        )

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
# __plugin_pythoncompat__ = ">=2.7,<3" # only python 2
# __plugin_pythoncompat__ = ">=3,<4" # only python 3
__plugin_pythoncompat__ = ">=2.7,<4"  # python 2 and 3

__plugin_name__ = "GPIO Gcode"
__plugin_version__ = "0.1.1"

def __plugin_check__():
    try:
        import RPi.GPIO as GPIO
        if GPIO.VERSION < "0.6":  # Need at least 0.6 for edge detection
            return False
    except ImportError:
        return False
    return True

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = GPIO_Gcode_Plugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.sending": __plugin_implementation__.sending_gcode
    }
