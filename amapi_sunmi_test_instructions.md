# AMAPI SUNMI Colab Setup Instructions

Use this guide to configure the environment variables and run the Colab notebook.

## 1) Prerequisites

- A Google Cloud project with the **Android Management API** enabled.
- A service account with access to Android Management API.
- The service account key downloaded as `service_account.json`.
- An existing **enterprise ID** from AMAPI (for example: `LC02abcd123`).

## 2) Configuration Variables

Set the following values in the notebook's **PROJECT CONFIGURATION** cell:

- `PROJECT_ID`: Your Google Cloud Project ID.
- `ENTERPRISE_ID`: The AMAPI enterprise ID.
- `POLICY_ID`: The policy identifier (default: `sunmi_test_policy`).

These values are also exported as environment variables for reuse:

- `GOOGLE_CLOUD_PROJECT`
- `AMAPI_ENTERPRISE_ID`
- `AMAPI_POLICY_ID`

## 3) Running the Notebook

1. Open `amapi_sunmi_test.ipynb` in Google Colab.
2. Run **SECTION 1** to install dependencies.
3. Run **SECTION 2** and upload `service_account.json` when prompted.
4. Update and run the **PROJECT CONFIGURATION** cell.
5. Run **SECTION 3** to create/update the policy.
6. Run **SECTION 4** to generate the enrollment QR code.
7. Run **SECTION 5** to list enrolled devices and verify status.

## 4) Optional Wi-Fi Provisioning

When generating a QR code, you can pass Wi-Fi credentials:

```python
generate_qr_code(wifi_ssid="MyWiFi", wifi_password="MyPassword")
```

If Wi-Fi parameters are omitted, the QR code will not include Wi-Fi settings.
