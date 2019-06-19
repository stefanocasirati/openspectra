#  Developed by Joseph M. Conti and Joseph W. Boardman on 3/17/19 2:30 PM.
#  Last modified 3/17/19 2:30 PM
#  Copyright (c) 2019. All rights reserved.
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QPoint
from PyQt5.QtGui import QColor, QBrush, QCloseEvent, QFont
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, \
    QTableWidget, QTableWidgetItem, QApplication, QStyle, QMenu, QAction

from openspectra.openspecrtra_tools import RegionOfInterest
from openspectra.utils import Logger, LogHelper


class RegionEvent(QObject):

    def __init__(self, region:RegionOfInterest):
        super().__init__(None)
        self.__region = region

    def region(self) -> RegionOfInterest:
        return self.__region


class RegionStatsEvent(RegionEvent):

    def __init__(self, region:RegionOfInterest):
        super().__init__(region)


class RegionToggleEvent(RegionEvent):

    def __init__(self, region:RegionOfInterest):
        super().__init__(region)


class RegionCloseEvent(RegionEvent):

    def __init__(self, region:RegionOfInterest, row:int):
        super().__init__(region)
        self.__row = row

    def row(self) -> int:
        return self.__row


class RegionNameChangeEvent(RegionEvent):

    def __init__(self, region:RegionOfInterest):
        super().__init__(region)


class RegionSaveEvent(RegionEvent):

    def __init__(self, region:RegionOfInterest, include_bands:bool=False):
        super().__init__(region)
        self.__include_bands = include_bands

    def include_bands(self) -> bool:
        return self.__include_bands


class RegionOfInterestControl(QWidget):

    __LOG:Logger = LogHelper.logger("RegionOfInterestControl")

    stats_clicked = pyqtSignal(RegionStatsEvent)
    region_toggled = pyqtSignal(RegionToggleEvent)
    region_name_changed = pyqtSignal(RegionNameChangeEvent)
    region_saved = pyqtSignal(RegionSaveEvent)
    region_closed =  pyqtSignal(RegionCloseEvent)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__regions = list()
        self.__selected_row = None

        layout = QVBoxLayout()

        self.__margins = 5
        layout.setContentsMargins(self.__margins, self.__margins, self.__margins, self.__margins)

        self.__rows = 0
        self.__table = QTableWidget(self.__rows, 4, self)
        self.__table.setShowGrid(False)
        self.__table.verticalHeader().hide()
        self.__table.cellClicked.connect(self.__handle_cell_clicked)
        self.__table.cellChanged.connect(self.__handle_cell_changed)

        self.__table.setColumnWidth(0, 40)

        self.__table.setHorizontalHeaderLabels(["Color", "Name", "Size (h x w)", "Description"])
        layout.addWidget(self.__table)
        self.setLayout(layout)

        self.__init_menu()

    def __init_menu(self):
        self.__menu:QMenu = QMenu(self)
        toggle_action = QAction("Toggle", self)
        toggle_action.triggered.connect(self.__handle_region_toggle)
        self.__menu.addAction(toggle_action)

        stats_action = QAction("Band stats", self)
        stats_action.triggered.connect(self.__handle_band_stats)
        self.__menu.addAction(stats_action)

        self.__menu.addSeparator()

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.__handle_region_save)
        self.__menu.addAction(save_action)

        close_action = QAction("Close", self)
        close_action.triggered.connect(self.__handle_region_close)
        self.__menu.addAction(close_action)

        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def add_item(self, region:RegionOfInterest, color:QColor):
        self.__table.cellClicked.disconnect(self.__handle_cell_clicked)
        self.__table.cellChanged.disconnect(self.__handle_cell_changed)
        self.__table.setRowCount(self.__rows + 1)

        name_item = QTableWidgetItem(region.display_name())

        color_item = QTableWidgetItem("...")
        font = QFont()
        font.setBold(True)
        color_item.setFont(font)
        color_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        color_item.setBackground(QBrush(color))
        color_item.setFlags(Qt.ItemIsEnabled)

        size_item = QTableWidgetItem(
            str(region.image_height()) + " x " + str(region.image_width()))
        size_item.setTextAlignment(Qt.AlignVCenter)
        size_item.setFlags(Qt.ItemIsEnabled)

        description_item = QTableWidgetItem(region.description())
        description_item.setFlags(Qt.ItemIsEnabled)

        self.__table.setItem(self.__rows, 0, color_item)
        self.__table.setItem(self.__rows, 1, name_item)
        self.__table.setItem(self.__rows, 2, size_item)
        self.__table.setItem(self.__rows, 3, description_item)

        if self.__rows == 0:
            self.__table.horizontalHeader().setStretchLastSection(True)

        self.__adjust_width()

        self.__regions.append(region)
        self.__rows += 1
        self.__table.cellClicked.connect(self.__handle_cell_clicked)
        self.__table.cellChanged.connect(self.__handle_cell_changed)

    def remove_all(self):
        self.__table.clearContents()
        self.__regions.clear()
        self.__rows = 0

    def remove(self, event:RegionCloseEvent):
        row = event.row()
        region = self.__regions[row]
        if region is not None:
            self.__table.removeRow(row)
            del self.__regions[row]
            self.__rows -= 1
            self.__selected_row = None

    def __adjust_width(self):
        self.__table.resizeColumnsToContents()
        length = self.__table.horizontalHeader().length()
        RegionOfInterestControl.__LOG.debug("Header length: {0}", length)
        self.setMinimumWidth(length + self.__margins * 2 +
                             QApplication.style().pixelMetric(QStyle.PM_DefaultFrameWidth) * 2)

    def __handle_cell_clicked(self, row:int, column:int):
        position = self.mapToGlobal(QPoint(self.__table.columnViewportPosition(column), self.__table.rowViewportPosition(row)))
        RegionOfInterestControl.__LOG.debug("Cell clicked row: {0}, column: {1}, y pos: {2}",
            row, column, position)
        if column == 0 and -1 < row < len(self.__regions):
            self.__selected_row = row
            RegionOfInterestControl.__LOG.debug("Found region: {0}", self.__regions[row].display_name())
            self.__menu.popup(position)

    def __handle_cell_changed(self, row:int, column:int):
        RegionOfInterestControl.__LOG.debug("Cell changed row: {0}, column: {1}", row, column)
        if column == 1:
            item = self.__table.item(row, column)
            RegionOfInterestControl.__LOG.debug("Cell changed, new value: {0}", item.text())
            region:RegionOfInterest = self.__regions[row]
            region.set_display_name(item.text())
            self.region_name_changed.emit(RegionNameChangeEvent(region))
            self.__adjust_width()

    def __handle_region_toggle(self):
        region = self.__regions[self.__selected_row]
        RegionOfInterestControl.__LOG.debug("Toogle region: {0}", region.display_name())
        self.region_toggled.emit(RegionToggleEvent(region))
        self.__selected_row = None

    def __handle_region_save(self):
        region = self.__regions[self.__selected_row]
        RegionOfInterestControl.__LOG.debug("Save region: {0}", region.display_name())
        self.region_saved.emit(RegionSaveEvent(region))
        self.__selected_row = None

    def __handle_region_close(self):
        region = self.__regions[self.__selected_row]
        RegionOfInterestControl.__LOG.debug("Close region: {0}", region.display_name())
        self.region_closed.emit(RegionCloseEvent(region, self.__selected_row))

    def __handle_band_stats(self):
        region = self.__regions[self.__selected_row]
        RegionOfInterestControl.__LOG.debug("Band stats region: {0}", region.display_name())
        self.stats_clicked.emit(RegionStatsEvent(region))
        self.__selected_row = None


class RegionOfInterestDisplayWindow(QMainWindow):

    __LOG:Logger = LogHelper.logger("RegionOfInterestDisplayWindow")

    stats_clicked = pyqtSignal(RegionStatsEvent)
    region_toggled = pyqtSignal(RegionToggleEvent)
    region_name_changed = pyqtSignal(RegionNameChangeEvent)
    region_saved = pyqtSignal(RegionSaveEvent)
    region_closed =  pyqtSignal(RegionCloseEvent)
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Region of Interest")
        self.__region_control = RegionOfInterestControl()
        self.setCentralWidget(self.__region_control)
        self.__region_control.stats_clicked.connect(self.stats_clicked)
        self.__region_control.region_toggled.connect(self.region_toggled)
        self.__region_control.region_name_changed.connect(self.region_name_changed)
        self.__region_control.region_saved.connect(self.region_saved)
        self.__region_control.region_closed.connect(self.region_closed)

    def add_item(self, region:RegionOfInterest, color:QColor):
        self.__region_control.add_item(region, color)

    def remove_all(self):
        self.__region_control.remove_all()

    def remove(self, event:RegionCloseEvent):
        self.__region_control.remove(event)

    def closeEvent(self, event:QCloseEvent):
        self.closed.emit()
        # accepting hides the window
        event.accept()
