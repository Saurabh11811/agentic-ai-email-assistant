from bs4 import BeautifulSoup

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n").strip()

def normalize_body(text):
    return extract_text_from_html(text or "")

def construct_email_doc(msg, account, full_body=""):
    return {
        "id": msg.get("id"),
        "subject": msg.get("subject", ""),
        "sender": msg.get("from", {}).get("emailAddress", {}).get("address", "") or msg.get("sender", ""),
        "body": normalize_body(full_body or msg.get("bodyPreview", "")),
        "receivedDateTime": msg.get("receivedDateTime") or msg.get("internalDate"),
        "messageId": msg.get("internetMessageId", msg.get("id")),
        "account": account,
        #"raw": msg
    }
