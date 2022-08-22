from abc import ABC, abstractmethod
from random import choice


from PyQt5 import QtGui
from PyQt5.QtCore import QPointF, QLineF, QRectF, QSizeF
from PyQt5.QtWidgets import (
    QGraphicsScene,
    QGraphicsItem,
)

from helpers.custom_types import ShapeCoords

# Dot radius (px)
DOT_RADIUS = 1.5


class QGraphicsSceneShape(ABC):
    """Possible map shapes abstract class with coords to shape (and vice versa) translation
       and rendering on the map
    """

    def __init__(self, coords: ShapeCoords) -> None:
        self.coords = coords
        self.shape = None

    @abstractmethod
    def render(self, map_frame: QGraphicsScene) -> QGraphicsItem:
        if self.shape is None:
            self.translate_coords_to_shape()
        item = self.shape_add_function(self.shape)
        item.setFlag(QGraphicsItem.ItemIsFocusable)

        return item

    @abstractmethod
    def translate_coords_to_shape(self):
        pass

    def translate_shape_to_coords(self) -> ShapeCoords:
        return self.coords


class QGraphicsSceneShapes:
    """Possible map shapes concrete classes
    """
    class Dot(QGraphicsSceneShape):
        DOT_SIZE = QSizeF(DOT_RADIUS*2, DOT_RADIUS*2)

        def render(self, map_frame: QGraphicsScene) -> QGraphicsItem:
            self.shape_add_function = map_frame.addEllipse
            item = super().render(map_frame=map_frame)
            item.setData(0, id(self.shape))
            return item

        def translate_coords_to_shape(self) -> QRectF:
            x, y = self.coords
            y = -y
            point_shape = QPointF(x - DOT_RADIUS, y - DOT_RADIUS)
            self.shape = QRectF(point_shape, self.DOT_SIZE)
            return self.shape

    class Line(QGraphicsSceneShape):
        def render(self, map_frame: QGraphicsScene) -> QGraphicsItem:
            self.shape_add_function = map_frame.addLine
            item = super().render(map_frame=map_frame)
            item.setData(0, id(self.shape))
            return item

        def translate_coords_to_shape(self) -> QLineF:
            x1, y1, x2, y2 = self.coords
            y1, y2 = -y1, -y2
            self.shape = QLineF(x1, y1, x2, y2)
            return self.shape

    class Polygon(QGraphicsSceneShape):
        def render(self, map_frame: QGraphicsScene) -> QGraphicsItem:
            self.shape_add_function = map_frame.addPolygon
            polygon = super().render(map_frame=map_frame)
            polygon.setBrush(QtGui.QColor(choice(QtGui.QColor.colorNames())))
            polygon.setData(0, id(self.shape))
            return polygon

        def translate_coords_to_shape(self) -> QtGui.QPolygonF:
            polygon_points = []
            coords_iterated = iter(self.coords)
            for coords_item in coords_iterated:
                x, y = coords_item, next(coords_iterated)
                y = -y
                polygon_points.append(QPointF(x, y))
            self.shape = QtGui.QPolygonF(polygon_points)
            return self.shape
