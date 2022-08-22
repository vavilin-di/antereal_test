from typing import List

from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
)
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from PyQt5 import QtGui

from map_rendering.shapes import QGraphicsSceneShape

MAP_ZOOM_RATIO = 1.25

HIGHLIGHTED_PEN_WIDTH = 3
DEFAULT_PEN_WIDTH = 1


class DraggableQGraphicsView(QGraphicsView):
    old_cursor_position = None

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.old_cursor_position = event.pos()
        else:
            return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if not (self.old_cursor_position is None):
            new_cursor_position = event.pos()
            cursor_position_diff = self.old_cursor_position - new_cursor_position
            self.set_map_center(position=cursor_position_diff)
            self.old_cursor_position = new_cursor_position
        else:
            return super().mouseMoveEvent(event)

    def set_map_center(self, position: QPointF):
        map_transform = self.transform()
        dx = position.x() / map_transform.m11()
        dy = position.y() / map_transform.m22()
        self.setSceneRect(self.sceneRect().translated(dx, dy))

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            self.shape_removed_signal.emit()
        else:
            return super().keyPressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.old_cursor_position is not None:
            item = self.itemAt(self.old_cursor_position)
            if hasattr(item, 'hasFocus'):
                item.setFocus()
        self.old_cursor_position = None
        return super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        if event.angleDelta().y() > 0:
            zoom = MAP_ZOOM_RATIO
        else:
            zoom = 1/MAP_ZOOM_RATIO
        self.scale(zoom, zoom)

    def set_shape_removed_signal(self, signal: pyqtSignal):
        self.shape_removed_signal = signal


class MapArea():
    def __init__(self, shape_removed_signal: pyqtSignal) -> None:
        self.map_frame = QGraphicsScene()
        self.map_frame.itemIndexMethod()
        self.map_frame.focusItemChanged.connect(self.highlight_focus_item)
        self.map_rendered_shapes = {}
        self.map_focused_item: QGraphicsItem = None

        self.map_widget = DraggableQGraphicsView()
        self.map_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.map_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.map_widget.setScene(self.map_frame)
        self.map_widget.set_shape_removed_signal(signal=shape_removed_signal)

    def get_focused_item(self) -> QGraphicsItem:
        return self.map_focused_item

    def get_focused_shape(self) -> QGraphicsSceneShape:
        return self.map_rendered_shapes.get(self.get_focused_item().data(0))

    def highlight_focus_item(self, newFocusItem: QGraphicsItem, oldFocusItem: QGraphicsItem, reason: Qt.FocusReason):
        """Highlight focus item: set new map_focused_item (for later use) change fill color to lighter (if any)
           and set pen wider. Lost focus item' s fill color and pen width are set to default.

        Args:
            newFocusItem (QGraphicsItem): got focus item
            oldFocusItem (QGraphicsItem): lost focus item
            reason (Qt.FocusReason): focus change reason
        """

        self.map_focused_item = newFocusItem
        if hasattr(newFocusItem, 'brush'):
            old_color = newFocusItem.brush().color()
            old_color.setAlpha(180)
            newFocusItem.setBrush(old_color)
        if hasattr(newFocusItem, 'pen'):
            newFocusItem.setPen(QtGui.QPen(QtGui.QColor('black'), HIGHLIGHTED_PEN_WIDTH))

        if hasattr(oldFocusItem, 'brush'):
            old_color = oldFocusItem.brush().color()
            old_color.setAlpha(255)
            oldFocusItem.setBrush(old_color)
        if hasattr(oldFocusItem, 'pen'):
            oldFocusItem.setPen(QtGui.QPen(QtGui.QColor('black'), DEFAULT_PEN_WIDTH))

    def clear_map(self):
        """Remove all figures from map frame
        """
        self.map_frame.clear()
        self.map_rendered_shapes = {}

    def remove_focused_item(self):
        self.map_frame.removeItem(self.get_focused_item())

    def render_shapes(self, shapes: List[QGraphicsSceneShape]) -> None:
        """Clear map frame and render shapes by specified coordinates

        Args:
            shapes (List[QGraphicsSceneShape]): list of shapes
        """
        self.clear_map()

        for shape in shapes:
            rendered_shape = shape.render(map_frame=self.map_frame)
            self.map_rendered_shapes[rendered_shape.data(0)] = shape
