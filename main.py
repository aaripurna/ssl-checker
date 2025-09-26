import ssl
import socket
import datetime
from urllib.error import HTTPError
import urllib.request
import json
import os

DAYS_THRESHOLD=os.getenv("DAYS_THRESHOLD") or "2"
TELEGRAM_ACCESS_TOKEN=os.getenv("TELEGRAM_ACCESS_TOKEN")
TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID")

class InvalidArgumentError(Exception):
    pass

def send_notification(message: str) -> None:
    try:
        json_data = json.dumps({
             "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "MarkdownV2"
        })

        encoded_data = json_data.encode('utf-8')

        request_data = urllib.request.Request(
            url=f"https://api.telegram.org/bot{TELEGRAM_ACCESS_TOKEN}/sendMessage",
            method="POST",
            headers={
                "Content-Type": "application/json"
            },
            data=encoded_data
        )
        with urllib.request.urlopen(request_data) as response:
            print(response)
    except HTTPError as e:
        print(e.code)
        print(e.reason)
        print(e.fp.read())
    except Exception as e:
        print(e)
        print("Failed to send telegram")
            

def parse_md_friendly(data: str) -> str:
    return data.replace(".", '\.').replace("#", '\#')


def check_ssl_status(hostname: str) -> None:
    """
    Checks the SSL certificate status for a given hostname.
    """
    try:
        if hostname is None or hostname == "":
            raise InvalidArgumentError("Hostname required")
        # Create a default SSL context for secure communication
        context = ssl.create_default_context()

        # Establish a socket connection to the hostname on port 443 (HTTPS)
        with socket.create_connection((hostname, 443)) as sock:
            # Wrap the socket with SSL/TLS and perform the handshake
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # Get the peer certificate details
                cert = ssock.getpeercert()

                # Extract and print relevant information
                print(f"SSL Certificate Status for {hostname}:")
                print(f"  Subject: {cert['subject']}")
                print(f"  Issuer: {cert['issuer']}")

                # Convert 'notAfter' timestamp to datetime object
                not_after_str = cert['notAfter']
                not_after_dt = datetime.datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
                print(f"  Expiration Date: {not_after_dt}")

                # Calculate days remaining until expiration
                days_left = (not_after_dt - datetime.datetime.now()).days
                print(f"  Days Remaining: {days_left}")
                
                print("  Certificate is valid.")

                if days_left <= int(DAYS_THRESHOLD):
                    text = f"*{hostname}*" \
                    f"\nThe Certificate will expire in {days_left} days"
                    send_notification(parse_md_friendly(text))

    except ssl.SSLError as e:
        send_notification(f"SSL Error for {hostname}: {e}")
        print(f"SSL Error for {hostname}: {e}")
    except socket.error as e:
        print(f"Socket Error for {hostname}: {e}")
    except IndexError as e:
        print(f"Hostname is required")
    except Exception as e:
        print(f"An unexpected error occurred for {hostname}: {e}")

check_ssl_status("ecoclean.co.id")