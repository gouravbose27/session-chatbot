"""Guardrails: checks on the user message before the model call and on the reply after it."""
import json
import os
import re

import settings
from llm_client import ask_llm

EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# A loose match; digits are counted below so dates like 2026-10-18 are left alone.
PHONE_PATTERN = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def load_config() -> dict:
    """Read the guardrail settings from the JSON file."""
    with open(settings.GUARDRAILS_FILE, encoding="utf-8") as config_file:
        return json.load(config_file)


def save_config(config: dict) -> None:
    """Write the guardrail settings to the JSON file, replacing it in one step."""
    temp_path = settings.GUARDRAILS_FILE + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=2)
    os.replace(temp_path, settings.GUARDRAILS_FILE)


def mask_phones(text: str) -> tuple[str, int]:
    """Replace phone numbers (10 or more digits) with [PHONE]. Return the text and the count."""
    count = 0

    def replace(match: re.Match) -> str:
        nonlocal count
        if sum(char.isdigit() for char in match.group()) < 10:
            return match.group()
        count += 1
        return "[PHONE]"

    return PHONE_PATTERN.sub(replace, text), count


def is_on_topic(text: str, allowed_topic: str) -> bool:
    """Ask the LLM judge whether the text fits the allowed topic. Expects YES or NO."""
    with open(settings.PROMPTS_FILE, encoding="utf-8") as prompts_file:
        judge_system = json.load(prompts_file)["topic-judge"]
    result = ask_llm(text, model=settings.MODEL, system=judge_system.format(allowed_topic=allowed_topic))
    return result["text"].strip().upper().startswith("YES")


def check_input(message: str, config: dict) -> tuple[bool, str, str | None]:
    """Return (allowed, cleaned_text, reason) for a user message."""
    if not config["enabled"]:
        return True, message, None

    if len(message) > config["max_input_chars"]:
        return False, message, "blocked: too long"

    if config["block_injection"]:
        normalized = " ".join(message.lower().split())
        for phrase in config["injection_phrases"]:
            if phrase.lower() in normalized:
                return False, message, "blocked: injection"

    cleaned = message
    masked = []
    if config["mask_pii"]:
        cleaned, email_count = EMAIL_PATTERN.subn("[EMAIL]", cleaned)
        cleaned, phone_count = mask_phones(cleaned)
        if email_count:
            masked.append("email")
        if phone_count:
            masked.append("phone")

    if config["topic_check"] and not is_on_topic(cleaned, config["allowed_topic"]):
        return False, cleaned, "blocked: off topic"

    reason = f"masked: {', '.join(masked)}" if masked else None
    return True, cleaned, reason


def check_output(reply: str, config: dict) -> tuple[bool, str, str | None]:
    """Return (allowed, cleaned_text, reason) for a model reply."""
    if not config["enabled"]:
        return True, reply, None

    if len(reply.split()) > config["max_output_words"]:
        return False, reply, "blocked: reply too long"

    for word in config["banned_output_words"]:
        if re.search(rf"\b{re.escape(word)}\b", reply, re.IGNORECASE):
            return False, reply, "blocked: banned word"

    return True, reply, None
