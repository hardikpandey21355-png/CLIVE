from flask import Flask, render_template, request, jsonify
import razorpay

app = Flask(__name__)

# Test-mode keys — move these to environment variables before going live
RAZORPAY_KEY_ID = "rzp_test_TBnXWTt9rFtOxe"
RAZORPAY_KEY_SECRET = "afZVuj7yyiPNjE1yfR1S6Miu"
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.route("/")
def home_page():
    return render_template("HomePage.html")

# Home page to about page
@app.route('/about')
def about():
    return render_template('about.html')

#  Home page to voice page
@app.route('/voice')
def voice():
    return render_template('voice.html')

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


if __name__ == "__main__":
    app.run(debug=True)