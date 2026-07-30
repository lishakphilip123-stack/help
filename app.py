import os
import json
import time
import hashlib
import requests
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from difflib import SequenceMatcher
from dotenv import load_dotenv
import urllib3
from ontology import find_category, find_disambiguation, find_keyword_scenario, find_matches, find_scenario_in_query, format_context, get_cascades, get_max_followup, get_scenario, get_subcategories
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

app = Flask(__name__)
app.secret_key = "emergency_chatbot_secret_2024"

# ── Config ───────────────────────────────────────────────────────────────────
BASE_URL = os.getenv("LITELLM_BASE_URL")
API_KEY  = os.getenv("LITELLM_API_KEY")
MODEL    = os.getenv("MODEL")
API_URL  = f"{BASE_URL}/v1/chat/completions"
HEADERS  = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# ── Load FAQ data ─────────────────────────────────────────────────────────────
with open("faq_data.json", "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)["scenarios"]

ALL_FAQS = []
for tag, scenario in FAQ_DATA.items():
    for faq in scenario["faqs"]:
        ALL_FAQS.append({"tag": tag, "label": scenario["label"], **faq})

# ── User storage ──────────────────────────────────────────────────────────────
USERS_FILE = "users.json"
CHAT_HISTORY_FILE = "chat_history.jsonl"

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def log_chat_history(prompt, response_data):
    """Append one auditable chat event, including the ontology mapping used."""
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "user": session.get("user", "anonymous"),
        "prompt": prompt,
        "ontology": response_data.get("ontology"),
        "response": response_data.get("answer") or response_data.get("error"),
        "state": response_data.get("clarification_type", "final"),
    }
    try:
        with open(CHAT_HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        app.logger.exception("Could not write chat history")

@app.after_request
def write_chat_history(response):
    """Log every completed chat response without changing the API response."""
    if request.path == "/chat" and request.method == "POST" and response.is_json:
        try:
            request_data = request.get_json(silent=True) or {}
            response_data = response.get_json(silent=True) or {}
            log_chat_history(request_data.get("message", ""), response_data)
        except Exception:
            app.logger.exception("Could not log chat event")
    return response

# ── Helpers ───────────────────────────────────────────────────────────────────
def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_relevant_faqs(query, scenario_tag=None, top_k=3):
    pool = [f for f in ALL_FAQS if f["tag"] == scenario_tag] if scenario_tag else ALL_FAQS
    scored = sorted(pool, key=lambda f: similarity(query, f["q"]), reverse=True)
    return scored[:top_k]

def get_confidence(query, faqs):
    if not faqs:
        return 0.0
    return round(similarity(query, faqs[0]["q"]) * 100, 1)

def detect_severity(text):
    text_lower = text.lower()
    critical = ["unconscious", "not breathing", "heart attack", "stroke", "trapped", "dying",
                "bleeding heavily", "fire spreading", "explosion", "collapsed", "drowning",
                "chest pain", "can't breathe", "cannot breathe", "severe", "critical"]
    moderate = ["injured", "smoke", "flood", "earthquake", "cyclone", "chemical", "burn",
                "fracture", "bleeding", "evacuate", "warning", "danger"]
    for w in critical:
        if w in text_lower:
            return "critical", "🔴"
    for w in moderate:
        if w in text_lower:
            return "moderate", "🟡"
    return "safe", "🟢"

def build_system_prompt(scenario_tag=None, language="English"):
    lang_note = ""
    if language != "English":
        lang_note = (
            f" Respond only in {language}, using its native script. "
            "Do not switch to English except for emergency numbers such as 112 or 108."
        )
    scenario_info = ""
    if scenario_tag and scenario_tag in FAQ_DATA:
        s = FAQ_DATA[scenario_tag]
        scenario_info = f"The user is asking about a {s['label']} emergency. "
    return (
        "You are an emergency response assistant for public safety in India. "
        f"{scenario_info}"
        "Answer questions clearly, calmly, and accurately. "
        "Prioritise life safety. Recommend the most relevant emergency number for the situation: "
        "112 (general/police/rescue), 101 (fire), 108 (ambulance/medical), 1077 (disaster), 1554 (coast guard). "
        "Only mention 112 if no more specific number applies. "
        "Keep answers concise (under 150 words). "
        "If unsure, say so and direct the user to official emergency services."
        f"{lang_note}"
    )

def clean_response(text):
    import re
    return re.sub(r'[*#`_]', '', text).strip()

def call_genai(messages):
    payload = {"model": MODEL, "messages": messages, "max_tokens": 200, "temperature": 0.3}
    try:
        resp = requests.post(
            API_URL, headers=HEADERS, json=payload, timeout=15,
            verify=False, proxies={"http": None, "https": None}
        )
        resp.raise_for_status()
        return clean_response(resp.json()["choices"][0]["message"]["content"])
    except requests.exceptions.Timeout:
        return "⚠️ The AI service took too long to respond. Please try again."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Could not reach the AI service. Please try again. ({str(e)[:80]})"
    except (KeyError, IndexError):
        return "⚠️ Unexpected response from AI service. Please try again."

def translate_text(text, target_language):
    if target_language == "English":
        return text
    messages = [
        {"role": "system", "content": f"Translate the following text to {target_language}. Return only the translated text, nothing else."},
        {"role": "user", "content": text}
    ]
    return call_genai(messages)

def translate_to_english(text, source_language):
    """Translate a non-English question for English FAQ retrieval only."""
    if source_language == "English":
        return text
    messages = [
        {"role": "system", "content": f"Translate this {source_language} emergency question to English. Return only the English translation."},
        {"role": "user", "content": text},
    ]
    return call_genai(messages)

def ontology_clarification(category, language):
    """Ask for the required scenario subtype in the user's selected language."""
    question = (
        f"You selected the category '{category}'. Please choose the subcategory that best "
        "matches the emergency so I can give scenario-specific guidance."
    )
    return translate_text(question, language)

def ontology_follow_up_questions(row):
    """Read the ordered follow-up questions defined for one ontology scenario."""
    questions = [q.strip() for q in row.get("follow_up_questions", "").split("|") if q.strip()]
    return questions[:get_max_followup([row])]

def find_ontology_row(category, subcategory):
    return get_scenario(category, subcategory)

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    data = request.get_json()
    email     = data.get("email", "").strip().lower()
    password  = data.get("password", "")
    firstname = data.get("firstname", "").strip()
    lastname  = data.get("lastname", "").strip()
    phone     = data.get("phone", "").strip()

    if not email or not password or not firstname:
        return jsonify({"error": "Please fill all required fields."}), 400

    users = load_users()
    if email in users:
        return jsonify({"error": "An account with this email already exists."}), 400

    users[email] = {
        "firstname": firstname,
        "lastname": lastname,
        "phone": phone,
        "password": hash_password(password)
    }
    save_users(users)
    return jsonify({"success": True})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    data     = request.get_json()
    email    = data.get("email", "").strip().lower()
    password = data.get("password", "")

    users = load_users()
    user  = users.get(email)
    if not user or user["password"] != hash_password(password):
        return jsonify({"error": "Invalid email or password."}), 401

    session["user"]  = email
    session["name"]  = user["firstname"]
    return jsonify({"success": True})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ── Main app routes ───────────────────────────────────────────────────────────
@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", scenarios=FAQ_DATA, username=session.get("name", "User"))

@app.route("/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data         = request.get_json()
    user_message = data.get("message", "").strip()
    scenario_tag = data.get("scenario")
    history      = data.get("history", [])
    language     = data.get("language", "English")
    if language not in {"English", "Malayalam", "Hindi", "Tamil", "Telugu", "Kannada"}:
        language = "English"

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    start = time.time()

    # RAG: find relevant FAQs (no translation call — language handled in prompt)
    retrieval_query = translate_to_english(user_message, language)
    # Check for ambiguous terms that need a cause-based clarification first.
    disambiguation = find_disambiguation(retrieval_query)
    if disambiguation:
        session.pop("ontology_flow", None)
        question = translate_text(disambiguation["question"], language)
        return jsonify({
            "answer": question,
            "clarification": True,
            "clarification_type": "disambiguation",
            "disambiguation_options": disambiguation["options"],
            "ontology": {"category": None, "subcategory": None},
            "response_time": round(time.time() - start, 2),
        })

    ontology_category = find_category(retrieval_query)
    if ontology_category:
        # A new category starts a new guided scenario assessment.
        session.pop("ontology_flow", None)
        subcategories = get_subcategories(ontology_category)
        return jsonify({
            "answer": ontology_clarification(ontology_category, language),
            "clarification": True,
            "clarification_type": "subcategory",
            "category": ontology_category,
            "subcategories": subcategories,
            "ontology": {"category": ontology_category, "subcategory": None},
            "response_time": round(time.time() - start, 2),
        })

    # Do not create the final answer until the selected ontology scenario has
    # collected each of its configured follow-up answers.
    active_flow = session.get("ontology_flow")
    if active_flow:
        questions = active_flow.get("questions", [])
        answer_index = len(active_flow.get("answers", []))
        if answer_index < len(questions):
            active_flow["answers"].append({
                "question": questions[answer_index], "answer": user_message
            })
            answer_index += 1

        if answer_index < len(questions):
            session["ontology_flow"] = active_flow
            return jsonify({
                "answer": translate_text(questions[answer_index], language),
                "clarification": True,
                "clarification_type": "follow_up",
                "ontology": {"category": active_flow["category"], "subcategory": active_flow["subcategory"]},
                "response_time": round(time.time() - start, 2),
            })

        row = find_ontology_row(active_flow["category"], active_flow["subcategory"])
        session.pop("ontology_flow", None)
        if row:
            user_details = "\n".join(
                f"{item['question']} Answer: {item['answer']}" for item in active_flow["answers"]
            )
            context = format_context([row], get_cascades([row]))
            messages = [
                {"role": "system", "content": build_system_prompt(None, language)},
                {"role": "system", "content": (
                    f"{context}\nThis is the selected scenario. Use the ontology as authoritative. "
                    "Now provide the final scenario-specific response based on the collected details. "
                    "Lead with immediate actions, then risks, escalation guidance, and responsible teams."
                )},
                {"role": "user", "content": f"Collected assessment details:\n{user_details}"},
            ]
            return jsonify({
                "answer": call_genai(messages),
                "confidence": 100,
                "severity": row.get("default_severity", "moderate").lower(),
                "severity_icon": "🚨",
                "response_time": round(time.time() - start, 2),
                "fallback": False,
                "matched_faqs": [],
                "ontology": {"category": row["category"], "subcategory": row["subcategory"]},
            })

    selected_row = (
        find_scenario_in_query(retrieval_query)
        or find_keyword_scenario(retrieval_query)
    )
    # Only explicit subcategory/keyword evidence may select a scenario.  A
    # fuzzy match is useful for FAQ context but must not silently map the user
    # to an unrelated ontology record.
    ontology_matches = [selected_row] if selected_row else []
    if selected_row:
        questions = ontology_follow_up_questions(selected_row)
        if questions:
            session["ontology_flow"] = {
                "category": selected_row["category"],
                "subcategory": selected_row["subcategory"],
                "questions": questions,
                "answers": [],
            }
            return jsonify({
                "answer": translate_text(questions[0], language),
                "clarification": True,
                "clarification_type": "follow_up",
                "ontology": {"category": selected_row["category"], "subcategory": selected_row["subcategory"]},
                "response_time": round(time.time() - start, 2),
            })
    ontology_context = format_context(ontology_matches, get_cascades(ontology_matches))
    relevant   = find_relevant_faqs(retrieval_query, scenario_tag, top_k=3)
    confidence = get_confidence(retrieval_query, relevant)
    severity, severity_icon = detect_severity(f"{user_message} {retrieval_query}")

    # Smart fallback if confidence too low
    if confidence < 30 and not ontology_matches:
        fallback_topics = [
            {"tag": t, "label": FAQ_DATA[t]["label"], "icon": FAQ_DATA[t]["icon"]}
            for t in list(FAQ_DATA.keys())[:6]
        ]
        return jsonify({
            "answer": translate_text("I couldn't find an exact answer to your question.", language),
            "confidence": confidence,
            "severity": severity,
            "severity_icon": severity_icon,
            "response_time": round(time.time() - start, 2),
            "fallback": True,
            "fallback_topics": fallback_topics,
            "matched_faqs": []
        })

    faq_context = "\n".join(f"Q: {f['q']}\nA: {f['a']}" for f in relevant)

    messages = [{"role": "system", "content": build_system_prompt(scenario_tag, language)}]
    if ontology_context:
        messages.append({
            "role": "system",
            "content": (
                f"{ontology_context}\nUse this ontology as authoritative scenario context. "
                "Give the listed immediate actions first, ask only the relevant follow-up "
                "questions, and mention escalation or cascading risks when applicable."
            ),
        })
    if faq_context:
        messages.append({"role": "system", "content": f"Relevant FAQ reference:\n{faq_context}"})
    messages.extend(history[-6:])
    messages.append({"role": "user", "content": user_message})

    answer  = call_genai(messages)
    elapsed = round(time.time() - start, 2)

    return jsonify({
        "answer": answer,
        "confidence": confidence,
        "severity": severity,
        "severity_icon": severity_icon,
        "response_time": elapsed,
        "fallback": False,
        "matched_faqs": [{"q": f["q"], "tag": f["tag"]} for f in relevant]
    })

@app.route("/chat/reset", methods=["POST"])
def reset_chat():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    session.pop("ontology_flow", None)
    return jsonify({"success": True})

# ── SOS Generator ────────────────────────────────────────────────────────────
@app.route("/sos", methods=["POST"])
def sos():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data     = request.get_json()
    situation = data.get("situation", "").strip()
    location  = data.get("location", "Unknown Location").strip()
    people    = data.get("people", "1")
    medical   = data.get("medical", False)
    if not situation:
        return jsonify({"error": "Please describe the situation."}), 400
    messages = [
        {"role": "system", "content": "Generate a concise SOS emergency message. Format it clearly with: EMERGENCY TYPE, SITUATION, LOCATION, PEOPLE TRAPPED, MEDICAL NEEDED, and IMMEDIATE ACTION REQUIRED. Keep it under 80 words."},
        {"role": "user", "content": f"Situation: {situation}. Location: {location}. People: {people}. Medical needed: {medical}."}
    ]
    sos_msg = call_genai(messages)
    return jsonify({"sos_message": sos_msg})

# ── Checklist ─────────────────────────────────────────────────────────────────
@app.route("/checklist", methods=["POST"])
def checklist():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data     = request.get_json()
    scenario = data.get("scenario", "general")
    checklists = {
        "fire":       ["Exit the building immediately", "Do not use the elevator", "Activate fire alarm", "Call 101 (Fire Services)", "Stay low to avoid smoke", "Close doors behind you", "Meet at designated assembly point"],
        "flood":      ["Move to higher ground", "Turn off electricity at main switch", "Avoid walking in floodwater", "Take emergency kit", "Call 1077 (Disaster Helpline)", "Lock your home", "Follow evacuation route"],
        "earthquake": ["Drop, Cover, Hold On", "Stay away from windows", "Turn off gas supply", "Check for injuries", "Watch for aftershocks", "Do not use elevators", "Call 112 if trapped"],
        "cyclone":    ["Stay indoors away from windows", "Secure loose outdoor objects", "Stock food and water", "Charge all devices", "Know nearest cyclone shelter", "Follow official evacuation orders", "Do not go out during eye of cyclone"],
        "medical":    ["Call 108 immediately", "Keep person calm and still", "Do not give food or water", "Perform CPR if trained", "Note time symptoms started", "Collect medicines and documents", "Stay on line with dispatcher"],
        "landslide":  ["Evacuate immediately uphill", "Do not stop for belongings", "Alert neighbours", "Call 112", "Avoid river valleys", "Watch for secondary slides", "Do not enter damaged buildings"],
        "heatwave":   ["Stay indoors 12pm-4pm", "Drink water every 30 minutes", "Wear light loose clothing", "Check on elderly and children", "Use fans or AC", "Avoid alcohol and caffeine", "Call 108 for heat stroke"],
        "chemical":   ["Evacuate upwind immediately", "Cover nose and mouth", "Do not touch the substance", "Call 112 and 101", "Remove contaminated clothing", "Flush skin with water 15 mins", "Shelter in place if told to"],
        "general":    ["Call 112 for any emergency", "Stay calm and assess situation", "Help injured if trained", "Follow official instructions", "Keep emergency kit ready", "Know your evacuation route", "Stay informed via radio/TV"]
    }
    items = checklists.get(scenario, checklists["general"])
    return jsonify({"checklist": items, "scenario": scenario})

# ── Admin Dashboard ───────────────────────────────────────────────────────────
@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect(url_for("login"))
    total_faqs = sum(len(s["faqs"]) for s in FAQ_DATA.values())
    users      = load_users()
    return render_template("admin.html",
        scenarios=FAQ_DATA,
        total_faqs=total_faqs,
        total_users=len(users),
        username=session.get("name", "Admin")
    )

@app.route("/admin/add-faq", methods=["POST"])
def add_faq():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data     = request.get_json()
    scenario = data.get("scenario", "").strip()
    question = data.get("question", "").strip()
    answer   = data.get("answer", "").strip()
    if not scenario or not question or not answer:
        return jsonify({"error": "All fields required."}), 400
    if scenario not in FAQ_DATA:
        return jsonify({"error": "Invalid scenario."}), 400
    with open("faq_data.json", "r", encoding="utf-8") as f:
        raw = json.load(f)
    raw["scenarios"][scenario]["faqs"].append({"q": question, "a": answer})
    with open("faq_data.json", "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    ALL_FAQS.append({"tag": scenario, "label": FAQ_DATA[scenario]["label"], "q": question, "a": answer})
    FAQ_DATA[scenario]["faqs"].append({"q": question, "a": answer})
    return jsonify({"success": True, "total": len(FAQ_DATA[scenario]["faqs"])})

@app.route("/admin/delete-faq", methods=["POST"])
def delete_faq():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data     = request.get_json()
    scenario = data.get("scenario", "")
    index    = data.get("index", -1)
    if scenario not in FAQ_DATA or index < 0 or index >= len(FAQ_DATA[scenario]["faqs"]):
        return jsonify({"error": "Invalid request."}), 400
    with open("faq_data.json", "r", encoding="utf-8") as f:
        raw = json.load(f)
    raw["scenarios"][scenario]["faqs"].pop(index)
    with open("faq_data.json", "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    FAQ_DATA[scenario]["faqs"].pop(index)
    return jsonify({"success": True})

@app.route("/admin/faqs/<scenario>")
def get_faqs(scenario):
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    if scenario not in FAQ_DATA:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"faqs": FAQ_DATA[scenario]["faqs"]})

# ── Quiz ──────────────────────────────────────────────────────────────────────
@app.route("/quiz")
def quiz():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("quiz.html", username=session.get("name", "User"))

# ── Contacts ──────────────────────────────────────────────────────────────────
# Maps ontology primary_response_team / supporting_response_teams to Indian numbers
TEAM_CONTACTS = {
    "fire and rescue":              {"name": "Fire Services",        "number": "101",           "icon": "🔥"},
    "ambulance/ems":                {"name": "Ambulance",            "number": "108",           "icon": "🚑"},
    "ambulance": {"name": "Ambulance", "number": "108", "icon": "🚑"},
    "police":                       {"name": "Police",               "number": "100",           "icon": "👮"},
    "disaster management":          {"name": "Disaster Helpline",    "number": "1077",          "icon": "🌊"},
    "coast guard":                  {"name": "Coast Guard",          "number": "1554",          "icon": "⚓"},
    "marine rescue":                {"name": "Coast Guard",          "number": "1554",          "icon": "⚓"},
    "fire hazmat unit":             {"name": "Chemical Emergency",   "number": "1800-180-5999", "icon": "☣️"},
    "hazmat":                       {"name": "Chemical Emergency",   "number": "1800-180-5999", "icon": "☣️"},
    "public health authority":      {"name": "Health Helpline",      "number": "104",           "icon": "🏥"},
    "electric utility":             {"name": "Power Emergency",      "number": "1912",          "icon": "⚡"},
    "gas utility":                  {"name": "Gas Emergency",        "number": "1906",          "icon": "💨"},
    "water authority":              {"name": "Water Authority",      "number": "1916",          "icon": "💧"},
    "ndma":                         {"name": "NDMA Helpline",        "number": "1070",          "icon": "🏛️"},
    "urban search and rescue":      {"name": "NDRF / USAR",          "number": "011-24363260",  "icon": "🪖"},
    "usar":                         {"name": "NDRF / USAR",          "number": "011-24363260",  "icon": "🪖"},
    "transit or rail control centre": {"name": "Railway Helpline",  "number": "139",           "icon": "🚆"},
    "aviation authority":           {"name": "Airport Emergency",    "number": "1800-180-1407", "icon": "✈️"},
    "forest fire":                  {"name": "Forest Fire",          "number": "1926",          "icon": "🌲"},
}

def get_scenario_contacts(scenario_tag):
    """Return relevant contacts for a FAQ scenario tag by matching ontology teams."""
    from ontology import _ROWS
    # Map FAQ tag to ontology category keywords
    tag_to_category = {
        "fire":       "Structural Collapse or Severe Fire",
        "flood":      "Flash Flooding and Infrastructure Failure",
        "earthquake": "Natural Disaster",
        "cyclone":    "Natural Disaster",
        "medical":    None,
        "chemical":   "Hazardous Chemical Leak or Toxic Gas Release",
    }
    category = tag_to_category.get(scenario_tag)
    rows = [r for r in _ROWS if category and r.get("category") == category] if category else []

    seen_numbers = set()
    contacts = []
    for row in rows:
        teams = [t.strip().lower() for t in
                 (row.get("primary_response_team", "") + ";" + row.get("supporting_response_teams", "")).split(";")]
        for team in teams:
            for key, info in TEAM_CONTACTS.items():
                if key in team and info["number"] not in seen_numbers:
                    seen_numbers.add(info["number"])
                    contacts.append(info)
    # Always include 112 as fallback
    if "112" not in seen_numbers:
        contacts.insert(0, {"name": "National Emergency", "number": "112", "icon": "🆘"})
    return contacts

@app.route("/contacts")
def contacts():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("contacts.html", username=session.get("name", "User"))

@app.route("/api/contacts/<scenario_tag>")
def api_contacts(scenario_tag):
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"contacts": get_scenario_contacts(scenario_tag)})

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    image_data = data.get("image", "")
    scenario_tag = data.get("scenario")
    language = data.get("language", "English")
    if not image_data:
        return jsonify({"error": "No image provided."}), 400
    start = time.time()
    messages = [
        {"role": "system", "content": build_system_prompt(scenario_tag, language)},
        {"role": "user", "content": [
            {"type": "text", "text": "Analyze this image in the context of emergency response. Describe what you see, identify any hazards, and provide relevant safety guidance."},
            {"type": "image_url", "image_url": {"url": image_data}}
        ]}
    ]
    answer = call_genai(messages)
    return jsonify({"answer": answer, "response_time": round(time.time() - start, 2)})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
