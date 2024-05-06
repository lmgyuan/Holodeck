import json
import os

from langchain.llms import OpenAI
from langchain import PromptTemplate
from modules.utils import get_top_down_frame


class object_identifier():
    def __init__(self, openai_api_key, objaverse_version, objaverse_asset_dir, single_room, scene):
        self.llm = OpenAI(model_name="gpt-4-1106-preview", max_tokens=2048)
        self.llm_fast = OpenAI(model_name="gpt-3.5-turbo", max_tokens=2048)
        self.scene = scene
        self.objaverse_asset_dir = objaverse_asset_dir

        os.environ["OPENAI_API_KEY"] = openai_api_key

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

        print("--------------------")
        print("objects: ")
        print(objects)
        print("--------------------")


        json_object_identify_prompt = """
        You are an experienced object identifier. 
        Please assist me in identifying the object in the scene. 
        You need to find the object in the scene and provide the object's information in its original json format.
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
        If you think there are multiple matching objects, you can return a list of them, separated by commas.
        The output should look like: "assetId: asset code,assetId: asset code,assetId: asset code"
        
        Your response should be direct and without additional text at the beginning or end.
        """

        json_object_identify_prompt_template = PromptTemplate(input_variables=["object", "location", "objects"],
                                                              template=json_object_identify_prompt)
        json_object = json.dumps(object_identify_response[0])
        json_location = json.dumps(object_identify_response[1])
        json_objects = json.dumps(objects)
        template = json_object_identify_prompt_template.format(object=json_object, location=json_location, objects=json_objects)
        llm_output = self.llm(template)
        # json_object_identify_response = json.loads(llm_output)

        print("--------------------")
        print(llm_output)
        print("--------------------")
        # print(json_object_identify_response)
        # print("--------------------")

        #Parse the llm output:
        assetID_to_delete = llm_output.split(",")[0].strip()
        assetID_to_delete = assetID_to_delete.split(":")[1].strip()

        print("--------------------")
        print("Asset ID to delete: ", assetID_to_delete)
        print("--------------------")

        filtered_objects = [obj for obj in objects if obj['assetId'] != assetID_to_delete.strip()]
        match_object = [obj for obj in objects if obj['assetId'] == assetID_to_delete.strip()]

        print("--------------------")
        print("Match Object: ", match_object)
        print("--------------------")

        self.scene["objects"] = filtered_objects
        top_image = get_top_down_frame(self.scene, self.objaverse_asset_dir, 1024, 1024)
        top_image.show()
        top_image.save("top_down_frame_deletion.png")

        return self.scene
