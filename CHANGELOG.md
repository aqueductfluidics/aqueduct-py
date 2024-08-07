# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.11] - XXXX-XX-XX

### Fixed

### Added

### Changed

## [0.0.10] - 2024-07-24

### Fixed

### Added

- Add ability to set config for peristaltic pump (see `peristaltic_pump_set_config_demo.py` in the Examples for a demo)
- Add the ability to clear a prompt using the `prompt.clear()` method (requires `version 0.0.10` of the Aqueduct application)

### Changed

## [0.0.9] - Skipped

## [0.0.8] - Skipped

## [0.0.7] - Skipped

## [0.0.6] - 2023-11-15

### Fixed

### Added

-   **New Feature:** Addition of McFarland Measurement to `OpticalDensityProbe`.

### Changed

## [0.0.5] - 2023-09-22

### Fixed

### Added

-   **New Feature:** Added PID-related classes and functions for advanced control.

    -   Introduced the `Pid`, `PidController`, `Schedule`, `Controller`, and `ControllerSchedule` classes.
    -   These classes enable more sophisticated control over processes, incorporating proportional-integral-derivative (PID) control strategies.
    -   The API now supports fine-tuning control parameters, setting schedules, and enabling/disabling PID controllers.
    -   Detailed documentation on these new features is available in the updated API documentation.

-   **New Feature:** Added the ability to control process registration during initialization.
    -   The new `register_process` argument has been introduced to the `InitParams` class.
    -   When initializing the system, you can now specify whether to register a process with the Aqueduct API.
    -   Registering a process installs UI-based recipe control, allowing users to perform actions like emergency stop (e-stop), pause, and resume for Python-based recipe processes.
    -   The `-r` or `--register` command-line option is used to control this feature.
    -   By default, if no value is provided for the `register` option, it is set to `1` (true), meaning a process will be registered.
    -   To skip process registration during initialization, explicitly set the `register` option to `0` (false).

### Changed

## [0.0.4] - Skipped

## [0.0.3] - 2023-07-20

### Initial Public Release

## [0.0.2]

### Yanked!

## [0.0.1]

### Yanked!
