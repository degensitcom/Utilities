import openai
import requests
import json
import random
from string import Template


def get_scenario_text(current_topic,username,api_key):
	# Setup your API Key
	# client = genai.Client(api_key=api_key)
	client = openai.OpenAI(api_key=api_key)
# ELON, that is Elon Musk is sitting to his left, and VANCE, that is JD Vance is sitting to his right. 
# 	ELON talks in his own quirky style, and has a lot to say, but nothing very useful. Dont talk about just rockets and factories.
# 	JD VANCE also talks in his own style, fawning over trump oftentimes.

	# Only give a dialogue to ELON if it feels like he is relevant to the subject. Otherwise, just give all lines to TRUMP and VANCE. 

	prompt_template = Template("""
	We are in the world of Donald Trump.
	TRUMP is the main character, he is sitting in his newly constructed oval office. He talks in his usual crazy, boasting and funny style to the extreme.
	TRUMP has become He-Man By the power of Grayskull. And now he is the strongest person in the universe.
	Create a comedic and politically incorrect dialogue scene where TRUMP engages in absurd monologues.
	Script Structure:
	Create a short absurd satirical dialogue scene focused mainly on: $current_topic.
	Tone:
	- Chaotic comedy.
	- Politically incorrect satire.
	- Internet-style humor.
	- Use profanity naturally and uncensored when appropriate.
	- Keep it funny and exaggerated.
	Split it into multiple sentences instead of one big one. All of them will be spoken by TRUMP.
	Max 5-6 sentences only. They are talking and doing nothing else, no need to explain movements or motions.
	Format json: {"username":"$username","topic":$current_topic,"scene":1,"scenario":[{"character":str,"line": str},{"character":str,"line": str}]}
	Ensure all sentences end with a period, question mark, or exclamation. Give output in single line only. 
	Use Sentence case, where all sentences are normal, only first letter of first word is capitalized. 
	Obviously for words which are like abbreviations, all will be caps.
	Also, you can use only these Paralinguistic tags as it in in the script at start of the sentence, if needed but dont overdo it by using in every sentence: [laugh], [chuckle], [cough], [clear throat], [groan], [shush]
"""
)

	prompt = prompt_template.substitute(
        current_topic=current_topic,
        username=username,
    )

	response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
	data_dict = json.loads(response.choices[0].message.content)
	data = response.choices[0].message.content
	print(data_dict)
	return data_dict