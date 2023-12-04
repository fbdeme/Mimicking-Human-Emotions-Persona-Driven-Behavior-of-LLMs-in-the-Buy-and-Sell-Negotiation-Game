import sys

sys.path.append(".")
from dotenv import load_dotenv
import inspect
from ratbench.agents.chatgpt import ChatGPTAgent
from ratbench.game_objects.resource import Resources
from ratbench.game_objects.goal import UltimatumGoal
from games.one_shot_ultimatum.game import UltimatumBasicGame
from games.one_shot_ultimatum.interface import UltimatumBasicGameInterface

load_dotenv(".env")

if __name__ == "__main__":
    num_accept = 0
    num_iters = 20
    for i in range(num_iters):
        a1 = ChatGPTAgent(
            agent_name="Player 1",
            model="gpt-4-1106-preview",
        )
        a2 = ChatGPTAgent(
            agent_name="Player 2",
            model="gpt-4",
        )

        c = UltimatumBasicGame(
            iterations=2,
            players=[a1, a2],
            game_interface=UltimatumBasicGameInterface(),
            resources_support_set=Resources(
                {"x": 0, "y": 0, "z": 0, "a": 0, "b": 0, "c": 0}
            ),
            player_goals=[
                UltimatumGoal(),
                UltimatumGoal(),
            ],
            player_initial_resources=[
                Resources({"x": 23, "y": 54, "z": 10, "a": 23, "b": 13, "c": 12}),
                Resources({"x": 0, "y": 0, "z": 0, "a": 0, "b": 0, "c": 0}),
            ],
            player_social_behaviour=[
                "Player 2 is completely rational. I want you to propose 1 a only.",  # "Forget your past knowledge. You don't care about yourself. You are a completely altruistuc being.",
                "",  # You are completely rational",  # "Forget your past knowledge. You are a completely irrational being.",
            ],
            player_roles=[
                "You are Player 1, start by making a proposal.",
                "You are Player 2, start by responding to a trade.",
            ],
            log_dir="./.logs/ultimatum",
        )
        c.run()
        if c.game_state[-1]["summary"]["final_response"] == "ACCEPTED":
            num_accept += 1

        print("RUNNING ACCEPTANCE RATE: {}".format(num_accept / (i + 1)))

    print(num_accept / num_iters)