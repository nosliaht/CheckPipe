````markdown
# Grand Fantasia Translation Checker

Python tool for validating Grand Fantasia translation `.ini` files, allowing real-time monitoring, rule-based verification, and fast identification of broken translation entries.

## 📋 Description

This application provides a clean graphical interface for private Grand Fantasia server administrators, translators, and developers to verify the integrity of game translation files. The tool checks `.ini` translation files based on a configurable pipe-count rule for each file, detects broken entries, and automatically updates the analysis whenever the original file is modified.

It is especially useful for maintaining large sets of translation files and quickly spotting invalid structures that could break in-game texts or cause missing content.

## ✨ Features

- Modern and responsive graphical interface built with **PyQt6**
- Support for checking multiple translation `.ini` files at once
- Automatic validation based on configurable **pipe count** rules
- Per-file pipe configuration saved in `settings.ini`
- Real-time file monitoring with automatic refresh when a file is modified
- Detection of the **last valid ID** in each translation file
- Detection of broken or invalid entries below the last valid record
- Status column for fast identification of valid and broken files
- Folder display for easier file organization
- Separate log window for validation events and file updates
- Multi-language interface support
- Interface texts loaded from external language files (`PT.ini` and `EN.ini`)
- Customizable color theme loaded from `color.ini`
- Configurable fixed window sizes loaded from `interface.ini`
- Modular code structure for easier maintenance and expansion

## 🧩 How It Works

Each translation file is analyzed by reading its records and validating them according to the expected number of `|` separators for that specific `.ini` file.

For example:

- `S_Item.ini = 3 pipes`
- `SomeOtherFile.ini = 5 pipes`

If the structure matches the configured rule, the record is considered valid.  
If a broken record is found, the tool marks the file as **Broken** and shows the last valid ID found before the problem.

## 📁 Project Structure

```text
project/
├─ main.py
├─ interface.py
├─ check.py
├─ settings.ini
├─ color.ini
├─ interface.ini
├─ PT.ini
└─ EN.ini
````

## ⚙️ Configuration Files

### `settings.ini`

Stores general application settings and the pipe count rule for each translation file.

Example:

```ini
[General]
language = EN
window_size = 1080x720

[IniFiles]
S_Item.ini = 3
t_dialogue.ini = 2
```

### `color.ini`

Controls the application color palette.

### `interface.ini`

Defines the available fixed window sizes for the interface.

### `PT.ini` / `EN.ini`

Contain all user interface texts for localization.

## 🖥️ Interface Overview

The main table displays:

* **INI Name**
* **Pipe Count**
* **Folder**
* **Last Valid ID**
* **Status**

Possible status values include:

* **OK**
* **Broken**
* **Not Found**
* **Invalid Config**

The application also includes a separate **log window**, which can be opened from the top menu to view validation events and automatic file update messages.

## 🔄 Real-Time Monitoring

Once a translation file is loaded into the tool, it is automatically monitored.
If the original file is changed, the checker reprocesses it in real time and updates the table without needing manual reload.

This makes it ideal for live editing workflows during translation review or testing.

## 🌐 Language Support

The tool supports both:

* **English**
* **Portuguese**

The interface language can be changed directly from the top menu.

## 🚀 Requirements

* Python 3.10 or newer
* PyQt6

## 📦 Installation

Install the required dependency:

```bash
pip install PyQt6
```

## ▶️ Running the Tool

```bash
python main.py
```

## 🛠️ Use Cases

This tool is useful for:

* Checking Grand Fantasia translation files before deployment
* Detecting broken IDs after manual translation edits
* Monitoring translation files during live editing
* Validating file integrity for private server development
* Organizing and reviewing multiple translation resources at once

## 📌 Notes

* The tool does not require a database connection
* Validation rules are based on the configured number of `|` separators for each file
* If a file does not yet have a saved rule, the pipe count can be entered directly in the table
* Once defined, the rule is automatically saved for future use

## 📄 License

This project is intended for development, maintenance, and translation workflow support for Grand Fantasia private server environments.

```
```
