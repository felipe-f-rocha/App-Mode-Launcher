# App Mode Launcher — Improvement Roadmap

## 1. Goal

Turn App Mode Launcher from a small utility into a productive desktop application with intelligent workspaces, improved UX, and more robust engineering.

---

## 2. High Priority Improvements

These improvements offer the greatest project impact:

1. Better user experience (UX)
2. Higher product quality
3. Stronger engineering foundation
4. Better demo readiness
5. Strong storytelling potential

---

### 2.1. Project Modularization ✅ **Completed**

**Goal:**
Separate interface, logic, configuration, and utilities into independent modules.

**Status:**
- Modular structure created under `app/` with subfolders for UI, core logic, config, plugins, and tests.
- Main app code and widgets separated.

---

### 2.2. Persistent Configuration System ✅ **Completed**

**Implemented:**
- Light/dark theme persistence now stored in `app/config/config.json`
- Theme restored automatically at launch
- Session persistence for the last launched workspace
- Startup presets support for auto-launching a configured workspace
- User preferences centralized in config

**Benefit:**
- Preferences and startup behavior are now easier to manage and persist consistently.

### 2.3. Better UX ✅ **Completed**

**Implemented:**
- Modern, organized layout with CustomTkinter
- Custom icons for each workspace
- Persistent theme switch
- Basic responsive layout for cards and window
- Recommendation and app detection areas

**Possible enhancements:**
- Animated transitions
- Dedicated loading states
- Visual success/failure feedback for actions
- Workspace search/filtering

### 2.4. Automatic App Detection ✅ **Completed**

**Goal:**
Detect installed apps automatically on the user system.

**Examples:**
- VS Code
- Discord
- Steam
- Chrome
- Spotify

**Implemented:**
- App detection for Windows, Linux, and macOS
- Refresh button in the UI
- Dynamic display of detected apps

**Benefits:**
- Smarter onboarding
- Better usability
- Stronger demos
- More intelligent experience

### 2.5. Intelligent Workspace System ✅ **Completed**

**Goal:**
Make workspaces the app’s core feature.

**Example modes:**
- Study
- Work
- Gaming
- AI development

**Implemented:**
- Workspaces loaded dynamically from `app/config/config.json`
- Support for `apps` and `talking` workspace types
- App launch and AUMID-based talking workspace launch
- Recommendations based on detected apps

**Capabilities:**
- Open apps
- Open websites
- Start preconfigured workspace modes

**Benefits:**
- Strong product differentiation
- Improved UX
- Realistic productivity flow
- Better demo impact

---

## 3. Medium Priority Improvements

### 3.1. Logging System ✅ **Completed**

**Goal:**
Improve debugging and maintenance.

**Implemented:**
- `app/core/logger.py` with rotating log files
- Config loading logs
- App detection logs
- Workspace launch logs

**Features:**
- Error logging
- Launch history
- Debug mode support
- Event tracing

### 3.2. Type Hints ✅ **Completed**

**Goal:**
Improve readability and maintainability.

**Implemented:**
- Type annotations across core and UI modules
- `Dict`, `List`, `Any`, and other typing helpers used in key modules
- Better autocomplete and static validation

**Benefits:**
- Better editor support
- Easier debugging
- Cleaner architecture
- Improved developer experience

### 3.3. Automated Tests ✅ **Completed**

**Goal:**
Increase reliability.

**Implemented:**
- Config parsing tests in `app/tests/test_profiles.py`
- App detection tests in `app/tests/test_detection.py`
- Workspace launch tests in `app/tests/test_launcher.py`
- Passing pytest suite

**Suggestions:**
- Add UI tests
- Add workspace integration tests
- Cover invalid config scenarios

---

## 4. Low Priority Improvements

Still valuable, but lower immediate impact.

### 4.1. PEP8 Standardization ✅ **Completed**

**Goal:**
Keep code clean and consistent.

**Implemented:**
- Added `pyproject.toml` with Black and Ruff configuration
- Formatted codebase with Black
- Validated syntax via Python compile and pytest
- Added `app/tests/test_plugins.py` to ensure plugin integration works

**Benefits:**
- Cleaner code style across the project
- Easier collaboration and code review
- Better static tooling support
- Stronger baseline for future contributions

### 4.2. Complete Docstrings ✅ **Completed**

**Goal:**
Improve documentation and onboarding.

**Implemented:**
- Module-level docstrings for all core modules
- Class and method docstrings for all public functions
- Type hints with full return value documentation

**Benefits:**
- Easier onboarding
- Better readability
- Longer-term maintainability
- IDE autocomplete and tooltips fully functional

---

## 5. Interesting Extras

### 5.1. Local Analytics ✅ **Completed**

**Implemented:**
- `app/core/analytics.py` tracks workspace launches and app detection history
- Saved analytics stored in `app/config/analytics.json` (gitignored for clean repo state)
- `app/config/analytics.example.json` provides zero-state template
- Analytics reset to zero on fresh clones

**Metrics:**
- Most-used workspaces with frequency tracking
- Recent launches with full context (apps, websites)
- Detection history for recommendations
- Total launches and detection counts

**Benefits:**
- More advanced product with data persistence
- Personalized experience with usage history
- Data-driven UX for smart recommendations
- Privacy-respecting local-only analytics

### 5.2. Smart Recommendations ✅ **Implemented**

**Example:**

> “You often open VS Code + Spotify + Chrome together. Create a new workspace?”

**Implemented:**
- Recommendation engine now uses detected apps and analytics history
- Recommends matching workspaces with usage frequency context
- Suggests creating a custom workspace for frequent app combos

**Benefits:**
- Smarter experience
- Better personalization
- Higher usability

### 5.3. Plugin System ✅ **Completed**

**Implemented:**
- `app/plugins/__init__.py` loads plugin modules automatically
- `load_plugin_workspaces` adds plugin-registered workspaces to the UI
- `notify_apps_detected` and `notify_workspace_launched` hooks support runtime events
- Example plugin included at `app/plugins/example_plugin.py`
- Plugin developer documentation added at `app/plugins/README.md`
- Plugin integration tests added in `app/tests/test_plugins.py`

**Goal:**
Enable extensibility and third-party integrations.

**Benefits:**
- Scalable architecture for custom workspace plugins
- Runtime hooks for detection and launch events
- Easier plugin development with local docs
- Strong foundation for future plugin marketplace or extension system

### 5.4. UX Polish and Feedback ✅ **Completed**

**Goal:**
Improve the workspace launcher experience with clearer feedback and interactive states.

**Implemented:**
- **Status feedback text** in main UI for detection and launch actions
- **Disabled detection button** while scanning apps
- **Error and success messages** with color-coded levels (info/success/warning/error)
- **Visual loading indicators** with animated spinner (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏) during detection
- **Non-blocking detection** via threading - UI remains responsive
- **Workspace search/filtering** with real-time input field
- **Clear button** to reset search filters
- **Contextual feedback** showing workspace type and app count on launch
- **Symbol indicators** in messages: ✓ (success), ✗ (error), ◐ (in progress), spinner (loading)
- **Workspace rebuild** on filter changes for instant visual feedback

**Key Features:**
- Search box in header: "Type workspace name..."
- Animated spinner during app detection
- Responsive threading prevents UI freezing
- Workspace-specific launch messages
- Dynamic message updates (✓, ✗, ◐) for quick visual scanning
- Quick window resize to accommodate new filter UI (+60px height)

**Benefits:**
- Much faster perceived performance
- Clearer user feedback during operations
- Better discoverability with workspace search
- Professional UX with smooth animations
- Improved accessibility with consistent feedback patterns

---

## 6. Project Strategy

**Focus on:**
- One impressive feature
- Multiple quality improvements

**Avoid:**
- Many isolated small features
- Overengineering
- Low-impact functionality

---

## 7. Recommended Differentiator

**Intelligent Workspace System**

**Why it matters:**
- Solves a real problem
- Improves demo value
- Enhances UX
- Enables better storytelling
- Makes the product feel real

---

## 8. Suggested Technologies

- Python 3.10+
- CustomTkinter
- Pillow
- JSON for configuration
- Threading/concurrency when needed
- logging
- PyInstaller

---

## 9. Final Vision

**Current state:**

> "A simple launcher utility"

**Desired state:**

> "A productive, intelligent workspace manager for developers, students, and gamers."

---

## 10. Before and After

**Before:**
- The project was described as a small launcher utility with mixed English and Portuguese in the roadmap.
- User-facing strings, setup instructions, and config placeholders were still in Portuguese.
- The documentation and startup scripts were not fully aligned for an English-speaking audience.

**After:**
- The app UI, logger messages, setup script, and docs are now English-first.
- Config samples and placeholders were translated for broader use.
- The roadmap now reflects the completed translation effort and the project’s move toward a polished English UX.