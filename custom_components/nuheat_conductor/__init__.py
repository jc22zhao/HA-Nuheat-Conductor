"""Nuheat Conductor integration with OAuth2 Authorization Code flow."""

from __future__ import annotations

import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    OAuth2TokenRequestError,
    OAuth2TokenRequestReauthError,
)
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers import config_validation as cv

from .config_flow import NuheatConductorLocalOAuth2Implementation
from .const import DOMAIN
from .signalr import NuheatSignalRManager

PLATFORMS = [Platform.CLIMATE]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_LOGGER = logging.getLogger(__name__)

type NuheatConductorConfigEntry = ConfigEntry


async def async_setup_entry(
    hass: HomeAssistant, entry: NuheatConductorConfigEntry
) -> bool:
    """Set up Nuheat Conductor from a config entry."""
    # Register the OAuth2 implementation
    # This is needed on restart since implementations aren't persisted
    config_entry_oauth2_flow.async_register_implementation(
        hass,
        DOMAIN,
        NuheatConductorLocalOAuth2Implementation(hass),
    )

    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )

    session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)

    # Verify we can get a valid token.
    #
    # 2026-09-19: this block used to swallow every exception and return False,
    # which deadlocked the integration. Home Assistant only opens a reauth flow
    # when an entry raises ConfigEntryAuthFailed; a falsy return just marks the
    # entry setup_error. So once the stored refresh token went stale, setup failed
    # here, the exception was swallowed, and no repair and no reauth prompt were
    # left for anyone to click - the entry could neither refresh nor ask to be
    # re-authenticated, and stayed dead until it was deleted and re-added.
    #
    # The two failures need opposite handling: a rejected token needs a human, an
    # unreachable endpoint just needs a retry. async_ensure_token_valid raises
    # OAuth2TokenRequestReauthError for any 4xx from the token endpoint and the
    # transient variant for 5xx, but neither derives from ConfigEntryAuthFailed and
    # config_entries.py does not special-case them, so translate them explicitly.
    try:
        await session.async_ensure_token_valid()
    except OAuth2TokenRequestReauthError as err:
        # Non-recoverable: NuHeat refused the refresh token. Raising this is what
        # makes HA create the reauth flow and the "Authentication expired" repair.
        raise ConfigEntryAuthFailed(
            "NuHeat rejected the stored credentials; re-authentication required"
        ) from err
    except (OAuth2TokenRequestError, aiohttp.ClientError, TimeoutError) as err:
        # Transient: a 5xx, a DNS blip, a timeout. HA retries with backoff.
        # OAuth2TokenRequestError is the PARENT of the reauth error above, so this
        # clause must stay second - swapping them would send real auth failures
        # down the retry path and the reauth prompt would never appear.
        raise ConfigEntryNotReady(
            f"Could not reach the NuHeat token endpoint: {err}"
        ) from err

    # Create and start the SignalR manager for real-time notifications
    signalr_manager = NuheatSignalRManager(hass, session)
    await signalr_manager.async_start()

    # Store both the session and SignalR manager for use by climate.py
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "session": session,
        "signalr": signalr_manager,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Stop the SignalR connection cleanly before unloading
    entry_data = hass.data[DOMAIN].get(entry.entry_id, {})
    signalr_manager: NuheatSignalRManager | None = entry_data.get("signalr")
    if signalr_manager:
        await signalr_manager.async_stop()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
