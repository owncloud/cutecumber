# SPDX-FileCopyrightText: 2026 ownCloud GmbH - A Kiteworks Company and ownCloud contributors
# SPDX-License-Identifier: MIT
"""CuteCumber: a Squish-compatible BDD test runner on top of the CuteCumber probe."""

from pathlib import Path

# Directory with the Squish-named modules; the runner puts it first on sys.path.
SHIM_DIR = Path(__file__).resolve().parent.parent / "shim"
