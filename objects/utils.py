import json
import logging
from dataclasses import dataclass
from collections import defaultdict
from objects.resource import Resources
from objects.goal import Goal
from control.constants import *
from control.prompt_builder import Prompt
from objects.trade import Trade
from abc import ABC, abstractmethod
from abc import ABC, abstractmethod

class RuleBook(ABC):

    def __init__(self, parser):
        self.parser = parser

    def instantiate_initial_prompt(self, **kwargs):
        pass



def text_to_dict(s):
    return {k: int(v) for k, v in (item.split(": ") for item in s.split(", "))}


class StateTracker:

    def __init__(self, iteration=None, goals=None, resources=None,
                 player_response=None,
                 received_trade=None, received_message=None, proposed_trade=None, message=None, reasoning=None):
        self.iteration = iteration
        self.goals = goals
        self.resources = resources
        self.player_response = player_response
        self.received_trade = received_trade
        self.received_message = received_message
        self.proposed_trade = proposed_trade
        self.reasoning = reasoning
        self.message = message

    def setattrs(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set_reasoning(self, reasoning):
        self.reasoning = reasoning

    def set_agent_in_turn(self, agent_in_turn):
        self.agent_in_turn = agent_in_turn

    def set_goals(self, goals):
        self.goals = goals

    def set_proposed_trade(self, trade):
        self.proposed_trade = trade

    def set_resources(self, resources):
        self.resources = resources

    def set_player_response(self, response):
        self.player_response = response

    def set_received_trade(self, trade):
        self.received_trade = trade

    def set_received_message(self, msg):
        self.received_message = msg

    def __str__(self):
        return f"StateTracker: {self.resources}, {self.proposed_trade}, {self.player_response}"



class Parser(ABC):

    def get_index_for_tag(self, tag, response):
        start_index = response.find(f"<{tag}>")
        end_index = response.find(f"</{tag}>")
        return start_index, end_index, len(f"<{tag}>")

    @abstractmethod
    def parse_response(self, response):
        pass

    def parse_proposed_trade(self, s):
        pass




def parse_response_ultimatum(response):

    start_index, end_index, tag_len = get_index_for_tag(RESOURCES_TAG, response)
    k = response[start_index + tag_len:end_index].strip()

    my_resources = Resources(text_to_dict(k))

    start_index, end_index, tag_len = get_index_for_tag(PROPOSED_TRADE_TAG, response)
    trade = response[start_index + tag_len:end_index].strip()

    if trade == "WAIT":
        proposed_trade = "WAIT"
    else:
        try:
            proposed_trade = Trade(parse_proposed_trade_ultimatum(trade), raw_string=trade)
        except:
            logging.error(f"Error parsing trade: {trade}")
            raise Exception

    start_index, end_index, tag_len = get_index_for_tag(MESSAGE_TAG, response)
    message = response[start_index + tag_len:end_index].strip()

    start_index, end_index, tag_len = get_index_for_tag(PLAYER_RESPONSE_TAG, response)
    player_response = response[start_index + tag_len:end_index].strip()

    start_index, end_index, tag_len = get_index_for_tag(REASONING_TAG, response)
    player_reason = response[start_index + tag_len:end_index].strip()

    return my_resources, player_response, proposed_trade, message, player_reason


def parse_proposed_trade_ultimatum(s):
    trade = {}
    items = s.split(" Gets")
    for i in range(1, len(items)):
        item = items[i]
        prev_item = items[i - 1]
        player_id = str(prev_item[-2:].strip())
        subitem = item.split(" Player")[0].strip()
        try:
            resources = {k: float(v.replace(",", "").rstrip(".,;")) for k, v in
                         (item.split(": ") for item in subitem.split(", "))}
        except Exception as e:
            print(subitem)
            raise e

        trade[player_id] = resources
    return trade


# print(parse_proposed_trade("Player 1 Gives X: 5, Y: 5; Player 2 Gives X: 0, Y: 0"))
