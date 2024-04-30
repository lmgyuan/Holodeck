import ast
import json
from tqdm import tqdm
from argparse import ArgumentParser
from modules.holodeck import Holodeck
import os
from langchain.llms import OpenAI
import parsing_prompt as pp
from modules.utils import get_top_down_frame
import yw_prompt as prompts
from langchain import PromptTemplate
import re

def generate_single_scene(args):
    folder_name = args.query.replace(" ", "_").replace("'", "")
    try:
        if args.original_scene is not None:
            scene = json.load(open(args.original_scene, "r"))
            print(f"Loading exist scene from {args.original_scene}.")
        else:
            scene = json.load(open(f"data/scenes/{folder_name}/{folder_name}.json", "r"))
            print(f"Loading exist scene from data/scenes/{folder_name}/{folder_name}.json.")
    except:
        scene = args.model.get_empty_scene()
        print("Generating from an empty scene.")

    args.model.generate_scene(
        scene=scene,
        query=args.query,
        save_dir=args.save_dir,
        used_assets=args.used_assets,
        generate_image=ast.literal_eval(args.generate_image),
        generate_video=ast.literal_eval(args.generate_video),
        add_ceiling=ast.literal_eval(args.add_ceiling),
        add_time=ast.literal_eval(args.add_time),
        use_constraint=ast.literal_eval(args.use_constraint),
        use_milp=ast.literal_eval(args.use_milp),
        random_selection=ast.literal_eval(args.random_selection)
    )


def generate_multi_scenes(args):
    with open(args.query_file, "r") as f:
        queries = f.readlines()
        queries = [query.strip() for query in queries]
    
    for query in tqdm(queries):
        args.query = query
        generate_single_scene(args)


def generate_variants(args):
    try: original_scene = json.load(open(args.original_scene, "r"))
    except: raise Exception(f"Could not load original scene from {args.original_scene}.")
    try:
        args.model.generate_variants(
            query=args.query,
            original_scene=original_scene,
            save_dir=args.save_dir,
            number_of_variants=int(args.number_of_variants),
            used_assets=args.used_assets,
        )
    except:
        print(f"Could not generate variants from {args.query}.")

# 7000 Project code START
def delete_object(scene):
    # Delete an object
    user_input = input("Do you want to remove some of the objects? \n")
    # Parse user input into a list of object names

    # For each object:
        # Identify which object the user is referring to

        # Show potential objects to the user
    
        # Get user to identify each object
    
        # Delete from json

        # Show new room to user to verify
    
    # dump final json

def object_parser(llm_client, user_word):
    baseline_temp = PromptTemplate(input_variables=["user_input"], template=prompts.object_parsing_prompt)
    baseline_prompt = baseline_temp.format(user_input=user_word)
    return llm_client(baseline_prompt)

def parse_existing_floor(scene, model, room_id):
    object_list = scene["floor_objects"]
    object_information = ""
    for obj in object_list:
        if (obj["roomId"]) == room_id:
            # Object in that room
            object_name = obj["object_name"]
            coor_x = obj["position"]["x"] * 100
            coor_z = obj["position"]["z"] * 100
            dimension = model.floor_object_generator.database[obj["assetId"]]['assetMetadata']['boundingBox']
            size_x = int(dimension["x"] * 100)
            size_z = int(dimension["z"] * 100)
            rot = obj["rotation"]["y"]
            object_information += f"{object_name}: {size_x} cm x {size_z} cm, X = {coor_x}, Y = {coor_z}, rotation = {rot}\n"
    return object_information

def parse_room_layer(scene, model, room_id):
    obj = scene["floor_objects"][0]
    return obj["layer"]
    

def add_object(scene, model, llm_client):
    rooms_types = [room["roomType"] for room in scene["rooms"]]
    room2area = {room["roomType"]: model.object_selector.get_room_area(room) for room in scene["rooms"]}
    room2size = {room["roomType"]: model.object_selector.get_room_size(room, scene["wall_height"]) for room in scene["rooms"]}
    room2perimeter = {room["roomType"]: model.object_selector.get_room_perimeter(room) for room in scene["rooms"]}
    room2vertices = {room["roomType"]: [(x * 100, y * 100) for (x, y) in room["vertices"]] for room in scene["rooms"]}

    room2floor_capacity = {room_type: [room_area * model.object_selector.floor_capacity_ratio, 0] for room_type, room_area in room2area.items()}
    room2floor_capacity = model.object_selector.update_floor_capacity(room2floor_capacity, scene)
    room2wall_capacity = {room_type: [room_perimeter * model.object_selector.wall_capacity_ratio, 0] for room_type, room_perimeter in room2perimeter.items()}

    # Add an object
    user_input = input("Do you want to add any objects? Please specify quantity of objects. Please be as specific as possible with your description. \n")
    # Parse user input into (quantity, object_name, object_description)
    object_str = object_parser(llm_client, user_input)
    object_list = object_str.split(";")

    # For each object:
    for oo_str in object_list:
        oo_str = oo_str.replace("(","",-1).replace(")","",-1)
        quantity, oo, descriptions = oo_str.split(",")
        quantity = int(quantity)

        # Input user prompt to object generation module
        my_query = f"a 3D model of a {oo}, {descriptions}"
        candidates = model.object_retriever.retrieve([my_query], threshold=28)

        # Prompt user to specify room
        room_all_str = ", ".join(rooms_types)
        pos_input = input(f"In this scene, I have the following rooms: {room_all_str}. Which room do you want to place the object in? Please just specify the full room name. \n")
        # Parse pos_input into room_type
        for rr in rooms_types:
            if (pos_input.find(rr) != -1):
                # Found!
                room_type = rr

        print(f"Placing object in {room_type}.")

        # TODO: parse position
        pos = "floor"

        if (pos == "floor"):
            # check on floor objects
            candidates = [candidate for candidate in candidates if model.object_selector.database[candidate[0]]["annotations"]["onFloor"] == True] # only select objects on the floor
            candidates = [candidate for candidate in candidates if model.object_selector.database[candidate[0]]["annotations"]["onCeiling"] == False] # only select objects not on the ceiling
            
            # ignore doors and windows and frames
            candidates = [candidate for candidate in candidates if "door" not in model.object_selector.database[candidate[0]]["annotations"]["category"].lower()]
            candidates = [candidate for candidate in candidates if "window" not in model.object_selector.database[candidate[0]]["annotations"]["category"].lower()]
            candidates = [candidate for candidate in candidates if "frame" not in model.object_selector.database[candidate[0]]["annotations"]["category"].lower()]

            # check if the object is too big
            room_size = room2size[room_type], 
            room_vertices = room2vertices[room_type]
            candidates = model.object_selector.check_object_size(candidates, room_size[0])

            # check if object can be placed on the floor
            candidates = model.object_selector.check_floor_placement(candidates[:20], room_vertices, scene)

            # No candidates found
            if len(candidates) == 0: print("No candidates found for {} {}".format(oo, descriptions))
            
            # TODO: Need to prompt user for more info!

            candidates = candidates[:10] # only select top 10 candidates

            # TODO: Show user to select?
            selected_candidate = candidates[0]
            selected_asset_id = selected_candidate[0]
            # TODO: Parse quantity
            quantity = 1
            selected_asset_ids = [selected_asset_id] * quantity
            
            add_candidates = []
            for i in range(quantity):
                selected_asset_id = selected_asset_ids[i]
                object_name = f"{oo}-{i}"
                add_candidates.append((object_name, selected_asset_id))

            # print(add_candidates)


            # Get existing objects and their size, coordinates, and rotation
            existing = parse_existing_floor(scene, args.model, room_type)
            object_information = ""
            baseline_temp = PromptTemplate(input_variables=["room_type", "room_size", "existing_object", "new_object"], template=prompts.floor_addition_prompt)
            # Get origin of the room
            room_origin = [min(v[0] / 100 for v in room_vertices), min(v[1] / 100 for v in room_vertices)]
            # Get room layer
            room_layer = parse_room_layer(scene, args.model, room_type)
            # For each candidate, prompt llm to get its placement
            for obj_name, a_id in add_candidates:
                # Prepare 
                dimension = model.floor_object_generator.database[a_id]['assetMetadata']['boundingBox']
                size_x = int(dimension["x"] * 100)
                size_z = int(dimension["z"] * 100)
                object_information += f"{obj_name}: {size_x} cm x {size_z} cm\n"
                baseline_prompt = baseline_temp.format(room_type=room_type, room_size=room_size[0], existing_object=existing, new_object=object_information)

                # Prompt llm
                completion_text = model.llm(baseline_prompt)

                # Parse the response into json
                completion_text = re.findall(r'```(.*?)```', completion_text, re.DOTALL)[0]
                completion_text = re.sub(r'^json', '', completion_text, flags=re.MULTILINE)
                data_tmp = json.loads(completion_text)

                # Standardize the json 
                placement = model.floor_object_generator.json_template.copy()
                placement["id"] = f"{obj_name} ({room_type})"
                placement["object_name"] = obj_name
                placement["assetId"] = a_id
                placement["roomId"] = room_type
                placement["position"] = {"x": room_origin[0] + (data_tmp['position']["X"]/100),
                                            "y": dimension["y"] / 2,
                                            "z": room_origin[1] + (data_tmp["position"]["Y"]/100)}
                placement["rotation"] = {"x": 0, "y": data_tmp["rotation"], "z": 0}
                # layer will just be the room's layer
                placement["layer"] = room_layer

                print(placement)

                # Add into scene
                scene["objects"].append(placement)
                # print(placement)


        elif (pos == "wall"):
            print("TODO")


    return scene

# 7000 Project code END
    
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--mode", help = "Mode to run in (generate_single_scene, generate_multi_scenes or generate_variants).", default = "generate_single_scene")
    parser.add_argument("--query", help = "Query to generate scene from.", default = "a living room")
    parser.add_argument("--query_file", help = "File to load queries from.", default = "./data/queries.txt")
    parser.add_argument("--number_of_variants", help = "Number of variants to generate.", default = 5)
    parser.add_argument("--original_scene", help = "Original scene to generate variants from.", default = None)
    parser.add_argument("--openai_api_key", help = "OpenAI API key.", default = None)
    parser.add_argument("--objaverse_version", help = "Version of objaverse to use.", default = "09_23_combine_scale")
    parser.add_argument("--asset_dir", help = "Directory to load assets from.", default = "./data/objaverse_holodeck/09_23_combine_scale/processed_2023_09_23_combine_scale")
    parser.add_argument("--save_dir", help = "Directory to save scene to.", default = "./data/scenes")
    parser.add_argument("--generate_image", help = "Whether to generate an image of the scene.", default = "True")
    parser.add_argument("--generate_video", help = "Whether to generate a video of the scene.", default = "False")
    parser.add_argument("--add_ceiling", help = "Whether to add a ceiling to the scene.", default = "False")
    parser.add_argument("--add_time", help = "Whether to add the time to the scene name.", default = "True")
    parser.add_argument("--use_constraint", help = "Whether to use constraints.", default = "True")
    parser.add_argument("--use_milp", help = "Whether to use mixed integer linear programming for the constraint satisfaction solver.", default = "False")
    parser.add_argument("--random_selection", help = "Whether to more random object selection, set to False will be more precise, True will be more diverse", default = "False")
    parser.add_argument("--used_assets", help = "a list of assets which we want to exclude from the scene", default = [])
    parser.add_argument("--single_room", help = "Whether to generate a single room scene.", default = "False")
    
    args = parser.parse_args()

    args.model = Holodeck(args.openai_api_key, args.objaverse_version, args.asset_dir, ast.literal_eval(args.single_room))

    # if args.used_assets != [] and args.used_assets.endswith(".txt"):
    #     with open(args.used_assets, "r") as f:
    #         args.used_assets = f.readlines()
    #         args.used_assets = [asset.strip() for asset in args.used_assets]
    # else:
    #     args.used_assets = []
    
    # if args.mode == "generate_single_scene":
    #     generate_single_scene(args)
    
    # elif args.mode == "generate_multi_scenes":
    #     generate_multi_scenes(args)
    
    # elif args.mode == "generate_variants":
    #     generate_variants(args)


    # 7000 Project code START
    os.environ['OPENAI_API_KEY'] = args.openai_api_key
    client = OpenAI(model_name="gpt-4-1106-preview", max_tokens=2048)
    # client = OpenAI(model_name="gpt-3.5-turbo", max_tokens=2048)

    # Load json back in
    original_scene = "./data/scenes/a_living_room_with_blue_walls_-2024-04-09-13-51-46-376192/a_living_room_with_blue_walls_.json"
    scene = json.load(open(original_scene, "r"))
    print(f"Loading exist scene from {original_scene}.")

    scene_new = add_object(scene, args.model, client)

    # top_image = get_top_down_frame(scene_new, args.model.objaverse_asset_dir, 1024, 1024)
    # top_image.show()
    # top_image.save(f"tmpppp.png")
    

    
    




        
        