"""OpenAI-based scam analysis. API key from .streamlit/secrets.toml (OPENAI_API_KEY)."""
import json
import os
import re
import hashlib
import httpx
from openai import OpenAI

SYSTEM_PROMPT = """You are a scam and spam analyst for the Philippines. Your job is to classify messages (SMS, Messenger, Email, or call scripts) into: SAFE, SUSPICIOUS, or SCAM.

Philippines-specific patterns to detect:
- GCash / Maya phishing (fake links, OTP requests, "verify your account")
- SSS / PhilHealth / Pag-IBIG impersonation (fake benefits, loan offers)
- Bank impersonation (BDO, BPI, etc.) and OTP/verification scams
- Fake job offers (work-from-home, high pay, upfront fees)
- Loan scams (easy approval, no collateral, advance fees)
- Romance / love scams (foreign contacts, money requests)
- Investment scams (crypto, "double your money", Ponzi)
- Urgency and fear tactics ("account suspended", "claim now")

Rules:
- Output ONLY valid JSON. No markdown, no extra text.
- If the message is clearly legitimate (e.g., official-looking, no red flags), use SAFE with high confidence.
- If there are some red flags but not definitive, use SUSPICIOUS with moderate confidence (40-70).
- If clearly a scam or phishing, use SCAM with high confidence (70-100).
- Avoid false certainty: when unclear, prefer SUSPICIOUS over SCAM.
- Detect language: English, Tagalog, or Mixed and note in safety_notes if relevant.

Output JSON schema (use exactly these keys):
{
  "verdict": "SAFE" | "SUSPICIOUS" | "SCAM",
  "confidence": <0-100 integer>,
  "category": "<short label, e.g. GCash phishing, Fake job offer, Loan scam, Romance scam, Investment scam, Bank OTP scam, SSS/PhilHealth impersonation, Maya phishing, or Unknown>",
  "reasons": ["reason 1", "reason 2", ...],
  "recommended_actions": ["action 1", "action 2", ...],
  "warning_message": "<short shareable warning text for friends, 1-2 sentences>",
  "red_flags": ["flag 1", "flag 2", ...],
  "safety_notes": "<optional brief note>"
}"""


def _hash_message(text: str) -> str:
    """Return SHA256 hex digest of normalized message (no raw storage)."""
    normalized = (text or "").strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _sanitize(text: str) -> str:
    """Basic sanitization: strip and limit length for API."""
    if not text or not isinstance(text, str):
        return ""
    t = text.strip()
    return t[:8000] if len(t) > 8000 else t


def _parse_response(raw: str) -> dict:
    """Parse JSON from model response with validation and fallbacks."""
    fallback = {
        "verdict": "SUSPICIOUS",
        "confidence": 50,
        "category": "Unknown",
        "reasons": ["Unable to fully analyze. Please verify through official channels."],
        "recommended_actions": [
            "Do not share OTP or personal details.",
            "Contact the official company/bank via their verified website or hotline.",
        ],
        "warning_message": "This message could not be fully verified. Stay cautious.",
        "red_flags": [],
        "safety_notes": "Analysis inconclusive.",
    }
    raw = (raw or "").strip()
    # Remove markdown code block if present
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return fallback
    if not isinstance(data, dict):
        return fallback
    verdict = (data.get("verdict") or "SUSPICIOUS").upper()
    if verdict not in ("SAFE", "SUSPICIOUS", "SCAM"):
        verdict = "SUSPICIOUS"
    confidence = data.get("confidence")
    if not isinstance(confidence, (int, float)):
        confidence = 50
    confidence = max(0, min(100, int(confidence)))
    category = data.get("category") or "Unknown"
    if not isinstance(category, str):
        category = "Unknown"
    reasons = data.get("reasons")
    if not isinstance(reasons, list):
        reasons = fallback["reasons"]
    reasons = [str(r) for r in reasons[:10]]
    recommended_actions = data.get("recommended_actions")
    if not isinstance(recommended_actions, list):
        recommended_actions = fallback["recommended_actions"]
    recommended_actions = [str(a) for a in recommended_actions[:10]]
    warning_message = data.get("warning_message")
    if not isinstance(warning_message, str):
        warning_message = fallback["warning_message"]
    red_flags = data.get("red_flags")
    if not isinstance(red_flags, list):
        red_flags = []
    red_flags = [str(f) for f in red_flags[:10]]
    safety_notes = data.get("safety_notes") or ""
    if not isinstance(safety_notes, str):
        safety_notes = ""
    return {
        "verdict": verdict,
        "confidence": confidence,
        "category": category,
        "reasons": reasons or fallback["reasons"],
        "recommended_actions": recommended_actions or fallback["recommended_actions"],
        "warning_message": warning_message or fallback["warning_message"],
        "red_flags": red_flags,
        "safety_notes": safety_notes,
    }


def analyze_message(
    message: str,
    channel: str = "",
    language: str = "",
    api_key: str = None,
) -> dict:
    """
    Call OpenAI to analyze message. Returns parsed dict with verdict, confidence, category, reasons, etc.
    Also returns msg_hash for storage (no raw message stored).
    """
    msg = _sanitize(message)
    if not msg:
        return {
            "verdict": "SUSPICIOUS",
            "confidence": 0,
            "category": "Unknown",
            "reasons": ["No message provided."],
            "recommended_actions": ["Paste a message to check."],
            "warning_message": "No message to analyze.",
            "red_flags": [],
            "safety_notes": "",
            "msg_hash": "",
        }
    user_content = f"Message to analyze:\n\n{msg}"
    if channel:
        user_content += f"\n\nChannel: {channel}"
    if language:
        user_content += f"\n\nLanguage: {language}"

    api_key = (api_key or "").strip()
    if not api_key:
        return {
            "verdict": "SUSPICIOUS",
            "confidence": 0,
            "category": "Unknown",
            "reasons": ["API key not configured. Contact support."],
            "recommended_actions": [],
            "warning_message": "Service temporarily unavailable.",
            "red_flags": [],
            "safety_notes": "",
            "msg_hash": _hash_message(msg),
        }

    try:
        # Avoid "proxies" argument error: unset proxy env so OpenAI/httpx don't pass proxies
        saved = {}
        for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            saved[k] = os.environ.pop(k, None)
        try:
            http_client = httpx.Client()
            client = OpenAI(api_key=api_key, http_client=http_client)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.2,
                max_tokens=1000,
            )
            raw = (resp.choices[0].message.content or "").strip()
            result = _parse_response(raw)
            result["msg_hash"] = _hash_message(msg)
            return result
        finally:
            for k, v in saved.items():
                if v is not None:
                    os.environ[k] = v
    except Exception as e:
        return {
            "verdict": "SUSPICIOUS",
            "confidence": 0,
            "category": "Unknown",
            "reasons": [f"Analysis failed: {str(e)[:200]}. Please try again or verify through official channels."],
            "recommended_actions": ["Do not share OTP or personal details.", "Contact official channels."],
            "warning_message": "Could not analyze. Stay cautious.",
            "red_flags": [],
            "safety_notes": "",
            "msg_hash": _hash_message(msg),
        }
