<!--
SPDX-FileCopyrightText: 2026 ownCloud GmbH - A Kiteworks Company and ownCloud contributors
SPDX-License-Identifier: MIT
-->

# Changelog

## 0.1.0 - unreleased

The first release, extracted from owncloud/client, where the tool ran that project's GUI tests without
Squish.

- The probe (`probe/`): a CMake package `CutecumberProbe` with the target `cutecumber::probe`, an object
  library that an application links in. Inert unless `CUTECUMBER_PROBE` names a local socket; then it
  serves newline-delimited JSON on a `QLocalServer`: finding Qt Widgets, item view items and Qt Quick
  items by Squish-style selectors, reading properties, calling slots and `Q_INVOKABLE` methods, mouse and
  keyboard input in Squish key syntax, the clipboard and screenshots.
- The runner (`harness/`): the Python package `cutecumber` with the `cutecumber` command. It runs a Squish
  BDD suite (`suite.conf`, `tst_*/test.py`, `.feature` files, `shared/steps`, `bdd_hooks.py`) unchanged,
  with the modules `squish`, `test`, `object`, `objectmaphelper` and `squishinfo`, Squish tag
  expressions, HTML and JUnit XML reports, per-launch application logs and a GitHub Actions console mode.
