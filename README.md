# GPIO GCode

This plugin is based off of Emergency Stop Simplified by Mechazawa. It reacts to a switch, button, or sensor, if triggered it issues custom G-code (default: **M112**) command to printer.

I made some edit to allow custom g-code to run rather than a hard codes M112. For my purposes, this allows me to use a MQ-2 sensor to detect smoke or combustible gases by connecting the direct voltage output (0 or 1) and issue a line of g-code. The M112 works properly with the base Emergency Stop Simplified, but the M112 does not trigger the TP-Link plugin auto shut off. For my purposes, the g-code I will be using is M81 [IP Address] to issue a shut off command that the TP-Link plugin will read to shut off power to the print. This is not a perfect solution, but if a board burns up, it will not trigger the thermal runaway on TP-Link. However, with this plugin and an MQ-2 sensor the goal is to be able to sense any electrical arcing or fire and shut power off to the printer before it can spread. 

Let's check some features:
* info pop-up when plugin hasn't been configured
* user-friendly and easy to configure
* runs on OctoPrint 1.3.0 and higher
* allows custom gcode input
* cleans up some set up options to make them more clear

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/tridactik/GPIO_Gcode

## Configuration

Configuration couldn't be simpler, all you need is to configure listening board pin (board mode) and if the second switch terminal is connected to ground or 3.3V.

Default pin is -1 (not configured) and ground (as it is safer, read below). Options were changed to be clearer and not voltage dependent, as I use 5V with a MQ-2. MQ-2 initial state it HIGH and when tripped, switches to LOW. 

Config for using MQ-2 Sensor DC:
Default Pin: 4
G-Code: M112 or M81 [IP]
Initial State: HIGH

**WARNING! If using a switch or button, never connect the switch input to 5V as it could fry the GPIO section of your Raspberry!**

#### Advice

I use an MQ-2 sensor wired to 5V, GRD, and GPIO 4 (DC). 

Install GPIO-Status to determine untrigger state (high or low): https://github.com/danieleborgo/OctoPrint-GPIOStatus

Install TP-Link Smart Plug to issue auto shut off of printer power (must have TP-Link Kasa Smart Plug): https://github.com/jneilliii/OctoPrint-TPLinkSmartplug

#### Advice for using switch from Emergency Stop Simplified by Mechazawa

You might experience the same problem as I experienced - the button was randomly triggered. Turns out that if running button wires along motor wires, it was enough to interfere with button reading.

To solve this connect a shielded wire to your button and ground the shielding, ideally on both ends.

If you are unsure about your button being triggered, check [OctoPrint logs](https://community.octoprint.org/t/where-can-i-find-octoprints-and-octopis-log-files/299)
