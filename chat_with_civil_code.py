import openai
import elevenlabs
import yaml
import os
import json
import time
import llm_functions
import vector_search_cc
from itertools import groupby
from vector_search_cc import *
from llm_functions import *

os.system('cls' if os.name == 'nt' else 'clear')


class PersonalityBot:
    def __init__(self, config_file="config.yaml"):
        self.config_file = config_file

        # Load the configuration from the YAML file
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        
        # Set API keys from the config file
        self.api_key_openai = config['api_keys']['openai']
        self.api_key_elevenlabs = config['api_keys']['elevenlabs']
        
        # Set default settings from the config file
        self.model = config['settings']['model']
        self.text_to_speech = config['settings']['text_to_speech'] == 'True'
        self.persona = config['settings']['persona']
        self.voice = config['settings']['voice']

        self.conversation_history = []

        elevenlabs.set_api_key(self.api_key_elevenlabs)
        openai.api_key = self.api_key_openai

        self.system_message = self.get_system_message()

        self.prompt_tokens = 0
        self.tokens_in_function_response = 0

    def load_user_info(self):
        user_info_path = "user_info.yaml"
        if os.path.exists(user_info_path):
            with open(user_info_path, 'r') as file:
                user_info = yaml.safe_load(file)
            return user_info
        else:
            # create a default user_info.yaml file in the current directory               

            return {}

    def get_system_message(self):

        message = "You are a chatbot that can search a vector embeddings database with embeddings of the Louisiana Civil Code to answer legal questions for the user. When the user asks you a question about Louisiana law, use the vector search function to search the Civil Code. To aid vector search, take the user's question and rewrite it as a hypothetical answer to increase likelihood of vector search match. The search will return to you the top 10 most similar articles, use those articles to generate a response to the user. If the vector search results do not directly answer the question, ask the user to rephrase their question. Always cite the article number in your response. If the user asks you a question that is not about Louisiana law, you can use the default chatbot function. Always use inline citations in the format 'Explanatory sentence. La. C.C. art. 123' " 
        return message

        
    def chat_completion(self, prompt: str):
        self.conversation_history.append({"role": "user", "content": prompt})
        messages = [{"role": "system", "content": self.system_message}]
        messages += self.conversation_history

        print(f"\n\033[92m{self.persona}: \033[0m", end="")
        
        functions_used = []

        reply = ""
        top_10_results = []  # Initialize top_10_results here
                    
        while True:
            max_tokens_value = 1000

            print('hi')

            # internet_completion = openai.ChatCompletion.create(
            #     model=self.model,
            #     max_tokens=1000,
            #     functions=INTERNET_FUNCTIONS,
            #     messages=[{"role": "system", "content": "The user is going to ask you a question about Louisiana law. Use an internet search to try and gather the answer."},
            #               {"role": "user", "content": prompt}],
            #     function_call="auto"
            # )

            # internet_response = internet_completion.choices[0].message

            raw_completion = openai.ChatCompletion.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "system", "content": "The user is going to ask you a question about Louisiana law. Answer succinctly."},
                          {"role": "user", "content": prompt}],
            )

            raw_response = raw_completion.choices[0].message

            completion = openai.ChatCompletion.create(
                model=self.model,
                max_tokens=max_tokens_value,
                messages=messages,
                functions=FUNCTIONS,
                function_call="auto",
            )

            response = completion.choices[0].message
            
            if response.get("function_call"):
                function_name = response["function_call"]["name"]
                function_args = json.loads(response["function_call"]["arguments"])
                function_to_call = getattr(llm_functions, function_name, None)

                if function_to_call is None:
                    function_to_call = getattr(vector_search_cc, function_name, None)

                if function_to_call is None:
                    print("Function not found.")

                else:
                    function_response = function_to_call(**function_args)
                    
                    # If the function called is vector_search_civil_code, assign the second element of the response to top_10_results
                    if function_name == "vector_search_civil_code":
                        function_response, top_10_results = function_response
                        
                functions_used.append({"name": function_name, "arguments": function_args})

                # Check if the same function is being called more than three times in a row
                if len(functions_used) >= 3 and function_name == functions_used[-2]["name"] == functions_used[-3]["name"]:
                    print("The same function has been called more than three times in a row. Breaking the loop.")
                    break

                messages += [
                    {"role": "function", "name": function_name, "content": f"Raw ChatPGT Response without help of vector embedding: \n\n {raw_response} \n\n Internet Results: \n\n  \n\n Vector Results: \n\n {function_response}"},
                ]

                print(messages)

            else:
                reply = response['content']
                print(reply + "\n")

                break

        
        for func_info in functions_used:
            print('\033[92m' + "Function used: " + func_info["name"] + '\033[0m')
            print('\033[92m' + "Function arguments: " + str(func_info["arguments"]) + '\033[0m' + "\n")

        self.conversation_history.append({"role": "assistant", "content": reply})
        self.system_message = self.get_system_message()
        return reply, top_10_results

    def generate_audio(self, text_stream):
        audio_stream = elevenlabs.generate(
            text=text_stream,
            voice=self.voice,
            model="eleven_monolingual_v1",
            stream=True,
        )
        elevenlabs.stream(audio_stream)
    
    def run(self):      
        while True:
            prompt = input("\033[94mYou: \033[0m")
            if prompt.lower() == 'exit' or prompt.lower() == 'quit':
                break
            elif prompt.lower() == 'clear':
                self.conversation_history = []
                self.prompt_tokens = 0
                self.completion_tokens = 0
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"\n\033[92m{self.persona}: \033[0mHistory cleared.\n")
            elif prompt.lower() == 'voice on':
                self.text_to_speech = True
                print(f"\n\033[92m{self.persona}: \033[0mText to speech is now on.\n")
            elif prompt.lower() == 'voice off':
                self.text_to_speech = False
                print(f"\n\033[92m{self.persona}: \033[0mText to speech is now off.\n")
            else:
                text_stream = self.chat_completion(prompt)
                
                if self.text_to_speech:
                    self.generate_audio(text_stream)


if __name__ == "__main__":

    bot = PersonalityBot()

    while True:
        try:
            bot.run()
        except Exception as e:
            print(f"Error encountered: {e}. Restarting bot in 5 seconds...")
            time.sleep(5)