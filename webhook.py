import stripe
import os
from flask import Flask, request, jsonify
from supabase import create_client

app = Flask(__name__)

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
endpoint_secret = os.environ["STRIPE_WEBHOOK_SECRET"]

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

@app.route("/webhook", methods=["POST"])
def stripe_webhook():

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception:
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session["id"]

        supabase.table("payments") \
            .update({"is_paid": True}) \
            .eq("session_id", session_id) \
            .execute()

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run()
