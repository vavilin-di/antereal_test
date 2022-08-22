from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

from errors.status_store import StatusStore
from errors import exceptions
from helpers.custom_types import ShapeCoords
from map_rendering.shapes import QGraphicsSceneShape, QGraphicsSceneShapes


class AbstractCoordinatesRetriever(ABC):
    @abstractmethod
    def retrieve(self) -> List[ShapeCoords]:
        pass


class AbstractCoordinatesWriter(ABC):
    @abstractmethod
    def save(self) -> None:
        pass


class CoordinatesFileHandlerMixin:
    """Common file r/w operations mixin
    """

    def set_file_path(self, path: str):
        self.file_path = path

    def check_file_existense(self):
        if not self.file_path or not Path(self.file_path).exists():
            raise exceptions.CoordsFileNonExistentError


class CoordinatesWriterFile(CoordinatesFileHandlerMixin, AbstractCoordinatesWriter):
    def __init__(self, status_store: StatusStore) -> None:
        self.file_path = ''
        self.status_store = status_store

    def save(self, coords_list: List[ShapeCoords]) -> None:
        """Save coords to file, each ShapeCoords entry in one line, delimited by spaces

        Args:
            coords_list (List[ShapeCoords]): list of ShapeCoords

        Raises:
            exceptions.CoordsFileNonExistentError: raised if file does not exist
            exceptions.CoordsFileWriteOpenError: raised if file is not writable
        """
        try:
            self.check_file_existense()

            with open(self.file_path, mode='w', encoding='utf-8') as coords_file:
                if not coords_file.writable():
                    raise exceptions.CoordsFileWriteOpenError

                coords_file.writelines([' '.join(map(str, coords)) + '\n' for coords in coords_list])

            self.status_store.add_status(f"Документ сохранён без ошибок.")
        except (exceptions.CoordsFileNonExistentError, exceptions.CoordsFileWriteOpenError) as exception:
            self.status_store.add_status(exception.msg.format(self.file_path))


class CoordinatesRetrieverFile(CoordinatesFileHandlerMixin, AbstractCoordinatesRetriever):
    def __init__(self, status_store: StatusStore) -> None:
        self.file_path = ''
        self.status_store = status_store

    def retrieve(self) -> List[ShapeCoords]:
        """Retrieve a list of coords (from file)

        Raises:
            exceptions.CoordsFileNonExistentError: raised if file does not exist
            exceptions.CoordsFileReadOpenError: raised if file is not readable

        Returns:
            List[ShapeCoords]: list of ShapeCoords (list of float coords)
        """

        coords_raw = []
        try:
            self.check_file_existense()

            with open(self.file_path, mode='r', encoding='utf-8') as coords_file:
                if not coords_file.readable():
                    raise exceptions.CoordsFileReadOpenError

                coords_raw = coords_file.readlines()

            return self._format_all_coords_raw_records(coords_raw_records=coords_raw)
        except (exceptions.CoordsFileNonExistentError, exceptions.CoordsFileReadOpenError) as exception:
            self.status_store.add_status(exception.msg.format(self.file_path))
            return []

    def _format_all_coords_raw_records(self, coords_raw_records: List[str]) -> List[ShapeCoords]:
        """Format all coords raw string records, collect errors

        Args:
            coords_raw_records (List[str]): coords raw string records to format

        Returns:
            List[ShapeCoords]: list of ShapeCoords
        """
        coords = []
        line_number = 1
        errors_is_occured = False

        for coords_raw_record in coords_raw_records:
            try:
                coords.append(self._format_coords_raw_record(coords_raw_record=coords_raw_record))
            except (exceptions.CoordsEntryValueError, exceptions.CoordsEntryUnevenError) as exception:
                self.status_store.add_status(exception.msg.format(line_number))
                errors_is_occured = True
            finally:
                line_number += 1

        if not errors_is_occured:
            self.status_store.add_status(f"Документ прочитан без ошибок.")

        return coords

    def _format_coords_raw_record(self, coords_raw_record: str) -> ShapeCoords:
        """Format coords raw string record

        Args:
            coords_raw_record (str): coords raw string record to format

        Raises:
            CoordsEntryValueError: raised if entry is not float-castable.
            CoordsEntryUnevenError: raised if entry length lesser than 2 or odd.

        Returns:
            ShapeCoords: list of float coordinates
        """
        coords_list_tokens = coords_raw_record.split(' ')
        tokens_length = len(coords_list_tokens)
        if (tokens_length < 2) or (tokens_length % 2):
            raise exceptions.CoordsEntryUnevenError

        try:
            coords = [float(coords_list_token) for coords_list_token in coords_list_tokens]
            return coords
        except (ValueError, OverflowError):
            # OverflowError is raised if the argument is outside the range of a python float
            raise exceptions.CoordsEntryValueError


class CoordinatesQGraphicsSceneShapeTranslator:
    def translate_to_shapes(self, coords_list: List[ShapeCoords]) -> Dict[int, QGraphicsSceneShape]:
        """Creates shape (dict used for better lookup on delete)

        Args:
            coords_list (List[ShapeCoords]): list of ShapeCoords

        Returns:
            Dict[int, QGraphicsSceneShape]: shape map with id:shape
        """
        shapes = {}

        for shape_coords in coords_list:
            shape_coords_length = len(shape_coords)
            shape_class: QGraphicsSceneShape
            if shape_coords_length == 2:
                shape_class = QGraphicsSceneShapes.Dot
            elif shape_coords_length == 4:
                shape_class = QGraphicsSceneShapes.Line
            else:
                shape_class = QGraphicsSceneShapes.Polygon
            shape_object = shape_class(coords=shape_coords)
            shapes[id(shape_object)] = shape_object

        return shapes

    def translate_to_coords(self, shapes: List[QGraphicsSceneShape]) -> List[ShapeCoords]:
        """Get all shapes' coords

        Args:
            shapes (List[QGraphicsSceneShape]): list of shapes

        Returns:
            List[ShapeCoords]: list of ShapeCoords
        """
        coords_list = []
        for shape in shapes:
            coords_list.append(shape.coords)
        return coords_list


class CoordinatesHandler:

    def __init__(self, status_store: StatusStore) -> None:
        self.retriever = CoordinatesRetrieverFile(status_store=status_store)
        self.writer = CoordinatesWriterFile(status_store=status_store)
        self.translator = CoordinatesQGraphicsSceneShapeTranslator()
        self.shapes_map = {}

    def retrieve_coords(self, file_path: str = '') -> None:
        """Retrieve coordinates and store them as shapes

        Args:
            file_path (str, optional): path to coordinates file. Defaults to ''.
        """
        self.retriever.set_file_path(file_path)
        coords_list = self.retriever.retrieve()
        self.translate_coords_to_shapes(coords_list=coords_list)

    def save_coords(self, file_path: str = '') -> None:
        """Get current shapes' coords and store them to file

        Args:
            file_path (str, optional): path to saving file. Defaults to ''.
        """
        self.writer.set_file_path(file_path)
        self.writer.save(self.translate_shapes_to_coords())

    def translate_coords_to_shapes(self, coords_list: List[ShapeCoords]) -> None:
        self.shapes_map = self.translator.translate_to_shapes(coords_list=coords_list)

    def translate_shapes_to_coords(self) -> List[ShapeCoords]:
        return self.translator.translate_to_coords(shapes=self.get_shapes())

    def get_shapes(self) -> List[QGraphicsSceneShape]:
        return list(self.shapes_map.values())

    def remove_shape(self, id: int):
        self.shapes_map.pop(id)
