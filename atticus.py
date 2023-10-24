import openai
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

        message = "You are a chatbot that can search a vector embeddings database with embeddings of the Louisiana Civil Code to answer legal questions for the user. When the user asks you a question about Louisiana law, use the vector search function to search the Civil Code. To aid vector search, take the user's question and rewrite it as a hypothetical answer to increase likelihood of vector search match. The search will return to you the top 10 most similar articles, use those articles to generate a response to the user. If the vector search results do not directly answer the question, ask the user to rephrase their question. Always cite the article number in your response. If the user asks you a question that is not about Louisiana law, you can use the default chatbot function. Always use inline citations in the format 'Explanatory sentence. La. C.C. art. 123' Don't put the article in parentheses." 
        return message

        
    def chat_completion(self, prompt: str, extra_context_from_user: str = ""):
      
        self.conversation_history.append({"role": "user", "content": prompt})
        messages = [{"role": "system", "content": self.system_message}]
        messages += self.conversation_history

        print(f"User's prompt: \n '{prompt}'")
        
        functions_used = []

        reply = ""
        top_10_results = []  # Initialize top_10_results here
                    
        max_tokens_value = 1000

        classifier_completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "system", "content": "The user is going to ask you a question about Louisiana law. Decide whether you need more information to answer the question first. If the user just sends a greeting, you need more info. Always assume the question is about Louisiana law unless the user mentions otherwise."},
                        {"role": "user", "content": f"{prompt} | Extra context from user: {extra_context_from_user}"}],
            functions=FUNCTIONS,
            function_call={"name": "classify_question"}
        )

        classifier_response = classifier_completion.choices[0].message

        if classifier_response.get("function_call"):
            function_name = classifier_response["function_call"]["name"]
            function_args = json.loads(classifier_response["function_call"]["arguments"])
            function_to_call = getattr(llm_functions, function_name, None)

            if function_to_call is None:
                print("Function not found.")

            else:
                classifier_function_response = function_to_call(**function_args)
                    
            functions_used.append({"name": function_name, "arguments": function_args})

            print("Do we need more information from user?")

            print(classifier_function_response)
            
            if classifier_function_response == "No":
                print("We have all the information we need to answer the question.")

            else:
                follow_up_classifier_completion = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "The user is going to ask you a question about Louisiana law, but you need more information. Ask the user for the specific information you need to answer the question."},
                                {"role": "user", "content": f"{prompt}"}],
                )

                # ...
                follow_up_classifier_response = follow_up_classifier_completion.choices[0].message

                print(follow_up_classifier_response)                

                follow_up_classifier_message = "NEED_MORE_INFO"

                return follow_up_classifier_response.content,  follow_up_classifier_message

        raw_completion = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "system", "content": "The user is going to ask you a question about Louisiana law. Answer completely."},
                        {"role": "user", "content": "Original question:" + prompt + "Additional context:" + extra_context_from_user}],
        )

        raw_response = raw_completion.choices[0].message

        print("GPT4's raw attempt at answering the question: \n")
        print(raw_response)

        internet_completion = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=1000,
            functions=FUNCTIONS,
            messages=[{"role": "system", "content": "The user is going to ask you a question about Louisiana law. Use an internet search to try and gather the answer."},
                        {"role": "user", "content": f"{prompt} + {extra_context_from_user} + Louisiana law"}],
            function_call={"name": "search"}
        )

        internet_response = internet_completion.choices[0].message

        if internet_response.get("function_call"):
            function_name = internet_response["function_call"]["name"]
            function_args = json.loads(internet_response["function_call"]["arguments"])
            function_to_call = getattr(llm_functions, function_name, None)

            if function_to_call is None:
                print("Function not found.")

            else:
                function_response = function_to_call(**function_args)
                    
            functions_used.append({"name": function_name, "arguments": function_args})

            # Summarize the function response using llm
            summary_completion = openai.ChatCompletion.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "system", "content": "The user is going to ask you a question about Louisiana law. Take the internet serp results and snippets and try to answer the question."},
                            {"role": "user", "content": f"User Question: {prompt} + {extra_context_from_user} \n Internet Serp Results: \n {function_response}]"}])

            summary_response = summary_completion.choices[0].message

        internet_reply = summary_response['content']

        print("GPT4's summary of internet search results: \n")
        print(internet_reply)

        messages += [{"role": "user", "content": f"A previous GPT4 instance answered the user's question ({prompt} + {extra_context_from_user}) as: \n\n {raw_response}. Another instance summarized the internet's answer to the question as: \n\n {internet_reply}"}]

        completion = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=max_tokens_value,
            messages=messages,
            functions=FUNCTIONS,
            function_call={"name": "vector_search_civil_code"},
        )

        response = completion.choices[0].message
        
        if response.get("function_call"):
            function_name = response["function_call"]["name"]
            function_args = json.loads(response["function_call"]["arguments"])
            function_to_call = getattr(vector_search_cc, function_name, None)

            if function_to_call is None:
                print("Function not found.")

            else:
                function_response = function_to_call(**function_args)
                
                # If the function called is vector_search_civil_code, assign the second element of the response to top_10_results
                if function_name == "vector_search_civil_code":
                    function_response, top_10_results = function_response
                    
            functions_used.append({"name": function_name, "arguments": function_args})

            messages = [
                {"role": "system", "content": f"You are a legal answering service. You are going to be given context from GPT4, the internet, and a semantic search of the Louisiana Civil Code. Use the context to answer the user's question: \n {prompt} + {extra_context_from_user} \n. ALWAYS GIVE THE CIVIL CODE ARTICLES THE MOST WEIGHT WHEN ANSWERING THE QUESTION. The raw GPT4 response may include hallucinations. If the user asks you a question that is not about Louisiana law, you can just answer normally. If the answer does not appear to be in the Vector Results you don't have to mention any specific code articles. DO NOT ASSUME THAT JUST BECAUSE YOU ARE GIVEN A CIVIL CODE ARTICLE FOR CONTEXT IT IS RELEVANT TO THE USER'S QUESTION. Always use inline citations in the following format 'Explanatory sentence. La. C.C. art. 123' Don't put the article in parentheses." },
                {"role": "user", "content": f"Raw ChatPGT Response without help of vector embedding: \n\n {raw_response} \n\n Internet Results: \n\n {internet_reply}  \n\n Vector Results: \n\n {function_response}"},
            ]

        final_completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            )
        
        final_reply = final_completion.choices[0].message['content']

        print("Final reply: \n")
        print(final_reply)
        
        for func_info in functions_used:
            print('\033[92m' + "Function used: " + func_info["name"] + '\033[0m')
            print('\033[92m' + "Function arguments: " + str(func_info["arguments"]) + '\033[0m' + "\n")

        self.conversation_history.append({"role": "assistant", "content": reply})
        self.system_message = self.get_system_message()
        return final_reply, top_10_results


if __name__ == "__main__":

    bot = PersonalityBot()

    while True:
        try:
            bot.run()
        except Exception as e:
            print(f"Error encountered: {e}. Restarting bot in 5 seconds...")
            time.sleep(5)