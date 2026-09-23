#!/usr/bin/env python3
"""Validate only the supplemental A-group E2 completion pack."""

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "samples"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
JOB_ID = re.compile(r"^job-[a-z0-9]+$")
ARTIFACT = re.compile(r"^artifact://pair[0-9]+/job-[a-z0-9]+/.+")


def load(name):
    with (SAMPLES / name).open(encoding="utf-8") as f:
        return json.load(f)


def die(message):
    print(f"FAIL {message}")
    sys.exit(1)


def require(condition, message):
    if not condition:
        die(message)


def check_sha(value, field):
    require(isinstance(value, str) and SHA40.match(value), f"{field} must be a 40-char lowercase SHA")


def check_artifact_uri(value, field):
    require(isinstance(value, str) and ARTIFACT.match(value), f"{field} must be an artifact URI")


def all_findings(job):
    output = job.get("output", {})
    findings = list(output.get("findings", []))
    delta = output.get("delta", {})
    findings.extend(delta.get("new_findings", []))
    findings.extend(delta.get("eliminated_findings", []))
    findings.extend(delta.get("unchanged_findings", []))
    return findings


def check_job_envelope(job):
    for field in ("schema_version", "job_id", "job_type", "status", "trace_id"):
        require(field in job, f"{job.get('job_id', '<unknown>')} missing {field}")
    require(job["schema_version"] == "1.0.0", "schema_version must be 1.0.0")
    require(JOB_ID.match(job["job_id"]), f"bad job_id {job['job_id']}")
    require(job["job_type"] in {"FULL_CHECK", "INCREMENTAL_CHECK"}, "A-group pack must only contain A-group job types")
    require(job["status"] in {"QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELLED"}, "bad status")

    has_error = bool(job.get("error"))
    has_findings = bool(all_findings(job))
    require(not (has_error and has_findings), f"{job['job_id']} has both error and findings")
    if job["status"] == "SUCCEEDED":
        require("output" in job, f"{job['job_id']} succeeded without output")
        require(not has_error, f"{job['job_id']} succeeded with error")
    if job["status"] in {"FAILED", "TIMED_OUT"}:
        require(has_error, f"{job['job_id']} failed without error")


def check_finding(finding, expected_commit):
    for field in ("finding_id", "type", "target", "dependency", "commit", "detector", "location"):
        require(field in finding, f"finding missing {field}")
    require(finding["type"] in {"MISSING", "REDUNDANT"}, "bad finding type")
    require(finding["detector"] in {"BUILDCHECKER", "ECHECKER", "INSTRUCTOR_ORACLE"}, "bad detector")
    check_sha(finding["commit"], "finding.commit")
    require(finding["commit"] == expected_commit, "finding commit must match checked commit")
    location = finding["location"]
    require("file" in location and "kind" in location, "finding.location must include file and kind")
    if "line" in location:
        require(isinstance(location["line"], int) and location["line"] >= 1, "line must start at 1")
    if "evidence_uri" in finding:
        check_artifact_uri(finding["evidence_uri"], "finding.evidence_uri")


def check_a_group_trace():
    doc = load("a_group_trace.sample.json")
    check_sha(doc["repository"]["c0"], "repository.c0")
    check_sha(doc["repository"]["c1"], "repository.c1")

    jobs = {job["job_id"]: job for job in doc["jobs"]}
    require(set(jobs) == {"job-full01", "job-incr01"}, "A-group trace must only contain full and incremental jobs")

    for job in jobs.values():
        check_job_envelope(job)
        repo = job["input"]["repository"]
        check_sha(repo["commit"], f"{job['job_id']}.input.repository.commit")
        for artifact in job.get("output", {}).get("artifacts", []):
            check_artifact_uri(artifact["uri"], f"{job['job_id']} artifact uri")
            require(artifact["producer_job_id"] == job["job_id"], "artifact producer must match job")
            require(artifact["type"] in {"ACTUAL_GRAPH", "DECLARED_GRAPH", "ERROR_REPORT", "BUILD_LOG"}, "A-group artifact type only")

    full = jobs["job-full01"]
    incr = jobs["job-incr01"]

    full_artifact_types = {a["type"] for a in full["output"]["artifacts"]}
    require({"ACTUAL_GRAPH", "DECLARED_GRAPH", "ERROR_REPORT"} <= full_artifact_types, "full check needs graph and report artifacts")

    baseline = incr["input"]["baseline"]
    require(baseline["commit"] == doc["repository"]["c0"], "incremental baseline commit must be C0")
    require(baseline["configuration_id"] == doc["configuration_id"], "baseline configuration mismatch")
    require(baseline["actual_graph_uri"] == "artifact://pair10/job-full01/actual.json", "baseline graph uri mismatch")

    for job in (full, incr):
        checked_commit = job["input"]["repository"]["commit"]
        for finding in all_findings(job):
            check_finding(finding, expected_commit=checked_commit)

    require(doc["acceptance"]["md_is_not_system_failure"] is True, "MD semantics flag must be true")
    print("OK A-group trace")


def check_baseline_mismatch_error():
    doc = load("baseline_mismatch.err.res.json")
    check_job_envelope(doc)
    require(doc["job_type"] == "INCREMENTAL_CHECK", "baseline error must be incremental")
    require(doc["status"] == "FAILED", "baseline mismatch must fail")
    require(doc["error"]["code"] == "BASELINE_2001", "baseline mismatch code")
    require("output" not in doc, "failed baseline mismatch must not include output")
    detail = doc["error"]["detail"]
    check_sha(detail["baseline_commit"], "detail.baseline_commit")
    check_sha(detail["actual_graph_commit"], "detail.actual_graph_commit")
    require(detail["baseline_commit"] != detail["actual_graph_commit"], "sample must actually mismatch")
    print("OK baseline mismatch error")


def main():
    check_a_group_trace()
    check_baseline_mismatch_error()
    print("OK A-group strict contract pack")


if __name__ == "__main__":
    main()

