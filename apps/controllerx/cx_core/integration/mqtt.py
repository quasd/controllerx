import json
from typing import Any, Dict, Optional

from appdaemon.plugins.mqtt.mqttapi import Mqtt
from cx_const import DefaultActionsMapping
from cx_core.integration import EventData, Integration


class MQTTIntegration(Integration):
    name = "mqtt"

    def get_default_actions_mapping(self) -> Optional[DefaultActionsMapping]:
        return self.controller.get_z2m_actions_mapping()

    async def listen_changes(self, controller_id: str) -> None:
        await Mqtt.listen_event(
            self.controller, self.event_callback, topic=controller_id, namespace="mqtt"
        )

    async def event_callback(
        self, event_name: str, data: EventData, kwargs: Dict[str, Any]
    ) -> None:
        payload_key = self.kwargs.get("key")
        if "payload" not in data:
            return
        if len(data["payload"]) == 0:
            self.controller.log(f"Empty payload", level="DEBUG")
            return
        else:
            try:
                payload = json.loads(data["payload"])
            except json.decoder.JSONDecodeError:
                raise ValueError(f"Following payload is not a valid JSON: {payload}")
        action_key: str
        if payload_key is None:
            action_key = payload
        else:
            try:
                action_key = str(payload[payload_key]).lower()
            except KeyError:
                raise ValueError(
                    f"Following payload does not contain `{payload_key}`: {payload}"
                )

        await self.controller.handle_action(action_key, extra=payload)
