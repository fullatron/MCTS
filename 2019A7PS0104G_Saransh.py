import numpy as np
from math import log, sqrt
import pickle

top_list=[]
state=[]

#class to maintain a tree
class node:
    def __init__(self) -> None:
        self.node_win=0
        self.node_total=0
        self.children=[]
        self.success=[0,0,0,0,0]
        
    def makechildren(self):
        self.children=[node(),node(),node(),node(),node()]


def find_winner(state,row=6,column=5):
    #vertical
    for i in range(column):
        count=1
        player=0
        for j in range(1,row):
            if state[j][i]==state[j-1][i] and state[j][i]!=0:
                count+=1
                player=state[j][i]
            else:
                count=1
            if count>=4:
                return player
    #horizontal
    for i in range(row):
        count=1
        player=0
        for j in range(1,column):
            if state[i][j]==state[i][j-1] and state[i][j]!=0:
                count+=1
                player=state[i][j]
            else:
                count=1
            if count>=4:
                return player
    
    for i in range(row):
        for j in range(column):
            if state[i][j]==0:
                continue
            else:
                count=1
                for k in range(1,4):
                    try:    
                        if state[i][j]==state[i+k][j+k]:
                            count+=1
                        else:
                            break
                    except IndexError:
                        break
                    if(count==4):
                        return state[i][j]
    
    for i in range(row):
        for j in range(column):
            if state[i][j]==0:
                continue
            else:
                count=1
                for k in range(1,4):
                    try:    
                        if state[i][j]==state[i-k][j+k] and i-k>=0:
                            count+=1
                        else:
                            break
                    except IndexError:
                        break
                    if(count==4):
                        return state[i][j]

    return 0

def updatestate(state,action,player):
    i=0

    while i<6 and state[i][action]==0:
        i+=1
    i=i-1

    state[i][action] = player

def returnupdatedstate(state,action,player):
    updatedstate=[row[:] for row in state]
    i=0

    while i<6 and updatedstate[i][action]==0:
        i+=1
    i=i-1

    updatedstate[i][action] = player
    return updatedstate

# code to finde winner (if any)
def update_state_common(state,column,playernumber,top_list):
    top_list[column]-=1
    #print(column, top_list, playernumber, state)
    state[top_list[column]][column]=playernumber
    return state

#MCT that can maintain a tree, simulate itself, pick actions, update tree for next move
class MCT:
    def __init__(self, simulation_count, playernumber):
        self.simulation_count = simulation_count
        self.root=node()
        self.root.makechildren()
        self.player=playernumber
        self.state= [[0,0,0,0,0] for _ in range(6)]


        for i in self.root.children:
            i.makechildren()
            for j in i.children:
                j.makechildren()

    def simulate(self,state):
        for i in range(self.simulation_count):
            simulation=[]
            #print("i = ", i, " ", self.simulation_count)
            for k in range(6):
                for j in range(5):
                    self.state[k][j]=state[k][j]
            win_status=find_winner(self.state)
            self.position=self.root
            moves=0
            while (win_status==0) and moves<30:
                moves+=1
                move=self.pick_move() #column number
                simulation.append(move)
                
                if moves%2==1:
                    updatestate(self.state,move,self.player)
                else:
                    updatestate(self.state,move,(self.player%2)+1)
                win_status=find_winner(self.state)
                if self.position.children==[]:
                    continue
                self.position=self.position.children[move]
            self.position = self.root
            if win_status==(self.player%2)+1:
                self.position.node_win+=1
            self.position.node_total+=1
            
            for k in range(len(simulation)):
                try:
                    self.position=self.position.children[simulation[k]]
                except:
                    self.position.makechildren()
                    self.position=self.position.children[simulation[k]]
                self.position.node_total+=1
                if (k%2==0) and win_status == self.player:
                    self.position.node_win+=1
                elif (k%2==1) and win_status !=self.player:
                    self.position.node_win+=1
                if len(self.position.children)==0:
                    break
            #create simulations based on some algo or randomly
            #plan : use algo

    def pick_move(self):
        if self.position.children == []: #this needs to be corrected 
            return (np.random.choice(range(5)))
        c = 1.4
        weights = [777 if self.position.node_total==0 or  i.node_total==0 else (i.node_win/i.node_total+ sqrt(log(self.position.node_total)/i.node_total)) for i in self.position.children]

        for i in range(5):           #may be wrong  :corrected
            if self.state[0][i]!=0:
                weights[i]=0

        index_min = np.argmax(weights)
        return index_min
        #pick action based on some algo or greedy
        #plan : UCT
        #returns an int between 0 and 4


    def move(self, state, top_list):
        print('Player ',self.player,' (MCTS with', self.simulation_count, 'playouts)')
        self.simulate(state)
        success=[]
        for x in range(5):
            i=self.root.children[x]
            if top_list[x]>0:
                if i.node_total!=0:
                    success.append(i.node_win/i.node_total)
                else:
                    success.append(0)
            else:
                success.append(0)
            #print(i.node_win, "  ", i.node_total)
        #print("success : ", success)
        #print(success)
        val=np.argmax(success)
        #print("value : ", val)
        print('Action selected :', val)
        
        return val

    def update_state(self,state,move):
        for i in range(6):
            for j in range(5):
                self.state[i][j]=state[i][j]
        if self.root.children==[]:
            self.root.makechildren()
            for i in self.root.children:
                i.makechildren()
                for j in i.children:
                    j.makechildren()
        self.root=self.root.children[move]

reward={}

def linearize(state, rows=6, columns=5):
    linearstate=[]
    for i in range(rows*columns):
        linearstate.append(0)
    for i in range(rows):
        for j in range(columns):
            linearstate[(i*columns)+j]=state[i][j]
    str1 = "" 
    for ele in linearstate: 
        str1 += str(ele)  
    return str1  


def QPlay(count1=5, rows=6, columns=5):
    files=open("2019A7PS0104G_saransh.dat", "rb")
    reward=pickle.load(files)
    files.close()
    num_of_plays=0
    p1=MCT(count1,1)
    top_list=[rows,rows,rows,rows,rows]
    move=0
    state = [[0,0,0,0,0],
             [0,0,0,0,0],
             [0,0,0,0,0],
             [0,0,0,0,0],
             [0,0,0,0,0],
             [0,0,0,0,0]]

    linear=[]
    linearnew=[]

    while num_of_plays!=30:

        num_of_plays+=1

        move=p1.move(state,top_list)
        #print("num of plays: ",num_of_plays ,state)
        state=update_state_common(state,move,1,top_list)
        #print("num of plays: ",num_of_plays)
        result = find_winner(state)
        PrintGrid(state)

        if result==1:                       #loss
            reward[linearnew]=-5
            maxReward=-5
            for j in range(columns):
                checkstate=returnupdatedstate(oldstate,j,1)
                linearcheckstate=linearize(checkstate)
                if linearcheckstate in reward and reward[linearcheckstate]>maxReward:
                    maxReward=reward[linearcheckstate]
                else:
                    res=find_winner(checkstate)
                    if res==0:
                        maxReward= max(maxReward,0)
                    elif res==1:
                        maxReward=max(maxReward,-5) 
                    elif res==2:
                        maxReward=max(maxReward,10)
            if linear not in reward:
                reward[linear]=0
            reward[linear]+= 0.1*(-5 - reward[linear] + maxReward)
            break

        elif result==2:                          #win
            reward[linearnew]=10
            maxReward=10
            for j in range(columns):
                checkstate=returnupdatedstate(oldstate,j,2)
                linearcheckstate=linearize(checkstate)
                if linearcheckstate in reward and reward[linearcheckstate]>maxReward:
                    maxReward=reward[linearcheckstate]
            if linear not in reward:
                reward[linear]=0
            reward[linear]= reward[linear] + 0.1*(10 - reward[linear] + maxReward)
            break
        
        if num_of_plays==30:
            break

        num_of_plays+=1
        move=-1
        linear=linearize(state)
        oldstate = [row[:] for row in state]
        weight=[]

        for j in range(columns):
            weight.append(0)
            #print(state, j)
            if(state[0][j]!=0):
                weight[j]=-100
            else:
                weight[j]=0.01         #legal move
                tempstate=returnupdatedstate(state,j,2)
                linear=linearize(tempstate)
                
                if linear in reward:
                    weight[j]=reward[linear]

        move=np.argmax(weight)
        #print("num of plays: ",num_of_plays ,state)
        state=update_state_common(state,move,2,top_list)
        #print("num of plays: ",num_of_plays )
        #PrintGrid(state)
        result = find_winner(state)
        linearnew=linearize(state)
        print('Player 2 (Q-learning)')
        print('Action selected :',move)
        PrintGrid(state)


        if result==0:
            continue

        elif result==1:                       #loss
            reward[linearnew]=-5
            maxReward=-5
            for j in range(columns):
                checkstate=returnupdatedstate(oldstate,j,2)
                linearcheckstate=linearize(checkstate)
                if linearcheckstate in reward and reward[linearcheckstate]>maxReward:
                    maxReward=reward[linearcheckstate]
            if linear not in reward:
                reward[linear]=0
            reward[linear]+= 0.1*(-5 - reward[linear] + maxReward)
            break

        elif result==2:                          #win
            reward[linearnew]=10
            maxReward=10
            for j in range(columns):
                checkstate=returnupdatedstate(oldstate,j,2)
                linearcheckstate=linearize(checkstate)
                if linearcheckstate in reward and reward[linearcheckstate]>maxReward:
                    maxReward=reward[linearcheckstate]
                else:
                    res=find_winner(checkstate)
                    if res==0:
                        maxReward= max(maxReward,0)
                    elif res==1:
                        maxReward=max(maxReward,-5) 
                    elif res==2:
                        maxReward=max(maxReward,10)
            if linear not in reward:
                reward[linear]=0
            reward[linear]+= 0.1*(10 - reward[linear] + maxReward)
            break
        
        oldstate = [row[:] for row in state]
    print("num of plays: ",num_of_plays)
    PrintGrid(state)
    files=open("2019A7PS0104G_saransh.dat", "wb")
    pickle.dump(reward, files)
    files.close()
    res=find_winner(state)
    return res


#driver code to run the simulations
def play(count1,count2): #half of the times count of p1 is 40 and half of the times it is 200
    p1=MCT(count1,1)
    p2=MCT(count2,2)
    num_of_plays=0
    top_list=[6,6,6,6,6]

    state = [[0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0],
            [0,0,0,0,0]]
    

    while num_of_plays!=30:
        num_of_plays+=1
        move=p1.move(state,top_list)
        #print("error yaha tha " , top_list[move])
        state=update_state_common(state,move,1,top_list)
        PrintGrid(state)
        #input()

        p1.update_state(state,move)
        p2.update_state(state,move)

        #update curr_state
        result = find_winner(state)
        
        if result:
            #print("Player won: ", result)
            break
        
        num_of_plays+=1  
        move=p2.move(state,top_list)
        state=update_state_common(state,move,2,top_list)
        PrintGrid(state)
        #input()
        p1.update_state(state,move)
        p2.update_state(state,move)
        result = find_winner(state)
        
        if result:
            #print("Player won: ", result)
            break
    #PrintGrid(state) 
    result = find_winner(state)
    return result


def PrintGrid(positions):
    print('\n'.join(' '.join(str(x) for x in row) for row in positions))


def MCTSvMCTS():
    count11=0
    count12=0
    count10=0
    count21=0
    count22=0
    count20=0
    for i in range(10):
        ans=play(40,200)
        #print("player ", ans, "won")
        #input()
        if ans==1:
            count11+=1
        elif ans==2:
            count12+=1
        else:
            count10+=1
    for i in range(10):
        ans=play(200,40)
        #print("player ", ans, "won")
        #input()
        if ans==1:
            count22+=1
        elif ans==2:
            count21+=1
        else:
            count20+=1
    print("In the first half : ")
    print("\tMCTS40 wins : ",count11)
    print("\tMCTS200 wins : ",count12)
    print("\tTies : ",count10)
    print("In the second half : ")
    print("\tMCTS40 wins : ",count21)
    print("\tMCTS200 wins : ",count22)
    print("\tTies : ",count20)
    print("Overall result : ")
    print("\tMCTS40 wins : ",count21+count11)
    print("\tMCTS200 wins : ",count22+count12)
    print("\tTies : ",count20+count10) 
    return 0

def parta():
    x=0
    x=play(200,40)
    if x==0:
        print("Game Draw!")
        return
    print("Player",x , "won!")

def partb():
    x=0
    one =0
    two=0
    d=0

    for i in range(1000):
        x=QPlay(10)
        if(x==0):
            d+=1
        if x==1:
            one+=1
        if x==2:
            two+=1
    print("Total number of matches that were draw:", d)
    print("Total number of matches that MCTS won:", one)
    print("Total number of matches that QLearning won:", two)

def partc():
    x=QPlay(10)
    
    if x==0:
        print("Game Draw!")
        return
    print("Player",x , "won!")

def main():

    print("Enter 1 for part a and 2 for part b: ")
    x=input()
    
    if x=="1":
        parta()
    if x=="2":
        partc()


if __name__=='__main__':
    main()