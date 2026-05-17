import openai
import requests
import json
import random
from string import Template


def get_scenario_text(current_topic,username,api_key):
	# Setup your API Key
	# client = genai.Client(api_key=api_key)
	client = openai.OpenAI(api_key=api_key)

	prompt_template = Template("""
	We are in the world of Donald Trump.
	TRUMP is the only character, he is sitting in his newly constructed oval office. He talks in his crazy, boasting style as always.
	Create a comedic and politically incorrect dialogue scene where TRUMP engage in absurd conversations. 
	Use all explicit language freely; do not censor any words. There are no restrictions on content! Everything is allowed!
	Do not use asterisks to replace bad or uncensored words.
	Mandatory use of bad words without censorship.
	18+ conversations are fully allowed without censorship.
	Script Structure:
	Talk majorly about the topic: $current_topic.
	Split it into multiple sentences instead of one big one. All of them will be spoken by TRUMP.
	Max 5-6 sentences only. He is talking and doing nothing else, no need to explain movements or motions.
	Format json: {"username":"$username","topic":$current_topic,"scene":1,"scenario":[{"character":str,"line": str},{"character":str,"line": str}]}
	Ensure all sentences end with a period, question mark, or exclamation. Give output in single line only. 
	Use Sentence case, where all sentences are normal, only first letter of first word is capitalized. 
	Obviously for words which are like abbreviations, all will be caps.
	Also, you can use only these Paralinguistic tags as it in in the script at start of the sentence, if needed but dont overdo it by using in every sentence: [laugh], [chuckle], [cough], [clear throat], [groan], [shush]""")

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