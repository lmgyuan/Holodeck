
import os
from getpass import getpass
from holodeck_extended import *

import ast
from argparse import ArgumentParser
from modules.holodeck import Holodeck

import ast
import json
from argparse import ArgumentParser
from modules.holodeck import Holodeck
import os
from langchain.llms import OpenAI
from modules.utils import get_top_down_frame

from modules.deletion import deletion


def loop(args):

    scene_path = "./data/scenes/a_living_room-2024-05-06-20-30-34-288761/a_living_room.json"

    # scene = generate_single_scene(args)
    scene =  scene = json.load(open(scene_path, "r"))

    while True:

        usr_input = input("Would you like to add or delete any object? Choose add, delete, or quit editing: ")
        
        # response = client.chat.completions.create(
        # model="gpt-4",
        # messages=[
        #     {
        #     "role": "system",
        #     "content": """
        #     You are helping a system to identify which mode the user chose.
        #     The mode could be delete, add, or quit.
        #     Output only one string, it could be delete, add, or quit.
        #     Make sure the output is only one word in lowercase that can be identified by a Python program.
        #     If the user inputs No Edit, it is likely to be quit.
        #     """
        #     },
        #     {
        #     "role": "user",
        #     "content": usr_input
        #     }
        # ],
        # temperature=0.25,
        # max_tokens=256,
        # top_p=1,
        # frequency_penalty=0,
        # presence_penalty=0
        # )

        # mode = response.choices[0].message.content.lowercase().strip()

        if usr_input == "add":
            scene_new = add_object(scene, args.model, client)
            top_image = get_top_down_frame(scene_new, args.model.objaverse_asset_dir, 1024, 1024)
            top_image.show()
            top_image.save(f"added.png")
            scene = scene_new
        elif usr_input == "delete":
            save_dir_deletion = "./data/deletion"
            user_input = input("Would you like to delete anything from the scene? ")
            folder_name_deletion = user_input.replace(" ", "_").replace("'", "")
            dlt = deletion(args.openai_api_key, args.asset_dir, save_dir_deletion, folder_name_deletion)
            dlt.delete_first_step(user_input, scene)
            updated_scene_deletions = dlt.identify_object(user_input)
            for image in updated_scene_deletions:
                assetID = image[0]
                image_path = image[1]
                print("assetID: ", assetID, "; image_path: ", image_path)
            scene_new = dlt.delete_second_step(updated_scene_deletions[0][0])
            scene = scene_new
        else:
            print("Quit Editing.")
            break

if __name__ == "__main__":
    # if 'OPENAI_API_KEY' not in os.environ:
    #     print("You didn't set your OPENAI_API_KEY on the command line.")
    #     os.environ['OPENAI_API_KEY'] = getpass("Please enter your OpenAI API Key: ")

    ## holodeck_extended main
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

    os.environ['OPENAI_API_KEY'] = args.openai_api_key
    client = OpenAI(model_name="gpt-4-1106-preview", max_tokens=2048)

    args.model = Holodeck(args.openai_api_key, args.objaverse_version, args.asset_dir, ast.literal_eval(args.single_room))
    
    loop(args)

    
