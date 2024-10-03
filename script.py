from openai import OpenAI
import random

newRoomId = 0
invntCreateId = 0

client = OpenAI(
    api_key=input('ChatGPT API Key: ')
)

system_data = [
    {"role": "system", "content": "Generate different parts of a text adventure such as the title, a room, or a new item. You must only name the requested item and not ramble about why you chose that name or value. Make sure to be creative, and not forget to make rooms based on their predecesors."}
]


def createResponse(prompt):
    system_data.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=system_data
    )
    assistant_response = response.choices[0].message.content
    system_data.append({"role": "assistant", "content": assistant_response})
    # print("Assistant: "+assistant_response)
    return(assistant_response)

title = createResponse('Text Adventure Name').upper()


lootTables = [
    # Table 0
    []
]

world = []


def generateRoom(n=-1, s=-1, e=-1, w=-1):
    print('~~~~~~~~~~')
    print('ChatGPT is generating a new room...')
    print('~~~~~~~~~~')
    pos = len(world)
    self = {
        "name": createResponse('Room ' + str(pos) + ' name/title'),
        "desc": createResponse('Room ' + str(pos) + ' short description'),
        "look": createResponse('Room ' + str(pos) + ' look closer short description'),
        "npc": {"name": '', "dial": ['']},
        "mnstrs": [],
        "loot": 0,
        "exits": ['N', 'S', 'E', 'W'],
        "next": [n, s, e, w]
    }
    if random.randint(1, 2) == 1 and pos != 0:
        monster = {"name": createResponse('Monster ' + str(pos) + ' name for room ' + str(pos)), "health": int(createResponse('Monster ' + str(pos) + ' health (INTEGER ONLY)')), "damage": [int(createResponse('Monster ' + str(pos) + ' damage minimum (INTEGER ONLY)')), int(createResponse('Monster ' + str(pos) + ' damage maximum (INTEGER ONLY)'))], "drops": [generateItem(), generateItem(), generateItem()], "respawn": createResponse('Monster ' + str(pos) + ' can respawn? (True/False ONLY)')}
        self['mnstrs'].append(monster)
    elif round(random.randrange(10, 25)/10) == 1 or pos == 0:
        self['npc'] = {'name': createResponse('Room ' + str(pos) + ' NPC name'), 'dial': [createResponse('Room ' + str(pos) + ' NPC short dialogue'), createResponse('Room ' + str(pos) + ' NPC short dialogue'),
                                          createResponse('Room ' + str(pos) + ' NPC short dialogue'), createResponse('Room ' + str(pos) + ' NPC short dialogue')]}
    else:
        self['loot'] = random.randrange(1, len(lootTables))
    return(self)


def generateItem(type=None):
    id = str(invntCreateId)
    if type == None:
        type = random.choice(['food', 'weapon', 'other'])
        notes = ''
        if type == 'other':
            notes = ' no game functionality'
        self = {
            "food": type == 'food',
            "name": createResponse("Inventory Item ("+type+notes+") (singular) #"+id+' name')
        }
    else:
        self = {
            "food": type == 'food',
            "name": createResponse("Inventory Item ("+type+") (singular) #" + id + ' name')
        }
    if self['food'] or type == 'other':
        self['damage'] = [1, 5]
        self['amount'] = random.randint(1, 3)
    else:
        self['damage'] = [int(createResponse("Inventory Item #"+id+' damage minimum (NUMBER ONLY INTEGER FORM)')), int(createResponse("Inventory Item #"+id+' damage maximum (NUMBER ONLY INTEGER FORM)'))]
        self['amount'] = 1
    return self


print('~~~~~~~~~~')
print('ChatGPT is generating loot tables...')
items = random.randint(2, 5)
for n in range(items):
    table = []
    print(str(n+1) + '/' + str(items))
    for i in range(random.randint(2, 5)):
        table.append(generateItem())
    lootTables.append(table)

world.append(generateRoom())


def genLoot(table):
    loot = []
    if table != lootTables[0]:
        while loot == []:
            for i in range(len(table)):
                chance = round(0.6 * len(table))
                chance = round(random.randrange(0, chance))
                chance = chance == 0
                if chance:
                    loot.append(table[i])
    return loot


def wrapText(txt):
    output = ''
    lineI = 0
    for i in range(len(txt)):
        lineI += 1
        output += txt[i]
        if lineI - 40 > 0:
            if txt[i] == ' ':
                lineI = 0
                output += '\n'
    return output


def aAn(txt):
    txt0 = txt[0].lower()
    if txt0 == 'a' or txt0 == 'e' or txt0 == 'o' or txt0 == 'u' or txt0 == 'i':
        return ('an ' + txt)
    else:
        return ('a ' + txt)


class Game:
    def __init__(this, name):
        this.title = name
        this.id = 0
        this.name = world[this.id]['name']
        this.desc = world[this.id]['desc']
        if len(world[this.id]['npc']['dial']) - 1 > 0:
            this.npcId = random.randrange(0, len(world[this.id]['npc']['dial']), 1)
        else:
            this.npcId = 0
        this.npc = {}
        this.npc['name'] = world[this.id]['npc']['name']
        this.npc['dial'] = world[this.id]['npc']['dial'][this.npcId]
        for i in range(len(world[this.id]['mnstrs'])):
            world[this.id]['mnstrs'][i]['dhealth'] = int(str(world[this.id]['mnstrs'][i]['health']))
        this.mnstrs = world[this.id]['mnstrs']
        this.loot = genLoot(lootTables[world[this.id]['loot']])
        this.look = world[this.id]['look']
        this.exits = world[this.id]['exits']
        this.next = world[this.id]['next']
        this.invent = [generateItem('food')]
        this.hand = generateItem('weapon')
        this.health = 100
        print()
        print(this.title)
        print('Text Adventure by ChatGPT')
        print('Type "help" for commands')
        this.whatHere()

    def whatHere(this):
        print()
        print(f'~{this.name}~')
        desc = wrapText(this.desc)
        print(desc)
        # Hand
        handtxt = this.hand['name']
        if this.hand[('food')]:
            handtxt += ' [food]'
        elif this.hand['damage'][1] > 5:
            handtxt+= ' [' + str(this.hand['damage'][0]) + '-' + str(this.hand['damage'][1]) + ' damage]'
        print('> You are holding ' + aAn(handtxt)+' <')
        # Exits
        go = 'Exits:'
        for i in range(len(this.exits)):
            if i == 0:
                go += ' ' + this.exits[i]
            else:
                go += ', ' + this.exits[i]
        print(go)
        print()

        if len(this.mnstrs) > 0:
            for i in range(len(this.mnstrs)):
                print('>> Its a ' + this.mnstrs[i]['name'] + ' with ' + str(this.mnstrs[i]['health']) + ' health! <<')
            print()
            this.fightMonsters()

        this.dialogue()

        this.treasure()

        this.command()

    def help(this):
        print('-Commands-')
        print(' Main:')
        print('  help')
        print('  H / health')
        print('  I / invent (inventory)')
        print(' Move:')
        print('  N / north')
        print('  S / south')
        print('  E / east')
        print('  W / west')
        print(' Actions:')
        print('  L / look')
        print('  T / talk')
        print('  C / carry')
        print('  loot')
        print('  eat')
        print(' Battle:')
        print('  A/Attack')
        print('  F/Flee')

    def addInvent(this, name, amount, damage, food):
        item = {}
        item['name'] = name
        item['amount'] = amount
        item['damage'] = damage
        item['food'] = food
        itemId = -1
        for i in range(len(this.invent)):
            if this.invent[i]['name'] == name:
                itemId = i
                i = len(this.invent)
        if itemId < 0:
            if this.hand['name'] == name:
                this.hand['amount'] += item['amount']
            else:
                this.invent.append(item)
        else:
            this.invent[itemId]['amount'] += item['amount']

    def command(this):
        this.health += round(random.randrange(1, 5))
        if this.health > 100:
            this.health = 100
        if this.health < 35:
            print('Your health is low! Eat food to heal!')
            print()
        user = input('>')
        user = user.lower()

        if user == '':
            print('What?')
            this.command()
        # help
        elif user == 'help':
            print()
            this.help()
            print()
            this.command()
        # invent
        elif user == 'i' or user == 'invent':
            this.inventory()
            print()
            this.command()
        # talk
        elif user == 't' or user == 'talk':
            print()
            if this.npc['dial'] == '':
                print('There is no one to talk to.')
                print()
            this.dialogue()
            this.command()
        # look
        elif user == 'l' or user == 'look':
            this.lookAround()
            this.command()
        # north
        elif user == 'n' or user == 'north':
            this.go(0)
        # south
        elif user == 's' or user == 'south':
            this.go(1)
        # east
        elif user == 'e' or user == 'east':
            this.go(2)
        # west
        elif user == 'w' or user == 'west':
            this.go(3)
        # attack
        elif user == 'a' or user == 'attack':
            print()
            print('There is nothing to attack!')
            print()
            this.command()
        # flee
        elif user == 'f' or user == 'flee':
            def fleeing(txt):
                print()
                print('Fleeing ' + txt + '!')

            prevId = this.id
            if 'N' in this.exits:
                fleeing('north')
                this.go(0)
            elif 'S' in this.exits:
                fleeing('south')
                this.go(1)
            elif 'E' in this.exits:
                fleeing('east')
                this.go(2)
            elif 'W' in this.exits:
                fleeing('west')
                this.go(3)
            else:
                print('I hate to break it to you, but there is nowhere to flee!')
                this.command()
        # health
        elif user == 'h' or user == 'health':
            print()
            print('You have ' + str(this.health) + '/100 health!')
            print()
            this.command()
        # carry
        elif user[0] == 'c' or 'carry' in user:
            item = ''
            itemId = 0
            addingItem = False
            whole = ''
            for i in range(len(user)):
                whole += user[i]
                if addingItem:
                    if not itemId == 0 and not item == ' ':
                        item += user[i]
                    itemId += 1
                else:
                    if i + 1 >= len(user):
                        print()
                        print('No, no, no...')
                        print('Try \"carry ' + this.hand['name'] + '\"')
                        item = 'undefined'
                    else:
                        if whole == 'c' and user[i + 1] != 'a' or whole == 'carry':
                            addingItem = True
            checkingI = True
            for i in range(len(this.invent)):
                if checkingI:
                    name = this.invent[i]['name'].lower()
                    if name == item:
                        hand = this.hand
                        invent = this.invent[i]
                        this.hand = invent
                        this.invent[i] = hand
                        checkingI = False
            if checkingI == True:
                if this.hand['name'].lower() == item:
                    print()
                    print("You're already holding " + aAn(this.hand['name']) + '.')
                else:
                    print()
                    print('You do not have \"' + aAn(item) + '\".')
                    if len(this.invent) > 0:
                        print('Try \"c ' + random.choice(this.invent)['name'].lower() + '\"')
            else:
                this.inventory()
            print()
            this.command()
        # loot
        elif user == 'loot':
            if this.loot != []:
                for i in range(len(this.loot)):
                    loot = this.loot[i]
                    this.addInvent(loot['name'], loot['amount'], loot['damage'], loot['food'])
                world[this.id]['loot'] = 0
                this.loot = []
                this.inventory()
                print()
                print('-Looted Chest-')
            else:
                print()
                print('There is no chest to loot.')
            print()
            this.command()
        # eat
        elif user == 'eat':
            print()
            if this.hand['food']:
                oghealth = this.health
                gain = round(random.randrange(15, 30))
                this.health += gain
                if this.health > 100:
                    this.health = 100
                gain = this.health - oghealth
                this.hand['amount'] -= 1
                print('You gained ' + str(gain) + ' health!')
                if this.health == 100:
                    print('You now have full health!')
                else:
                    print('You now have ' + str(this.health) + '/100 health!')
                if this.hand['amount'] < 1:
                    itemId = round(random.randrange(0, len(this.invent)))
                    this.hand = this.invent[itemId]
                    print('Moved ' + this.invent[itemId]['name'] + ' to hand')
                    this.invent.pop(itemId)
            else:
                print("You're not holding food in your hand!")
                randomItem = random.choice(this.invent)['name'].lower()
                print(f'Try \"c {randomItem}\"')
                print()
            this.command()
        else:
            print('What?')
            this.command()

    def treasure(this):
        if this.loot != []:
            print('~CHEST~')
            for i in range(len(this.loot)):
                display = ''
                if this.loot[i]['amount'] > 1:
                    display += ' ' + str(this.loot[i]['amount']) + ' ' + this.loot[i]['name'] + ' -s'
                else:
                    display += ' ' + str(this.loot[i]['amount']) + ' ' + this.loot[i]['name']
                if this.loot[i][('food')]:
                    display += ' [food]'
                elif this.loot[i]['damage'][1] > 5:
                    display += ' [' + str(this.loot[i]['damage'][0]) + '-' + str(this.loot[i]['damage'][1]) + ' damage]'
                print(display)
            print('Type \"loot\" to move all items to inventory.')
            print()

    def lookAround(this):
        print()
        print(wrapText(this.look))
        print()

    def alive(this):
        if this.health <= 0:
            print()
            print()
            print('-!-!-!-')
            print('You Died')
            print('Restart Window :(')
            print('-!-!-!-')
            exit()

    def go(this, i):
        prev = this.id
        this.id = this.next[i]
        if this.id == -1:
            this.id = len(world)
            world[prev]['next'][i] = this.id

        if this.id >= len(world):
            if i == 0:
                world.append(generateRoom(-1, prev, -1, -1))
            elif i == 1:
                world.append(generateRoom(prev, -1, -1, -1))
            elif i == 2:
                world.append(generateRoom(-1, -1, -1, prev))
            else:
                world.append(generateRoom(-1, -1, prev, -1))

        this.name = world[this.id]['name']
        this.desc = world[this.id]['desc']
        if len(world[this.id]['npc']['dial']) - 1 > 0:
            this.npcId = random.randrange(0, len(world[this.id]['npc']['dial']), 1)
        else:
            this.npcId = 0
        this.npc = {}
        this.npc['name'] = world[this.id]['npc']['name']
        this.npc['dial'] = world[this.id]['npc']['dial'][this.npcId]
        for i in range(len(world[this.id]['mnstrs'])):
            world[this.id]['mnstrs'][i]['dhealth'] = int(str(world[this.id]['mnstrs'][i]['health']))
        this.mnstrs = world[this.id]['mnstrs']
        this.loot = genLoot(lootTables[world[this.id]['loot']])
        this.look = world[this.id]['look']
        this.exits = world[this.id]['exits']
        this.next = world[this.id]['next']
        print()
        print('=====')
        this.whatHere()

    def fightMonsters(this):
        print("You've entered a battle! Use A/Attack, H/Health, or F/Flee!")
        monsters = len(this.mnstrs)
        while monsters > 0:
            for i in range(len(this.mnstrs)):
                monster = this.mnstrs[i]
                if monster['health'] != 'ded':
                    if monster['health'] <= 0:
                        monster['health'] = 'ded'
                        drop = monster['drops'][round(random.randrange(0, len(monster['drops'])))]
                        this.addInvent(drop['name'], drop['amount'], drop['damage'], drop['food'])
                        monsters -= 1
                        print('Killed ' + monster['name'] + '!')
                    else:
                        damage = round(random.randrange(monster['damage'][0], monster['damage'][1]))
                        this.health -= damage
                        print(monster['name'] + ' dealed ' + str(damage) + ' damage!')
            this.alive()
            if monsters > 0:
                user = input('>')
                user = user.lower()
                if user == 'a' or user == 'attack':
                    if len(this.mnstrs) > 0:
                        for i in range(len(this.mnstrs)):
                            monster = this.mnstrs[i]
                            damage = round(random.randrange(this.hand['damage'][0], this.hand['damage'][1]))
                            if monster['health'] != 'ded':
                                monster['health'] -= damage
                                print('You dealed ' + str(damage) + ' damage to ' + monster['name'])
                    print()
                elif user == 'h' or user == 'health':
                    print()
                    print('You have ' + str(this.health) + '/100 health!')
                    print()
                elif user == 'f' or user == 'flee':
                    def fleeing(txt):
                        print()
                        print('Fleeing ' + txt + '!')

                    prevId = this.id
                    if 'N' in this.exits:
                        fleeing('north')
                        this.go(0)
                    elif 'S' in this.exits:
                        fleeing('south')
                        this.go(1)
                    elif 'E' in this.exits:
                        fleeing('east')
                        this.go(2)
                    elif 'W' in this.exits:
                        fleeing('west')
                        this.go(3)
                    else:
                        print('I hate to break it to you, but there is nowhere to flee!')
        print()
        print('>>><<<')
        print('Success!')
        print('You have ' + str(this.health) + '/100 health!')
        print()
        i2 = 0
        for i in range(len(world[this.id]['mnstrs'])):
            if world[this.id]['mnstrs'][i - i2]['respawn'] == False:
                world[this.id]['mnstrs'].pop(i)
                i2 += 1
            else:
                world[this.id]['mnstrs'][i - i2]['health'] = world[this.id]['mnstrs'][i - i2]['dhealth']

    def inventory(this):
        print()
        print('-Inventory-')
        for i in range(len(this.invent)):
            if this.invent[i]['amount'] > 1:
                display = ' ' + str(this.invent[i]['amount']) + ' ' + this.invent[i]['name'] + ' -s'
            else:
                display = ' ' + this.invent[i]['name']
            if this.invent[i][('food')]:
                display+=' [food]'
            elif this.invent[i]['damage'][1] > 5:
                display+=' ['+str(this.invent[i]['damage'][0])+'-'+str(this.invent[i]['damage'][1])+' damage]'
            print(display)
        if len(this.invent) == 0:
            print(' empty')
        print()
        handtxt = this.hand['name']
        if this.hand['amount'] > 1:
            handtxt += 's'
        if this.hand[('food')]:
            handtxt += ' [food]'
        elif this.hand['damage'][1] > 5:
            handtxt+= ' [' + str(this.hand['damage'][0]) + '-' + str(this.hand['damage'][1]) + ' damage]'
        if this.hand['amount'] > 1:
            print('> You have ' + str(this.hand['amount']) + ' ' + handtxt + ' in your hand <')
        else:
            print('> You have ' + aAn(handtxt) + ' in your hand <')

    def dialogue(this):
        if this.npc['dial'] != '':
            if len(world[this.id]['npc']['dial']) - 1 > 0:
                this.npcId = random.randrange(0, len(world[this.id]['npc']['dial']), 1)
            else:
                this.npcId = 0
            this.npc = {}
            this.npc['name'] = world[this.id]['npc']['name']
            this.npc['dial'] = world[this.id]['npc']['dial'][this.npcId]

            print('~' + this.npc['name'] + '~')
            print(wrapText(this.npc['dial']))
            print()


Game(title)
