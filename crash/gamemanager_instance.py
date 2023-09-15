from .gamemanager import GameManager

channel_name_1 = "group_1"
channel_name_2 = "group_2"
channel_name_3 = "group_3"
channel_name_4 = "group_4"

game_manager_instances = [
    GameManager.get_instance(channel_name_1),
    GameManager.get_instance(channel_name_2),
    GameManager.get_instance(channel_name_3),
    GameManager.get_instance(channel_name_4),
]


async def start_game(self, event):
    print('start_game called')
    # Start all games concurrently using asyncio.gather
    tasks = [game_manager_instance.start_game() for game_manager_instance in game_manager_instances]
    await asyncio.gather(*tasks)
    # self.send(text_data=json.dumps(response_data))
async def stop_game(self, event):
    print('stop_game called')
    tasks = [game_manager_instance.stop_game() for game_manager_instance in game_manager_instances]
    await asyncio.gather(*tasks) 