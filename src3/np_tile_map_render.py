import numpy as np

def render_color_grid(
    color_grid: list[list[tuple[int, int, int]]],
    pixels_per_cell: int,
    border_thickness: int,
    border_color: tuple[int, int, int] = None,
) -> np.ndarray:
    """Given a 2D grid of RGB tuples, render an image where each grid
    cell is rendered as a solid color filled square.

    Arguments:
        color_grid: list[list[tuple[int, int, int]]]
        pixels_per_cell: int
        border_thickness: int
        border_color: tuple[int, int, int]
    """
    if border_color is None:
        border_color = (0, 0, 0)
    nrows = len(color_grid)
    ncols = len(color_grid[0])
    assert all(len(color_grid_row) == ncols for color_grid_row in color_grid)
    shape = (nrows * pixels_per_cell, ncols * pixels_per_cell)
    rgb_planes = [
        np.full(shape=shape, fill_value=border_color[ch], dtype=np.uint8)
        for ch in range(3)
    ]
    for row in range(nrows):
        row_start = row * pixels_per_cell + border_thickness
        row_stop =  (row + 1) * pixels_per_cell - border_thickness
        for col in range(ncols):
            col_start = col * pixels_per_cell + border_thickness
            col_stop =  (col + 1) * pixels_per_cell - border_thickness
            color_tuple = color_grid[row][col]
            for ch in range(3):
                rgb_planes[ch][row_start:row_stop, col_start:col_stop] = color_tuple[ch]
    return np.stack(rgb_planes, axis=-1)
