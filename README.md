# ginseng-strip-2002
A Server Configuration Tool for an Enshrouded Game Server
# Enshrouded Server Config Editor (GUI)

A user-friendly graphical interface (GUI) tool built with Python and Tkinter to manage and edit the `enshrouded_server.json` configuration file for your Enshrouded dedicated server.

This tool aims to simplify server configuration by providing an intuitive interface, reducing the risk of manual JSON syntax errors, and offering helpful features like backups, default restoration, and dynamic setting updates based on the game's official readme file.

## Features

* **Graphical User Interface:** Easy-to-navigate tabbed interface for different setting categories.
* **Readme-Driven Defaults:**
    * Parses `enshrouded_server_readme.txt` (if present in the same directory) for the latest game version and default JSON structure.
    * Automatically merges new default settings from the readme into your existing configuration, preserving your customizations.
    * Provides warnings for structural differences or potential setting mismatches, clarifying when it's a normal update vs. a potential issue with your existing file.
* **User-Friendly Setting Edits:**
    * **Durations (Day/Night/Starvation):** Input and displayed in minutes, automatically converted to/from nanoseconds for the JSON.
    * **Factor Settings (Percentages):** Input and displayed as percentages (e.g., "150%") for float-based multipliers, converted to/from float for the JSON. Includes min/max validation.
    * **String Choices:** Dropdown menus for settings with predefined options (e.g., Tombstone Mode, Weather Frequency), preventing typos.
    * **Booleans:** Simple checkboxes.
    * **File/Directory Paths:** "Browse..." button for easy selection.
* **Backup Management:**
    * **Automatic Backup on Save:** Creates a timestamped backup of your `enshrouded_server.json` before any changes are saved.
    * **Manual Backup:** Option to create a backup at any time.
    * **Granular Restore:** List and restore specific previous backup versions.
    * **Pre-Restore/Revert Backups:** Automatically backs up the current state before restoring an old backup or reverting to defaults.
    * Backup reasons are appended to filenames for easier identification.
* **User Group Management:**
    * View and edit existing user groups.
    * **Add New User Groups:** Easily append new groups with default permissions and placeholders.
    * **Delete User Groups:** Remove unwanted user groups with confirmation.
* **Randomization (Experimental):**
    * "Randomize Settings on This Tab" button for Player, World, Enemy, Resources, and Experience tabs.
    * Provides varied configurations for experimentation.
    * Includes a difficulty assessment that warns if randomization might make the game substantially harder based on deviations from normal values.
* **Informative Tooltips:** Concise tooltips for most settings, providing a quick explanation and valid ranges/options.
* **Unsaved Changes Tracking:**
    * Window title indicates unsaved changes with an asterisk (\*).
    * Prompts to save before exiting if changes are pending.
* **Preset Interaction Logic:**
    * Warns if individual game settings might be overridden when a `gameSettingsPreset` other than "Custom" is selected.
    * Automatically sets `gameSettingsPreset` to "Custom" if an individual game setting (under the `gameSettings` object) is modified.
* **Password Security Reminder:** Tooltip reminder for user group password fields to encourage changing default/weak passwords.

## How to Use

1.  **Prerequisites:**
    * Python 3.x installed on your system. This tool uses only standard Python libraries, so no additional `pip install` steps are typically needed.
2.  **Setup:**
    * Download the script (e.g., `enshrouded_config_gui.py`).
    * Place the script in your Enshrouded dedicated server's root directory. This is usually the folder that contains `enshrouded_server.exe` and where `enshrouded_server.json` will be located.
    * **Important (for best results):** Ensure the official `enshrouded_server_readme.txt` file (often provided by the game developers with server files) is also in this same directory. The tool uses this readme to get the latest game version and default settings structure. If the readme is not found, the tool will use its internal fallback defaults, which might not be the most up-to-date for your game version.
3.  **Running the Editor:**
    * Open a terminal, command prompt, or PowerShell in the server directory.
    * Run the script using: `python enshrouded_config_gui.py` (or `python3 enshrouded_config_gui.py` depending on your system setup).
4.  **Using the Interface:**
    * The application will load your existing `enshrouded_server.json`. If one doesn't exist, it will create it based on the readme or its internal defaults.
    * You'll see the detected game version in the window title.
    * Navigate through the tabs (General, Player, World, etc.) to find settings.
    * Modify settings using the provided input fields, checkboxes, and dropdowns.
    * Hover over setting labels to see tooltips with more information.
    * If you change a setting under `gameSettings` (most settings in Player, World, Enemy, Resources, Experience tabs), the `gameSettingsPreset` on the "World" tab will automatically switch to "Custom" if it wasn't already.
    * If you select a `gameSettingsPreset` other than "Custom", an informational message will appear on relevant tabs reminding you that individual settings might be overridden by the game.
    * Use the "Randomize Settings on This Tab" button if you want to experiment with random configurations for certain game aspects. Be mindful of any difficulty warnings.
    * Manage user groups on the "Server Roles" tab (add, delete, edit details).
    * Click "Save All Settings" (or use File > Save Settings) to apply your changes to `enshrouded_server.json`. A backup will be created automatically before saving. The asterisk (\*) in the window title indicates unsaved changes.
    * Use the "Actions" menu for:
        * "Load Defaults (from Readme)": Reverts the settings in the GUI to the defaults (from readme or fallback). You still need to save for these to take effect.
        * "Manual Backup Current Settings": Creates an immediate backup.
        * "Restore Specific Backup...": Allows you to choose from previously created `.old` backup files to restore.

## Configuration Files

* **`enshrouded_server.json`:** The main configuration file for your Enshrouded dedicated server. The editor reads from and writes to this file.
* **`enshrouded_server_readme.txt`:** (Highly Recommended) Place this official file (if available from your server provider or game files) in the same directory as the script. It's used to:
    * Detect the game version.
    * Provide the most current default settings structure, ensuring the editor is up-to-date with new game settings.
* **`old/` directory:** Automatically created by the editor in the same directory as the script. It stores all timestamped backups of `enshrouded_server.json` with `.old` extensions. Backup filenames include a timestamp and a reason for the backup (e.g., `_before_gui_save`, `_manual_backup`).

## Dependencies

* Python 3.x (uses only the standard library, including Tkinter for the GUI).
* No external packages need to be installed.

## Contributing 

We welcome contributions! If you have ideas for improvements, new features, or find any bugs, please:

1.  Check the existing issues to see if your suggestion or bug has already been reported.
2.  If not, open a new issue to discuss your idea or report the bug.
3.  If you'd like to contribute code:
    * Fork the repository.
    * Create a new branch for your feature or bugfix (`git checkout -b feature/your-new-feature` or `fix/bug-description`).
    * Make your changes and commit them with clear, descriptive messages.
    * Push your branch to your fork (`git push origin feature/your-new-feature`).
    * Open a Pull Request against the main repository, explaining your changes.

## License

This project is not licensed.  Feel free to use or modify however you like.  Just be cool about it.

---

*Disclaimer: This is a third-party tool developed to assist with Enshrouded server configuration. Always ensure you have backups of your important server data before making any changes. The authors of this tool are not responsible for any issues, data loss, or problems that may arise from its use.*
