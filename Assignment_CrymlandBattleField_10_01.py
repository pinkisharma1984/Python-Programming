# Written By:--Pinki Sharma
# Date:----November 20,2020
# video link is:--https://youtu.be/0HKhFOlv6f4
# Honor statement:-- "I have not given or received any unauthorized assistance on this assignment."
# Crymland Battle field

## crymbland simulation input file:
# weeks = 500
# n_thieves = 7
# heist_coef = 1000
# promotion_wealth = 1000000
# lieut_thieves = 7
# n_detectives = 3
# solve_init = .25
# solve_cap = .75
# n_witness = 4
# init_prob_bribing = .1
# prob_det_caught_bribe = .05
import random

inPath = 'C:/Users/shivk/Desktop/week 5 section 1 python/DSC-430/SimulationCrymlandInputs.txt'
outPath = 'C:/Users/shivk/Desktop/week 5 section 1 python/DSC-430/output_list.txt'

class SixSidedDie:
    'Class that represents a six sided die.'
    def __init__(self):
        'constructor to initialize the facevalue as 0'
        self.facevalue = 0                          #initializing the self.facevalue = 0

    def roll(self):
        'the function rolls the die.'
        self.facevalue = random.randint(1,6)        #assigning the self.facevalue to random generated interger from 1 to 6
        return(self.facevalue)                      # returns the face value of the die

class TenSidedDie (SixSidedDie):                    # extention of the SixSidedDie
    'Class that represents a ten sided die.'  
    def roll(self):
        'the function rolls the die.'
        self.facevalue = random.randint(1,10)       #assigning the self.facevalue to random generated interger from 1 to 10
        return(self.facevalue)                      # # returns the face value of the die

class TwentySidedDie (SixSidedDie):
    'Class that represents a twenty sided die.'      # extention of the SixSidedDie 
    def roll(self):
        'the function rolls the die.'
        self.facevalue = random.randint(1,20)       #assigning the self.facevalue to random generated interger from 1 to 20
        return(self.facevalue)                      # returns the face value of the die

class inputFields():
    """ Reads from simulation file containing information used to play the simulation. """
    def __init__(self, inputConfigDict):
        """ initialize all class variables and some global variables. """
        self.weeks = inputConfigDict['weeks']                      # Number of weeks in simulation
        self.nThieves = inputConfigDict['n_thieves']               # initial Number Of Thieves.
        self.heistCoef = inputConfigDict['heist_coef']             # The base $/heist
        self.promoWealth = inputConfigDict['promotion_wealth']     # $ needed for thief to promo to lieutenant
        self.lieutThieves = inputConfigDict['lieut_thieves']       # thieves lieutanat can create
        self.nDetectives = inputConfigDict['n_detectives']         # number of detectives created at start 
        self.initSolvProb = inputConfigDict['solve_init']          # initial probability of heist solve for each detective
        self.capSolvProb = inputConfigDict['solve_cap']            # The maximum % probability of solving a heist
        self.numWitnessNeeded = inputConfigDict['n_witness']       # number of witnesses needed to take down a lieutenant
        self.initialBribeProbabilityAmt = inputConfigDict['init_prob_bribing']          # Initial probability of bribing
        self.detCaughtBribing = inputConfigDict['prob_det_caught_bribe']   # likelyhood a bribed detective is caughtTakingBribe

        
        self.detBribeStart = 1000000                        # The amt a detective needs to seize to get first bribe
        self.detBribeIncrement =  1000000                   # Amount of money between additional bribe attempts
        self.bribesAccepted = 0                             # Total amount of bribes accepted
        self.disgracedDetectives = 0                        # detectives caught taking bribes
        self.activeBribedDetectives = 0                     # Number of active bribed detectives
        self.numberOfThieves = 0                                 # Current number of actives thieves
        self.activeLieutanants = 0                                  # Current number of actives lieutenants
        self.numJailedThieves = 0                           # Thieves in jail
        self.numOfJailedLieut = 0                            
        self.lootStolen = 0                                 

        # attributes used in program operation
        self.outcome = 'notYetDone' # Current outcome of the simulation
        self.curWeek = 0 # Current week
        self.activeThieves = set()  # List of active thieves
        self.promoList = list() # List of thieves to be promoted
        self.thiefArrestList = list() # List of thieves to be arrested
        
        # initialize detectives
        self.detectiveList = [detective(self) for i in range(self.nDetectives)]


    # Add The Don because we're lazy and it will make passing variables easy
    def addDon(self, theDon): self.theDon = theDon

    def advanceWeek(self):
       """ Advances the book and Don by one week """
       self.curWeek += 1
       self.promoList = list()
       self.theDon.resetEarnings()


class thief():
    """ super class for lieutenant class and syndicateHead.  This class initializes
    each thief and allows it to perform its duties.  """
    
    def __init__(self, globalWealthRecord, boss):
        """ Initializes thief class """
        self.globalWealthRecord = globalWealthRecord
        self.globalWealthRecord.numberOfThieves += 1
        self.boss = boss 
        self.bankWealthInAccount = 0
        self.inJail = False
        self.heistCoef = self.globalWealthRecord.heistCoef
        self.promoWealth = self.globalWealthRecord.promoWealth
        self.globalWealthRecord.activeThieves.add(self)
    
    def addToBank(self, amount):
        """ Add money to bank account and send half to boss """
        self.boss.addToBank(amount/2)
        self.bankWealthInAccount += amount/2

    def arrestThief(self):
        """ Add thief to jailed list and remove from active; add 1 to boss's
        witness counter """
        self.inJail = True
        self.globalWealthRecord.activeThieves.remove(self)
        self.globalWealthRecord.numJailedThieves += 1
        try:
            self.boss.thieves.remove(self)
        except:
            print("couldn't remove thief ")
        self.boss.witnesses += 1                        #  reveal against boss.
        self.boss.validateArrest()

    def performHeist(self):
        """ conducts a heist/robbery. """
        twtySidedDie = TwentySidedDie()
        robAmt = self.globalWealthRecord.heistCoef*(twtySidedDie.roll()**2)
        self.globalWealthRecord.lootStolen += robAmt
        self.boss.addToBank(robAmt/2)                              # Add money to bank account and send half to boss.
        self.bankWealthInAccount += robAmt/2
        if self.bankWealthInAccount >= self.globalWealthRecord.promoWealth:   #Check if thief is promoted.  If so, add to list for promotion
            self.globalWealthRecord.promoList.append(self)


class lieutenant(thief):
    """ Runs the thieves. Extends thief class. Collects money and passes up to boss. 
    Also promotes thieves. """
    
    def __init__(self, globalWealthRecord, boss):
        """ Initializes the lieutenant class """
        self.boss = boss
        self.globalWealthRecord = globalWealthRecord
        self.inJail = False
        self.witnesses = 0
        self.thieves = [thief(globalWealthRecord, self) for i in range(self.globalWealthRecord.lieutThieves)]  # Create initial list of thieves
        self.globalWealthRecord.activeLieutanants += 1                                                         # Add lieutenant to active lieutenant list
    
    def promoteThief(self, thief):
        """ Promote the thief  to Lieutanant as thief is promoted to boss when he crosses x wealth.        
        """
        self.thieves.append(lieutenant(self.globalWealthRecord, self))
        self.globalWealthRecord.activeLieutanants += 1          # new object (lieutenant) to this boss's list of thieves
        self.globalWealthRecord.numberOfThieves -= 1               
        self.thieves[-1].bankWealthInAccount = thief.bankWealthInAccount               # transfer bank acct balance
        self.thieves[-1].boss = self                             # transfer boss
        self.globalWealthRecord.activeThieves.remove(thief)      # remove thieves as he is promoted to Lieutenant
        del thief

    def validateArrest(self):
        """ if lieutanant has more than 4 witnessing arrest the lieutanant."""
        if self.witnesses >= self.globalWealthRecord.numWitnessNeeded:
            self.inJail = True
            self.globalWealthRecord.activeLieutanants -= 1
            self.globalWealthRecord.numOfJailedLieut += 1
            for thief in self.thieves:                         # Thieves that lose their Lieutanant begin reporting to next higher boss
                thief.boss = self.boss
                thief.boss.thieves.append(thief)
            self.boss.witnesses += 1                            # testify against boss
            try:
                self.boss.thieves.remove(self)
            except:
                print(" Couldn't remove ")
            self.boss.validateArrest()
        

class syndicateHead(lieutenant):
    """ Syndicate aka Mr Bigg is the final boss which extends lieutenant class and thus extending Thief class,
    takes all the passed money but does not pass it on.
    input: globalWealthRecord
    """

    def __init__(self, globalWealthRecord):
        """ Initialize Mr Bigg """
        self.witnesses = 0
        self.bankWealthInAccount = 0
        self.weeklyWealthEarnings = 0
        self.globalWealthRecord = globalWealthRecord
        self.globalWealthRecord.addDon(self)
        self.thieves = [thief(self.globalWealthRecord, self) for i in range(self.globalWealthRecord.nThieves)]
        self.inJail = False
        self.globalWealthRecord.activeLieutanants += 1

    def addToBank(self, amount):
        """ Adds to bank account and does not pass the money upwards as it ends here.
        """
        self.weeklyWealthEarnings += amount
        self.bankWealthInAccount += amount
    
    def resetEarnings(self):
        """ Resets weekly earnings and is used in bribes. """
        self.weeklyWealthEarnings = 0

    def validateArrest(self):
        """ Check if self is arrested """
        if self.witnesses >= self.globalWealthRecord.numWitnessNeeded:
            self.inJail = True
            self.globalWealthRecord.activeLieutanants -= 1
            self.globalWealthRecord.numOfJailedLieut += 1
            self.globalWealthRecord.outcome = 'detectives'
    
    def bribe(self, detective):
        """ Attempt to bribe a detective 
        Bribe amount is the percentage specified in input file * weekly earnings
        """

        bribeAmt = self.globalWealthRecord.initialBribeProbabilityAmt*self.weeklyWealthEarnings

        if bribeAmt <= 10000: bribeProb = .05
        elif bribeAmt <= 100000: bribeProb = .10
        elif bribeAmt <= 1000000: bribeProb = .25
        else: bribeProb = .5

        if random.random() < bribeProb:
            detective.acceptedTakingBribe(bribeAmt)
        else:
            detective.nextBribeAttempt += detective.globalWealthRecord.detBribeIncrement


class detective():
    """ Detective Class.  investigates thieves, can be bribed """

    def __init__(self, globalWealthRecord):
        """ Initialize Detective """
        
        self.globalWealthRecord = globalWealthRecord
        self.bribed = False
        self.dollarsSeized = 0                                          # Dollars seized; drives bribe amount
        self.arrests = 0                                                # Number of arrests made by detective.
        self.solveProb = self.globalWealthRecord.initSolvProb           # Probability of solving the case
        self.nextBribeAttempt = self.globalWealthRecord.detBribeStart   # Set the first bribe amount; this will increase by self.detBribeIncrement
        self.discoveryProb = self.globalWealthRecord.detCaughtBribing   # Likelihood of being caughtTakingBribe; starts at some setting.
    
    def acceptedTakingBribe(self, bribeAmt):
        """ The detective is caught taking bribes  and will no longer solve crimes. """
        self.bribed = True
        self.solveProb = 0
        self.globalWealthRecord.activeBribedDetectives += 1
        self.globalWealthRecord.bribesAccepted += bribeAmt
    
    def caughtTakingBribe(self):
        """ Remove detectives once they've been caughtTakingBribe """
        self.globalWealthRecord.detectiveList.remove(self)
        self.globalWealthRecord.activeBribedDetectives -= 1
        self.globalWealthRecord.disgracedDetectives += 1
        self.globalWealthRecord.detectiveList.append(detective(self.globalWealthRecord))        # Hire new detective to fill their spot
        del self                                                                                # Remove detective object to free up memory

    def investigate(self, thief):
        """ investigate a heist """
        TenDie = TenSidedDie()
        if random.random() < self.solveProb:
            thief.arrestThief()
            self.dollarsSeized += thief.bankWealthInAccount
            self.arrests += 1
            self.solveProb = min(self.solveProb + TenDie.roll()/100, 
                self.globalWealthRecord.capSolvProb)
            
    def investigationForDetectiveBribe(self):
        """ Internal Affairs is investigating this detective for checkForDetectiveBribery... """
        if random.random() > self.discoveryProb:
            self.discoveryProb += (random.randint(1, 20)/100)
        else:
            self.caughtTakingBribe()
    

def readSimulationInput(path):
    """ Loads the simulation file and convert it into a dictionary """
    inputs = open(path)
    inputConfigList = inputs.read().splitlines()
    inputs.close()
    inputConfigDict = dict()
    for row in inputConfigList:
        key, value = row.split(sep = '=')
        key = key.strip()
        value = eval(value.strip())
        inputConfigDict[key] = value
    return inputConfigDict

def investigate(globalWealthRecord):
    """ start investigation phase for detective.
    """
    numInvestigations = min(len(globalWealthRecord.detectiveList), len(globalWealthRecord.activeThieves)) # Determine number of investigations which is the lesser of the number of the number of detectives or heists.
    heistsUnderInvestigation = random.sample(globalWealthRecord.activeThieves, numInvestigations)         # Randomly select heists to investigate
    for i in range(numInvestigations):                                                                    # Cycle through each investigation and assign a detective then investigate it
        detective = globalWealthRecord.detectiveList[i]                                                   # If the detective is bribed then activate investigation
        detective.investigate(heistsUnderInvestigation[i])

def simulateThieves(globalWealthRecord):
    """ call thief class methods. """
    globalWealthRecord.promoList = list()
    for thief in globalWealthRecord.activeThieves:
        thief.performHeist()                            # call heist method for all thieves. 
    for promote in globalWealthRecord.promoList:        # promote thief to Leitunant if promoList of a thief has it.
        promote.boss.promoteThief(promote)

def checkForDetectiveBribery(globalWealthRecord):
    """ attempt to bribe each detective that does enough damage """
    for detective in globalWealthRecord.detectiveList:
        if detective.bribed == False: # Only check when detective isn't on the take
            if detective.dollarsSeized > detective.nextBribeAttempt:
                globalWealthRecord.theDon.bribe(detective)
        else:
            detective.investigationForDetectiveBribe()

def initializeOutfile(outFile):
    """ initialize the output file with first row."""
    outString = "week,gangstersNotJailed,gangstersJailed,syndicateHeadWealth,"\
        "bribesAccepted,winner"   
    outFile.write(outString + '\n')
    outFile.flush()

    
def finalWeeklyReportSaved(globalWealthRecord, outFile):
    """ Items printed to the file for later retrieval """
    gangstersNotJailed = globalWealthRecord.numberOfThieves + globalWealthRecord.activeLieutanants
    gangstersjailed = globalWealthRecord.numJailedThieves + globalWealthRecord.numOfJailedLieut   
    outString = "{}, {}, {}, {}, {}, {}".format(globalWealthRecord.curWeek,
        gangstersNotJailed, gangstersjailed, int(globalWealthRecord.theDon.bankWealthInAccount),
        int(globalWealthRecord.bribesAccepted), globalWealthRecord.outcome)
    outFile.write(outString +'\n')
    outFile.flush()

def finalOutComeOfPlay(globalWealthRecord):
    """" Calls the finalOutComeOfPlay outcomes """
    if globalWealthRecord.outcome == 'detectives':
        print("\n\nThe brave detectives of Crymland have succeeded! Mr Biggs "\
        "has been arrested after {} weeks on the street!".format(globalWealthRecord.curWeek))
        for i in range(len(globalWealthRecord.detectiveList)):
            detective = globalWealthRecord.detectiveList[i]
            print("Detective {}:  Dollars Recovered: {}  Thieves Arrested: {}".format(i + 1, detective.dollarsSeized, detective.arrests))
    elif globalWealthRecord.outcome == 'syndicateHead':
        print("\n\nAfter {} weeks {} 'Mr Bigg' {} evades to a unknown country. \nTotal Earnings: ${}".format(globalWealthRecord.curWeek, globalWealthRecord.theDon.firstName, globalWealthRecord.theDon.lastName, int(globalWealthRecord.theDon.bankWealthInAccount)))
    else:
        print('finalOutComeOfPlay declared out of turn.')

def crymlandSimulation():
    """ Runs the Crymland simulation  class which reads simulation input file and then initializes all classes and their methods to find whether Mr Bigg succeeded in evading or was caught by detectives. """
    outFile = open(outPath, 'w')
    initializeOutfile(outFile)
    inputConfigDict = readSimulationInput(inPath)
    globalWealthRecord = inputFields(inputConfigDict)
    theDon = syndicateHead(globalWealthRecord)
    print("\nWelcome to Mr Bigg syndicate of crime in Crymland which has heist every week and there are detectives who are fighting to stop the crime and eradicate the syndicate.")
    print("Let us see what happens as a part of the simulation game. ")
    for i in range(globalWealthRecord.weeks):           # Cycle through the designated number of weeks
        globalWealthRecord.advanceWeek()                # advance week counter, reset weekly lists
        simulateThieves(globalWealthRecord)                 # Conduct thief actions
        investigate(globalWealthRecord)                 # Detectives investigate thieves
        checkForDetectiveBribery(globalWealthRecord)                     # Mr Bigg attempts to bribe the detectives
        if theDon.inJail == False and (i + 1) == globalWealthRecord.weeks:
            globalWealthRecord.outcome = "syndicateHead"    
        finalWeeklyReportSaved(globalWealthRecord, outFile)   # Output weekly results to file
        if theDon.inJail == True:
            finalOutComeOfPlay(globalWealthRecord)                 # outcome is updated in the syndicateHead class
            break            
    if theDon.inJail == False:
        finalOutComeOfPlay(globalWealthRecord)    
    outFile.close()


# main function call
crymlandSimulation()
