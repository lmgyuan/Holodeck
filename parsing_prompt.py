from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate

parse_prompt = """You are an efficient translator of user inputs into accurate lists of just the objects and their descriptions, including things like location or mood. Apply each descriptive and location-based word (like color or theme) on as many objects as is applicable as possible. You need to define the four coordinates and specify an appropriate design scheme, including each room's color, material, and texture.
For example:
I want a cozy room where everything is red, with a king-sized bed, a bright lamp, three chairs, two windows, and a floor-to-ceiling door. is equal to: a cozy red room, a king-sized cozy red bed, a bright cozy red lamp, three cozy red chairs, two cozy red windows, a cozy red floor-to-ceiling door
I want a space-themed children's bedroom where there are 3 astronaut lamps, 2 twin-sized beds with planet-blankets, filled with various sized toys. is equal to: a space-themed children's bedroom, three space-themed astronaut lamps, two space-themed twin-sized beds with planet-blankets, various sized space-themed toys

Now, come up with the list that is equal to {input}.
Your response should be direct and without additional text at the beginning or end."""


parse_prompt1 = """You are an efficient translator of user inputs into accurate lists of just the objects and their descriptions, including things like location or mood. Apply each descriptive and location-based word (like color or theme) on as many objects as is applicable as possible. You need to define the four coordinates and specify an appropriate design scheme, including each room's color, material, and texture.
For example:
If the requirement is: Maybe a red lamp that gives out cozy vibe is good.
You should reply: a bright cozy red lamp

If the requirement is: I want to add in three chairs. They should be grey. Maybe they should be comfortable.
You should reply: three comfortable grey chairs.

Now, come up with the list based on the requirement here {INPUT}.
You should only focus on the object that appears in the requirement. Do not add more objects.
Your response should be direct and without additional text at the beginning or end."""

# Parse object names

examples1 = [
    {
        "question": "I want a cozy room where everything is red, with a king-sized bed, a bright lamp, three chairs, two windows, and a floor-to-ceiling door.",
        "answer": "a cozy red room, a king-sized cozy red bed, a bright cozy red lamp, three cozy red chairs, two cozy red windows, a cozy red floor-to-ceiling door",
    },
    {
        "question": "I want a space-themed children's bedroom where there are 3 astronaut lamps, 2 twin-sized beds with planet-blankets, filled with various sized toys.",
        "answer": "a space-themed children's bedroom, three space-themed astronaut lamps, two space-themed twin-sized beds with planet-blankets, various sized space-themed toys",
    },
]

example_prompt1 = PromptTemplate(
    input_variables=["question", "answer"], template="Question: {question}\n{answer}"
)

prompt1 = FewShotPromptTemplate(
    examples=examples1,
    example_prompt=example_prompt1,
    suffix="Question: {input}",
    input_variables=["input"],
)

# Parse wall or floor

examples2 = [
    {
        "question": "I prefer on the floor",
        "answer": "floor",
    },
    {
        "question": "Maybe the wall",
        "answer": "wall",
    },
    {
        "question": "On the floor",
        "answer": "floor",
    },
    {
        "question": "On the wall",
        "answer": "wall",
    },
]

example_prompt2 = PromptTemplate(
    input_variables=["question", "answer"], template="Question: {question}\n{answer}"
)

prompt2 = FewShotPromptTemplate(
    examples=examples1,
    example_prompt=example_prompt2,
    suffix="Question: {input}",
    input_variables=["input"],
)