# telegram_bot.py
import os
import time
import logging
import requests
from urllib.parse import urljoin

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not set in .env")
if not API_USERNAME or not API_PASSWORD:
    raise RuntimeError("API_USERNAME or API_PASSWORD not set in .env")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Bot API base URL
TG_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"


class BackendClient:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.access_token = None

    def login(self) -> None:
        """
        Login to FastAPI backend to get JWT token using /auth/login
        (for protected endpoints like /students/{id}/analyze).
        """
        url = urljoin(self.base_url + "/", "auth/login")
        data = {
            "username": self.username,
            "password": self.password,
        }
        resp = requests.post(url, data=data)
        if not resp.ok:
            raise RuntimeError(
                f"Login failed: HTTP {resp.status_code} - {resp.text}"
            )
        data = resp.json()
        self.access_token = data.get("access_token")
        if not self.access_token:
            raise RuntimeError("Login response did not contain access_token")

        logger.info("Logged in to backend as %s", self.username)

    def get_headers(self):
        if not self.access_token:
            # for open endpoints we can call without token
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}

    def analyze_student(self, student_id: str) -> dict:
        """
        Call GET /students/{student_id}/analyze and return JSON.
        """
        url = urljoin(self.base_url + "/", f"students/{student_id}/analyze")
        resp = requests.get(url, headers=self.get_headers())
        if not resp.ok:
            raise RuntimeError(
                f"Analyze failed: HTTP {resp.status_code} - {resp.text}"
            )
        return resp.json()

    def register_bot_link(self, student_id: str, chat_id: int, username: str | None):
        """
        Call POST /bot/register to link chat_id to student_id.
        """
        url = urljoin(self.base_url + "/", "bot/register")
        payload = {
            "student_id": student_id,
            "chat_id": str(chat_id),
            "username": username,
        }
        resp = requests.post(url, json=payload)  # open endpoint
        if not resp.ok:
            raise RuntimeError(
                f"Bot register failed: HTTP {resp.status_code} - {resp.text}"
            )
        return resp.json()

    def get_daily_checkup(self, student_id: str) -> dict:
        """
        Call GET /bot/daily_checkup/{student_id} to get today's questions.
        """
        url = urljoin(self.base_url + "/", f"bot/daily_checkup/{student_id}")
        resp = requests.get(url)  # open endpoint
        if not resp.ok:
            raise RuntimeError(
                f"Daily checkup failed: HTTP {resp.status_code} - {resp.text}"
            )
        return resp.json()

    def log_bot_activity(
        self,
        student_id: str,
        chat_id: int,
        activity_type: str,
        activity_code: str,
        answer_text: str,
        score: float | None = None,
    ):
        """
        Call POST /bot/activity to log student response.
        """
        url = urljoin(self.base_url + "/", "bot/activity")
        payload = {
            "student_id": student_id,
            "chat_id": str(chat_id),
            "activity_type": activity_type,
            "activity_code": activity_code,
            "answer_text": answer_text,
            "score": score,
        }
        resp = requests.post(url, json=payload)  # open endpoint
        if not resp.ok:
            raise RuntimeError(
                f"Bot activity failed: HTTP {resp.status_code} - {resp.text}"
            )
        return resp.json()


backend_client = BackendClient(API_BASE_URL, API_USERNAME, API_PASSWORD)

# In-memory chat state (for this bot process)
# { chat_id: {"student_id": str|None,
#             "pending_questions": list[dict],
#             "current_index": int} }
CHAT_STATE: dict[int, dict] = {}


def tg_get_updates(offset=None, timeout=30):
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset
    resp = requests.get(TG_API_BASE + "getUpdates", params=params)
    if not resp.ok:
        logger.error("getUpdates failed: %s", resp.text)
        return []
    data = resp.json()
    if not data.get("ok"):
        logger.error("getUpdates returned not ok: %s", data)
        return []
    return data.get("result", [])


def tg_send_message(chat_id, text, parse_mode=None):
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    resp = requests.post(TG_API_BASE + "sendMessage", data=payload)
    if not resp.ok:
        logger.error("sendMessage failed: %s", resp.text)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def handle_start(chat_id):
    text = (
        "👋 Welcome to the Syntax of Success Student Bot!\n\n"
        "Commands:\n"
        "/register <student_id> – Link your student account (e.g., /register S001)\n"
        "/daily – Start today's multi-step check-in (4–5 short questions)\n"
        "/risk <student_id> – (for counselor/testing) see risk analysis\n"
        "/help – Show this help\n"
    )
    tg_send_message(chat_id, text)


def handle_help(chat_id):
    text = (
        "Commands:\n"
        "/register <student_id> – Link your student account\n"
        "/daily – Start today's multi-question wellbeing check-in\n"
        "/risk <student_id> – Counselor/test risk lookup\n"
    )
    tg_send_message(chat_id, text)


def handle_register(chat_id, username, text):
    parts = text.strip().split(maxsplit=1)
    if len(parts) < 2:
        tg_send_message(
            chat_id,
            "Please provide your student ID.\nExample: /register S001",
        )
        return

    student_id = parts[1].strip()

    try:
        backend_client.register_bot_link(student_id, chat_id, username)
    except Exception as e:
        logger.exception("Error in /register")
        tg_send_message(chat_id, f"Error registering: {e}")
        return

    # Save in memory
    state = CHAT_STATE.get(chat_id, {})
    state["student_id"] = student_id
    state["pending_questions"] = []
    state["current_index"] = 0
    CHAT_STATE[chat_id] = state

    tg_send_message(
        chat_id,
        f"✅ Registered this chat with student ID `{student_id}`.\n"
        f"Now you can use /daily to do today's activities.",
        parse_mode="Markdown",
    )


def ask_current_question(chat_id, state):
    """
    Send the current pending question (based on current_index) to the student.
    """
    questions = state.get("pending_questions") or []
    idx = state.get("current_index", 0)

    if idx >= len(questions):
        tg_send_message(
            chat_id,
            "✅ All today's questions are completed. Thank you!",
        )
        state["pending_questions"] = []
        state["current_index"] = 0
        CHAT_STATE[chat_id] = state
        return

    q = questions[idx]
    total = len(questions)
    text = f"Question {idx + 1}/{total}:\n{q['question']}"
    tg_send_message(chat_id, text)


def handle_daily(chat_id):
    state = CHAT_STATE.get(chat_id)
    if not state or not state.get("student_id"):
        tg_send_message(
            chat_id,
            "You are not registered yet.\nPlease use /register <student_id> first.",
        )
        return

    student_id = state["student_id"]

    try:
        data = backend_client.get_daily_checkup(student_id)
    except Exception as e:
        logger.exception("Error calling /bot/daily_checkup")
        tg_send_message(chat_id, f"Error getting today's activities: {e}")
        return

    activities = data.get("activities") or []
    if not activities:
        tg_send_message(
            chat_id,
            "No activities configured for today. Please try again later.",
        )
        return

    state["pending_questions"] = activities
    state["current_index"] = 0
    CHAT_STATE[chat_id] = state

    tg_send_message(
        chat_id,
        "🧠 Starting today's check-in.\n"
        "Please answer the next few short questions honestly.",
    )

    ask_current_question(chat_id, state)


def handle_risk(chat_id, text):
    parts = text.strip().split(maxsplit=1)
    if len(parts) < 2:
        tg_send_message(
            chat_id,
            "Please provide a student ID.\nExample: /risk S001",
        )
        return

    student_id = parts[1].strip()

    try:
        data = backend_client.analyze_student(student_id)
    except Exception as e:
        logger.exception("Error calling analyze_student")
        tg_send_message(chat_id, f"Error: {e}")
        return

    # Build a nice response
    name = data.get("name", student_id)
    baseline_risk = data.get("baseline_risk")
    final_risk = data.get("final_risk")
    dropout_prob = data.get("dropout_probability", 0) * 100
    ml_score = data.get("ml_risk_score", 0)
    cluster_name = data.get("cluster_name")
    cluster_desc = data.get("cluster_description")
    stage = data.get("stage")
    recs = data.get("recommendations", "")

    # Normalize recommendations to a string
    if isinstance(recs, list):
        if recs:
            recs_text = "\n".join(f"- {r}" for r in recs)
        else:
            recs_text = ""
    else:
        recs_text = recs or ""

    text_lines = [
        f"📊 Risk Analysis for *{name}* (ID: `{student_id}`)",
        "",
        f"• Baseline Risk: *{baseline_risk}*",
        f"• Final Risk: *{final_risk}*",
        f"• Dropout Probability: *{dropout_prob:.1f}%*",
        f"• ML Risk Score: *{ml_score:.1f}*",
    ]
    if stage is not None:
        text_lines.append(f"• Stage: *{stage}*")
    if cluster_name:
        text_lines.append(f"• Cluster: *{cluster_name}*")
    if cluster_desc:
        text_lines.append(f"  _{cluster_desc}_")

    if recs_text:
        text_lines.append("")
        text_lines.append("*Recommendations:*")
        text_lines.append(recs_text)

    msg = "\n".join(text_lines)

    tg_send_message(chat_id, msg, parse_mode="Markdown")


# ---------------------------------------------------------------------------
# Non-command text handler (answers)
# ---------------------------------------------------------------------------

def handle_text_message(chat_id, username, text):
    """
    Handle non-command messages.
    Used to capture answers to pending daily questions.
    """
    state = CHAT_STATE.get(chat_id)
    questions = state.get("pending_questions") if state else None

    if not state or not questions:
        tg_send_message(
            chat_id,
            "I received your message, but I don't know what to do with it.\n"
            "Use /daily to start today's check-in or /help to see commands.",
        )
        return

    student_id = state.get("student_id")
    if not student_id:
        tg_send_message(
            chat_id,
            "You are not registered. Please use /register <student_id> first.",
        )
        state["pending_questions"] = []
        state["current_index"] = 0
        CHAT_STATE[chat_id] = state
        return

    idx = state.get("current_index", 0)
    if idx >= len(questions):
        tg_send_message(
            chat_id,
            "All today's questions are already completed.\nUse /daily to start again tomorrow.",
        )
        state["pending_questions"] = []
        state["current_index"] = 0
        CHAT_STATE[chat_id] = state
        return

    q = questions[idx]
    activity_type = q["activity_type"]
    activity_code = q["activity_code"]
    answer_text = text.strip()

    # Try to convert answer to numeric score if possible
    score = None
    try:
        score = float(answer_text)
    except ValueError:
        # textual / non-numeric answer is also allowed
        score = None

    try:
        backend_client.log_bot_activity(
            student_id=student_id,
            chat_id=chat_id,
            activity_type=activity_type,
            activity_code=activity_code,
            answer_text=answer_text,
            score=score,
        )
    except Exception as e:
        logger.exception("Error logging bot activity")
        tg_send_message(chat_id, f"Error saving your response: {e}")
        return

    # Move to next question
    state["current_index"] = idx + 1
    CHAT_STATE[chat_id] = state

    if state["current_index"] >= len(questions):
        tg_send_message(
            chat_id,
            "✅ Thank you, all your responses for today have been recorded.",
        )
        state["pending_questions"] = []
        state["current_index"] = 0
        CHAT_STATE[chat_id] = state
    else:
        # Ask next question
        ask_current_question(chat_id, state)


# ---------------------------------------------------------------------------
# Main polling loop
# ---------------------------------------------------------------------------

def main():
    # Login once (for /risk; /bot endpoints don’t strictly need auth)
    try:
        backend_client.login()
    except Exception as e:
        logger.warning("Backend login failed (risk calls may not work): %s", e)

    logger.info("Starting Telegram polling bot...")

    offset = None
    while True:
        try:
            updates = tg_get_updates(offset=offset, timeout=30)
            for update in updates:
                offset = update["update_id"] + 1

                message = update.get("message")
                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text")
                if not text:
                    continue

                from_user = message.get("from", {})
                username = from_user.get("username")

                text = text.strip()
                logger.info("Received message from %s: %s", username, text)

                if text.startswith("/start"):
                    handle_start(chat_id)
                elif text.startswith("/help"):
                    handle_help(chat_id)
                elif text.startswith("/register"):
                    handle_register(chat_id, username, text)
                elif text.startswith("/daily"):
                    handle_daily(chat_id)
                elif text.startswith("/risk"):
                    handle_risk(chat_id, text)
                else:
                    # Not a command: treat as answer to current question
                    handle_text_message(chat_id, username, text)

        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.exception("Error in polling loop: %s", e)
            time.sleep(5)


if __name__ == "__main__":
    main()