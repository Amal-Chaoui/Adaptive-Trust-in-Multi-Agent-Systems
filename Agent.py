import random
import math
import numpy as np

class Agent :

    def __init__(self, uniqueId, ethicalTendency):

        self.uniqueId  = uniqueId
        self.deception = False  # this is a boolean
        self.memory = {}  # it will contain agents with their successes and failures in the sight of the agent at stake

        self.credibility = 0.5  # the credibility of all agents is initialised to 0.5
        self.ethicalTendency = ethicalTendency

        self.numberOfSuccesses = 0
        self.memoryFactor = 0.8
        self.numberOfFailures = 0
        self.rate = 0
        self.credits = 1



    def step(self, mas):
        '''
        We will consider at each time that each agent is able to pick only 3 sellers
        '''

        self.time = mas.currentRound * 5  # recording the current time

        potentialSellers = [agent for agent in mas.agentList if agent is not self]  # other agents rather than self
        #sellers = []  # list of randomly choosen sellers
        sellers = random.sample(potentialSellers, 3)  # selecting randomly 4 agents form the list without repetition


        # choosing the sellers
        # for i in range(4):
        #     seller = random.choice(otherAgents)
        #     sellers.append(seller)
        #     otherAgents.remove(seller)

        overallTrustSellers = {}  # dictionary of sellers with their overall BPAs
        directTrustWitnesses = {} # dictionary of 'sellers' with their testifying witnesses and direct BPAs
        indirectTrustWitnesses = {} # dictionary of 'sellers' with their testifying witnesses and indirect BPAs

        potentialWitnesses = [witness for witness in potentialSellers if witness not in sellers]




        for seller in sellers:


            # making place in dictionaries
            directTrustWitnesses[seller] = {}
            indirectTrustWitnesses[seller] = {}

            # choosing the witnesses
            witnesses = [ witness for witness in potentialWitnesses if seller in witness.memory]

            otherWitnesses = [witness for witness in potentialWitnesses if witness not in witnesses ]

            if witnesses == []:
                witnesses = random.sample(otherWitnesses , 2)
            elif len(witnesses) == 1:
                witnesses.append(random.choice(otherWitnesses))



            # testifying
            for witness in witnesses:

                # calculating direct mass function
                directReputation = self.directBpa(witness, seller)  # direct mass function
                if witness.deception :
                    firstTerm = directReputation[1]
                    secondTerm = directReputation[0]
                    thirdTerm = directReputation[2]
                    directReputation = [firstTerm, secondTerm, thirdTerm]

                directTrustWitnesses[seller][witness] = directReputation

            for witness in witnesses:
                # calculating indirect mass function
                #consistency = self.consistency(witness, directTrustWitnesses[seller], seller)
                #certainty = self.certainty(witness, seller)

                confidence = self.confidence(witness, directTrustWitnesses[seller], seller)

                #selfTrustWitness = self.directBpa(self, witness)  # here we are calculating the direct mass function of the client = self regarding the witness

                firstTerm = directTrustWitnesses[seller][witness][0] * confidence # trust
                secondTerm = directTrustWitnesses[seller][witness][1] * confidence # untrust
                thirdTerm = 1 - firstTerm - secondTerm

                indirectReputation = [firstTerm, secondTerm, thirdTerm]
                indirectTrustWitnesses[seller][witness] = indirectReputation

            overallIndirectTrust = self.combiningBpa(indirectTrustWitnesses[seller])  # the overall generated indirect mass function

            selfTrustSeller = self.directBpa(self, seller)  # the direct mass function of the client == self regarding the seller

            psi = 0.7 # the weight of direct trust

            firstTerm = psi * selfTrustSeller[0] + (1 - psi) * overallIndirectTrust[0]   # this if for trust
            secondTerm = psi * selfTrustSeller[1] + (1 - psi) * overallIndirectTrust[1]  # this is for untrust
            thirdTerm = 1 - firstTerm - secondTerm  # this is for uncertainty

            overallBpa = [firstTerm, secondTerm, thirdTerm]

            overallTrustSellers[seller] = overallBpa  # associating the overall trust to the seller at stake


        # ranking the sellers
        listTrustSellers = [overallTrustSellers[seller][0] for seller in overallTrustSellers]
        maxTrust = max(listTrustSellers)

        listMaxTrustSellers = [seller for seller in overallTrustSellers if overallTrustSellers[seller][0] == maxTrust]

        N = len(listMaxTrustSellers)

        if N > 1:
            listUntrustSellers = [overallTrustSellers[seller][1] for seller in listMaxTrustSellers]
            minUntrust = min(listUntrustSellers)
            listMinUntrustSellers = [seller for seller in listMaxTrustSellers if overallTrustSellers[seller][1] == minUntrust]

            bestSeller = random.choice(listMinUntrustSellers)  # the best seller in choosen

        else :
            bestSeller = listMaxTrustSellers[0]  # the best seller is choosen


        listBestSellerWitnesses = [ witness for witness in indirectTrustWitnesses[bestSeller] ]

        ethicalTendency = bestSeller.ethicalTendency   # the ethical tendency of the seller

        feedbackOutcome = np.random.choice( [0, 1], p = [1- ethicalTendency, ethicalTendency])

        # calculating the feedback outcome

        if feedbackOutcome :
            self.numberOfSuccesses += 1

            if bestSeller in self.memory:
                self.memory[bestSeller]["successes"] += 1
            else :
                self.memory[bestSeller] = {"successes" : 1, "failures" : 0}
        else:

            self.numberOfFailures += 1
            if bestSeller in self.memory:
                self.memory[bestSeller]["failures"] += 1
            else:
                self.memory[bestSeller] = {"successes" : 0, "failures" : 1}

        # updating credits of the witnesses testifying for the best seller

        self.updateCredits(indirectTrustWitnesses[bestSeller], bestSeller, feedbackOutcome)
        self.updateRate()


        # if feedbackOutcome:
        #     #self.successes += 1
        #
        #     if seller in self.memory:
        #         self.memory[seller]["currentSatisfaction"] = 1
        #         self.memory[seller]["numberOfInteractions"] += 1
        #     else:
        #         self.memory[seller] = {"histSatisfaction" : 0 ,"currentSatisfaction" : 1, "numberOfInteractions" : 1}
        #
        # else:
        #     #self.failures += 1
        #     if seller in self.memory:
        #         self.memory[seller]["currentSatisfaction"] = 0
        #         self.memory[seller]["numberOfInteractions"] += 1
        #     else:
        #         self.memory[seller] = {"histSatisfaction" : 0 ,"currentSatisfaction" : 0, "numberOfInteractions" : 1}




        # updating the credibility of the witnesses for the best seller

        for witness in directTrustWitnesses[bestSeller]:
            self.updatingCredibility(witness, directTrustWitnesses[bestSeller], bestSeller, feedbackOutcome, overallTrustSellers[bestSeller])



    # main functions
    #---------------


    # generating BPAs
    #----------------


    # With the satisfaction expression defined in the article

    # def directBpa(self, witness, seller):
    #     """
    #     This method is calculating the direct mass function of the witness regarding the seller
    #        Output : directTrust -- [ , , ]
    #     """
    #
    #     if seller in witness.memory:
    #         histSatisfaction = witness.memory[seller]["histSatisfaction"]
    #         currentSatisfaction = witness.memory[seller]["currentSatisfaction"]
    #
    #         delta = abs( histSatisfaction - currentSatisfaction)
    #         c = ( witness.memoryFactor * math.exp(histSatisfaction) ) / ( witness.memoryFactor * math.exp(histSatisfaction) + math.exp(delta) )  # the coefficient c
    #
    #         newSatisfaction = histSatisfaction * c + (1 - c) * currentSatisfaction
    #         witness.memory[seller]["histSatisfaction"] = newSatisfaction
    #         frequency = math.exp(-witness.memory[seller]["numberOfInteractions"] / self.time)
    #
    #         firstTerm = newSatisfaction * frequency
    #         secondTerm = (1 - newSatisfaction) * frequency
    #         thirdTerm = 1 -firstTerm - secondTerm
    #
    #         directTrust = [firstTerm, secondTerm, thirdTerm]
    #     else :
    #         directTrust = [0.45, 0.45, 0.1]
    #
    #     return directTrust


    # With the classical way of defining satisfaction

    def directBpa(self, witness, seller):
        """
        This method is generating the BPA of the seller from the witness' point of view
             Input : the seller and the witness
             Ouput : the bpa in form of [ , , ]
        """

        if seller in witness.memory:
            numberOfSuccesses = witness.memory[seller]["successes"]
            numberOfFailures = witness.memory[seller]["failures"]

            frequency = math.exp(-( numberOfSuccesses + numberOfFailures ) / self.time)

            firstTerm =(numberOfSuccesses / (numberOfSuccesses + numberOfFailures)) * frequency  # Trust
            secondTerm =( numberOfFailures / (numberOfSuccesses + numberOfFailures)) * frequency  # Untrust
            thirdTerm = 1 - firstTerm - secondTerm  # Uncertainty
            bpa = [firstTerm,secondTerm, thirdTerm]

        else:
            bpa = [0.45, 0.45, 0.1]   # the default BPA if no interaction has been made before

        return bpa


    def combiningBpa(self, witnesses):
        '''
        This method is for combining BPAs by Dempster-Shafer rule of combining BPAs

            Input  :  dictionary of witnesses for a certain seller with the BPAs
            Output :  final combined evidence
        '''

        numberOfBpa = len(witnesses)
        listWitnesses = [witness for witness in witnesses]
        finalEvidence = witnesses[listWitnesses[0]]

        for i in range(1, numberOfBpa):
            evidence = witnesses[listWitnesses[i]]
            k = finalEvidence[0] * evidence[1] + finalEvidence[1] * evidence[0]   # degree of conflict
            if k!= 1:
                firstTerm =round( ( finalEvidence[0] * evidence[0] + finalEvidence[0] * evidence[2] + finalEvidence[2] * evidence[0]) * 1/(1 - k), 2)   # this is for Trust (T)
                thirdTerm =round( ( finalEvidence[2] * evidence[2]) * 1/(1 - k), 2)    # much easier to calculate the uncertainty (T,nT)
                secondTerm = 1 - firstTerm - thirdTerm  # this is for untrust (nT)
                finalEvidence = [firstTerm, secondTerm , thirdTerm]

            return finalEvidence


    def distanceOfJousselme(self, bpa1, bpa2):
        '''
        This method is for calculating Jousselme's distance
            Input : BPA 1, BPA 2
            Ouput : number -- the distance
        '''
        bpa1, bpa2 = np.asarray(bpa1), np.asarray(bpa2)   # convert a list to a numpy array
        difference = bpa1 - bpa2  # calculating the difference of the vectors

        matrixD =np.array([ [1, 0, 0.5], [0, 1, 0.5], [0.5, 0.5, 1] ])  # the matrix D defined in the article

        result = np.dot(matrixD, difference)
        result = np.dot(difference, result)  #this is a number

        distance =(0.5 * result) ** 0.5
        return distance


    def consistency(self, witness, witnesses, seller):
        '''
        This method is calculating similarity (i.e cocnsitency) of the evidence provided by a witness Wk about the service provider = the seller Sj
            Input  : witness, the dictionary of the received witnesses and their testimonies
            Output : similarity ==  consistency
        '''

        mainBpa = self.directBpa(witness, seller)
        otherWitnesses = {}
        for wit in witnesses :
            if wit is  not witness:
                otherWitnesses[wit] = witnesses[wit]

        N = len(otherWitnesses)
        sum = 0
        for wit in otherWitnesses:
            sum += self.distanceOfJousselme(mainBpa, otherWitnesses[wit])
        similarity = 1 - sum / N
        return similarity




    def dempsterEntropy(self, witness, seller):
        '''
        the method is calculating the Dempster-Shafer entropy
            Input : the witness at stake, the seller == the service provider
        '''
        bpa = self.directBpa(witness, seller)  # the BPA of the direct Trust of the witness regarding the service provider == the seller

        plausFunc = self.plausibilityFunction(witness, seller)  # list of two elements
        plausTrans = self.plausibilityTransform(plausFunc)

        firstPart = 0    # first part of the entropy
        for i in range(1):
            if plausTrans[i] != 0:
                firstPart += plausTrans[i] * math.log2(1 / plausTrans[i])

        secondPart = bpa[2]   # second  part of the entropy
        entropy = firstPart + secondPart
        return entropy



    def certainty(self, witness, provider):
        """
        this is for calculating certainty of an evidence provided to a witness Wk from a service provider Sj
            Input  : bpa of the witness
            Ouput  : number -- certainty
        """
        entropy = self.dempsterEntropy(witness, provider)
        certainty = 1 - entropy / 2
        return certainty



    def sumDelta(self, witnesses, provider):

        N = len(witnesses)
        sum = 0
        for witness in witnesses:
            consistency = self.consistency(witness, witnesses, provider)
            credibility = witness.credibility
            sum += credibility * consistency
        return sum



    def confidence(self ,witness, witnesses, provider):
        """
        This method is calculating confidence of a witness
        Input  : witness, receivedInformation, BPAs
        Output : number  --- confidence
        """
        credibility = witness.credibility
        consistency = self.consistency(witness, witnesses, provider)
        sumDelta = self.sumDelta(witnesses, provider)
        delta = min(0, credibility * consistency - sumDelta)
        absDelta = abs(delta)

        certainty = self.certainty(witness, provider)
        certainty = certainty **absDelta


        confidence = consistency * credibility * certainty

        return confidence


    def plausibilityFunction(self, witness, seller):
        '''
        this method is calculating the plausibility function of a certain bpa of a witness regarding a service provider == the seller
        Input  : bpa of a certain witness
        Output : plausibility - [ , ]

        '''
        bpa = self.directBpa(witness, seller)  # the BPA of the direct Trust of the witness regarding the service provider == the seller

        firstTerm = bpa[0] + bpa[2]  # this is for Trust
        secondTerm = bpa[1] + bpa[2]  # this is for Untrust
        # the we won't use the uncertainty

        plausibility = [firstTerm, secondTerm]    # the plausibilty is then a list of two elements, one for trust, tha other is for untrust
        return plausibility


    def plausibilityTransform(self, plausibility):
        """
        This method is calculating the plausibilty transform of a plausibility function
            Input  : plausibility  - [ , ]
            Output : plausilibity transform - [ , ]
        """
        plaus = plausibility
        firstTerm  = plaus[0] / (plaus[0] + plaus[1])  # Trust
        secondTerm = plaus[1] / (plaus[0] + plaus[1])  # Untrust
        plausTransf = [firstTerm , secondTerm]
        return plausTransf

    def distanceOne(self, witness, witnesses, BPA):
        '''
        This method is calculating the fisrt distance to take into consideration when  updating credibility

            Input  : witness, provider, BPA == bpa(outcome)
            Output : the distance between BPA and the directTrust of the provider
        '''

        directTrust = witnesses[witness]
        distance = self.distanceOfJousselme(directTrust, BPA)

        return distance


    def distanceCredibility(self, witness, witnesses, seller, BPA):
        '''
        this is for calculating the overall distance we nee to update witness credibility
            Output : number -- distance
        '''
        firstDistance = self.distanceOne(witness, witnesses, BPA)
        secondDistance = self.consistency(witness, witnesses, seller)  # same as consistency
        xi = 0.7
        overallDistance = xi * firstDistance + (1 - xi) * secondDistance

        return overallDistance


    # Updating credibility with the method defined in the article

    # def updatingCredibility(self,witness, witnesses,seller, feedback, BPA):
    #
    #     '''
    #     the method is for updating credibilty according to the feedback outcome
    #     '''
    #
    #     plausFunc = self.plausibilityFunction(witness, seller)
    #     plausTrans = self.plausibilityTransform(plausFunc)
    #
    #
    #     distance = self.distanceCredibility(witness, witnesses, seller, BPA)
    #
    #     if (feedback and plausTrans[0] >= 0.5) or (not feedback and plausTrans[0] < 0.5):  # if the result is positive
    #         witness.credibility *= (1+distance) # to create the related functions
    #
    #     else :        # if the result is negative
    #         witness.credibility *= (1 - distance)
    #
    #     if witness.credibility > 1:   # we force the credibility to be always in the range between 0 and 1
    #         witness.credibility = 1



    def updateCredits(self, witnesses, seller, feedbackOutcome):
        '''
        This method is updating witnesses' credits after the interaction based on indirect
            Input : witnesses- indirect mass functions , seller-- the best seller ,the feedback
        '''
        for witness in witnesses:
            credibility = witness.credibility
            certainty = self.certainty(witness, seller)
            trust = witnesses[witness][0]
            untrust = witnesses[witness][1]

            if (feedbackOutcome and trust >= untrust) or ( not feedbackOutcome and untrust >= trust):               # here the witness is trustworthy
                witness.credits *= (1 + credibility * certainty)

            else:     # here the witness is untrustworthy
                witness.credits *= (1 - credibility * certainty)

            if witness.credits > 2:  # we force the credibility to be in the range [0, 2]
                witness.credits = 2


    # The new way of updating credibility
    def updatingCredibility(self, witness, witnesses, seller, feedback, BPA):

        distance = self.distanceOne(witness, witnesses, BPA)
        certainty = self.certainty(witness, seller)

        if distance < 0.5:
            witness.credibility *= (1 + certainty)

        else:
            witness.credibility *= (1 - certainty)

        if witness.credibility > 1:
            witness.credibility = 1


    def updateRate(self):
        '''
        This method is updating successful and failed interactions' rate of the client at stake
        '''
        successes = self.numberOfSuccesses
        failures = self.numberOfFailures

        rate1 = successes / (successes + failures)
        #rate2 = failures / (successes + failures)

        self.rate = rate1