"""Pytest wrapper for the E2E demo script.

Runs the full demo_e2e.py as a single test case so it integrates
with the test suite and CI pipelines.
"""

import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


def test_demo_e2e():
    """Run the full E2E demo script and assert it passes."""
    result = subprocess.run(
        [sys.executable, str(BACKEND_DIR / "demo_e2e.py")],
        capture_output=True,
        text=True,
        cwd=str(BACKEND_DIR),
        env={
            **__import__("os").environ,
            "PYTHONPATH": str(BACKEND_DIR),
        },
        timeout=120,
    )

    # Print output for visibility in test reports
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        # Filter out noisy Azure credential warnings
        lines = result.stderr.splitlines()
        filtered = [
            l for l in lines
            if "DefaultAzureCredential" not in l
            and "EnvironmentCredential" not in l
            and "ManagedIdentityCredential" not in l
            and "SharedTokenCacheCredential" not in l
            and "AzureCliCredential" not in l
            and "AzurePowerShellCredential" not in l
            and "AzureDeveloperCliCredential" not in l
            and "troubleshoot" not in l
            and "npm error" not in l
            and "npm notice" not in l
            and "Attempted credentials:" not in l
            and l.strip() != ""
        ]
        if filtered:
            print("STDERR (filtered):", file=sys.stderr)
            for line in filtered:
                print(line, file=sys.stderr)

    assert result.returncode == 0, (
        f"Demo script failed with exit code {result.returncode}\n"
        f"STDOUT:\n{result.stdout[-2000:]}\n"
        f"STDERR:\n{result.stderr[-2000:]}"
    )

    assert "ALL CHECKS PASSED" in result.stdout, (
        f"Demo did not report all checks passed\n{result.stdout[-1000:]}"
    )
