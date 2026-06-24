"""Nudge delivery service — real channel senders, consent-gated.

Sends an approved nudge over its channel using a real provider:
  - WhatsApp : Meta Cloud API  OR  Twilio
  - SMS      : Twilio
  - email / app_notification : SMTP

Every send is (1) blocked unless the customer has active consent covering the
channel, (2) attempted against the real provider when configured, and (3)
recorded as a DeliveryReceipt + audit entry. When a provider isn't configured
the result is an honest "not_configured" — it is never faked as "sent".
"""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from config import settings
from database.connection import SessionLocal
from database.models import DeliveryReceipt, Nudge
from services import audit, consent

log = logging.getLogger("finpulse.delivery")


def _receipt(nudge_id: str, customer_id: str, channel: str, provider: str,
             status: str, provider_message_id: str | None = None,
             error: str | None = None) -> dict:
    db = SessionLocal()
    try:
        rec = DeliveryReceipt(
            nudge_id=nudge_id, customer_id=customer_id, channel=channel,
            provider=provider, status=status, provider_message_id=provider_message_id,
            error=error,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        rid = rec.id
    finally:
        db.close()
    audit.record("nudge.delivery", customer_id=customer_id, actor="system",
                 entity_type="nudge", entity_id=nudge_id,
                 detail={"channel": channel, "provider": provider, "status": status,
                         "receipt_id": rid, "error": error})
    return {"receipt_id": rid, "channel": channel, "provider": provider,
            "status": status, "provider_message_id": provider_message_id, "error": error}


# --- channel senders -------------------------------------------------------
def _send_whatsapp(to: str, body: str) -> tuple[str, str | None, str | None]:
    """Returns (status, provider_message_id, error)."""
    if settings.whatsapp_provider == "meta":
        if not settings.has_meta_whatsapp:
            return "not_configured", None, "Meta WhatsApp not configured"
        url = f"https://graph.facebook.com/v19.0/{settings.meta_wa_phone_id}/messages"
        headers = {"Authorization": f"Bearer {settings.meta_wa_token}"}
        payload = {"messaging_product": "whatsapp", "to": to, "type": "text",
                   "text": {"body": body}}
        try:
            r = httpx.post(url, headers=headers, json=payload, timeout=30.0)
            r.raise_for_status()
            mid = (r.json().get("messages") or [{}])[0].get("id")
            return "sent", mid, None
        except Exception as e:
            return "failed", None, str(e)
    # twilio
    if not (settings.has_twilio and settings.twilio_whatsapp_from):
        return "not_configured", None, "Twilio WhatsApp not configured"
    return _twilio_message(f"whatsapp:{to}" if not to.startswith("whatsapp:") else to,
                           settings.twilio_whatsapp_from, body)


def _send_sms(to: str, body: str) -> tuple[str, str | None, str | None]:
    if not (settings.has_twilio and settings.twilio_sms_from):
        return "not_configured", None, "Twilio SMS not configured"
    return _twilio_message(to, settings.twilio_sms_from, body)


def _twilio_message(to: str, frm: str, body: str) -> tuple[str, str | None, str | None]:
    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
    try:
        r = httpx.post(url, data={"To": to, "From": frm, "Body": body},
                       auth=(settings.twilio_account_sid, settings.twilio_auth_token),
                       timeout=30.0)
        r.raise_for_status()
        return "sent", r.json().get("sid"), None
    except Exception as e:
        return "failed", None, str(e)


def _split_disclaimer(message: str) -> tuple[str, str]:
    """Peel a trailing regulatory disclaimer off the message body (if present)."""
    parts = [p.strip() for p in (message or "").split("\n\n") if p.strip()]
    if len(parts) >= 2 and any(tok in parts[-1].lower() for tok in
                               ("subject to", "solicitation", "free-look",
                                "read all scheme", "market risk", "key fact")):
        return "\n\n".join(parts[:-1]).strip(), parts[-1].strip()
    return (message or "").strip(), ""


def _build_nudge_email(customer_name: str, product: str,
                       message: str) -> tuple[str, str, str]:
    """Return (subject, plain_text, html) for a polished, branded nudge email."""
    name = (customer_name or "Customer").split()[0]
    product = product or "Your finances"
    body, disclaimer = _split_disclaimer(message)

    subject = f"{product}: a personalised suggestion from SBI FinPulse"

    # ---- plain-text fallback (always sent alongside the HTML) ----
    plain_lines = [f"Dear {name},", "", body, ""]
    if disclaimer:
        plain_lines += [disclaimer, ""]
    plain_lines += [
        "Manage your preferences or withdraw consent anytime in the SBI FinPulse app.",
        "",
        "Warm regards,",
        "SBI FinPulse - your proactive financial companion",
        "",
        "You are receiving this because you enabled proactive engagement "
        "(consent under the DPDP Act, 2023).",
    ]
    plain = "\n".join(plain_lines)

    # ---- HTML body (inline styles — required for email clients) ----
    body_html = "".join(
        f'<p style="margin:0 0 14px;font-size:15px;line-height:1.6;color:#33334d;">{p.strip()}</p>'
        for p in body.split("\n\n") if p.strip()
    )
    disclaimer_html = (
        f'<div style="margin-top:22px;padding:12px 14px;background:#f5f6ff;'
        f'border-left:3px solid #C49B2A;border-radius:6px;">'
        f'<p style="margin:0;font-size:11px;line-height:1.5;color:#8a8aa3;">'
        f'<strong style="color:#6b6b85;">Important:</strong> {disclaimer}</p></div>'
        if disclaimer else ""
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#eef0f8;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
  <div style="display:none;max-height:0;overflow:hidden;">{product} — a personalised suggestion picked for you.</div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef0f8;padding:28px 12px;">
    <tr><td align="center">
      <table role="presentation" width="600" cellpadding="0" cellspacing="0"
        style="max-width:600px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;
        box-shadow:0 8px 28px rgba(26,35,126,0.12);">

        <!-- header -->
        <tr><td style="background:linear-gradient(135deg,#1A237E 0%,#283593 55%,#3F51B5 100%);
          padding:26px 32px;">
          <table role="presentation" width="100%"><tr>
            <td style="font-family:'Segoe UI',Arial,sans-serif;color:#ffffff;font-size:20px;font-weight:700;
              letter-spacing:.3px;">SBI <span style="font-weight:400;">FinPulse</span></td>
            <td align="right" style="color:rgba(255,255,255,.85);font-size:11px;font-weight:600;
              text-transform:uppercase;letter-spacing:.6px;">State Bank of India</td>
          </tr></table>
        </td></tr>

        <!-- gold accent rule -->
        <tr><td style="height:3px;background:#C49B2A;line-height:3px;font-size:0;">&nbsp;</td></tr>

        <!-- body -->
        <tr><td style="padding:30px 32px 8px;">
          <p style="margin:0 0 18px;font-size:16px;color:#1a1a2e;font-weight:600;">Dear {name},</p>
          {body_html}
          <table role="presentation" cellpadding="0" cellspacing="0" style="margin:22px 0 6px;">
            <tr><td style="border-radius:10px;background:linear-gradient(135deg,#1A237E,#3F51B5);">
              <a href="https://yono.sbi" target="_blank"
                style="display:inline-block;padding:12px 26px;font-size:14px;font-weight:700;
                color:#ffffff;text-decoration:none;border-radius:10px;">Explore on YONO &rarr;</a>
            </td></tr>
          </table>
          {disclaimer_html}
        </td></tr>

        <!-- footer -->
        <tr><td style="padding:22px 32px 28px;border-top:1px solid #ececf4;">
          <p style="margin:0 0 6px;font-size:12px;color:#6b6b85;line-height:1.6;">
            Warm regards,<br><strong style="color:#1A237E;">SBI FinPulse</strong> — your proactive financial companion
          </p>
          <p style="margin:12px 0 0;font-size:11px;color:#a0a0b5;line-height:1.6;">
            You are receiving this because you enabled <strong>proactive engagement</strong>
            (consent under the DPDP Act, 2023). You can withdraw consent anytime from the
            SBI FinPulse app &middot; Profile &middot; Proactive engagement.
          </p>
          <p style="margin:10px 0 0;font-size:11px;color:#b8b8c8;">
            &copy; State Bank of India &middot; This is a service communication from SBI FinPulse.
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body></html>"""
    return subject, plain, html


def _send_email(to: str, subject: str, body: str,
                html: str | None = None) -> tuple[str, str | None, str | None]:
    if not settings.has_smtp:
        return "not_configured", None, "SMTP not configured"
    if not to:
        return "failed", None, "no email address on customer"
    try:
        if html:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(body, "plain", "utf-8"))
            msg.attach(MIMEText(html, "html", "utf-8"))
        else:
            msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = to

        # Port 465 uses implicit SSL; 587 uses STARTTLS; anything else: STARTTLS.
        if int(settings.smtp_port) == 465:
            import ssl
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port,
                                  context=ctx, timeout=30) as s:
                s.login(settings.smtp_user, settings.smtp_password)
                s.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as s:
                s.starttls()
                s.login(settings.smtp_user, settings.smtp_password)
                s.send_message(msg)
        return "sent", None, None
    except Exception as e:
        return "failed", None, str(e)


# --- public API ------------------------------------------------------------
def deliver_nudge(nudge_id: str, *, actor: str = "system") -> dict:
    """Deliver a single nudge over its channel after consent + state checks."""
    db = SessionLocal()
    try:
        n = db.query(Nudge).filter(Nudge.id == nudge_id).first()
        if not n:
            raise ValueError("Nudge not found")
        customer_id = n.customer_id
        channel = (n.channel or "app_notification").lower()
        message = n.message_draft or ""
        product = n.product_name or "SBI"
        compliance_status = n.compliance_status
        from database.models import Customer
        cust = db.query(Customer).filter(Customer.id == customer_id).first()
        phone = cust.phone if cust else None
        email = cust.email if cust else None
        cust_name = cust.name if cust else "Customer"
    finally:
        db.close()

    # 1. compliance gate
    if compliance_status not in ("approved", "approved_with_modification"):
        return _receipt(nudge_id, customer_id, channel, "none", "blocked_compliance",
                        error=f"compliance status is '{compliance_status}'")

    # 2. consent gate (DPDP)
    decision = consent.check(customer_id, purpose=consent.PURPOSE_ENGAGEMENT, channel=channel)
    if not decision["allowed"]:
        return _receipt(nudge_id, customer_id, channel, "none", "blocked_no_consent",
                        error=decision["reason"])

    # 3. send over the real channel
    if channel in ("whatsapp", "wa"):
        status, mid, err = _send_whatsapp(phone or "", message)
        provider = settings.whatsapp_provider
    elif channel == "sms":
        status, mid, err = _send_sms(phone or "", message)
        provider = "twilio"
    else:  # email / app_notification / push
        subject, plain, html = _build_nudge_email(cust_name, product, message)
        status, mid, err = _send_email(email or "", subject, plain, html=html)
        provider = "smtp"

    # 4. reflect status back onto the nudge
    db = SessionLocal()
    try:
        n = db.query(Nudge).filter(Nudge.id == nudge_id).first()
        if n:
            n.status = "sent" if status == "sent" else "failed"
            db.commit()
    finally:
        db.close()

    return _receipt(nudge_id, customer_id, channel, provider, status,
                    provider_message_id=mid, error=err)
