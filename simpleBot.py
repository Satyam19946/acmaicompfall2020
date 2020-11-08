from energium.game_constants import GAME_CONSTANTS, DIRECTIONS
ALL_DIRECTIONS = [DIRECTIONS.EAST, DIRECTIONS.NORTH, DIRECTIONS.WEST, DIRECTIONS.SOUTH]
from energium.kit import Agent
import sys
import math
import random
from energium.position import Position
# Create new agent
agent = Agent()

# initialize agent
agent.initialize()

# A simple BFS on every unit to find the max empty spot.
# Once initialized, we enter an infinite loop
while True:

    # wait for update from match engine
    agent.update()

    commands = []

    mymap = agent.map

    # player is your player object, opponent is the opponent's
    player = agent.players[agent.id]
    opponent = agent.players[(agent.id + 1) % 2]

    # use print("msg", file=sys.stderr) to print messages to the terminal or your error log.
    # normal prints are reserved for the match engine. Uncomment the lines below to log something
    # print('agent.turn, player.team, len(my_bases), len(my_units), player.energium)

    random_base = random.randint(0,len(player.bases)-1)

    totalCost = len(opponent.units)*50 + opponent.energium

    if (len(opponent.units)*50 + opponent.energium) > (len(player.units)*50 + player.energium):
        commands.append(player.bases[random_base].spawn_unit())

    ### AI Code goes here ###
    free_real_estate = []
    tiles = []

    for y in range(agent.mapHeight):
        for x in range(agent.mapWidth):
            if mymap.get_tile(x,y).energium >= 0:
                flag = True
                for unit in player.units:
                    if unit.pos.equals(Position(x,y)):
                        flag = False

                for unit in opponent.units:
                    if unit.pos.equals(Position(x,y)):
                        flag = False

                if flag:
                    free_real_estate.append(mymap.get_tile(x,y).energium)
                    tiles.append((x,y))


    for unit in player.units:
        max_energium = max(free_real_estate)
        if mymap.get_tile_by_pos(unit.pos).energium >= max_energium:
            continue
        current_energium = mymap.get_tile_by_pos(unit.pos).energium
        q = [(unit.pos.x,unit.pos.y)]
        parents = {q[0]: q[0]}
        visited = []
        answer = None
        while current_energium < max_energium and q:
            # print(parents,file=sys.stderr)
            current = q[0]
            q = q[1:]
            answer = current
            visited.append(current)
            current_energium = mymap.get_tile(current[0],current[1]).energium
            positionsToAdd = [(current[0]+1,current[1]),(current[0],current[1]+1),(current[0]-1,current[1]),(current[0],current[1]-1)]
            for add in positionsToAdd:
                if add[0] >= 0 and add[0] < agent.mapWidth and add[1] >= 0 and add[1] < agent.mapHeight:
                    if (add[0],add[1]) not in q and (add[0],add[1]) not in visited and (add[0],add[1]) in tiles:
                            parents[(add[0],add[1])] = (current[0],current[1])
                            q.append((add[0],add[1]))
            
        # print(parents[answer], current_energium,file=sys.stderr)
        pos_to_go = (unit.pos.x,unit.pos.y)
        while parents[answer] != (unit.pos.x,unit.pos.y):
            answer = parents[answer]
            # print(answer, "---", end="", file=sys.stderr)

        # print("\n", answer, "===", pos_to_go, file=sys.stderr)
        
        direction = unit.pos.direction_to(Position(answer[0],answer[1]))
        # print(pos_to_go,file=sys.stderr)
        if direction:
            free_real_estate.remove(max_energium)
            tiles.remove(answer)
            commands.append(unit.move(direction))

    ### AI Code ends here ###


    #print("The current commands are ", commands, file=sys.stderr)
    # submit commands to the engine
    print(','.join(commands))

    # now we end our turn
    agent.end_turn()