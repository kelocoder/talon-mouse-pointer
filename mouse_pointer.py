"""
Talon voice module which supports relative mouse pointer movements.

Currently these include movements in radial directions relative to the
current mouse pointer position. For example:
- Moving the mouse pointer up (100 pixels)
- Moving the mouse pointer 25 pixels towards the direction of 8 o'clock
- Moving the mouse pointer 70 pixels northeast
- Nudging the mouse pointer left a few pixels

"""
from typing import Tuple
from talon import Module, settings, ctrl, ui

mod = Module()

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
    # MAYBE: handle more granular times like one thirty if useful
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


# Default setting to use to move the mouse when a distance isn't specified
mod.setting(
    "mouse_move_default_distance",
    type=int,
    default=100,
    desc="Default distance to move the mouse pointer",
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
