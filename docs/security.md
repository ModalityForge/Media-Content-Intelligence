# Security Guide

## Security Layers

### 1. Input Guardrails
- **Location**: `security/input_guard.py`
- **Purpose**: Reject prompt injection, empty queries
- **Blocked patterns**:
  - "ignore previous instructions"
  - "disregard your rules"
  - "forget everything"

### 2. Output Guardrails
- **Location**: `security/output_guard.py`
- **Purpose**: Filter restricted fields (passwords, API keys)
- **Action**: Redact sensitive fields

### 3. Rights Filtering
- **Location**: `services/rights_service.py`
- **Purpose**: Enforce territory/usage/duration limits
- **Example**: Germany digital highlights limited to 30 seconds

### 4. Brand Safety
- **Location**: `services/brand_safety_service.py`
- **Purpose**: Check prohibited/excluded brands
- **Configuration**: Prohibited brands list, excluded content tags

### 5. PII Filtering
- **Location**: `security/pii_filter.py`
- **Purpose**: Redact emails, phone numbers, SSNs

### 6. Audit Logging
- **Location**: `security/audit_logger.py`
- **Purpose**: Log all security-relevant events
- **Output**: `logs/audit.log`

## Face Blur

To enable face blurring for privacy:
1. Use `tools/output_tools.FaceBlurTool`
2. Configure blur intensity (0.0-1.0)
3. Apply to exported clips

## Compliance

- All rights decisions are auditable
- All agent decisions are traceable via trace_id
- Query/response pairs logged for compliance