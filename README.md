<!--
SPDX-FileCopyrightText: 2026 ownCloud GmbH - A Kiteworks Company and ownCloud contributors
SPDX-License-Identifier: MIT
-->

# CuteCumber

Squish-compatible BDD GUI testing for Qt Widgets and Qt Quick apps.

CuteCumber runs an existing Squish BDD test suite (Gherkin `.feature` files with Python step definitions)
against a Qt application, without a Squish installation or license. It has two parts:

- **The probe** (`probe/`, C++): a small library linked into the application under test. It stays inert
  unless the environment variable `CUTECUMBER_PROBE` is set; then it listens on that local socket (a
  `QLocalServer`, never TCP) and lets the runner find objects, read properties, call methods and send
  mouse and keyboard input, all on the GUI thread.
- **The runner** (`harness/`, Python): the `cutecumber` command. It reads the suite like `squishrunner`
  does, starts the application with the probe activated and provides the Squish Python modules the
  suite imports.

Never ship an application built with the probe. The probe is meant for test builds only.

## Quick start

### 1. Build the probe into your application

The probe is a CMake project of its own (CMake 3.18+, Qt 6.8+ with Widgets, Network, Test, Quick and
QuickWidgets). Add it as a subproject, for example with `FetchContent`, and link `cutecumber::probe`
into the application executable, behind an option of your own that is off by default:

```cmake
option(MYAPP_WITH_CUTECUMBER "Link the CuteCumber probe (test builds only)" OFF)
if(MYAPP_WITH_CUTECUMBER)
    include(FetchContent)
    FetchContent_Declare(cutecumber
        GIT_REPOSITORY https://github.com/owncloud/cutecumber.git
        GIT_TAG <commit sha> # v0.1.0
        SOURCE_SUBDIR probe
    )
    FetchContent_MakeAvailable(cutecumber)
    target_link_libraries(myapp PRIVATE cutecumber::probe)
endif()
```

The probe is an object library and starts itself from a `Q_COREAPP_STARTUP_FUNCTION`, so the
application needs no code changes. A standalone build also installs a `CutecumberProbe` package for
`find_package(CutecumberProbe 0.1)`, with the same `cutecumber::probe` target. While the version is
0.x, only the same minor version matches.

The probe's own tests build when the probe is the top-level project and `BUILD_TESTING` is on (the
default; `-DBUILD_TESTING=OFF` or `-DCUTECUMBER_BUILD_TESTS=OFF` skips them). As a subproject they are
off unless the application sets `CUTECUMBER_BUILD_TESTS=ON`. Standalone:

```sh
cmake -S probe -B build -G Ninja
cmake --build build
QT_QPA_PLATFORM=offscreen ctest --test-dir build --output-on-failure
```

### 2. Install the runner

Python 3.10 or later:

```sh
pip install ./harness          # or: pip install "cutecumber @ git+https://github.com/owncloud/cutecumber.git@<sha>#subdirectory=harness"
pip install "./harness[test]"  # with pytest, for the runner's own tests
```

### 3. Run a suite

```sh
cutecumber --testsuite path/to/suite --aut myapp=build/bin --tags ~@skip
```

`python -m cutecumber` works the same way. The exit code is 0 only if nothing failed or errored.

## Command line

| Option | Meaning |
|---|---|
| `--testsuite DIR` | the suite directory, with `suite.conf` (required) |
| `--testcase NAME` | run only this test case (repeatable); by default all `tst_*` run |
| `--tags EXPR` | run only scenarios matching a Squish tag expression, e.g. `~@skip` or `@a,@b` (repeatable, ANDed) |
| `--abortOnFail` | stop after the first failed scenario |
| `--envvar KEY=VALUE` | set an environment variable for the applications (repeatable) |
| `--aut NAME=DIR` | where the application `NAME` that `startApplication` starts lives (repeatable) |
| `--aut-log-dir DIR` | write each launch's output to `DIR/<test case>/<NN>-<name>.log` instead of the console; the HTML report links them |
| `--reportgen html,DIR` | write an HTML report to `DIR/index.html` (repeatable) |
| `--reportgen junitxml,FILE` | write a JUnit XML report |
| `--console MODE` | `pretty` prints features, scenarios and steps; `github` adds groups, annotations and a job summary for GitHub Actions; `quiet` prints nothing; `auto` (default) is `github` where `GITHUB_ACTIONS=true`, else `pretty` |

`cutecumber --help` lists them as well.

## The Squish surface

The suite's files run unchanged: `suite.conf` (with `ENVVARS`), each `tst_*/test.py` with `source`,
`findFile`, `setupHooks`, `collectStepDefinitions` and `runFeatureFile`, the `.feature` files (parsed
with Cucumber's `gherkin-official`: Background, Scenario Outline with Examples, tags, tables and doc
strings), the step decorators `Given`/`When`/`Then`/`Step` with Squish placeholders (`|any|`, `|word|`,
`|integer|`) or `regexp=True`, the hooks in `bdd_hooks.py`, and `context.table`, `context.multiLineText`
and `context.title`.

The runner provides these modules under their Squish names:

- `squish`: `waitForObject`, `waitForObjectExists`, `waitForObjectItem`, `findObject`,
  `findAllObjects`, `mouseClick`, `doubleClick`, `clickButton`, `type`, `nativeType`, `activateItem`,
  `getClipboardText`, `saveDesktopScreenshot`, `snooze`, `waitFor`, `startApplication`,
  `applicationContextList`, `currentApplicationContext`, `squish.Qt` and `testSettings`.
- `test`: `compare`, `verify`, `fail`, `warning`, `log`, `resultCount`, `startVideoCapture` and
  `stopVideoCapture`.
- `object`: `children`, `exists`.
- `objectmaphelper`: `RegularExpression`, `Wildcard`.
- `squishinfo`.

Selectors are Squish's: `type`, `name`, `window`, `container`, `unnamed`, `visible`, `enabled`,
`buddy`, `aboveWidget`, `leftWidget` and `occurrence`, and any other key matches the Qt property of that
name (`text`, say), with exact values, regular expressions, wildcards and nested selectors. They resolve against QWidgets, item view items (`QModelIndex`) and the Qt Quick
items below a `QQuickWidget`, where `type` is the QML type name and `id` the QML id. Objects come back
as proxies: attribute access reads a Qt property, and a method name calls the slot or `Q_INVOKABLE`.

## Limits

- **Linux** is the only platform built and verified so far. The probe is plain Qt and uses
  `QLocalServer`, so macOS and Windows should work, but nothing checks them yet.
- **Qt 6.8 or later.**
- **Calls are synchronous.** A method call through a proxy (a slot or `Q_INVOKABLE`) runs inside the
  probe's request. A slot that opens a modal dialog, such as `close()` with a `closeEvent()` that asks
  for confirmation, blocks the protocol until the dialog closes, and the request times out. Open
  dialogs with input instead (`mouseClick`, `clickButton`, `type`, `activateItem`), which is posted and
  answered at once.
- **Input errors surface late.** Input is checked, then posted. If it fails when it runs (the target
  went away, no widget to type into), that is written to the application's log, and the test notices
  only as a later wait that times out.
- **Methods that are neither slots nor `Q_INVOKABLE`** are refused, except a small allowlist:
  `QAbstractItemView::model()` and `QAbstractItemModel::rowCount`, `columnCount`, `index` and `data`.
- **`nativeType`** types into the focused Qt widget through the probe; native, non-Qt dialogs are not
  reached.
- **No video recording:** `test.startVideoCapture` and `test.stopVideoCapture` only log.
- No Squish IDE features: no recorder, object spy or verification point files.

The design documents in [`docs/design/`](docs/design/) describe how the tool came about inside
owncloud/client and the decisions behind it.

## Development

```sh
cd harness
pip install -e ".[test]" "black==24.3.*" "pylint==3.2.*"
pytest
black --check .
pylint cutecumber cutecumber/shim/*.py tests/*.py
```

CI (`.github/workflows/ci.yml`) builds the probe with Qt 6.8 and runs its tests, runs the runner's tests
on Python 3.10 and 3.12 with black and pylint, and checks the workflows with zizmor.

## License

MIT, see [LICENSE](LICENSE).
