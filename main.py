import ast
import json
from tqdm import tqdm
from argparse import ArgumentParser
from modules.holodeck import Holodeck
import modules.object_identifier as object_identifier
from modules.utils import get_top_down_frame
from modules.deletion import deletion

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
    # added for continuous generation
    parser.add_argument("--allow_edit", help = "Whether to allow edit the scene", default = "False")
    parser.add_argument("--allow_delete", help="Whether to allow delete the scene", default= "False")

    args = parser.parse_args()

    args.model = Holodeck(args.openai_api_key, args.objaverse_version, args.asset_dir, ast.literal_eval(args.single_room))

    # if args.used_assets != [] and args.used_assets.endswith(".txt"):
    #     with open(args.used_assets, "r") as f:
    #         args.used_assets = f.readlines()
    #         args.used_assets = [asset.strip() for asset in args.used_assets]
    # else:
    #     args.used_assets = []
    #
    # if args.mode == "generate_single_scene":
    #     generate_single_scene(args)
    #
    # elif args.mode == "generate_multi_scenes":
    #     generate_multi_scenes(args)
    #
    # elif args.mode == "generate_variants":
    #     generate_variants(args)

    if args.allow_edit == "True":
        user_input = input("Please enter what edit you want: add, modify, or delete:").strip()
        if user_input == "add":
            user_input = input("Please enter the asset you want to add:")
            args.original_scene = args.save_dir + "/" + args.query.replace(" ", "_").replace("'", "") + "/" + args.query.replace(" ", "_").replace("'", "") + ".json"
            args.query = args.query + "add" + user_input
            generate_single_scene(args)


    # Test deleting a couch from the scene
    if args.allow_delete == "True":
        # scene_to_edit = json.load(open("/Users/yuanyuan/workspace/Holodeck/data/scenes/a_living_room-2024-04-18-14-06-36-338216/a_living_room.json", "r"))
        # user_input = "delete the couch in the living room"

        scene_to_edit = json.load(open(
            "/Users/yuanyuan/workspace/Holodeck/data/scenes/a_living_room_with_blue_walls-2024-04-16-16-17-57-462309/a_living_room_with_blue_walls.json",
            "r"))
        user_input = "delete the couch in the living room"

        # scene_to_edit = json.load(open(
        #     "/Users/yuanyuan/workspace/Holodeck/data/scenes/a_small_conference_room-2023-12-09-22-38-58-210944/a_small_conference_room.json",
        #     "r"))
        # user_input = "delete a shelve in the living room"
        save_dir_deletion = "./data/deletion"
        folder_name_deletion = user_input.replace(" ", "_").replace("'", "")
        print("user_input: ", user_input)
        deletion = deletion(args.openai_api_key, args.asset_dir, save_dir_deletion, folder_name_deletion)
        deletion.delete_first_step(user_input, scene_to_edit)
        updated_scene_deletions = deletion.identify_object(user_input)
        for image in updated_scene_deletions:
            assetID = image[0]
            image_path = image[1]
            print("assetID: ", assetID, "; image_path: ", image_path)

        deletion.delete_second_step(updated_scene_deletions[0][0])
        # top_image = get_top_down_frame(updated_scene_deletion, args.asset_dir)









