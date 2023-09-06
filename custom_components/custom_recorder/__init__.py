"""The Detailed Hello World Push integration."""
import asyncio
import logging

import os
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.core import HomeAssistant

from .const import *

_LOGGER = logging.getLogger(__name__)

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Hello World component."""
    # Ensure our name space for storing objects is a known type. A dict is
    # common/preferred as it allows a separate instance of your class for each
    # instance that has been created in the UI.
    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hello World from a config entry."""
    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.
    _LOGGER.debug("call async_setup_entry")
    #hass.data[DOMAIN][entry.entry_id] = DOMAIN
    hass.data[DOMAIN][entry.entry_id] = {}
    hass.data[DOMAIN][entry.entry_id]["listener"] = []

    entry.async_on_unload(entry.add_update_listener(update_listener))
    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True

# async def async_remove_config_entry_device(
#     hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
# ) -> bool:
#     """Remove a config entry from a device."""
#     _LOGGER.debug("async_remove_config_entry_device : " + str(device_entry))

#     device_entry.config_entries.remove(config_entry.entry_id)
#     #config_entry.async_remove(hass)


async def update_listener(hass, entry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    _LOGGER.debug("call async_unload_entry")

    for listener in hass.data[DOMAIN][entry.entry_id]["listener"]:
        listener()
    
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(
                    entry, component)
                for component in PLATFORMS
            ]
        )
    )

    _LOGGER.debug("entry : " + str(entry.options))
    data_dir = entry.options.get(CONF_DATA_DIR)
    if os.path.isdir(data_dir):
        file_list = os.listdir(data_dir)
        if len(file_list) <= 0:
            _LOGGER.debug("remove dir : %s", data_dir)
            os.removedirs(data_dir)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
