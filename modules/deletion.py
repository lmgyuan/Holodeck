import datetime
import json
import os

from langchain.llms import OpenAI
from langchain import PromptTemplate
from modules.utils import get_top_down_frame


class deletion():
    def __init__(self, openai_api_key, objaverse_asset_dir, save_dir_deletion, folder_name_deletion):
        create_time = str(datetime.datetime.now()).replace(" ", "-").replace(":", "-").replace(".", "-")

        self.llm = OpenAI(model_name="gpt-4-1106-preview", max_tokens=2048, temperature=0.1)
        self.llm_fast = OpenAI(model_name="gpt-3.5-turbo", max_tokens=2048)
        self.objaverse_asset_dir = objaverse_asset_dir
        self.scene_objects = []
        self.scene = {}
        self.save_dir_deletion = save_dir_deletion
        self.folder_name_deletion = f"{folder_name_deletion}-{create_time}"
        self.first_query = ""

        os.environ["OPENAI_API_KEY"] = openai_api_key
        os.mkdir(f"{self.save_dir_deletion}/{self.folder_name_deletion}")

    def delete_first_step(self, first_query, scene):
        self.scene = scene
        self.first_query = first_query

        object_identify_response = self.parse_to_object(self.first_query)

    def delete_second_step(self, assetID_confirmed):
        final_scene = self.delete(assetID_confirmed)
        final_scene_name = self.first_query.replace(" ", "_").replace("'", "")
        final_scene_name = f"{final_scene_name}-delete_{assetID_confirmed}"
        with open(f"{self.save_dir_deletion}/{self.folder_name_deletion}/{final_scene_name}.json", "w") as f:
            json.dump(final_scene, f, indent=4)
        final_scene_image = get_top_down_frame(final_scene, self.objaverse_asset_dir)
        final_scene_image.show()
        final_scene_image.save(f"{self.save_dir_deletion}/{self.folder_name_deletion}/{final_scene_name}.png")

    def delete(self, assetID_to_delete):
        objects = self.scene["objects"]
        for obj in objects:
            if obj["assetId"] == assetID_to_delete:
                objects.remove(obj)
                break

        self.scene["objects"] = objects
        return self.scene

    def parse_to_object(self, user_input):
        object_identify_prompt = """
        You are an experienced sentence parser and object identifier. 
        Please assist me in reading a descriptive sentence into the object and finding its objects: 

        For example: 
        'delete the red chair in the living room' should be 'red chair,living room'
        'get rid of the table in the kitchen' should be 'table,kitchen'
        'remove the bed in the bedroom' should be 'bed,bedroom'

        Now, I want to parse: {input}
        Your response should be direct and without additional text at the beginning or end."""

        object_identify_prompt_templat = PromptTemplate(input_variables=["input"],
                                                        template=object_identify_prompt)
        template = object_identify_prompt_templat.format(input=user_input)
        object_identify_response = self.llm(template)

        return object_identify_response

    def identify_object(self, user_input):
        object_identify_response = self.parse_to_object(user_input)
        object_identify_response = object_identify_response.split(",")
        print("--------------------")
        print(object_identify_response)
        print("object: " + object_identify_response[0])
        print("location: " + object_identify_response[1])
        print("--------------------")

        objects = self.scene["objects"]
        self.scene_objects = objects

        print("--------------------")
        print("objects: ")
        print(objects)
        print("--------------------")

        json_object_identify_prompt = """
        You are an experienced object identifier. 
        Please assist me in identifying the objects in the scene. 
        You need to find three objects in the scene and provide the objects' assetID.
        You will be given a list of json objects, each of which is like this: 
        {{
            "assetId": ID of an object,
            "id": Descriptive ID of an object,
            "kinematic": "True" or "False",
            "position": {{
                "x": ,
                "y": ,
                "z": 
            }},
            "rotation": {{
                "x": ,
                "y": ,
                "z": 
            }},
            "material": the material of the object,
            "roomId": where the object is located,
            "layer": the render layer of the object in the scene,
        }}

        Your job is to find the one that matches the description. You will have two inputs, "object" and "location". 
        For example, if the "object" is a book and the "location" is living room, you should find the object that is a book in the living room:
        {{
            "assetId": "158b8078af03494b9e4f51664b7848fc",
            "id": "book-4|bookcase-0 (living room)",
            "kinematic": false,
            "position": {{
                "x": 0.12154440581798553,
                "y": 2.1542962076454644,
                "z": 6.849490642547607
            }},
            "rotation": {{
                "x": -0.0,
                "y": 3,
                "z": -0.0
            }},
            "material": null,
            "roomId": "living room",
            "layer": "Procedural0"
        }}

        Currently, the object we want to find is: {object}, and its location is {location}.
        The list of objects in the scene is: {objects}
        Beware that the object and location may not perfectly match the descriptions in the list of objects. 
        If you can't find exact matches, find synonym and other variations.
        Don't modify the object's information. Just return the assetID of the original json object in the list.
        You have to find three and only three most relevant objects in the scene. Even if you think there are only one or two objects that match the description, you still need to find three objects. They also have to be distinct.
        Return a list of them, separated by commas.
        The output should look like: "asset_code,asset_code,asset_code", where asset_code is the assetId of the object.

        Your response should be direct and without additional text at the beginning or end.
        """

        json_object_identify_prompt_template = PromptTemplate(input_variables=["object", "location", "objects"],
                                                              template=json_object_identify_prompt)
        json_object = json.dumps(object_identify_response[0])
        json_location = json.dumps(object_identify_response[1])
        json_objects = json.dumps(objects)
        template = json_object_identify_prompt_template.format(object=json_object, location=json_location,
                                                               objects=json_objects)
        llm_output = self.llm(template)
        # json_object_identify_response = json.loads(llm_output)

        print("--------------------")
        print("llm output: ", llm_output)
        print("--------------------")

        list_of_asset_ids = []

        # Parse the llm output:
        for assetID in llm_output.split(","):
            assetID = assetID.strip()
            print("Asset ID to choose from: ", assetID)
            image_path = self.visualize_asset(assetID, self.objaverse_asset_dir)
            list_of_asset_ids.append((assetID, image_path))

        return list_of_asset_ids



    def visualize_asset(self, asset_id, version):
        # empty_house = json.load(open("empty_house.json", "r"))
        file_name_deletion = asset_id.replace(" ", "_").replace("'", "")

        empty_house = json.load(open("/Users/yuanyuan/workspace/Holodeck/modules/empty_house.json", "r"))
        empty_house["objects"] = [{
            "assetId": asset_id,
            "id": "test_asset",
            "kinematic": True,
            "position": {
                "x": 0,
                "y": 0,
                "z": 0
            },
            "rotation": {
                "x": 0,
                "y": 0,
                "z": 0
            },
            "material": None
        }]
        image = get_top_down_frame(empty_house, version)
        image.show()
        image_path = f"{self.save_dir_deletion}/{self.folder_name_deletion}/{file_name_deletion}.png"
        image.save(image_path)
        return image_path
