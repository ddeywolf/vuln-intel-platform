"""Composite risk scoring helpers combining CVSS, EPSS, exploit, and KEV data."""


def calculate_risk_score(
    cvss_score: float | None = None,
    epss_score: float | None = None,
    exploit_available: bool = False,
    cisa_kev: bool = False,
) -> float | None:
    """Calculate a composite risk score (0–10) from available signals.

    Weights:
    - CVSS base score:  50% (normalized to 0–1 from 0–10)
    - EPSS score:       20% (already 0–1)
    - Exploit bonus:    +1.5 flat
    - CISA KEV bonus:   +2.0 flat (capped at 10)

    Returns None if no signals are available.
    """
    if cvss_score is None and epss_score is None:
        return None

    score = 0.0
    if cvss_score is not None:
        score += (cvss_score / 10.0) * 5.0  # 0–5 component
    if epss_score is not None:
        score += epss_score * 2.0  # 0–2 component

    if exploit_available:
        score += 1.5
    if cisa_kev:
        score += 2.0

    # Scale back to 0–10 range
    score = min(score * 10 / 9.5, 10.0) if score > 0 else 0.0
    return round(score, 2)


def severity_from_cvss(cvss_score: float) -> str:
    """Return a CVSS severity label from a numeric score.

    Based on NVD/FIRST severity rating scale:
    - CRITICAL: 9.0 – 10.0
    - HIGH:     7.0 – 8.9
    - MEDIUM:   4.0 – 6.9
    - LOW:      0.1 – 3.9
    - NONE:     0.0
    """
    if cvss_score >= 9.0:
        return "CRITICAL"
    if cvss_score >= 7.0:
        return "HIGH"
    if cvss_score >= 4.0:
        return "MEDIUM"
    if cvss_score > 0.0:
        return "LOW"
    return "NONE"
