def verify_license(license_number, document=None):
    result = {
        "license_number": license_number,
        "document_received": bool(document),
        "license_format_valid": False,
        "confidence": 0,
        "status": "failed",
        "message": "",
    }

    if not license_number:
        result["message"] = "License number is required."
        return result

    license_number = license_number.strip()

    if len(license_number) < 4:
        result["message"] = "License number appears invalid."
        return result

    result["license_format_valid"] = True

    if not document:
        result["status"] = "needs_review"
        result["confidence"] = 50
        result["message"] = (
            "License number is present, but no credential "
            "document was provided."
        )
        return result

    # Temporary verification logic.
    #
    # Later this is where OCR/AI verification will be connected.

    result["status"] = "needs_review"
    result["confidence"] = 70
    result["message"] = (
        "Credential document received. Manual or AI verification "
        "is required."
    )

    return result