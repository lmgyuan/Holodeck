import json
import os

from langchain.llms import OpenAI
from langchain import PromptTemplate
import modules.utils


class object_identifier():
    def __init__(self, openai_api_key, objaverse_version, objaverse_asset_dir, single_room, scene):
        self.llm = OpenAI(model_name="gpt-4-1106-preview", max_tokens=2048)
        self.llm_fast = OpenAI(model_name="gpt-3.5-turbo", max_tokens=2048)
        self.scene = scene

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
        small_objects = self.scene["small_objects"]

        print("--------------------")
        print("objects: ")
        print(objects)
        print("--------------------")
        print("small_objects: ")
        print(small_objects)


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
        Your response should be direct and without additional text at the beginning or end.
        """

        json_object_identify_prompt_template = PromptTemplate(input_variables=["object", "location"],
                                                              template=json_object_identify_prompt)
        json_object = json.dumps(object_identify_response[0])
        json_location = object_identify_response[1]
        template = json_object_identify_prompt_template.format(object=json_object, location=json_location)
        json_object_identify_response = json.loads(self.llm(template))

        print("--------------------")
        print(json_object_identify_response)
        print("--------------------")
        return object_identify_response
