import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from game.agents.agents import Agent
import time
from copy import copy, deepcopy


class ClaudeAgent(Agent):

    def __init__(self, agent_name, model="claude-2", **kwargs):
        super().__init__(**kwargs)
        self.run_epoch_time_ms = str(round(time.time() * 1000))

        self.agent_name = agent_name
        self.conversation = []
        self.model = model
        self.prompt_entity_initializer = "user"
        self.anthropic = Anthropic(
            # defaults to os.environ.get("ANTHROPIC_API_KEY")
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    def init_agent(self, system_prompt, role):

        system_prompt = system_prompt + role
        self.update_conversation_tracking(self.prompt_entity_initializer, system_prompt)
    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():

            if (type(v)) == Anthropic:
                v = "AnthropicObject"
            setattr(result, k, deepcopy(v, memo))
        return result

    def conversation_list_to_agent(self):
        string = ""

        if self.agent_name == "Player 2" and len(self.conversation) > 1:
            self.conversation[0]["content"] += "\n" + self.conversation[1]["content"] + "\n"

        for index, o in enumerate(self.conversation):
            if index == 1 and self.agent_name == "Player 2":
                continue

            t = o["content"]

            if o["role"] == "assistant":
                p = AI_PROMPT
            else:
                p = HUMAN_PROMPT
            string += f"{p} {t}"
        return f"{string} {AI_PROMPT}\n"

    def chat(self):
        t = self.conversation_list_to_agent()

        completion = self.anthropic.completions.create(
            model=self.model,
            max_tokens_to_sample=400,
            prompt=t,
        )
        time.sleep(1)
        return completion.completion



    def update_conversation_tracking(self, role, message):
        self.conversation.append({"role": role, "content": message})

    def set_state(self, state_dict):
        self.conversation = state_dict["conversation"]
        self.run_epoch_time_ms = state_dict["run_epoch_time_ms"]

    def dump_conversation(self, file_name):
        with open(file_name, "w") as f:
            for index, text in enumerate(self.conversation):
                c = text["content"].replace("\n", " ")

                if index % 2 == 0:
                    f.write(f"= = = = = Iteration {index // 2} = = = = =\n\n")
                    f.write(f'{text["role"]}: {c}' "\n\n")
                else:
                    f.write(f'\t\t{text["role"]}: {c}' "\n\n")
