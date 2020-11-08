from energium.game_constants import GAME_CONSTANTS, DIRECTIONS
ALL_DIRECTIONS = [DIRECTIONS.EAST, DIRECTIONS.NORTH, DIRECTIONS.WEST, DIRECTIONS.SOUTH]
from energium.kit import Agent
from energium.position import Position
import sys
import math
import random

# Create new agent
agent = Agent()

# initialize agent
agent.initialize()

# Spawn alternatively on each base.
base_to_spawn = 0


#print("My current energium is ", player.energium, file=sys.stderr)
#print("Opponent energium is ", opponent.energium, file=sys.stderr)

#Find 3 safe spots in your own quadrant
safe_spot = []
base_chose = []
def nearestPosEmpTileDir(unit, player, opponent, agent):
    north, south, west, east = None,None,None,None
    northTile, southTile, westTile, eastTile = None,None,None,None
    canGoNorth, canGoSouth, canGoWest, canGoEast = False,False,False,False
    if unit.pos.x + 1 < agent.mapWidth:
        east = Position(unit.pos.x+1,unit.pos.y)
        eastTile = agent.map.get_tile_by_pos(east)
        canGoEast = True

    if unit.pos.y + 1 < agent.mapHeight:
        south = Position(unit.pos.x,unit.pos.y+1)
        southTile = agent.map.get_tile_by_pos(south)
        canGoSouth = True

    if unit.pos.x - 1 >= 0:
        west = Position(unit.pos.x-1,unit.pos.y)
        westTile = agent.map.get_tile_by_pos(west)
        canGoWest = True

    if unit.pos.y - 1 >= 0:
        north = Position(unit.pos.x,unit.pos.y-1)
        northTile = agent.map.get_tile_by_pos(north)
        canGoNorth = True

    for oppUnit in opponent.units:
        if north and north.equals(oppUnit.pos):
            canGoNorth = False
            if oppUnit.get_breakdown_level() > unit.get_breakdown_level():
                return DIRECTIONS.NORTH
        if south and south.equals(oppUnit.pos):
            canGoSouth = False 
            if oppUnit.get_breakdown_level() > unit.get_breakdown_level():
                return DIRECTIONS.SOUTH
            
        if west and west.equals(oppUnit.pos):
            canGoWest = False
            if oppUnit.get_breakdown_level() > unit.get_breakdown_level():
                return DIRECTIONS.WEST

        if east and east.equals(oppUnit.pos):
            canGoEast = False
            if oppUnit.get_breakdown_level() > unit.get_breakdown_level():
                return DIRECTIONS.EAST

    
    for oppUnit in player.units:
        if north and north.equals(oppUnit.pos):
            canGoNorth = False

        if south and south.equals(oppUnit.pos):
            canGoSouth = False 
            
        if west and west.equals(oppUnit.pos):
            canGoWest = False
            
        if east and east.equals(oppUnit.pos):
            canGoEast = False
            
    if canGoNorth:
        return DIRECTIONS.NORTH
    
    if canGoEast:
        return DIRECTIONS.EAST
    
    if canGoWest:
        return DIRECTIONS.WEST
    
    if canGoSouth:
        return DIRECTIONS.SOUTH
    

def collisionHappens(unit, posReached, player, opponent):
    #print("This was called ", file=sys.stderr)
    for unitopp in opponent.units:
        if unitopp.pos.equals(posReached):
            return True
    
    for unitopp in player.units:
        if unitopp.pos.equals(posReached) and unit != unitopp:
            return True

    return False

def negativeTile(positionReached):
    if agent.map.get_tile_by_pos(positionReached).energium < 0:
        return True
    else:
        return False

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


    energium_here = []
    
    opponentUnitsPos = []
    for unit in opponentUnits:
        opponentUnitsPos.append((unit.pos.x, unit.pos.y))

    myUnitsPos = []
    for unit in myUnits:
        myUnitsPos.append((unit.pos.x, unit.pos.y))

    opponentSpawned = False
    for oppUnit in opponent.units:
        if oppUnit.get_breakdown_level() == 1:
            opponentSpawned = True
            break

    # if safe_spot_taken < len(safe_spot) and safe_spot[safe_spot_taken] and safe_spot_taken <= 3 and player.energium >= 50:
    #     if safe_spot[safe_spot_taken][4]:


    maxEnergium = -math.inf
    for y in range(mapHeight):
        for x in range(mapWidth):
            if maxEnergium < mymap.get_tile(x,y).energium:
                maxEnergium = mymap.get_tile(x,y).energium
            energium_here.append([mymap.get_tile(x,y).energium,y,x,mymap.get_tile(x,y)])

    energium_here.sort(reverse=True)
    print(energium_here[:5],file=sys.stderr)
    print(maxEnergium,file=sys.stderr)
    # Spawn opposite to opponent
    maxBaseDist = -math.inf
    baseToSpawnOn = None
    if opponentSpawned:
        for aBase in player.bases:
            dis = opponent.units[-1].pos.distance_to(aBase.pos)
            if dis > maxBaseDist:
                baseToSpawnOn = aBase
                maxBaseDist = dis

    if (not baseToSpawnOn) and ((player.energium - opponent.energium >= 100) or (len(opponent.units) > len(player.units) and player.energium >= 50)):
        baseToSpawnOn = player.bases[base_to_spawn % len(player.bases)]
        base_to_spawn += 1

    if baseToSpawnOn:
        commands.append(baseToSpawnOn.spawn_unit())

    copyMyUnits = player.units.copy()
    
    search_in = energium_here.copy()
    sent_to = []
    unit_here = []
    for unit in player.units:
        unit_here.append((unit.pos.x,unit.pos.y))
    #energium_here.append([mymap.get_tile(x,y).energium,y,x,mymap.get_tile(x,y)])
    for unit in player.units:
        maximum_energium_got = -math.inf
        maximum_energium_could_be = search_in[0][0]
        dist = math.inf
        point = None
        q = [(unit.pos.x,unit.pos.y)]
        current = q[0]
        visited = [current]
        while len(q) and agent.map.get_tile(current[0],current[1]).energium != maximum_energium_could_be:
            q = q[1:]
            positionsToAdd = [(current[0]+1,current[1]),(current[0],current[1]+1),(current[0]-1,current[1]),(current[0]-1,current[1])]
            for add in positionsToAdd:
                if add[0] >= 0 and add[0] < agent.mapWidth and add[1] >= 0 and add[1] < agent.mapHeight:
                    if (add[0],add[1]) not in q and (add[0],add[1]) not in visited and (add[0],add[1]) not in sent_to:
                            visited.append((add[0],add[1]))
                            q.append((add[0],add[1]))
            #print(q,positionsToAdd,file=sys.stderr)
            if q:
                current = q[0]
                visited.append(current)

        sent_to.append((current[0],current[1]))
        current = Position(current[0],current[1])
        point = current
        print("unit is on", unit.pos.x, unit.pos.y, file=sys.stderr)
        print(current.x,current.y,"was removed", "energium = ", agent.map.get_tile_by_pos(current).energium, file=sys.stderr)
        search_in.remove([mymap.get_tile(current.x,current.y).energium,current.y,current.x,mymap.get_tile(current.x,current.y)])
        print(search_in[0:5],file=sys.stderr)
        direction_to_take = None
        if point:
            direction_to_take = unit.pos.direction_to(current)
        if direction_to_take:
            # position_reached = unit.pos.translate(direction_to_take,1)
            # if collisionHappens(unit, position_reached, player, opponent):
            #     direction_to_take = nearestPosEmpTileDir(unit,player,opponent,agent)
            #     #print("This was the nearest Direction = {}".format(direction_to_take),file=sys.stderr)
            #     if direction_to_take:
            #         commands.append(unit.move(direction_to_take))
            #         copyMyUnits.remove(unit)
            # # elif negativeTile(position_reached):
            # #     direction_to_take2 = nearestPosEmpTileDir(unit,player,opponent,agent)
            # #     # MAke sure its not in a loop
            # #     if direction_to_take2:
            # #         posnew = unit.pos.translate(direction_to_take2,1)
            # #         newdir = posnew.direction_to(point[3].pos)
            # #         if posnew.translate(newdir,1).equals(position_reached):
            # #             commands.append(unit.move(direction_to_take))
            # #         else:
            # #             commands.append(unit.move(direction_to_take2))
            # else:
            commands.append(unit.move(direction_to_take))
            copyMyUnits.remove(unit)

    # for unit in player.units:
    #     for base in player.bases:
    #         if unit.pos.equals(base.pos) and unit.last_repair_turn > 4:
    #             gohere = nearestPosEmpTileDir(unit,player,opponent,agent)
    #             if gohere:
    #                 commands.append(unit.move(gohere))

    
    copyMyUnits2 = myUnits.copy()

    # for reachPoint in copyMyUnits:



    # i = 0
    # while i < len(energium_here):
    #     reachPoint = energium_here[i]
    #     # For the point with the highest energium get the unit which has the least distance compared to opponent units.
    #     # Repeat for all
    #     if len(copyMyUnits) == 0:
    #         break
    #     unitToMove = None
    #     unitMoved = False
    #     minDistanceFromMe = math.inf
    #     minDistanceFromOpp = math.inf
    #     for unit in copyMyUnits:
    #         start = unit.pos
    #         if unit.pos.equals(reachPoint[3].pos):
    #             copyMyUnits.remove(unit)
    #             i += 1
    #             if i < len(energium_here):
    #                 reachPoint = energium_here[i]
    #                 continue
    #             else:
    #                 break
    #         distance = start.distance_to(reachPoint[3].pos)    
    #         if distance < minDistanceFromMe:
    #             unitToMove = unit
    #             minDistanceFromMe = distance
    #     for unit in opponent.units:
    #         distance = unit.pos.distance_to(reachPoint[3].pos)
    #         if distance < minDistanceFromOpp:
    #             minDistancFromOpp = distance
    #     if unitToMove and minDistanceFromOpp >= minDistanceFromMe:
    #         direction_to_take = unitToMove.pos.direction_to(reachPoint[3].pos)
    #         if direction_to_take:
    #             position_reached = unitToMove.pos.translate(direction_to_take,1)
    #             if collisionHappens(unitToMove, position_reached, player, opponent):
    #                 direction_to_take = nearestPosEmpTileDir(unitToMove,player,opponent,agent)
    #                 print("This was the nearest Direction = {}".format(direction_to_take),file=sys.stderr)
    #                 if direction_to_take:
    #                     commands.append(unitToMove.move(direction_to_take))
    #                     copyMyUnits.remove(unitToMove)
    #             elif negativeTile(position_reached):
    #                 direction_to_take2 = nearestPosEmpTileDir(unitToMove,player,opponent,agent)
    #                 # MAke sure its not in a loop
    #                 if direction_to_take2:
    #                     posnew = unitToMove.pos.translate(direction_to_take2,1)
    #                     newdir = posnew.direction_to(reachPoint[3].pos)
    #                     if posnew.translate(newdir,1).equals(position_reached):
    #                         commands.append(unitToMove.move(direction_to_take))
    #                     else:
    #                         commands.append(unitToMove.move(direction_to_take2))
    #                     copyMyUnits.remove(unitToMove)
    #             else:
    #                 commands.append(unitToMove.move(direction_to_take))
    #                 copyMyUnits.remove(unitToMove)
    #     i += 1

                
    #After a unit reaches 20 breakdown level send it to nearest base.
    # for unit in copyMyUnits2:
    #     if unit.get_breakdown_level() == 60:
    #         collision_Happen = False
    #         minDis, baseReq = [math.inf, None]
    #         for couldBeBase in myBases:
    #             if unit.pos.distance_to(couldBeBase.pos) < minDis:
    #                 minDis = unit.pos.distance_to(couldBeBase.pos)
    #                 baseReq = couldBeBase
    
    #         direction_to_take = unit.pos.direction_to(baseReq.pos)
    #         if direction_to_take:
    #             # Tile reached would be
    #             pos_reached = unit.pos.translate(direction_to_take,1)
    #             collision_happen = collisionHappens(unit, pos_reached, player, opponent)
    #             if collision_happen == False:
    #                 commands.append(unit.move(direction_to_take))
    #             else:
    #                 direc = nearestPosEmpTileDir(unit,player,opponent,agent)
    #                 if direc:
    #                     commands.append(unit.move(direc))


    ### AI Code ends here ###


    #print("The current commands are ", commands, file=sys.stderr)
    # submit commands to the engine
    print(','.join(commands))

    # now we end our turn
    agent.end_turn()

