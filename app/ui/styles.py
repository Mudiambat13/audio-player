"""Styles communs de l'interface."""

import re

APP_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0B0D12;
    color: #F4F5F7;
    font-family: "Segoe UI";
    font-size: 13px;
}

#sidebar {
    background-color: #101218;
    border-right: 1px solid #222630;
}

#logo {
    color: #F7F7FA;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 2px;
    padding: 18px 12px;
}

#sidebar QPushButton {
    background-color: transparent;
    color: #969BA8;
    border: none;
    border-radius: 9px;
    text-align: left;
    padding: 13px 15px;
    margin: 2px 8px;
    font-weight: 600;
}

#sidebar QPushButton:hover {
    background-color: #1B1E27;
    color: #FFFFFF;
}

#sidebar QPushButton:checked {
    background-color: #222032;
    color: #C0AEFF;
    border-left: 3px solid #A78BFA;
}

#sidebar QPushButton#themeToggleButton {
    background-color: transparent;
    color: #969BA8;
    border: 1px solid #303541;
    border-radius: 9px;
    text-align: left;
    padding: 11px 12px;
    margin: 8px;
    font-weight: 600;
}

#sidebar QPushButton#themeToggleButton:hover {
    background-color: #1B1E27;
    color: #FFFFFF;
}

#pageTitle {
    color: #FAFAFC;
    font-size: 29px;
    font-weight: 750;
}

#artistHeading {
    color: #F7F7FA;
    font-size: 19px;
    font-weight: 700;
    padding: 4px 0;
}

#mutedText {
    color: #8C92A0;
    font-size: 12px;
}

#countBadge {
    color: #B9A6FF;
    background-color: #211C34;
    border-radius: 10px;
    padding: 8px 11px;
    font-size: 10px;
    font-weight: 700;
}

QPushButton {
    background-color: #20232C;
    color: #F4F5F7;
    border: 1px solid #2B2F3A;
    border-radius: 9px;
    padding: 11px 15px;
    font-weight: 650;
}

QPushButton:hover {
    background-color: #2A2E39;
    border-color: #474D5C;
}

QPushButton#primaryButton {
    background-color: #9B7BFF;
    color: #101014;
    border: none;
    padding: 12px 18px;
    font-weight: 750;
}

QPushButton#secondaryActionButton {
    background-color: #1A1D25;
    color: #CDD0D8;
    border: 1px solid #303541;
}

QToolButton#libraryActionButton, QToolButton#importButton {
    border-radius: 12px;
    padding: 0;
}

QToolButton#libraryActionButton {
    background-color: #1A1D25;
    border: 1px solid #303541;
}

QToolButton#libraryActionButton:hover {
    background-color: #262833;
    border-color: #555B6A;
}

QToolButton#importButton {
    background-color: #A78BFA;
    border: none;
}

QToolButton#importButton:hover {
    background-color: #B9A5FF;
}

QToolButton#albumCard {
    background-color: #14171E;
    color: #F4F5F7;
    border: 1px solid #252A34;
    border-radius: 12px;
    padding: 11px;
    font-size: 12px;
    font-weight: 650;
    text-align: left;
}

QToolButton#albumCard:hover {
    background-color: #20232C;
    border-color: #7259B7;
}

QScrollArea#artistsScrollArea, QWidget#artistsContent {
    background-color: transparent;
    border: none;
}

QToolButton#artistCard {
    background-color: #14171E;
    color: #F4F5F7;
    border: 1px solid #252A34;
    border-radius: 12px;
    padding: 11px;
    font-size: 12px;
    font-weight: 650;
    text-align: center;
}

QToolButton#artistCard:hover {
    background-color: #20232C;
    border-color: #7259B7;
}

QPushButton#primaryButton:hover {
    background-color: #B09AFF;
}

QToolButton#iconButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 19px;
    padding: 0;
}

QToolButton#iconButton:hover {
    background-color: #262833;
    border-color: #333744;
}

QToolButton#iconButton:checked {
    background-color: #302748;
    border-color: #5D4A8A;
}

QToolButton#playButton {
    background-color: #A78BFA;
    border: none;
    border-radius: 21px;
    padding: 0;
}

QToolButton#playButton:hover {
    background-color: #B9A5FF;
}

QLineEdit#searchField {
    background-color: #14171E;
    color: #F4F5F7;
    border: 1px solid #292D37;
    border-radius: 10px;
    padding: 12px 15px;
    selection-background-color: #7658FF;
}

QLineEdit#searchField:focus {
    border-color: #8C70E8;
}

QFrame#tableFrame {
    background-color: #11141A;
    border: 1px solid #222630;
    border-radius: 14px;
}

QScrollArea#albumsScrollArea, QWidget#albumsContent {
    background-color: transparent;
    border: none;
}

QTableWidget#libraryTable, QListWidget {
    background-color: transparent;
    color: #EBECF0;
    border: none;
    outline: none;
}

QHeaderView::section {
    background-color: transparent;
    color: #777E8D;
    border: none;
    border-bottom: 1px solid #292D37;
    padding: 12px 8px;
    font-size: 10px;
    font-weight: 750;
}

QTableWidget::item {
    border: none;
    padding: 7px 8px;
}

QTableWidget::item:hover {
    background-color: #1B1E27;
}

QTableWidget::item:selected {
    background-color: #29233A;
    color: #FFFFFF;
}

QListWidget::item {
    padding: 13px 10px;
    border-bottom: 1px solid #20232C;
    border-radius: 5px;
}

QListWidget::item:selected {
    background-color: #29233A;
}

#emptyState {
    color: #858B99;
    font-size: 14px;
    padding: 28px;
}

#player {
    background-color: #14171E;
    border: 1px solid #292D37;
    border-radius: 14px;
}

#albumArtwork {
    color: #E5DBFF;
    background-color: #29233A;
    border: 1px solid #3B3152;
    border-radius: 10px;
    font-size: 24px;
}

#songTitle {
    color: #FAFAFC;
    font-size: 13px;
    font-weight: 700;
}

#nowPlayingEyebrow {
    color: #A78BFA;
    font-size: 11px;
    font-weight: 750;
    letter-spacing: 2px;
}

#nowPlayingArtwork {
    color: #E5DBFF;
    background-color: #29233A;
    border: 1px solid #3B3152;
    border-radius: 20px;
    font-size: 76px;
}

#nowPlayingTitle {
    color: #FAFAFC;
    font-size: 27px;
    font-weight: 750;
}

#nowPlayingSubtitle {
    color: #9A9EAA;
    font-size: 14px;
}

QToolButton#nowPlayingPlayButton {
    background-color: #A78BFA;
    border: none;
    border-radius: 27px;
    padding: 0;
}

QToolButton#nowPlayingPlayButton:hover {
    background-color: #B9A5FF;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #363A45;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #B29AFF;
    width: 10px;
    margin: -4px 0;
    border-radius: 5px;
}

QSlider::sub-page:horizontal {
    background: #9B7BFF;
    border-radius: 2px;
}
"""

_LIGHT_PALETTE = {
    "#0B0D12": "#F5F6FA",
    "#101218": "#FFFFFF",
    "#222630": "#E2E4EB",
    "#F4F5F7": "#252735",
    "#969BA8": "#686D7B",
    "#1B1E27": "#EFF0F5",
    "#FFFFFF": "#252735",
    "#222032": "#EEEAF7",
    "#C0AEFF": "#6248B1",
    "#A78BFA": "#7658D1",
    "#FAFAFC": "#252735",
    "#F7F7FA": "#252735",
    "#8C92A0": "#6F7481",
    "#B9A6FF": "#6248B1",
    "#211C34": "#EEEAF7",
    "#20232C": "#F0F1F6",
    "#2B2F3A": "#D6D9E2",
    "#2A2E39": "#E6E7ED",
    "#474D5C": "#B9BDC8",
    "#101014": "#FFFFFF",
    "#1A1D25": "#F7F7FA",
    "#CDD0D8": "#424653",
    "#303541": "#D9DBE3",
    "#262833": "#E8E9EF",
    "#555B6A": "#B3B7C2",
    "#B9A5FF": "#8C72D6",
    "#14171E": "#FFFFFF",
    "#252A34": "#E2E4EB",
    "#7259B7": "#7658D1",
    "#302748": "#EAE5F5",
    "#5D4A8A": "#C8B9E8",
    "#292D37": "#DDE0E8",
    "#7658FF": "#7658D1",
    "#11141A": "#F9FAFC",
    "#777E8D": "#747987",
    "#EBECF0": "#252735",
    "#29233A": "#EAE5F5",
    "#858B99": "#6F7481",
    "#292D37": "#DDE0E8",
    "#3B3152": "#DDD5EF",
    "#E5DBFF": "#4D3D70",
    "#9A9EAA": "#6F7481",
    "#363A45": "#D9DBE3",
    "#B29AFF": "#7658D1",
    "#9B7BFF": "#7658D1",
}


def stylesheet_for_theme(theme: str) -> str:
    if theme == "dark":
        return APP_STYLESHEET

    return re.sub(
        r"#[0-9A-Fa-f]{6}",
        lambda match: _LIGHT_PALETTE.get(match.group(0), match.group(0)),
        APP_STYLESHEET,
    )
