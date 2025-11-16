#- OVERVIEW
#
# Talon Voice module which supports relative mouse pointer movements.
#
# Currently these include movements in radial directions relative to the
# current mouse pointer position.

-

#- SETTINGS

# settings():
#     user.mouse_move_default_distance = 100

#- VOICE COMMANDS

#-- Move using Screen Directions

# Example: roam up
roam <user.screen_direction>:
    user.mouse_move_by_direction(user.screen_direction)
    # TODO: using user.mouse_show_cursor() for now to clear old pointer image
    user.mouse_show_cursor()

# Example: roam left 50 pixels
roam <user.screen_direction> ([<number> [pixels]]):
    user.mouse_move_by_direction(user.screen_direction, number)
    user.mouse_show_cursor()


#-- Move using Nudge, Step, Hop, Skip, Jump and Screen Directions

# Example: nudge right
# Example: step up
# Example: jump left
<user.motion_distance_descriptor> <user.screen_direction>:
    user.mouse_move_by_direction(user.screen_direction, user.motion_distance_descriptor)
    user.mouse_show_cursor()


#-- Move using Clock Time Directions

# Example: roam 2 o'clock
roam <user.clocktime_direction> o'clock:
    user.mouse_move_by_direction(user.clocktime_direction)
    user.mouse_show_cursor()

# Example: roam 7 o'clock 35 pixels
roam <user.clocktime_direction> o'clock ([<number> [pixels]]):
    user.mouse_move_by_direction(user.clocktime_direction, number)
    user.mouse_show_cursor()


#-- Move using Compass Directions

# Example: roam northeast
roam <user.compass_direction>:
    user.mouse_move_by_direction(user.compass_direction)
    user.mouse_show_cursor()

# Example: roam south 15 pixels
roam <user.compass_direction> ([<number> [pixels]]):
    user.mouse_move_by_direction(user.compass_direction, number)
    user.mouse_show_cursor()

