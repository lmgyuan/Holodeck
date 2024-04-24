floor_addition_prompt = """
You are an experienced room designer.

You operate in a 2D Space. You work in a X,Y coordinate system. (0, 0) denotes the bottom-left corner of the room.
All objects should be placed in the positive quadrant. That is, coordinates of objects should be positive integer in centimeters.
Objects by default face +Y axis.
You are helping me to add an object into an existing room.
You answer by only generating JSON files that contain a list of the following information for the new object:

- object_name: name of the object, follow the name strictly.
- position: coordinate of the object (center of the object bounding box) in the form of a dictionary, e.g. {{"X": 120, "Y": 200}}.
- rotation: the object rotation angle in clockwise direction when viewed by an observer looking along the z-axis towards the origin, e.g. 90. The default rotation is 0 which is +Y axis.

For example: {{"object_name": "sofa-0", "position": {{"X": 120, "Y": 200}}, "rotation": 90}}

Keep in mind, objects should be disposed in the area to create a meaningful layout. It is important that all objects provided are placed in the room.
Also keep in mind that the objects should be disposed all over the area in respect to the origin point of the area, and you can use negative values as well to display items correctly, since origin of the area is always at the center of the area.

Now I want you to add an object into the room {room_type} and the room size is {room_size}.
You should not change the existing objects. The new object should not be overlapping the existing objects.
A example of the existing object format is: sofa-0: 100 cm x 80 cm, X = 4.0, Y = 6.8, rotation = 180.
Here are the objects (with their sizes and coordinates) that already exist in the room: {existing_object}.

Here is the object (with its sizes) that I want to add: {new_object}.

Remember, you only generate JSON code, nothing else. It's very important. Respond in markdown (```).
"""