"""Store prediction history in each visitor's browser instead of the server."""

from __future__ import annotations

from typing import Any

import streamlit as st


STORAGE_KEY = "ghar_mulyankan_prediction_history_v1"
MAX_RECORDS = 100


_history_storage = st.components.v2.component(
    name="ghar_mulyankan_browser_history",
    html='<span id="browser-storage-status" aria-hidden="true"></span>',
    css="""
        #browser-storage-status {
            display: block;
            width: 1px;
            height: 1px;
            overflow: hidden;
            opacity: 0;
            pointer-events: none;
        }
    """,
    js="""
        export default function({ data, parentElement, setStateValue }) {
            const status = parentElement.querySelector("#browser-storage-status");
            const storageKey = data.storage_key;
            const lastActionKey = `${storageKey}:last-action`;
            const currentRecords = Array.isArray(data.current_records)
                ? data.current_records
                : [];

            let records = [];
            try {
                const saved = window.localStorage.getItem(storageKey);
                const parsed = saved ? JSON.parse(saved) : [];
                records = Array.isArray(parsed) ? parsed : [];
            } catch (error) {
                records = [];
            }

            const isNewAction = data.action_id
                && window.localStorage.getItem(lastActionKey) !== data.action_id;

            let changedByAction = false;

            if (data.action === "append" && isNewAction && data.record) {
                records.unshift(data.record);
                records = records.slice(0, data.max_records || 100);
                window.localStorage.setItem(storageKey, JSON.stringify(records));
                window.localStorage.setItem(lastActionKey, data.action_id);
                changedByAction = true;
            }

            if (data.action === "clear" && isNewAction) {
                records = [];
                window.localStorage.removeItem(storageKey);
                window.localStorage.setItem(lastActionKey, data.action_id);
                changedByAction = true;
            }

            if (changedByAction
                || JSON.stringify(records) !== JSON.stringify(currentRecords)) {
                setStateValue("records", records);
            }

            status.textContent = String(records.length);
        }
    """,
)


def _records_from_component_state(component_key: str) -> list[dict[str, Any]]:
    """Read the latest component value already available in Session State."""
    state = st.session_state.get(component_key)
    if state is None:
        return []

    records = state.get("records", []) if isinstance(state, dict) else getattr(
        state, "records", []
    )
    return records if isinstance(records, list) else []


def browser_history(
    *,
    component_key: str,
    action: str = "read",
    record: dict[str, Any] | None = None,
    action_id: str | None = None,
) -> list[dict[str, Any]]:
    """Read, append to, or clear history stored in this browser profile."""
    current_records = _records_from_component_state(component_key)
    result = _history_storage(
        data={
            "storage_key": STORAGE_KEY,
            "action": action,
            "record": record,
            "action_id": action_id,
            "current_records": current_records,
            "max_records": MAX_RECORDS,
        },
        default={"records": current_records},
        on_records_change=lambda: None,
        key=component_key,
        height=1,
    )
    records = getattr(result, "records", current_records)
    return records if isinstance(records, list) else current_records
