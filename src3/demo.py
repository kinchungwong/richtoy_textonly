from src3.tile_map_builder import TileMapBuilder, StreetDirection
from src3.np_tile_map_render import render_color_grid
from src3.cv2_showimage import showimage


def print_blank_lines_with_delay():
    import time
    for k in range(2):
        time.sleep(0.5)
        s = "_" if k == 0 else ""
        print(f"{s}\r\n")


if __name__ == "__main__":
    
    print_blank_lines_with_delay()

    streets_args = [
        (StreetDirection.Lat, 0),
        (StreetDirection.Lat, 7),
        (StreetDirection.Lat, 12),
        (StreetDirection.Lat, 19),
        (StreetDirection.Lat, 24),
        (StreetDirection.Lat, 31),
        (StreetDirection.Lon, 0),
        (StreetDirection.Lon, 7),
        (StreetDirection.Lon, 12),
        (StreetDirection.Lon, 19),
        (StreetDirection.Lon, 24),
        (StreetDirection.Lon, 31),
    ]
    builder = TileMapBuilder()
    
    for street_dir, street_pos in streets_args:
        builder.add_thru_street(street_dir, street_pos)
    
    builder.populate_grid_from_thru_streets()

    one_char_map = builder.textformat_as_one_char_map()
    for line in one_char_map:
        print(line)

    char_colorize_dict: dict[str, tuple[int, int, int]] = dict([
        ("+", (255, 255, 255)),
        ("-", (255, 0, 128)),
        ("|", (128, 0, 255)),
        (" ", (32, 32, 32)),
    ])

    rgb_tuple_map = [
        [char_colorize_dict[c] for c in one_cha_map_row]
        for one_cha_map_row in one_char_map
    ]

    img = render_color_grid(
        rgb_tuple_map,
        pixels_per_cell=28,
        border_thickness=2,
        border_color=(0, 0, 0),
    )
    showimage(img, window_title="map")
