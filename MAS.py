import random
import matplotlib.pyplot as plt


class MAS:

    def __init__(self, numberOfAgents, numberOfDeceptiveAgents, rounds):

        self.numberOfAgents = numberOfAgents
        self.numberOfDeceptiveAgents = numberOfDeceptiveAgents
        self.rounds = rounds

        self.agentList = []   # the list gathering all the agents in the model

        self.currentRound = 0

        self.credibility = [0.5]   # this is recording the credibility evolution of the agent 2
        self.successesRate = [0]   # this is recording the success rate of each agent of the agent at stake
        self.agentCredits = [1]    # this is recording the credits of the agent at stake


        # adding agents to the model
        # --------------------------

        for i in range( int(self.numberOfAgents / 2) ):
            self.agentList.append( Agent(i, 0.9) )    # half of the  agents in the model provide 'good quality' services with a tendancy of 0.9

        for i in range( int(self.numberOfAgents /2) , self.numberOfAgents):
            self.agentList.append( Agent(i, 0.1) )    # the other half of the agents provide 'bad quality' services with a tendancy of 0.1

        #random.shuffle(self.agentList)       # shuffling the list of agents


        # distributing deceptive agents in the model -- agents providing falsehood testimonies
        # ------------------------------------------------------------------------------------

        otherAgents = [agent for agent in self.agentList if agent is not self.agentList[2]]  # other agents rather than the second agent

        randomDeceptives = random.sample(otherAgents, self.numberOfDeceptiveAgents)   # choosing random deceptive agents in the model

        for agent in randomDeceptives:
            agent.deception = True


        self.agentList[2].deception = True  # here the agent is no longer reliable as a witness


        self.run()


    def run(self):
        '''
        This method is running the model for a certain number of rounds
        '''

        for i in range(self.rounds):
            self.currentRound += 1
            self.runOnce()


    def runOnce(self):
        '''
        This method is picking up a random agent to represent the client of the round
        '''

        chosenAgent = random.choice(self.agentList)
        while chosenAgent.credits < 0.2:    # the agent has to gather enough credits to request for testimonies
            chosenAgent = random.choice(self.agentList)

        chosenAgent.step(self)  # running the agent

        agent = self.agentList[2]  # the agent for whom we want to track the evolution of credibility
        self.credibility.append(agent.credibility)   # adding current credibility to the list of credibility evolution
        #self.successesRate.append(agent.rate)
        #self.agentCredits.append(agent.credits)





# Running the model

# For credibility diagrams

# averageCredibility = []
#
# for i in range(200):
#     N =  100
#     model = MAS (10, 0, N)    # creating a model of 10 agents, no deceptive witnesses, run for 100 rounds = 100 steps
#     y = model.credibility
#     #y = model.successesRate
#     average = sum(y) / 101    # because the list contains an initial value of 0.5
#     averageCredibility.append(average)
#
#
# plt.hist(averageCredibility, bins = 10)
#
# plt.xlabel('Average credibility')
# plt.ylabel('Number of rounds of 100 steps')
# plt.title('Average credibility of the agent 2 : reliable witness')


# For success rate and agents credits

N =  300
model = MAS (10, 0, N)    # creating a model of 10 agents, no deceptive witnesses, run for 100 rounds = 100 steps
y1 = model.successesRate
y2 = model.agentCredits
#y3 = model.credibility
x = range(N + 1)

plt.plot(x, y1 , 'b', label = 'success rate')
plt.plot(x, y2, 'r', label = 'agent credits')
#plt.plot(x, y3, 'y', label = 'credibility')
plt.xlabel('rounds')
plt.ylabel('success rate, agent credits ')
plt.title('success rate of the agent 2 and his credits ')
plt.legend()

plt.grid( axis= 'y', alpha = 0.75)

plt.show()