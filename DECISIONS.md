# Architectural Decisions — Vision Moderation as a Service (VMaaS)

This document details the core architectural and design decisions for the VMaaS API contract.

## 1. Versioning
We selected path-based versioning (`/v1/`) over header-based versioning because of its superior visibility, caching friendliness, and simplicity for client integrations. Path-based routing allows API gateways and reverse proxies to perform static routing easily without inspecting headers, ensuring robust performance at scale.

## 2. Batch Ordering and Partial Failures
When `/v1/predict-batch` is called with 32 items and one is corrupt, the API returns a `200 OK` status with a JSON object mapping each caller-supplied ID to its individual outcome (either a success structure with prediction results or an error structure). We rejected the "all-or-nothing" transactional approach because an isolated image failure should not block the moderation outcomes of the remaining 31 valid images. Keying the response by caller-supplied IDs ensures clients can correlate results efficiently, even if the processing sequence changes.

## 3. Async Lifecycle
An asynchronous prediction job progresses through the states `queued` -> `running` -> `completed` (or `failed`). Upon submission, the API immediately returns a `202 Accepted` response with a unique job ID and a `check_url` to query status. Completed and failed job results are retained in a Redis or database cache for exactly 24 hours to balance operational storage costs with reasonable client retrieval windows.
