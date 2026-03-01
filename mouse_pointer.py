"""
Talon Voice module which supports relative mouse pointer movements.

These include movements in radial directions relative to the
current mouse pointer position. For example:
- Moving the mouse pointer up (100 pixels)
- Moving the mouse pointer 25 pixels towards the direction of 8 o'clock
- Moving the mouse pointer 70 pixels northeast
- Nudging the mouse pointer left a few pixels

It also supports movements to virtual grid cell locations that are based on
the size of the main screen. For example:
- Moving the mouse pointer to the center of the lower right quadrant of the
  the main screen

"""
from typing import Tuple
from talon import Module, settings, ctrl, ui

mod = Module()

# TODO: Maybe need to look into handling multiple and/or different sized screens

# Map keyed by screen direction descriptions. Their values are their unit
# vector equivalents.
screen_direction_vector_map: dict[str, Tuple[float, float]] = {
    "up": (0.0, -1.0),
    "down": (0.0, 1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
    "upper left": (-1.0, -1.0),
    "upper right": (1.0, -1.0),
    "lower left": (-1.0, 1.0),
    "lower right": (1.0, 1.0)
}

screen_direction_matcher \
    = "(" + "|".join(screen_direction_vector_map.keys()) + ")"


# Map keyed by clocktime directions. Their values are their unit vector
# equivalents.
clocktime_direction_vector_map: dict[str, Tuple[float, float]] = {
    "one": (0.5, -0.866),
    "two": (0.866, -0.5),
    "three": (1.0, 0.0),
    "four": (0.866, 0.5),
    "five": (0.5, 0.866),
    "six": (0.0, 1.0),
    "seven": (-0.5, 0.866),
    "eight": (-0.866, 0.5),
    "nine": (-1.0, 0.0),
    "ten": (-0.866, -0.5),
    "eleven": (-0.5, -0.866),
    "twelve": (0.0, -1.0)
 }

clocktime_direction_matcher \
    = "(" + "|".join(clocktime_direction_vector_map.keys()) + ")"


# Map keyed by compass directions. Their values are their unit vector
# equivalents.
compass_direction_vector_map: dict[str, Tuple[float, float]] = {
    "north": (0.0, -1.0),
    "south": (0.0, 1.0),
    "west": (-1.0, 0.0),
    "east": (1.0, 0.0),
    "northwest": (-1.0, -1.0),
    "northeast": (1.0, -1.0),
    "southwest": (-1.0, 1.0),
    "southeast": (1.0, 1.0)
}

compass_direction_matcher \
    = "(" + "|".join(compass_direction_vector_map.keys()) + ")"


# Map keyed by motion verbs. Their values are percentages of movement that
# the actions might roughly equate to.  For examples, a "nudge" would
# equate to a very small percentage.
#
# The percentages are used to compute a distance in pixels that is
# relative to screen size. For example, when using a screen dimension of
# 768 pixels, the distances the motion verbs would be mapped to are:
#   nudge: ~ 4 pixels (0.0055 * 768)
#   step:  ~20        (0.025  * 768)
#   hop:   ~40        (0.05   * 768)
#   skip: ~120        (0.155  * 768)
#   jump: ~240        (0.31   * 768)
motion_distance_descriptor_percent_map: dict[str, float] = {
    "nudge": 0.0055,
    "step": 0.025,
    "hop": 0.05,
    "skip": 0.155,
    "jump": 0.31
}

motion_distance_descriptor_matcher \
    = "(" + "|".join(motion_distance_descriptor_percent_map.keys()) + ")"


# Map keyed by nicknames describing portions of evenly divided grids. The
# values are the size of the grids.
grid_descriptor_size_map: dict[str, int] = {
    "quad": 4,
    "hex": 6,
    "oct": 8,
    "nona": 9
}

grid_descriptor_matcher \
    = "(" + "|".join(grid_descriptor_size_map.keys()) + ")"



# Default setting to use to move the mouse when a distance isn't specified
mod.setting(
    "mouse_move_default_distance",
    type=int,
    default=100.0,
    desc="Default distance to move the mouse pointer (in pixels)",
)


@mod.capture(rule=f"{screen_direction_matcher}")
def screen_direction(direction: str) -> Tuple[float, float]:
    """
    Converts the given screen 'direction' to a unit vector.

    Parameters:
        direction: Screen direction (ex. up, down, left, right, upper left,
        lower right, etc.) to convert.

    Returns:
        Unit vector pointing in the given screen direction.
    """
    direction_vector = screen_direction_vector_map[str(direction)]

    return direction_vector


@mod.capture(rule=f"{clocktime_direction_matcher}")
def clocktime_direction(time: str) -> Tuple[float, float]:
    """
    Converts the given clock 'time' direction to a unit vector.

    Parameters:
        direction: Clock time direction (ex. 1 (o'clock), 2
        3, ...12) to convert

    Returns:
        Unit vector pointing in the given clock time direction.
    """

    direction_vector = clocktime_direction_vector_map[str(time)]
    return direction_vector


@mod.capture(rule=f"{compass_direction_matcher}")
def compass_direction(direction: str) -> Tuple[float, float]:
    """
    Converts the given compass 'direction' to a unit vector.

    Parameters:
        direction: Compass direction (ex. north, west, northeast,
        etc.) to convert

    Returns:
        Unit vector pointing in the given compass direction.
    """
    direction_vector = compass_direction_vector_map[str(direction)]
    return direction_vector


@mod.capture(rule=f"{motion_distance_descriptor_matcher}")
def motion_distance_descriptor(descriptor: str) -> int:
    """Converts the given motion verb 'descriptor' to a distance that the
    movement action might roughly equate to.

    Verb descriptors map to percentages (See
    'motion_distance_descriptor_percent_map').  The percentages are used to
    compute distances relative to the size of the main screen.

    For example, a "nudge" verb on a lower resolution laptop screen might
    return a very small distance such as 4 pixels.

    Parameters:
        descriptor: Motion verb (ex. nudge, step, hop, skip, jump)

    Returns:
        Number of pixels which the motion verb roughly equates to based on
        the smaller dimension (height or width) of the main screen size.
    """

    min_dim = min(ui.main_screen().height, ui.main_screen().width)

    return motion_distance_descriptor_percent_map[str(descriptor)] * min_dim


@mod.capture(rule=f"{grid_descriptor_matcher}")
def grid_descriptor(descriptor: str) -> int:
    """
    Converts a nickname descriptor describing a portion of an evenly
    divided grid to the size of the grid.

    Parameters:
        descriptor: Nickname for a portion of an evenly divided grid (ex. quad)

    Returns:
        Size of the grid that the grid descriptor is a portion of
        (ex. returns size of 4 when given the 'descriptor' value of "quad")

    """
    return grid_descriptor_size_map[str(descriptor)]



@mod.action_class
class MouseMoverActions:
    """
    Talon action class which provides functions (that can be called by
    voice commands) for moving the mouse pointer.
    """

    def mouse_move_by_direction(direction_vector: Tuple[float, ...], distance:int = None):
        """
        Moves the mouse pointer from its current position in the
        direction of the given 'direction_vector' by the the given
        'distance' measured in pixels.  If no distance is given, then the
        'mouse_move_default_distance' setting value is used.

        Parameters:
            direction_vector:
                Unit vector describing the direction to move the mouse pointer.
            distance:
                Distance in pixels to move the mouse pointer.
        Raises:
            TypeError: If 'direction_vector' is not a Tuple[float, float]
            ValueError If 'distance' is <= 0
        """
        # if direction_vector is not of type Tuple
        if not isinstance(direction_vector, Tuple):
            raise TypeError(
                (f"mouse_move_by_direction(): Invalid argument type for direction vector,"
                 f"{type(direction_vector)}, encountered."))

        if distance is None:
            distance = settings.get("user.mouse_move_default_distance")
        elif distance <= 0:
            raise ValueError(
                f"mouse_move_by_direction(): Distance, {distance} cannot be zero or negative.")
        curr_mouse_pos = ctrl.mouse_pos()
        new_mouse_pos = (curr_mouse_pos[0] + direction_vector[0] * distance,
                         curr_mouse_pos[1] + direction_vector[1] * distance)
        ctrl.mouse_move(new_mouse_pos[0], new_mouse_pos[1])
        # TODO: figure out best way to clear the old mouse point image.
        # For now, use user.mouse_show_cursor()  in .talon file as workaround.

    def mouse_move_by_grid_index(grid_size: int, index:int):
        """Moves the mouse pointer to the center of the nth cell of a grid
        of the main screen where n is the given 'index' and the grid is
        virtual (not drawn) and is evenly divided into 'grid_size' number
        of cells.

        For example, a 'grid_size' of 4 and an 'index' value of 3 would
        result in moving of the mouse pointer to the center of the lower
        left quadrant of the main screen.

        For 'grid_size' values such as 8 which would produce a non-square
        grid, the virtual grid orientation that is used is the one that
        best matches the orientation of the screen.  For example, a grid of
        size 8 for a landscape screen, would layout the virtual grid as a
        2 x 4 (2 rows, 4 col).

        Parameters:
            grid_size:
                The total number of cells in the virtual (not actually
                drawn) grid of the screen.

            index: One-based index of the cell to move to the center
                of. Indexes are numbered from left to right, and top to
                bottom.

        Raises:
            ValueError: if 'grid_size' is not one of the values. Supported
            values include: 4, 6, 8, and 9.

            IndexError: if 'index' is < 1 or > 'grid_size'.
        """

        if (index > grid_size):
           raise IndexError(
               f"mouse_move_by_grid_index(): Given 'index', {index}, cannot be greater than the 'grid_size', {grid_size}.")
        if (index < 1):
           raise IndexError(
               f"mouse_move_by_grid_index(): Given 'index', {index}, cannot be less than 1.")

        screen_height = ui.main_screen().height
        screen_width = ui.main_screen().width

        screen_orientation = "landscape" if screen_width > screen_width else "portrait"

        if (grid_size == 4):
            grid_dim = (2, 2)
        elif (grid_size == 6):
            grid_dim = (3, 2) if screen_orientation == "landscape" else (2, 3)
        elif (grid_size == 8):
            grid_dim = (4, 2) if screen_orientation == "landscape" else (2, 4)
        elif (grid_size == 9):
            grid_dim = (3, 3)
        else:
            raise ValueError(
                f"mouse_move_by_grid_index(): Unsupported grid size, {grid_size}, encountered.")

        grid_index = index - 1
        grid_num_rows = grid_dim[0]
        grid_num_cols = grid_dim[1]

        cell_height = (int)(ui.main_screen().height / grid_num_rows)
        cell_width = (int)(ui.main_screen().width / grid_num_cols)

        grid_row_index = (int)((grid_index) / grid_num_cols)
        grid_col_index = (int)((grid_index) % grid_num_cols)

        y = (grid_row_index * cell_height) + (cell_height / 2)
        x = (grid_col_index * cell_width) + (cell_width / 2)

        ctrl.mouse_move(x, y)

        # TODO: figure out best way to clear the old mouse pointer image.
        # For now, use user.mouse_show_cursor()  in .talon file as workaround.

