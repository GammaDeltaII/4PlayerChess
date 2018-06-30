<!--
This file is part of the Four-Player Chess project, a four-player chess GUI.

Copyright (C) 2018, GammaDeltaII

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
-->

<img src="resources/img/icon.png" width="100" height="100">

# 4 Player Chess GUI
A basic GUI for 4 Player Chess to analyze lines. This project is a work in progress. Currently, it only supports the Teams variant. Free-For-All (FFA) may be added in the future.

## Getting Started
This program is cross-platform compatible (macOS, Linux, Windows). The following instructions will guide you to install the prerequisites and run the program.

### Prerequisites
- [Python3](https://www.python.org/downloads/)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/download5)

### Install & Run
Follow the instructions for your operating system. If you are not familiar with the command line interface:
- The `cd` command is used to change directory, e.g. `cd path/to/directory`
    - Type `cd` or `cd ~` to go to your home directory
    - Type `cd /` to go to the root directory
    - Type `cd ..` to go to the parent directory of the current directory
    - Type `cd -` to go to the previous directory you were in
- The `ls` (macOS & Linux) or `dir` (Windows) command will list the contents of the current directory

#### macOS
Open Terminal to enter the commands at the following steps.

1. Install package manager Homebrew to install Python3 (or install Python3 manually and skip to 3.):
    ```
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    ```
2. Install Python3:
    ```
    brew install python3
    ```
3. Install PyQt5:
    ```
    pip3 install pyqt5
    ```
4. Navigate to the `/4PlayerChess` directory and run the main file:
    ```
    cd path/to/directory
    python3 4pc.py
    ```
#### Windows
Open Command Prompt (open Windows menu and search "command") to enter the commands at the following steps.

1. Launch Python3 installer to install Python3 manually and make sure to check the options to add Python3 to environment
    variables or PATH and to include pip. Alternatively, install package manager Chocolatey:
    ```
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
    ```
    And install Python3 with Chocolatey:
    ```
    choco install python
    ```
2. Install PyQt5:
    ```
    py -m pip install pyqt5
    ```
3. Navigate to the `/4PlayerChess` directory and run the main file:
    ```
    cd path/to/directory
    py 4pc.py
    ```

#### Linux
Open a terminal to enter the commands at the following steps.

1. Use package manager to install or update Python3, e.g. on Ubuntu:
    ```
    sudo apt-get update
    sudo apt-get -y upgrade
    sudo apt-get install -y python3.6
    ```
2. Install `pip`:
    ```
    sudo apt-get install -y python3-pip
    ```
3. Install PyQt5:
    ```
    pip3 install pyqt5
    ```
4. Navigate to the `/4PlayerChess` directory and run the main file:
    ```
    cd path/to/directory
    python3 4pc.py
    ```

#### Notes
- Multiple versions of Python may be (pre-)installed. If so, use `python3` and `pip3` for Python3 (`python` and
    `pip` are for Python2). Check the version and update Python3 to the latest version, if needed.
    
    - `python3 --version` (macOS)
    - `python3 -V` (Linux)
    - `py -v` (Windows)
- On Windows, if Python version < 3.6, use `python` instead of `py`. To force latest version 3, use `py -3`, if needed.

## Contribute / Contact
If you would like to contribute to this project, feel free to create a pull request.
Contact: [GDII](https://www.chess.com/member/gdii) (a.k.a. GammaDeltaII on Discord).

## Repository
https://github.com/GammaDeltaII/4PlayerChess

## License
This project is licensed under the GNU General Public License v3.0. See the [COPYING](COPYING) file for details.