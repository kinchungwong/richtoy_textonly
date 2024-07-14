from enum import Enum

class StreetDirection(Enum):
    Lat = "Lat" # Horizontal streets, each taking up a row
    Lon = "Lon" # Vertical streets, each taking up a column

StreetIndex = int

class Street:
    index: int
    street_dir: StreetDirection
    position: int

    def __init__(self, index: int, street_dir: StreetDirection, position: int) -> None:
        self.index = index
        self.street_dir = street_dir
        self.position = position

class GridCell:
    """GridCell are the items in the 2D grid.

    Init arguments:
        row: int
        col: int

    Post-init attributes:
        is_lat_street: bool
        is_lon_street: bool

    Computed properties:
        is_street = lambda: is_lat_street or is_lon_street
        is_crossroad = lambda: is_lat_street and is_lon_street

            Remark:
        All post-init attributes can be initialized later,
        because not all information is available at init call.
    """
    row: int
    col: int
    is_lat_street: bool
    is_lon_street: bool

    @property
    def is_street(self) -> bool:
        return self.is_lat_street or self.is_lon_street

    @property
    def is_crossroad(self) -> bool:
        return self.is_lat_street and self.is_lon_street

    def __init__(self, row: int, col: int) -> None:
        assert type(row) == int
        assert type(col) == int
        assert row >= 0
        assert col >= 0
        self.row = row
        self.col = col
        self.is_lat_street = False
        self.is_lon_street = False

class TileMapBuilder:
    streets: list[Street]
    lat_streets: dict[int, Street]
    lon_streets: dict[int, Street]
    grid: list[list[GridCell]]

    def __init__(self) -> None:
        self.streets = list()
        self.lat_streets = dict()
        self.lon_streets = dict()

    def add_thru_street(self, street_dir: StreetDirection, position: int) -> StreetIndex:
        assert isinstance(street_dir, StreetDirection)
        assert type(position) == int
        assert position >= 0
        lat_lon_dict = self.lat_streets if street_dir is StreetDirection.Lat else self.lon_streets
        assert position not in lat_lon_dict
        street_index = len(self.streets)
        street = Street(street_index, street_dir, position)
        self.streets.append(street)
        lat_lon_dict[position] = street

    def populate_grid_from_thru_streets(self) -> None:
        lat_positions = sorted(self.lat_streets.keys())
        lon_positions = sorted(self.lon_streets.keys())
        grid_nrows = lat_positions[-1] + 1
        grid_ncols = lon_positions[-1] + 1
        
        self.grid = [
            [
                GridCell(row=row, col=col)
                for col in range(grid_ncols)
            ]
            for row in range(grid_nrows)
        ]
        
        for lat in lat_positions:
            row = lat
            for col in range(grid_ncols):
                self.grid[row][col].is_lat_street = True
        
        for lon in lon_positions:
            col = lon
            for row in range(grid_nrows):
                self.grid[row][col].is_lon_street = True

    def textformat_as_one_char_map(self) -> list[str]:
        def fn_gridcell_to_one_char(cell: GridCell) -> str:
            if cell.is_crossroad:
                return "+"
            elif cell.is_lat_street:
                return "-"
            elif cell.is_lon_street:
                return "|"
            else:
                return " "
        text: list[str] = list()
        for row, row_of_cells in enumerate(self.grid):
            line: list[str] = list()
            for col, cell in enumerate(row_of_cells):
                line.append(fn_gridcell_to_one_char(cell))
            text.append("".join(line))
        return text
