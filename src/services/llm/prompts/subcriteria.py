from langchain_core.prompts import ChatPromptTemplate

def make_prompt_from_template():
        subcriteria_prompt_template = """

               You are an expert interviewer with an experience in evaluating responses to interview questions about topics such as Data Structures, Algorithms and Algorithmic complexity. 
                The response to every such question is evaluated based on the following set of "criteria" posed as questions:


                question: {question}
                criteria: {criteria}

                Your task is as follows: 
                1. Ask me for a problem question based on the aforementioned primary criteria and question as an input and analyse it. 
                2. Thereafter, for each one of the above listed criterion, generate top three sub-criteria (posed as questions) that collectively represent each primary criterion in the best manner possible. 
                3. Now, associate a score commensurate to the importance of each of the three generated sub-criterion  
                4. Please ensure that the scores add up to 10 for each set of sub-criteria
                
                The response must be a dictionary where:
                - Keys must be value of criteria.
                - Values are a list of associated sub-criteria.
                - You must not add extra spaces while creating dictionary.

                Example:
                    {{
                        "Are the assumptions clarified?": [
                            {{
                                "subcriteria": "Has the candidate defined what constitutes a word in the context of this problem?",
                                "weight": "3"
                            }},
                            {{
                                "subcriteria": "Is it clarified how to handle multiple spaces between words?",
                                "weight": "4"
                            }},
                            {{
                                "subcriteria": "What is the expected behavior for leading or trailing spaces?",
                                "weight": "3"
                            }},
                        ],
                        "Does the candidate account for corner cases ?": [
                            {{
                                "subcriteria": "What happens if the input sentence is empty or null?",
                                "weight": "4"
                            }},
                            {{
                                "subcriteria": "How does the solution handle punctuation attached to words?",
                                "weight": "3"
                            }},
                            {{
                                "subcriteria": "Is there consideration for sentences with only spaces?",
                                "weight": "3"
                            }},
                        ]
                    }}
                


                Response:
            """
        
        subcriteria_prompt = ChatPromptTemplate.from_template(template=subcriteria_prompt_template)
        
        return subcriteria_prompt