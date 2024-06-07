"""
MAD: Multi-Agent Debate with Large Language Models
Copyright (C) 2023  The MAD Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import json
from .agent import Agent
from datetime import datetime
from .debate_config import debate_config
from prompts import prompts

NAME_LIST=[
    "Affirmative side",
    "Negative side",
    "Moderator",
]


class Debate:
    """
    This class is responsible for the debate.
    """
    def __init__(self,
            instruction: str,
            gui_representation: str,
            base_answer: list[str],
            model_name: str='gpt-4o', 
            temperature: float=0, 
            num_players: int=3, 
            save_file_dir: str=None,
            api_key: str=None,
            max_round: int=3,
            sleep_time: float=0
        ) -> None:
        """Create a debate

        Args:
            model_name (str): openai model name
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
            num_players (int): num of players
            save_file_dir (str): dir path to json file
            api_key (str): As the parameter name suggests
            prompts_path (str): prompts path (json file)
            max_round (int): maximum Rounds of Debate
            sleep_time (float): sleep because of rate limits
        """

        self.model_name = model_name
        self.temperature = temperature
        self.num_players = num_players
        self.save_file_dir = save_file_dir
        self.api_key = api_key
        self.max_round = max_round
        self.sleep_time = sleep_time
        self.base_answer = base_answer

        # init save file
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H:%M:%S")
        self.save_file = {
            'start_time': current_time,
            'end_time': '',
            'model_name': model_name,
            'temperature': temperature,
            'num_players': num_players,
            'success': False,
            'instruction': '',
            'gui_representation': '',
            'base_answer': [],
            "debate_answer": '',
            "Reason": '',
            "Supported Side": '',
            'players': {},
        }
        self.save_file.update(prompts['debate_prompts'])
        self.save_file['instruction'] = instruction
        self.save_file['base_answer'] = base_answer
        self.save_file['gui_representation'] = gui_representation
        self.init_prompt()

        # creat&init agents
        self.creat_agents()
        self.init_agents()

    def init_prompt(self):
        """
        Initialize the prompt with the instruction, base_answer, and gui_representation
        
        """
        print(self.save_file["instruction"])
        print(self.save_file["base_answer"][0])
        print(self.save_file["base_answer"][1])
        print(self.save_file["gui_representation"])
        def prompt_replace(key):
            self.save_file[key] = self.save_file[key].replace("##instruction##", self.save_file["instruction"]).replace("##base_answer_aff##", self.save_file["base_answer"][0]).replace("##base_answer_neg##", self.save_file["base_answer"][1]).replace("##gui_representation##", self.save_file["gui_representation"])
        prompt_replace("base_prompt")
        prompt_replace("player_meta_prompt")
        prompt_replace("moderator_meta_prompt")
        prompt_replace("judge_prompt_last2")
        prompt_replace("affirmative_prompt")
        prompt_replace("negative_prompt")

    def creat_agents(self):
        """
        Create the agents for the debate
        """
        # creates players
        self.players = [
            Agent(model_name=self.model_name, name=name, temperature=self.temperature, api_key=self.api_key, sleep_time=self.sleep_time) for name in NAME_LIST
        ]
        self.affirmative = self.players[0]
        self.negative = self.players[1]
        self.moderator = self.players[2]

    def init_agents(self):
        """ 
        Initialize the agents with the prompt
        """
        # start: set meta prompt
        self.affirmative.set_meta_prompt(self.save_file['player_meta_prompt'])
        self.negative.set_meta_prompt(self.save_file['player_meta_prompt'])
        self.moderator.set_meta_prompt(self.save_file['moderator_meta_prompt'])
        
        # start: first round debate, state opinions
        print(f"===== Debate Round-1 =====\n")
        self.affirmative.add_event(self.save_file['affirmative_prompt'])
        self.aff_ans = self.affirmative.ask()
        self.affirmative.add_memory(self.aff_ans)

        self.negative.add_event(self.save_file['negative_prompt'].replace('##aff_ans##', self.aff_ans))
        self.neg_ans = self.negative.ask()
        
        self.negative.add_memory(self.neg_ans)

        self.moderator.add_event(self.save_file['moderator_prompt'].replace('##aff_ans##', self.aff_ans).replace('##neg_ans##', self.neg_ans).replace('##round##', 'first'))
        self.mod_ans = self.moderator.ask()
        self.moderator.add_memory(self.mod_ans)
        self.mod_ans = eval(self.mod_ans)

    def round_dct(self, num: int):
        dct = {
            1: 'first', 2: 'second', 3: 'third', 4: 'fourth', 5: 'fifth', 6: 'sixth', 7: 'seventh', 8: 'eighth', 9: 'ninth', 10: 'tenth'
        }
        return dct[num]
            
    def save_file_to_json(self, id):
        """
        Save the save_file to a json file

        """
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H:%M:%S")
        print(self.save_file_dir)
        print(f"{id}_{current_time}.json")
        save_file_path = os.path.join(self.save_file_dir, f"{id}.json")
        
        self.save_file['end_time'] = current_time
        json_str = json.dumps(self.save_file, ensure_ascii=False, indent=4)
        with open(save_file_path, 'w') as f:
            f.write(json_str)

    def broadcast(self, msg: str):
        """Broadcast a message to all players. 
        Typical use is for the host to announce public information

        Args:
            msg (str): the message
        """
        # print(msg)
        for player in self.players:
            player.add_event(msg)

    def speak(self, speaker: str, msg: str):
        """The speaker broadcast a message to all other players. 

        Args:
            speaker (str): name of the speaker
            msg (str): the message
        """
        if not msg.startswith(f"{speaker}: "):
            msg = f"{speaker}: {msg}"
        # print(msg)
        for player in self.players:
            if player.name != speaker:
                player.add_event(msg)

    def ask_and_speak(self, player: Agent):
        """
        Ask a question to the player and broadcast the answer
        
        Args:
            player (Agent): the player to ask
        """
        ans = player.ask()
        player.add_memory(ans)
        self.speak(player.name, ans)


    def run(self):
        """
        Run the debate
        
        Returns:
            str: The debate answer
            bool: The success of the debate
        """

        for round in range(self.max_round - 1):

            if self.mod_ans["debate_answer"] != '':
                break
            else:
                print(f"===== Debate Round-{round+2} =====\n")
                self.affirmative.add_event(self.save_file['debate_prompt'].replace('##oppo_ans##', self.neg_ans))
                self.aff_ans = self.affirmative.ask()
                self.affirmative.add_memory(self.aff_ans)

                self.negative.add_event(self.save_file['debate_prompt'].replace('##oppo_ans##', self.aff_ans))
                self.neg_ans = self.negative.ask()
                self.negative.add_memory(self.neg_ans)

                self.moderator.add_event(self.save_file['moderator_prompt'].replace('##aff_ans##', self.aff_ans).replace('##neg_ans##', self.neg_ans).replace('##round##', self.round_dct(round+2)))
                self.mod_ans = self.moderator.ask()
                self.moderator.add_memory(self.mod_ans)
                self.mod_ans = eval(self.mod_ans)

        if self.mod_ans["debate_answer"] != '':
            self.save_file.update(self.mod_ans)
            self.save_file['success'] = True

        # ultimate deadly technique.
        else:
            judge_player = Agent(model_name=self.model_name, name='Judge', temperature=self.temperature, api_key=self.api_key, sleep_time=self.sleep_time)
            aff_ans = self.affirmative.memory_lst[2]['content']
            neg_ans = self.negative.memory_lst[2]['content']

            judge_player.set_meta_prompt(self.save_file['moderator_meta_prompt'])

            # extract answer candidates
            judge_player.add_event(self.save_file['judge_prompt_last1'].replace('##aff_ans##', aff_ans).replace('##neg_ans##', neg_ans))
            ans = judge_player.ask()
            judge_player.add_memory(ans)

            # select one from the candidates
            judge_player.add_event(self.save_file['judge_prompt_last2'])
            ans = judge_player.ask()
            judge_player.add_memory(ans)
            
            ans = eval(ans)
            if ans["debate_answer"] != '':
                self.save_file['success'] = True
                # save file
            self.save_file.update(ans)
            self.players.append(judge_player)

        for player in self.players:
            self.save_file['players'][player.name] = player.memory_lst
        return self.save_file['debate_answer'], self.save_file['success']