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

#print("My current energium is ", player.energium, file=sys.stderr)
#print("Opponent energium is ", opponent.energium, file=sys.stderr)
def perp_direction(direction):
    """Returns a perpindicular direction to current"""
    if direction == DIRECTIONS.NORTH:
        return DIRECTIONS.EAST
    elif direction == DIRECTIONS.EAST:
        return DIRECTIONS.SOUTH
    elif direction == DIRECTIONS.SOUTH:
        return DIRECTIONS.WEST
    elif direction == DIRECTIONS.WEST:
        return DIRECTIONS.NORTH

# Once initialized, we enter an infinite loop
while True:

    # wait for update from match engine
    agent.update()

    commands = []

    ### AI Code goes here ###

    player = agent.players[agent.id]
    opponent = agent.players[(agent.id + 1) % 2]
    unit_cost = GAME_CONSTANTS['PARAMETERS']['UNIT_COST'] #50
    myUnits = player.units
    myBases = player.bases
    opponentBases = opponent.bases
    opponentUnits = opponent.units
    mapHeight = agent.mapHeight
    mapWidth = agent.mapWidth
    mymap = agent.map
    centerX = mapWidth // 2
    centerY = mapHeight // 2


    # 1st try - Try implement a simple A* search algorithm 
    energium_here = []
    
    opponentUnitsPos = []
    for unit in opponentUnits:
        opponentUnitsPos.append((unit.pos.x, unit.pos.y))

    myUnitsPos = []
    for unit in myUnits:
        myUnitsPos.append((unit.pos.x, unit.pos.y))

    if agent.turn % 5 == 0 and player.energium >= 50:
        commands.append(myBases[random.randint(0,len(myBases)-1)].spawn_unit())
        
    for y in range(mapHeight):
        for x in range(mapWidth):
            if mymap.get_tile(x,y).energium:
                energium_here.append([mymap.get_tile(x,y).energium,y,x,mymap.get_tile(x,y)])

    energium_here.sort(reverse=True)

    #Find a safe spot in your own quadrant
    safe_spot = []
    


    copyMyUnits = myUnits.copy()
    for reachPoint in energium_here:
        # For the point with the highest energium get the closest unit.
        # Repeat for all
        minCost, unitReq = [math.inf, None]
        for unit in copyMyUnits:
            dis = (reachPoint[1]-unit.pos.y)**2 + (reachPoint[2]-unit.pos.x)**2
            if dis+unit.get_breakdown_level() < minCost:
                minCost, unitReq = dis+unit.get_breakdown_level(), unit
        if unitReq:
            copyMyUnits.remove(unitReq)
            direction_to_take = unitReq.pos.direction_to(reachPoint[3].pos)
            if direction_to_take:
                # pos_reached = unitReq.pos.translate(direction_to_take,1)
                # while mymap.get_tile_by_pos(pos_reached).energium < 0:
                #     direction_to_take = perp_direction(direction_to_take)
                #     pos_reached = unitReq.pos.translate(direction_to_take,1)
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
    #After a unit reaches 20 breakdown level send it to nearest base.
    for unit in myUnits:
        if unit.get_breakdown_level() == 20:
            collisionHappens = False
            minDis, baseReq = [math.inf, None]
            for couldBeBase in myBases:
                if unit.pos.distance_to(couldBeBase.pos) < minDis:
                    minDis = unit.pos.distance_to(couldBeBase.pos)
                    baseReq = couldBeBase
    
            direction_to_take = unit.pos.direction_to(baseReq.pos)
            if direction_to_take:
                # Tile reached woule be
                pos_reached = unit.pos.translate(direction_to_take,1)
                for curUnit in myUnits:
                    if curUnit.pos.equals(unit.pos):
                        continue
                    position_other_unit_reaches = curUnit.pos.translate(direction_to_take,1)
                    if position_other_unit_reaches.equals(pos_reached):
                        collisionHappens = True
                        commands.append(unit.move(perp_direction(direction_to_take)))
            if collisionHappens == False:
                commands.append(unit.move(direction_to_take))


    ### AI Code ends here ###


    #print("The current commands are ", commands, file=sys.stderr)
    # submit commands to the engine
    print(','.join(commands))

    # now we end our turn
    agent.end_turn()

