# This file is part of the Four-Player Chess project, a four-player chess GUI.
#
# Copyright (C) 2018, GammaDeltaII
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Compiler
C = pyuic5

# Compiler flags
FLAGS = --from-imports

# Target files
TARGET := mainwindow.py settings.py infodialog.py

# For all target files
all: $(TARGET)

# Output file $@ is .py and (first) dependency $< is .ui
%.py : %.ui
	$(C) $(FLAGS) -o $@ $<