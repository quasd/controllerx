import asyncio
import appdaemon.plugins.hass.hassapi as hass
import appdaemon.plugins.mqtt.mqttapi as mqtt
import pytest

from cx_core.controller import Controller
from tests.test_utils import fake_fn


async def fake_run_in(self, fn, delay, **kwargs):
    async def inner():
        await asyncio.sleep(delay)
        await fn(kwargs)

    task = asyncio.ensure_future(inner())
    return task


async def fake_cancel_timer(self, task):
    task.cancel()


@pytest.fixture(autouse=True)
def hass_mock(monkeypatch, mocker):
    """
    Fixture for set up the tests, mocking appdaemon functions
    """

    monkeypatch.setattr(hass.Hass, "__init__", fake_fn())
    monkeypatch.setattr(hass.Hass, "listen_event", fake_fn())
    monkeypatch.setattr(mqtt.Mqtt, "listen_event", fake_fn())
    monkeypatch.setattr(hass.Hass, "listen_state", fake_fn())
    monkeypatch.setattr(hass.Hass, "log", fake_fn())
    monkeypatch.setattr(hass.Hass, "call_service", fake_fn(async_=True))
    monkeypatch.setattr(hass.Hass, "get_ad_version", fake_fn(to_return="4.0.0"))
    monkeypatch.setattr(hass.Hass, "run_in", fake_run_in)
    monkeypatch.setattr(hass.Hass, "cancel_timer", fake_cancel_timer)


@pytest.fixture(autouse=True)
def fake_controller(hass_mock):
    c = Controller()
    c.args = {}
    return c
