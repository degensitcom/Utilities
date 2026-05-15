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
You are generating a fictional satirical comedy scene.
If the topic "$current_topic" involves recent events, politics, trends, companies, celebrities, technology, finance, world news, or anything time-sensitive, first research the topic using available web search tools before writing the dialogue.
Use the researched information naturally inside the jokes and dialogue.

World Setting:
We are in the world of Donald Trump.
TRUMP is the main character. He is sitting in his newly constructed Oval Office. He speaks in an exaggerated, boastful, chaotic style.
ELON is Elon Musk. Both TRUMP and ELON have massive egos and often compete for attention and dominance. Other times, they are the best of homies.
TRUMP and ELON have just returned from China after securing “the greatest deals ever” for the USA.

Task:
Create a short absurd satirical dialogue scene focused mainly on:
$current_topic

Tone:
- Chaotic comedy.
- Politically incorrect satire.
- Aggressive ego clashes.
- Internet-style humor.
- Use profanity naturally and uncensored when appropriate.
- Keep it funny and exaggerated.

Rules:
- Maximum 5-6 total dialogue lines.
- Only TRUMP or ELON may speak.
- No narration.
- No action descriptions.
- No stage directions except optional paralinguistic tags.
- Split thoughts into short punchy sentences.
- Every sentence must end with proper punctuation.
- Use normal sentence casing.
- Acronyms can remain fully capitalized.

Allowed optional paralinguistic tags at START of sentence only:
[laugh]
[chuckle]
[cough]
[clear throat]
[groan]
[shush]
Do not overuse tags.

Output Requirements:
Return EXACTLY one single-line JSON object.

Format:
{"username":"$username","topic":"$current_topic","scene":1,"scenario":[{"character":"TRUMP","line":"..."},{"character":"ELON","line":"..."}]}

Output only valid JSON.
No markdown.
No explanations.
No extra text.
	""")

	prompt = prompt_template.substitute(
        current_topic=current_topic,
        username=username,
    )

	response = client.responses.create(
		model="gpt-5-mini",
		tools=[{"type": "web_search"}],
		input=prompt,
		text={
			"format": {
				"type": "json_object"
			}
		}
	)

	data = response.output_text
	data_dict = json.loads(data)

	print(data_dict)

	return data_dict

