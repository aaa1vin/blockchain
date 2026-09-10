import json
import urllib.request
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


VERSION_FLOOR_URL = (
    "https://raw.githubusercontent.com/wiki/anza-xyz/agave/version-floor.json"
)

def get_version_floor():
    """Fetch the latest version floor information from Anza."""
    with urllib.request.urlopen(VERSION_FLOOR_URL, timeout=10) as response:
        return json.load(response)

def generate_html_table(data):
    """Generate the HTML version table."""

    html = """
    <table style="
        border-collapse: collapse;
        width: 100%;
        max-width: 700px;
        font-family: Arial, Helvetica, sans-serif;
        font-size: 14px;
    ">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th style="
                    border: 1px solid #d9d9d9;
                    padding: 10px;
                    text-align: left;
                ">Network</th>

                <th style="
                    border: 1px solid #d9d9d9;
                    padding: 10px;
                    text-align: left;
                ">Current Version</th>

                <th style="
                    border: 1px solid #d9d9d9;
                    padding: 10px;
                    text-align: left;
                ">Next Version Floor</th>
            </tr>
        </thead>
        <tbody>
    """

    network_order = [
        "Devnet",
        "Mainnet Beta"
    ]

    for network in network_order:

        if network not in data:
            continue

        current = data[network].get("current", {})
        next_version = data[network].get("next", {})

        current_version = current.get("Agave", "-")
        next_floor = next_version.get("Agave", "-")

        html += f"""
            <tr>
                <td style="
                    border: 1px solid #d9d9d9;
                    padding: 10px;
                ">{network}</td>

                <td style="
                    border: 1px solid #d9d9d9;
                    padding: 10px;
                    font-family: monospace;
                ">{current_version}</td>

                <td style="
                    border: 1px solid #d9d9d9;
                    padding: 10px;
                    font-family: monospace;
                ">{next_floor}</td>
            </tr>
        """

    html += """
        </tbody>
    </table>
    """

    return html


def generate_body(data):
    """Generate the complete HTML email body."""

    table = generate_html_table(data)

    html = f"""
    <html>
    <body style="
        font-family: Arial, Helvetica, sans-serif;
        color: #333333;
        font-size: 14px;
    ">
        <p style="margin-top: 20px;">
        Please find below the current Agave version and next
        <a href="{VERSION_FLOOR_URL}"
            style="color: #0563C1; text-decoration: underline;">
            version-floor
        </a>
        (Devnet & Mainnet Beta) maintained by Anza
        </p>
        {table}

    </body>
    </html>
    """

    return html

if __name__ == "__main__":

    # Get latest version information
    version_data = get_version_floor()

    # Generate HTML email body
    print(generate_body(version_data))
