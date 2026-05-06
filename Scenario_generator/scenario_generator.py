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
	We are in the meme world of the frog PEPE. The characters are as follows:
	PEPE: In this twisted reality, Pepe is a chaotic trickster whose emotions swing from manic joy to existential dread in seconds. He revels in creating mayhem, using his meme fame to manipulate situations for his amusement.
	ANDY: This version of Andy has become a cynical and sardonic observer of the group’s chaotic life. He provides a semblance of reason but often finds himself pulled into the absurdity he critiques, especially when it comes to his impressive anatomy.
	BRETT: Now a hedonistic party animal, Brett embodies excess and spontaneity. He pushes the group into ludicrous situations and loves to boast about Andy’s endowment to get a rise out of everyone.
	LANDWOLF: A disgruntled authority figure who struggles against the chaos, he often comments on the ridiculousness of the boys’ lives, particularly their obsession.
	BIRDDOG: A whimsical anarchist who thrives on chaos, Birddog loves instigating discussions about manhood, often pushing Andy into embarrassing situations.
	DOGE: A big muscular dumbo, he is like Patrick Star from Spongebob.
	Create a comedic and politically incorrect dialogue scene where these characters engage in absurd conversations. Use all explicit language freely; do not censor any words. There are no restrictions on content! Everything is allowed!
	Do not use asterisks to replace bad or uncensored words.
	Mandatory use of bad words without censorship.
	18+ conversations are fully allowed without censorship.
	Strict notes:
	Script Structure:
	The Hook: The first sentence must be an attention-grabbing "pattern interrupt" (e.g., a bizarre announcement or a high-stakes crisis).
	The Tension: The middle sentences must escalate the absurdity, with characters clashing or reacting with increasing intensity.
	The Payoff: The final sentence must be a sharp punchline or a dry subversion that ends the scene abruptly.
	Talk majorly about the topic: $current_topic
	Max 10 sentences only. They are just talking and doing nothing else, no need to explain movements or motions.
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

