# AMAPI SUNMI Colab Script (cell-friendly)
# Copy/paste each section into separate Colab cells as needed.

# SECTION 1: ENVIRONMENT SETUP
# Install required libraries for AMAPI and QR generation
!pip -q install google-api-python-client google-auth-oauthlib qrcode[pil]

# SECTION 2: AUTHENTICATION
# Upload service_account.json into the Colab environment
from google.colab import files

uploaded = files.upload()  # Select your service_account.json

# Initialize the Android Management API service using the service account
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ["https://www.googleapis.com/auth/androidmanagement"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Build the AMAPI service client
amapi_service = build("androidmanagement", "v1", credentials=credentials)

# PROJECT CONFIGURATION
# Set the project-level variables used throughout this notebook.
# Google Cloud Project ID that hosts Android Management API
PROJECT_ID = "YOUR_GCP_PROJECT_ID"

# Android Management API enterprise ID (e.g., "LC02abcd123")
ENTERPRISE_ID = "ENTERPRISE_ID_HERE"

# Policy ID used in this notebook (the policy name will be derived from it)
POLICY_ID = "sunmi_test_policy"

# Optional: set environment variables for reuse in other cells/tools
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["AMAPI_ENTERPRISE_ID"] = ENTERPRISE_ID
os.environ["AMAPI_POLICY_ID"] = POLICY_ID

# SECTION 3: ENTERPRISE & POLICY DEFINITION
# Full resource name for the policy
policy_name = f"enterprises/{ENTERPRISE_ID}/policies/{POLICY_ID}"

policy_body = {
    # Applications to manage on the device
    "applications": [
        {
            # Application 1: Managed Home Screen (Microsoft Launcher)
            "packageName": "com.microsoft.launcher.enterprise",
            # Install type ensures it is installed before kiosk setup
            "installType": "FORCE_INSTALLED",
            # Managed configuration for Managed Home Screen
            "managedConfiguration": {
                # Home screen layout for a 3x3 grid
                "home_screen": {
                    "grid": {"rows": 3, "columns": 3},
                    # Pin apps to specific positions in the grid
                    "pinnedApps": [
                        {
                            # Top center position (1) in a 3x3 grid
                            "packageName": "com.android.settings",
                            "position": 1,
                        },
                        {
                            # Center position (4) in a 3x3 grid
                            "packageName": "com.your.lablit",
                            "position": 4,
                        },
                    ],
                    # Create a "Tools" folder containing remote assistance
                    "folders": [
                        {
                            "name": "Tools",
                            "apps": [
                                {"packageName": "com.sunmi.remoteassistance"}
                            ],
                        }
                    ],
                },
            },
        },
        {
            # Application 2: SUNMI OEMConfig
            "packageName": "com.sunmi.oemconfig.V2S",
            "installType": "FORCE_INSTALLED",
            # Managed configurations specific to SUNMI OEMConfig
            "managedConfiguration": {
                # Mute media volume on the device
                "media_volume": 0,
                # Show battery percentage in the status bar
                "show_battery_percentage": True,
            },
        },
        {
            # Application 3: Main App (Your custom app)
            "packageName": "com.your.lablit",
            # Force install the main app
            "installType": "FORCE_INSTALLED",
            # Grant all runtime permissions automatically
            "defaultPermissionPolicy": "GRANT",
        },
    ],
    # System update policy to allow updates only during a maintenance window
    "systemUpdate": {
        "type": "WINDOWED",
        # Start time in minutes after midnight (02:00)
        "startMinutes": 120,
        # End time in minutes after midnight (05:00)
        "endMinutes": 300,
    },
}

# Create or update the policy in AMAPI
policy = (
    amapi_service.enterprises()
    .policies()
    .patch(name=policy_name, body=policy_body)
    .execute()
)

print("Policy updated:")
print(json.dumps(policy, indent=2))

# SECTION 4: QR CODE GENERATION
import qrcode
from IPython.display import display

# Constants for AMAPI/CloudDPC provisioning
CLOUD_DPC_COMPONENT = "com.google.android.apps.work.clouddpc/.receivers.CloudDpcReceiver"
CLOUD_DPC_DOWNLOAD_URL = "https://play.google.com/managed/downloadManagingApp?identifier=setup"


def generate_qr_code(wifi_ssid=None, wifi_password=None):
    # Generates a QR code for device provisioning.
    # wifi_ssid: Wi-Fi SSID if device should join Wi-Fi during setup.
    # wifi_password: Wi-Fi password if device should join Wi-Fi during setup.

    # Create an enrollment token tied to the policy
    token_body = {
        # Policy name to apply during enrollment
        "policyName": policy_name,
    }

    token = (
        amapi_service.enterprises()
        .enrollmentTokens()
        .create(parent=f"enterprises/{ENTERPRISE_ID}", body=token_body)
        .execute()
    )

    enrollment_token = token["value"]

    # Build provisioning extras for QR code
    provisioning_extras = {
        # CloudDPC component used for AMAPI provisioning
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_COMPONENT_NAME": CLOUD_DPC_COMPONENT,
        # Where to download CloudDPC if not present
        "android.app.extra.PROVISIONING_DEVICE_ADMIN_PACKAGE_DOWNLOAD_LOCATION": CLOUD_DPC_DOWNLOAD_URL,
        # AMAPI enrollment token injected into the admin extras bundle
        "android.app.extra.PROVISIONING_ADMIN_EXTRAS_BUNDLE": {
            "com.google.android.apps.work.clouddpc.EXTRA_ENROLLMENT_TOKEN": enrollment_token
        },
    }

    # Optional Wi-Fi provisioning parameters
    if wifi_ssid and wifi_password:
        provisioning_extras.update(
            {
                "android.app.extra.PROVISIONING_WIFI_SSID": wifi_ssid,
                "android.app.extra.PROVISIONING_WIFI_PASSWORD": wifi_password,
                # WPA is the most common; change if you use another security type
                "android.app.extra.PROVISIONING_WIFI_SECURITY_TYPE": "WPA",
            }
        )

    # Generate and display QR code
    qr_data = json.dumps(provisioning_extras)
    qr_img = qrcode.make(qr_data)
    display(qr_img)

    print("Enrollment token:", enrollment_token)


# Example usage
# generate_qr_code(wifi_ssid="MyWiFi", wifi_password="MyPassword")

# SECTION 5: DEVICE MONITORING
# List enrolled devices for the enterprise
response = (
    amapi_service.enterprises()
    .devices()
    .list(parent=f"enterprises/{ENTERPRISE_ID}")
    .execute()
)

for device in response.get("devices", []):
    print("Device name:", device.get("name"))
    print("Management mode:", device.get("managementMode"))
    print("State:", device.get("state"))
    print("---")
