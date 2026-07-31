from flask import Flask, render_template, request, jsonify, session
import razorpay
import requests
import base64
from Backend.project_files import extract_project_file_content, build_project_context
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()
from Backend.file_reader import build_file_context
from Backend.free_brain_plan import get_ai_response, generate_chat_title
from Backend.paid_plan_brain import get_paid_ai_response
from Backend.web_search import get_web_search_response
from Backend.deep_research import get_deep_research_response
from Backend.coder_mode import get_coder_response
from Backend.short_response import get_short_response
from flask import Response
from Backend.moods.funny_mode import get_funny_response
from Backend.moods.tutor_mode import get_tutor_response
from Backend.moods.friendly_mode import get_friendly_response
from Backend.moods.rude_mode import get_rude_response
from Backend.moods.sigma_mode import get_sigma_response

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-string"

# Test-mode keys — move these to environment variables before going live
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY")# paste your real key here
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


@app.route("/")
def home_page():
    return render_template("HomePage.html")


@app.route('/api/project/extract-file', methods=['POST'])
def extract_project_file():
    f = request.files.get('file')
    if not f:
        return jsonify({"error": "No file provided"}), 400
    content = extract_project_file_content(f)
    return jsonify({
        "name": f.filename,
        "content": content
    })

# Home page to about page
@app.route('/about')
def about():
    return render_template('about.html')

#  Home page to voice page
@app.route('/voice')
def voice():
    return render_template('voice.html')

@app.route('/voice/chat', methods=['POST'])
def voice_chat():
    data = request.get_json()
    user_message = (data or {}).get('message', '').strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    history = session.get('voice_chat_history', [])

    try:
        reply = get_ai_response(user_message, history=history)
    except Exception as e:
        print("Voice AI error:", e)
        return jsonify({"error": "AI request failed"}), 500

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    session['voice_chat_history'] = history[-20:]

    return jsonify({"reply": reply})


@app.route('/voice/speak', methods=['POST'])
def voice_speak():
    data = request.get_json()
    text = (data or {}).get('text', '').strip()

    if not text:
        return jsonify({"error": "Empty text"}), 400

    try:
        response = requests.post(
            "https://api.fish.audio/v1/tts",
            headers={
                "Authorization": f"Bearer {FISH_AUDIO_API_KEY}",
                "Content-Type": "application/json",
                "model": "s2.1-pro-free"
            },
            json={
                "text": text,
                "reference_id": "bf322df2096a46f18c579d0baa36f41d",
                "format": "mp3",
                "sample_rate": 44100,
                "mp3_bitrate": 128,
                "latency": "normal",
                "normalize": True
            }
        )

        if response.status_code != 200:
            print("Fish Audio TTS failed:", response.status_code, response.text[:500])
            return jsonify({"error": "Speech generation failed"}), 500

        return Response(response.content, mimetype="audio/mpeg")

    except Exception as e:
        print("Voice speak error:", e)
        return jsonify({"error": "Speech generation failed"}), 500
    

# Home page to projects page
@app.route("/projects")
def projects():
    return render_template("projects.html")

# Home page to personalize page
@app.route("/personalize")
def personalize():
    return render_template("personalize.html")

# Home page to background page 
@app.route('/Background')
def background():
    return render_template('Change_BackgroundVideos.html')

# Home page to setting page
@app.route('/setting')
def setting():
    return render_template('settings.html')

# Home page to upgrade page
@app.route('/upgrade')
def upgrade():
    return render_template('upgrade.html')


@app.route('/admin/payments')
def admin_payments():
    return render_template('admin_payments.html')


@app.route('/share/<share_id>')
def view_shared_chat(share_id):
    return render_template('share_view.html', share_id=share_id)


# Home page to Help button pop up option common issue page 
@app.route('/common-issues')
def common_issues():
    return render_template('components/Common_Issue.html')


# Home page to Help button pop up option Personal issue page 
@app.route('/personal-issue')
def personal_issue():
    return render_template('components/Personal_Issue.html')


@app.route('/login')
def login():
    return render_template('auth/login.html')


@app.route('/signup')
def signup():
    return render_template('auth/signup.html')


@app.route('/forgot-password')
def forgot_password():
    return render_template('auth/forgot_password.html')

# ── Student verification: ₹1 authorization hold, refunded instantly ──
@app.route('/api/create-verification-order', methods=['POST'])
def create_verification_order():
    order = razorpay_client.order.create({
        "amount": 100,  # ₹1 in paise — Razorpay doesn't support ₹0 orders
        "currency": "INR",
        "payment_capture": 1,
        "notes": {"purpose": "student-verification-hold"}
    })
    return jsonify({
        "order_id": order["id"],
        "key_id": RAZORPAY_KEY_ID,
        "amount": order["amount"]
    })


@app.route('/api/verify-and-refund', methods=['POST'])
def verify_and_refund():
    data = request.get_json()
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
    except razorpay.errors.SignatureVerificationError:
        return jsonify({"success": False, "error": "Signature verification failed"}), 400

    # Refund the ₹1 hold immediately — it only existed to verify the card is real
    razorpay_client.payment.refund(data['razorpay_payment_id'], {"amount": 100})

    return jsonify({"success": True, "payment_id": data['razorpay_payment_id']})



@app.route('/api/generate-title', methods=['POST'])
def api_generate_title():
    data = request.get_json()
    user_message = (data or {}).get('user_message', '').strip()
    ai_message = (data or {}).get('ai_message', '').strip()

    if not user_message or not ai_message:
        return jsonify({"error": "Missing messages"}), 400

    try:
        title = generate_chat_title(user_message, ai_message)
    except Exception as e:
        print("Title generation error:", e)
        return jsonify({"error": "Title generation failed"}), 500

    return jsonify({"title": title})




@app.route('/api/chat', methods=['POST'])
def api_chat():
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        user_message = str((payload or {}).get('message', '')).strip()
        privacy_value = (payload or {}).get('privacy', 'false')
        is_private = str(privacy_value).lower() == 'true'
        feature = str((payload or {}).get('feature', 'none'))
        mood = str((payload or {}).get('mood', 'default'))
        plan = str((payload or {}).get('plan', 'free')).lower()
        uploaded_files = []
    else:
        payload = request.form or request.values
        user_message = str(payload.get('message', '')).strip()
        privacy_value = payload.get('privacy', 'false')
        is_private = str(privacy_value).lower() == 'true'
        feature = str(payload.get('feature', 'none'))
        mood = str(payload.get('mood', 'default'))
        plan = str(payload.get('plan', 'free')).lower()
        uploaded_files = request.files.getlist('files')

    file_context = build_file_context(uploaded_files)

    if request.is_json:
        project_name = str((payload or {}).get('project_name', ''))
        project_description = str((payload or {}).get('project_description', ''))
        project_resources_raw = (payload or {}).get('project_resources', '[]')
    else:
        project_name = str(payload.get('project_name', ''))
        project_description = str(payload.get('project_description', ''))
        project_resources_raw = payload.get('project_resources', '[]')

    try:
        project_resources = json.loads(project_resources_raw) if project_resources_raw else []
    except (ValueError, TypeError):
        project_resources = []

    project_context = build_project_context(project_name, project_description, project_resources)

    if not user_message and not file_context:
        return jsonify({"error": "Empty message"}), 400

    combined_message = user_message
    if file_context:
        combined_message += (
            f"\n\n[The user attached the following file(s) — use them as context "
            f"for your answer:]{file_context}"
        )
    if project_context:
        combined_message += project_context

    CODE_REQUEST_PATTERN = re.compile(
        r"\b(full code|entire code|complete code|whole code|entire file|"
        r"full file|show me the code|give me the code|share the code|"
        r"paste the code|the updated code|rewrite the code|updated file)\b",
        re.IGNORECASE
    )
    if (project_context or file_context) and CODE_REQUEST_PATTERN.search(user_message):
        combined_message += (
            "\n\n[Note: The user is asking you to output code or file content. "
            "You MUST wrap the ENTIRE code/content in a fenced code block using "
            "triple backticks with the correct language tag (e.g. ```html, "
            "```python, ```javascript) matching the relevant file's type. Do NOT "
            "output code as plain unformatted paragraphs. Preserve original "
            "formatting/indentation exactly. Do this even for long files — split "
            "into multiple fenced blocks if needed, but never drop the backticks.]"
        )

    history = session.get('chat_history', [])
    print("DEBUG — feature:", feature, "| mood:", mood, "| plan:", plan)

    try:
        if feature == 'webSearch':
            reply = get_web_search_response(combined_message, history=history)
        elif feature == 'deepResearch':
            reply = get_deep_research_response(combined_message, history=history)
        elif feature == 'coder':
            reply = get_coder_response(combined_message, history=history)
        elif feature == 'shortResponse':
            reply = get_short_response(combined_message, history=history)
        elif mood == 'funny':
            reply = get_funny_response(combined_message, history=history)
        elif mood == 'tutor':
            reply = get_tutor_response(combined_message, history=history)
        elif mood == 'friendly':
            reply = get_friendly_response(combined_message, history=history)
        elif mood == 'rude':
            reply = get_rude_response(combined_message, history=history)
        elif mood == 'sigma':
            reply = get_sigma_response(combined_message, history=history)
        else:
            if plan != 'free':
                reply = get_paid_ai_response(combined_message, history=history)
            else:
                reply = get_ai_response(combined_message, history=history)
    except Exception as e:
        print("AI error:", e)
        return jsonify({"error": "AI request failed"}), 500

    if not is_private:
        history.append({"role": "user", "content": user_message or "[Sent an attachment]"})
        history.append({"role": "assistant", "content": reply})
        session['chat_history'] = history[-20:]

    return jsonify({"reply": reply})



@app.route('/api/generate-image', methods=['POST'])
def api_generate_image():
    data = request.get_json()
    prompt = (data or {}).get('prompt', '').strip()

    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400

    try:
        url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"

        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "prompt": prompt
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print("Cloudflare image gen failed:", response.status_code, response.text[:500])
            return jsonify({"error": "Image generation failed"}), 500

        try:
            result_json = response.json()
        except ValueError:
            print("Cloudflare returned non-JSON response:", response.text[:500])
            return jsonify({"error": "Image generation failed"}), 500

        if not result_json.get("success"):
            print("Cloudflare image gen error:", result_json.get("errors"))
            return jsonify({"error": "Image generation failed"}), 500

        image_b64 = result_json.get("result", {}).get("image")
        if not image_b64:
            print("Cloudflare response missing image data:", result_json)
            return jsonify({"error": "Image generation failed"}), 500

        return jsonify({
            "image": f"data:image/jpeg;base64,{image_b64}"
        })

    except Exception as e:
        print("Image generation error:", e)
        return jsonify({"error": "Image generation failed"}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)