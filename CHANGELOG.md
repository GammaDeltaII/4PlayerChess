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

# Changelog
All notable changes to the Four-Player Chess project are documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0).

<!-- Types of changes: Added, Changed, Deprecated, Removed, Fixed -->

## [0.10.0] - 06/11/2018
### Added:
- Support for CurrentMove tag in chess.com PGN4, allowing to start at a certain move in the game ("ply-variation-move")


## [0.9.0] - 18/09/2018
**NOTE:** The chess.com analysis board does not support subvariations and hence will not be able to read any PGN4 with subvariations.
### Added:
- Option to use chess.com compatible FEN4 and PGN4
- Player rating (editable)


## [0.8.0] - 03/09/2018
### Added:
- Legal move indicators
- Mouseover coordinates
- Check for absolute pins
- About PyQt
### Fixed:
- Bug allowing castling when in check


## [0.7.0] - 24/08/2018
### Added:
- Promote variation (right-click context menu)
- Different color arrows and square highlights (hold num key 0, 1, 2, 3 or 4 while dragging or clicking) and option to change color with board orientation
- Help menu with quick reference guide and link to GitHub issues to report bugs or request features
### Changed:
- Changed lastMove() to go to last move of main line instead of variation
- Changed About class to generic InfoDialog class to use for different dialogs
### Fixed:
- Bug that allowed drawing arrows and square highlights outside board (in 3x3 corners)


## [0.6.1] - 23/08/2018
### Fixed:
- Bug that caused a crash when making a move


## [0.6.0] - 20/08/2018
### Added:
- Option to remove moves from the move list (right-click context menu)
- Check if player is in check and highlight king square red if so
- Draw arrows (right-click drag) and highlight squares (right-click). Drawing same arrow or square highlight again removes arrow or square highlight. Left-clicking any empty square removes all arrows and highlighted squares.
- Set and save preferences (show coordinates, show names, auto-rotate board)
- Check for updates (compares version to latest GitHub release)

### Changed:
- Cleaned up code About dialog (now class based on .ui file)


## [0.5.0] - 16/08/2018
### Added:
- Pseudo-legal move/attack generation using bitboards
- Castling availability (also pseudo-legal)
### Changed:
- Moved (pseudo-)legality checks and handling of castling moves from algorithm to board (bitboard based)
- Restricted cursor movement to board area while dragging pieces
### Fixed:
- Castling bug (prevMove / nextMove now moves king and rook back to correct squares)
- Move selection bug (did not select move in move list if existing move played)


## [0.4.0] - 12/08/2018
### Added:
- Rotate and flip board view
- Bitboard position representation


## [0.3.0] - 14/07/2018
### Added:
- Game annotations


## [0.2.0] - 06/07/2018
### Added:
- Move pieces by drag-drop
- Board coordinates
### Changed:
- Style and layout
### Removed:
- View select (to be added back when implemented)
### Fixed:
- Minor bugs


## [0.1.0] - 30/06/2018
Initial development release.
### Added:
- Click-to-move chess board with move list and support for variations
- Load and save games and set positions with FEN4 and PGN4
- Play through games, lines and variations by clicking moves, using arrow keys or navigation buttons 
- Move, turn and clicked piece highlighting
- Editable player name labels


<!-- Links to releases -->
[0.10.0]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.10.0
[0.9.0]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.9.0
[0.8.0]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.8.0
[0.7.0]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.7.0
[0.6.1]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.6.1
[0.6.0]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.6.0
[0.5.0]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.5.0
[0.4.0]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.4.0
[0.3.0]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.3.0
[0.2.0]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.2.0
[0.1.0]: https://github.com/GammaDeltaII/4PlayerChess/releases/tag/0.1.0