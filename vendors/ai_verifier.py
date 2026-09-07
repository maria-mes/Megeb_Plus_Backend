import datetime
import re
from decimal import Decimal


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LICENSE_REGEX = re.compile(
    r"^(LIC[-/][A-Z0-9\-\/]{3,}|[A-Z0-9\-\/]{5,})$",
    re.IGNORECASE,
)

FREE_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
}

CURRENT_YEAR = datetime.date.today().year

WEIGHTS = {
    "completeness": 25,
    "format_valid": 20,
    "dates_valid": 20,
    "consistency": 20,
    "documents": 15,
}

VERIFIED_THRESHOLD = 85
NEEDS_REVIEW_THRESHOLD = 50


# ---------------------------------------------------------------------------
# OCR
# ---------------------------------------------------------------------------

def ocr_check(application):
    """
    Extract text from the vendor's documents and compare
    the extracted information against submitted information.

    Replace the placeholder OCR section with your real OCR provider.
    """

    result = {
        "ran": False,
        "match_score": None,
        "details": {},
    }

    if not application.license_document:
        return result

    try:

        # ---------------------------------------------------------------
        # TODO: Replace this with your OCR provider.
        #
        # Example:
        #
        # from .ocr_provider import extract_text
        # text = extract_text(application.license_document.path)
        #
        # ---------------------------------------------------------------

        text = ""

        details = {}
        matches = 0
        checks = 0

        # License number
        if application.license_number:

            checks += 1

            if application.license_number.lower() in text.lower():

                matches += 1
                details["license_number_found"] = True

            else:

                details["license_number_found"] = False

        # Business name
        if application.business_name:

            checks += 1

            business_words = application.business_name.lower().split()

            # Require at least one meaningful business-name word.
            meaningful_words = [
                word for word in business_words
                if len(word) >= 3
            ]

            name_found = any(
                word in text.lower()
                for word in meaningful_words
            )

            if name_found:
                matches += 1

            details["business_name_found"] = name_found

        # Owner name
        if application.user and application.user.full_name:

            checks += 1

            owner_words = application.user.full_name.lower().split()

            meaningful_words = [
                word for word in owner_words
                if len(word) >= 3
            ]

            owner_found = any(
                word in text.lower()
                for word in meaningful_words
            )

            if owner_found:
                matches += 1

            details["owner_name_found"] = owner_found

        result["ran"] = True

        result["match_score"] = (
            int((matches / checks) * 100)
            if checks
            else 0
        )

        result["details"] = details

    except Exception as exc:

        result["details"] = {
            "error": str(exc)
        }

    return result


# ---------------------------------------------------------------------------
# Forgery / tampering
# ---------------------------------------------------------------------------

def forgery_check(application):
    """
    Placeholder for document-forensics / tamper detection.

    This should NOT automatically declare a document fraudulent
    unless the external detector provides a sufficiently reliable signal.
    """

    result = {
        "ran": False,
        "suspected": False,
        "details": {},
    }

    if not application.license_document:
        return result

    # ---------------------------------------------------------------
    # TODO:
    #
    # signals = forensics_provider.analyze(
    #     application.license_document.path
    # )
    #
    # result["ran"] = True
    # result["suspected"] = signals["is_manipulated"]
    # result["details"] = signals
    # ---------------------------------------------------------------

    return result


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def registry_check(application):
    """
    Placeholder for official business/license registry verification.

    If an official registry becomes available, this should become
    an authoritative verification layer.
    """

    return {
        "ran": False,
        "match": None,
        "details": {
            "note": "No registry API configured"
        },
    }


# ---------------------------------------------------------------------------
# Completeness
# ---------------------------------------------------------------------------

def _check_completeness(app):

    required = [
        "business_name",
        "business_address",
        "business_type",
        "license_number",
        "license_document",
        "food_safety_certificate",
        "owner_id_document",
    ]

    missing = []

    for field in required:

        value = getattr(app, field, None)

        if not value:
            missing.append(field)

    # User information is also required.
    user = getattr(app, "user", None)

    if not user:
        missing.append("user")

    else:

        if not user.full_name:
            missing.append("owner_name")

        if not user.email:
            missing.append("email")

        if not user.phone:
            missing.append("phone")

    return (
        len(missing) == 0,
        {
            "missing_fields": missing
        }
    )


# ---------------------------------------------------------------------------
# Format validation
# ---------------------------------------------------------------------------

def _check_format(app):

    issues = []

    # License number
    if (
        not app.license_number
        or not LICENSE_REGEX.match(
            app.license_number.strip()
        )
    ):
        issues.append("license_number_format")

    # Business name
    if (
        not app.business_name
        or len(app.business_name.strip()) < 2
    ):
        issues.append("business_name_invalid")

    # Business address
    if (
        not app.business_address
        or len(app.business_address.strip()) < 5
    ):
        issues.append("business_address_invalid")

    # Business type
    if not app.business_type:
        issues.append("business_type_missing")

    # Email
    if app.user and app.user.email:

        domain = app.user.email.split("@")[-1].lower()

        if domain in FREE_EMAIL_DOMAINS:
            # Soft signal only.
            issues.append("free_email_domain")

    return (
        len([
            issue
            for issue in issues
            if issue != "free_email_domain"
        ]) == 0,
        {
            "issues": issues
        }
    )


# ---------------------------------------------------------------------------
# Date validation
# ---------------------------------------------------------------------------

def _check_dates(app):

    """
    Vendor applications currently don't have an explicit
    expiration-date field.

    The real expiration date should eventually come from:
        1. OCR
        2. document metadata
        3. official registry
        4. manually entered expiration field

    Until that exists, this layer is neutral/pass.
    """

    return (
        True,
        {
            "issues": [],
            "note": "No explicit expiration date field configured"
        }
    )


# ---------------------------------------------------------------------------
# Consistency
# ---------------------------------------------------------------------------

def _check_consistency(app):

    issues = []

    user = getattr(app, "user", None)

    if user:

        # Owner name must exist.
        if not user.full_name:
            issues.append("owner_name_missing")

        # Email must exist.
        if not user.email:
            issues.append("email_missing")

        # Phone must exist.
        if not user.phone:
            issues.append("phone_missing")

    # Business type must be one of the accepted choices.
    valid_types = {
        choice[0]
        for choice in app.BUSINESS_TYPE_CHOICES
    }

    if app.business_type not in valid_types:
        issues.append("business_type_mismatch")

    return (
        len(issues) == 0,
        {
            "issues": issues
        }
    )


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

def _check_documents(app):

    documents = {
        "license_document": bool(
            app.license_document
        ),
        "food_safety_certificate": bool(
            app.food_safety_certificate
        ),
        "owner_id_document": bool(
            app.owner_id_document
        ),
    }

    passed = all(documents.values())

    return (
        passed,
        documents
    )


# ---------------------------------------------------------------------------
# Main verification engine
# ---------------------------------------------------------------------------

def verify_application(application, persist=True):

    checks = {

        "completeness": _check_completeness(
            application
        ),

        "format_valid": _check_format(
            application
        ),

        "dates_valid": _check_dates(
            application
        ),

        "consistency": _check_consistency(
            application
        ),

        "documents": _check_documents(
            application
        ),
    }

    # ---------------------------------------------------------------
    # Rule-based score
    # ---------------------------------------------------------------

    rule_score = 0

    breakdown = {}

    for name, (passed, detail) in checks.items():

        weight = WEIGHTS[name]

        earned = weight if passed else 0

        rule_score += earned

        breakdown[name] = {
            "passed": passed,
            "weight": weight,
            "earned": earned,
            "detail": detail,
        }

    # ---------------------------------------------------------------
    # Additional AI layers
    # ---------------------------------------------------------------

    ocr = ocr_check(application)

    forgery = forgery_check(application)

    registry = registry_check(application)

    # ---------------------------------------------------------------
    # Hard failures
    # ---------------------------------------------------------------

    hard_fail = False

    if "license_number_format" in (
        checks["format_valid"][1].get(
            "issues",
            []
        )
    ):
        hard_fail = True

    if forgery.get("suspected") is True:
        hard_fail = True

    # ---------------------------------------------------------------
    # Initial status
    # ---------------------------------------------------------------

    if hard_fail:

        status = "failed"

    elif rule_score >= VERIFIED_THRESHOLD:

        status = "verified"

    elif rule_score >= NEEDS_REVIEW_THRESHOLD:

        status = "needs_review"

    else:

        status = "failed"

    # ---------------------------------------------------------------
    # Build result
    # ---------------------------------------------------------------

    result = {

        "engine_version": "1.0-vendor-rules",

        "score": rule_score,

        "status": status,

        "hard_fail": hard_fail,

        "breakdown": breakdown,

        "layers": {
            "ocr": ocr,
            "forgery": forgery,
            "registry": registry,
        },
    }

    # ---------------------------------------------------------------
    # Optional ML layer
    # ---------------------------------------------------------------

    try:

        from .ml_scorer import ml_score

        ml = ml_score(result)

    except (ImportError, Exception):

        ml = None

    if ml is not None:

        result["ml_score"] = ml

        # Blend only if the model actually returned a score.
        final_score = int(
            round(
                (rule_score + float(ml)) / 2
            )
        )

    else:

        final_score = rule_score

    # Clamp score.
    final_score = max(
        0,
        min(100, final_score)
    )

    result["score"] = final_score

    # ---------------------------------------------------------------
    # Recalculate status AFTER final score.
    # ---------------------------------------------------------------

    if hard_fail:

        final_status = "failed"

    elif final_score >= VERIFIED_THRESHOLD:

        final_status = "verified"

    elif final_score >= NEEDS_REVIEW_THRESHOLD:

        final_status = "needs_review"

    else:

        final_status = "failed"

    result["status"] = final_status

    # ---------------------------------------------------------------
    # Persist
    # ---------------------------------------------------------------

    if persist:

        application.ai_status = final_status

        application.ai_score = Decimal(
            str(final_score)
        )

        application.ai_result = result

        application.save(
            update_fields=[
                "ai_status",
                "ai_score",
                "ai_result",
                "updated_at",
            ]
        )

    return result