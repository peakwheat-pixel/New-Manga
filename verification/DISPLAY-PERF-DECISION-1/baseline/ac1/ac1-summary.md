# AC1 summary (auto-generated)

runs: 3  exe: 1136bb0a8d582a30c6ef0b16959b86a62dd26d2c6d9ce49e298c9b86c3343226
cdp: unknown

| stage (ms after process start) | median | min | max | values |
|---|---|---|---|---|
| coreSidecarSpawned | 40 | 35 | 44 | [44,35,40] |
| coreDerivedGcLog | 513 | 489 | 517 | [489,513,517] |
| coreReadyPingLog | 554 | 531 | 554 | [531,554,554] |
| windowVisible | 558 | 540 | 582 | [540,582,558] |
| webview2FirstSeen | 650 | 620 | 666 | [620,666,650] |
| firstContentPainted | n/a | n/a | n/a | [] |
| visualSettled | n/a | n/a | n/a | [] |
| firstTitleLog | 2944 | 2943 | 2992 | [2943,2992,2944] |

## per run
```json
[
  {
    "label": "ac1-02",
    "appStartEpochMs": 1793017625457,
    "coreSpawnMs": 44,
    "coreDerivedGcMs": 489,
    "allowlistSetupMs": 531,
    "windowVisibleMs": 540,
    "windowTitle": "N",
    "firstContentMs": null,
    "visualSettledMs": null,
    "paintFrames": 0,
    "paintIntervalMs": null,
    "supervisorRestarts": 0,
    "coreCrashes": 0,
    "killedOrphans": ""
  },
  {
    "label": "ac1-03",
    "appStartEpochMs": 1793017636045,
    "coreSpawnMs": 35,
    "coreDerivedGcMs": 513,
    "allowlistSetupMs": 554,
    "windowVisibleMs": 582,
    "windowTitle": "N",
    "firstContentMs": null,
    "visualSettledMs": null,
    "paintFrames": 0,
    "paintIntervalMs": null,
    "supervisorRestarts": 0,
    "coreCrashes": 0,
    "killedOrphans": ""
  },
  {
    "label": "ac1-04",
    "appStartEpochMs": 1793017646671,
    "coreSpawnMs": 40,
    "coreDerivedGcMs": 517,
    "allowlistSetupMs": 554,
    "windowVisibleMs": 558,
    "windowTitle": "",
    "firstContentMs": null,
    "visualSettledMs": null,
    "paintFrames": 0,
    "paintIntervalMs": null,
    "supervisorRestarts": 0,
    "coreCrashes": 0,
    "killedOrphans": ""
  }
]
```