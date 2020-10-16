from energium.game_constants import GAME_CONSTANTS, DIRECTIONS
ALL_DIRECTIONS = [DIRECTIONS.EAST, DIRECTIONS.NORTH, DIRECTIONS.WEST, DIRECTIONS.SOUTH]
from energium.kit import Agent
import sys
import math
import random

# Create new agent
agent = Agent()

# initialize agent
agent.initialize()

# Once initialized, we enter an infinite loop
while True:

    # wait for update from match engine
    agent.update()

    commands = []

    # player is your player object, opponent is the opponent's
    player = agent.players[agent.id]
    opponent = agent.players[(agent.id + 1) % 2]

    # use print("msg", file=sys.stderr) to print messages to the terminal or your error log.
    # normal prints are reserved for the match engine. Uncomment the lines below to log something
    # print('agent.turn, player.team, len(my_bases), len(my_units), player.energium)

    ### AI Code goes here ###

    mapHeight = agent.mapHeight
    mapWidth = agent.mapWidth
    mymap = agent.map

    unit_cost = GAME_CONSTANTS['PARAMETERS']['UNIT_COST'] #50
    myUnits = player.units
    myBases = player.bases
    opponentBases = opponent.bases
    opponentUnits = opponent.units
    #print("My current energium is ", player.energium, file=sys.stderr)
    #print("Opponent energium is ", opponent.energium, file=sys.stderr)

    # Play Greedy
    if len(myUnits) < 4 and player.energium >= unit_cost:
        commands.append(myBases[0].spawn_unit())

    # Keep on spawning units as much as possible.

    # 1st try - Try implement a simple A* search algorithm 
    energium_here = []
    
    opponentUnitsPos = []
    for unit in opponentUnits:
        opponentUnitsPos.append((unit.pos.x, unit.pos.y))

    myUnitsPos = []
    for unit in myUnits:
        myUnitsPos.append((unit.pos.x, unit.pos.y))

    #print("My units are here", myUnitsPos, file=sys.stderr)
    #print("Opponent units are here", opponentUnitsPos, file=sys.stderr)
    # Search the grid where the energium is 
    for y in range(mapHeight):
        for x in range(mapWidth):
            if mymap.get_tile(x,y).energium > 0:
                energium_here.append([mymap.get_tile(x,y).energium,y,x,mymap.get_tile(x,y)])

    energium_here.sort(reverse=True)
    #print("Energium Positions", energium_here, file=sys.stderr)


    copyMyUnits = myUnits.copy()
    for reachPoint in energium_here:
        # For the point with the highest energium get the closest unit.
        # Repeat for all
        minDistance, unitReq = [math.inf, None]
        for unit in copyMyUnits:
            dis = (reachPoint[1]-unit.pos.y)**2 + (reachPoint[2]-unit.pos.x)**2
            if dis < minDistance:
                minDistance, unitReq = dis, unit
        if unitReq:
            copyMyUnits.remove(unitReq)
            direction_to_take = unitReq.pos.direction_to(reachPoint[3].pos)
            if direction_to_take:
                commands.append(unitReq.move(direction_to_take))

            # If moving is not possible, go to nearest base.
            """
            else:
                minDis, baseReq = [math.inf, None]
                for couldBeBase in myBases:
                    if unitReq.pos.distance_to(couldBeBase.pos) < minDis:
                        minDis = unitReq.pos.distance_to(couldBeBase.pos)
                        baseReq = couldBeBase
            
                direction_to_take = unitReq.pos.direction_to(baseReq.pos)
                if direction_to_take:
                    commands.append(unitReq.move(direction_to_take))
                else:
                    commands.append(unitReq.move(ALL_DIRECTIONS[math.floor(random.random() * len(ALL_DIRECTIONS))]))
            """
        #If invalid - cant move go in perpindicular distance

    ### AI Code ends here ###


    #print("The current commands are ", commands, file=sys.stderr)
    # submit commands to the engine
    print(','.join(commands))

    # now we end our turn
    agent.end_turn()