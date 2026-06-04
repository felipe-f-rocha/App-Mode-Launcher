# App Mode Launcher Plugins

Plugins extend App Mode Launcher by providing additional workspaces or reacting to runtime events.

## Plugin discovery

The launcher scans `app/plugins/` for Python modules and imports each file except `__init__.py`.

## Supported hooks

### `register_workspaces(config)`
Return a list of workspace dictionaries to add to the main workspace list.

Example:

```python
from typing import Dict, Any, List


def register_workspaces(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            'name': 'Research',
            'type': 'apps',
            'apps': ['firefox'],
            'description': 'Open a lightweight research workspace with browser tools.'
        }
    ]
```

### `on_workspace_launched(workspace)`
Called after any workspace launches.

### `on_apps_detected(detected_apps)`
Called after automatic app detection completes.

## Plugin workspace format

Each workspace dictionary should follow the same structure as `config.json` workspaces:

- `name`: workspace display name
- `type`: `apps` or `talking`
- `apps`: list of app commands or paths
- `aumid`: optional for talking workspaces
- `description`: optional human-friendly description

## Example plugin

See `app/plugins/example_plugin.py` for a working template.
