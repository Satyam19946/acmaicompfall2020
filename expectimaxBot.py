from energium.game_constants import GAME_CONSTANTS, DIRECTIONS
ALL_DIRECTIONS = [DIRECTIONS.EAST, DIRECTIONS.NORTH, DIRECTIONS.WEST, DIRECTIONS.SOUTH]
from energium.kit import Agent
from energium.game_objects import Unit
import sys
import math
import random
import copy

# Create new agent
agent = Agent()

# initialize agent
agent.initialize()

playerID = -1
oppID = -1

#print("My current energium is ", player.energium, file=sys.stderr)
#print("Opponent energium is ", opponent.energium, file=sys.stderr)
# def perp_direction(direction):
#     """Returns a perpindicular direction to current"""
#     if direction == DIRECTIONS.NORTH:
#         return DIRECTIONS.EAST
#     elif direction == DIRECTIONS.EAST:
#         return DIRECTIONS.SOUTH
#     elif direction == DIRECTIONS.SOUTH:
#         return DIRECTIONS.WEST
#     elif direction == DIRECTIONS.WEST:
#         return DIRECTIONS.NORTH

class gameNode:
    def __init__(self, currMap, myPlayer, oppPlayer):
        self.myMap = currMap
        self.myUnits = myPlayer.units
        self.oppUnits = oppPlayer.units
        self.myPlayer = myPlayer
        self.oppPlayer = oppPlayer
        self.children = []
        self.commands = []

    # Get the score of the current gameNode
    def get_score(self):
        myScore = 0
        oppScore = 0
        for unit in self.myUnits:
            myScore += self.myMap.get_tile_by_pos(unit.pos).energium
            myScore += 60
            if (unit.pos.x,unit.pos.y) in self.myPlayer.bases:
                myScore += 20

        for unit in self.oppUnits:
            oppScore += self.myMap.get_tile_by_pos(unit.pos).energium
            oppScore += 60
            if (unit.pos.x,unit.pos.y) in self.oppPlayer.bases:
                oppScore += 20
        
        return self.commands, myScore - oppScore

    # Check if the current gameNode is terminal or not
    def is_terminal(self):
        print(len(self.children),file=sys.stderr)
        if len(self.children) <= 0:
            return True

# Execute the current commands and get a new gameNode.
def execute_commands(parentNode, commands):
    childNode = gameNode(parentNode.myMap, parentNode.myPlayer, parentNode.oppPlayer)
    childNode.commands = commands
    for command in commands:
        type_of_command = command[0]
        if type_of_command == "b":
            details = command[1].split()
            x = details[1]
            y = details[2]
            unitCreated = Unit(gameNode.myPlayer.team, 0, x, y, agent.turn, agent.turn)
            childNode.myPlayer.units.append(unitCreated)
    
    for unit in childNode.myPlayer.units:
        unit.match_turn += 1
    for unit in childNode.oppPlayer.units:
        unit.match_turn += 1
        
    return childNode


def build_tree(gameNode, depth):
    if depth == 0:
        return
    
    # add commands to be executed.
    copyNode = copy.deepcopy(gameNode)
    tempCommands1 = []
    tempCommands2 = []
    # First - to add an unit or not to add an unit.
    for bases in copyNode.myPlayer.bases:
        if copyNode.myPlayer.energium >= 50:
            tempCommands1.append(("b",copyNode.myPlayer.bases[0].spawn_unit()))
            copyNode.myPlayer.energium -= 50
    
    child = execute_commands(copyNode, tempCommands1)
    build_tree(child,depth-1)
    gameNode.children.append(child)

    # First child let all units stay where they are and spawn a unit

    # Second - for all the units which direction does each unit take


def minimax_alpha_beta(gameNode, alpha, beta):
    #print(alpha, beta, file=sys.stderr)
    bestCommands = []

    if gameNode.is_terminal():
        #print("Cant get terminal node")
        return gameNode.get_score()

    #This is the max
    elif gameNode.myPlayer.team == playerID:
        for n in gameNode.children:
            commandsTook, valueReturned = minimax_alpha_beta(gameNode, alpha, beta)
            if value < valueReturned:
                bestCommands = commandsTook
                value = valueReturned
            alpha = max(value, alpha)
            if alpha >= beta:
                break
        return bestCommands, value

    # This is the min player
    elif gameNode.myPlayer.team == oppID:
        for n in gameNode.children:
            commandsTook, valueReturned = minimax_alpha_beta(gameNode, alpha, beta)
            if valueReturned <= value:
               value = valueReturned
               bestCommands = commandsTook
            beta = min(value, beta)
            if beta <= alpha:
                break
        return bestCommands, value

    else:
        print("This shouldnt happen", file=sys.stderr)
        return

# Once initialized, we enter an infinite loop
while True:

    # wait for update from match engine
    agent.update()

    commands = []

    player = agent.players[agent.id]
    playerID = agent.id
    opponent = agent.players[(agent.id + 1) % 2]
    oppID = (agent.id+1) % 2
    ### AI Code goes here ###
    alpha = -math.inf
    beta = math.inf
    root = gameNode(agent.map, player, opponent)
    print("reached here", file=sys.stderr)
    build_tree(root,1)
    commands, value = minimax_alpha_beta(root, alpha, beta)
    print("Commands returned are {}".format(commands), file=sys.stderr)

    ### AI Code ends here ###

    #print("The current commands are ", commands, file=sys.stderr)
    # submit commands to the engine
    print(','.join(commands))

    # now we end our turn
    agent.end_turn()

