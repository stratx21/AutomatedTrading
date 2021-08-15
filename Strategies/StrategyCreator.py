# from Strategies.Renko.Renko_CON_TSFH import Renko_CON_TSFH
# from Strategies.Renko.Renko_BAH_TSFH import Renko_BAH_TSFH 
# from Strategies.Renko.Renko_TSFH import Renko_TSFH
from Strategies.Renko.Renko_HL import Renko_HL
from Strategies.Range.Range_SMI import Range_SMI
from Strategies.Renko.Renko_SMI import Renko_SMI
from Strategies.Renko.Renko_wContext_VS import Renko_WC_VS
from Strategies.Renko.Renko_wContextSMI_vs import Renko_WCSMI_VS
from Strategies.Renko.Renko_CON_VS import Renko_CON_VS
from Strategies.Renko.Renko_CON_SA import Renko_CON_SA
from Strategies.Renko.Renko_BAH_SA import Renko_BAH_SA
import Strategies.RegisteredStrategyNames as RegisteredStrategyNames
from Strategies.Range.PriceActionTrader import PriceActionTrader
from Strategies.Range.Conservative_PAT import Conservative_PAT
from Strategies.Range.PAT_SMAgreen_LastbarnotPAT import PAT_SMAgreen_LastbarnotPAT
from Strategies.Range.CPAT_SMAG_LNB import CPAT_SMAG_LNB
from Strategies.Range.Bollinger_backwardsPAT import BB_bPAT   
from Strategies.Range.BollingerBandsRange_v32W import BBR_v32W
from Strategies.Range.BBMR import BBMR 
from Strategies.Range.BBMR_MAS import BBMR_MAS
from Strategies.Range.Range_CaV import Range_CaV
# from Strategies.Range.Range_SMI_TSFH import Range_SMI_TSFH
# from Strategies.Range.Range_CON_TSFH import Range_CON_TSFH
from Strategies.Renko.Renko_VBS import Renko_VBS
from Strategies.Renko.Renko_SA import Renko_SA
from Strategies.Renko.Renko_BAH import Renko_BAH
from Strategies.Renko.Renko_CaV import Renko_CaV

import Terminal.TerminalStrings as TerminalStrings 

# NOTE : register your strategy here for it to be included 

acceptableStrategyNames =  [RegisteredStrategyNames.PRICE_ACTION_TRADER, \
                            RegisteredStrategyNames.PAT_SMAisG_LastNPAT, \
                            RegisteredStrategyNames.CONSERVATIVE_PAT, \
                            RegisteredStrategyNames.CPAT_SMAG_LastNPAT, \
                            RegisteredStrategyNames.BOLLINGER_BACKWARDS_PAT, \
                            RegisteredStrategyNames.BOLLINGER_RANGE_V32W, \
                            RegisteredStrategyNames.BOLLINGER_MIDLINE_RANGE, \
                            RegisteredStrategyNames.BOLLINGER_MIDLINE_RANGE_MAS, \
                            RegisteredStrategyNames.RANGE_CaV, \
                            RegisteredStrategyNames.RANGE_SMI, \
                            # RegisteredStrategyNames.RANGE_SMI_TSFH, \
                            # RegisteredStrategyNames.RANGE_CON_TSFH, \
                            RegisteredStrategyNames.RENKO_VBS, \
                            RegisteredStrategyNames.RENKO_SA, \
                            RegisteredStrategyNames.RENKO_BAH, \
                            RegisteredStrategyNames.RENKO_CaV, \
                            RegisteredStrategyNames.RENKO_BAH_SA, \
                            RegisteredStrategyNames.RENKO_CON_SA, \
                            RegisteredStrategyNames.RENKO_CON_VS, \
                            RegisteredStrategyNames.RENKO_WCONTEXT_VS, \
                            RegisteredStrategyNames.RENKO_WCONTEXTSMI_VS, \
                            RegisteredStrategyNames.RENKO_SMI, \
                            RegisteredStrategyNames.RENKO_HL]
                            # RegisteredStrategyNames.RENKO_TSFH, \
                            # RegisteredStrategyNames.RENKO_BAH_TSFH, \
                            # RegisteredStrategyNames.RENKO_CON_TSFH \

def create(strategyName, strategyTicker, strategyAggregation, optionalArg1 = None, optionalArg2 = None):
    if strategyName not in acceptableStrategyNames:
        print(TerminalStrings.ERROR + " Strategy.StrategyCreator.create : strategy name \""+strategyName+"\" not found! ")
        print(TerminalStrings.ERROR + "    available strategies: " + str(acceptableStrategyNames))
    else: 
        if strategyName == RegisteredStrategyNames.PRICE_ACTION_TRADER:
            instance = PriceActionTrader(strategyTicker, strategyAggregation)
            return instance 
        elif strategyName == RegisteredStrategyNames.CONSERVATIVE_PAT:
            instance = Conservative_PAT(strategyTicker, strategyAggregation, optionalArg1 if optionalArg1 != None else 0.00)
            return instance 
        elif strategyName == RegisteredStrategyNames.PAT_SMAisG_LastNPAT:
            if optionalArg1 == None: # SMALength 
                print(TerminalStrings.ERROR + " PAT_SMAG_LNB Strategy.StrategyCreator.create : optional arg 1 is None, should have an SMA length")
            else: 
                instance = PAT_SMAgreen_LastbarnotPAT(strategyTicker, strategyAggregation, optionalArg1)
                return instance 
        elif strategyName == RegisteredStrategyNames.CPAT_SMAG_LastNPAT:
            if optionalArg1 == None: # SMALength 
                print(TerminalStrings.ERROR + " CPAT_SMAG_LNB Strategy.StrategyCreator.create : optional arg 1 is None, should have an SMA length")
            else: 
                if optionalArg2 == None:
                    instance = CPAT_SMAG_LNB(strategyTicker, strategyAggregation, optionalArg1)
                else:
                    instance = CPAT_SMAG_LNB(strategyTicker, strategyAggregation, optionalArg1, float(optionalArg2))
                return instance 

        
        elif strategyName == RegisteredStrategyNames.BOLLINGER_BACKWARDS_PAT:
            instance = BB_bPAT(strategyTicker, strategyAggregation)
            return instance 

        elif strategyName == RegisteredStrategyNames.BOLLINGER_RANGE_V32W:
            instance = BBR_v32W(strategyTicker, strategyAggregation)
            return instance 
            
            
        elif strategyName == RegisteredStrategyNames.BOLLINGER_MIDLINE_RANGE:
            instance = BBMR(strategyTicker, strategyAggregation)
            return instance 
        elif strategyName == RegisteredStrategyNames.BOLLINGER_MIDLINE_RANGE_MAS:
            if optionalArg1 == None: # SMALength
                print(TerminalStrings.ERROR + " BBMR_MAS Strategy.StrategyCreator.create : optional arg 1 is None, should have an SMA length")
            else:
                instance = BBMR_MAS(strategyTicker, strategyAggregation, optionalArg1)
                return instance 

        elif strategyName == RegisteredStrategyNames.RANGE_CaV:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Range CaV first optional parameter of SMA Length is required")
            else:
                instance = Range_CaV(strategyTicker, strategyAggregation, int(optionalArg1))
                return instance 
        
        elif strategyName == RegisteredStrategyNames.RANGE_SMI:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Range SMI first optional parameter of percent D Length is required")
            elif optionalArg2 == None:
                print(TerminalStrings.ERROR + " Range SMI second optional parameter of percent K Length is required")
            else:
                instance = Range_SMI(strategyTicker, strategyAggregation, int(optionalArg1), int(optionalArg2))
                return instance 
        
        # elif strategyName == RegisteredStrategyNames.RANGE_SMI_TSFH:
        #     if optionalArg1 == None:
        #         print(TerminalStrings.ERROR + " Range SMI TSFH first optional parameter of sellOutX (cents float amount for trailing stoploss) is required")
        #     else:
        #         instance = Range_SMI_TSFH(strategyTicker, strategyAggregation, float(optionalArg1))
        #         return instance 

        # elif strategyName == RegisteredStrategyNames.RANGE_CON_TSFH:
        #     if optionalArg1 == None:
        #         print(TerminalStrings.ERROR + " Range CON TSFH first optional parameter of SMA Length is required")
        #     elif optionalArg2 == None:
        #         print(TerminalStrings.ERROR + " Range CON TSFH second optional parameter of sellOutX (cents float amount for trailing stoploss) is required")
        #     else:
        #         instance = Range_CON_TSFH(strategyTicker, strategyAggregation, int(optionalArg1), float(optionalArg2))
        #         return instance 


        # RENKO 


        elif strategyName == RegisteredStrategyNames.RENKO_VBS:
            if optionalArg1 == None or optionalArg2 == None:
                print(TerminalStrings.ERROR + " Renko VBS requires first optional parameter of green bricks required for buy condition, and second optional parameter of red bricks required for sell condition.")
            else:
                instance = Renko_VBS(strategyTicker, strategyAggregation, int(optionalArg1), int(optionalArg2))
                return instance 

        elif strategyName == RegisteredStrategyNames.RENKO_SA:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Renko SA first optional parameter of how many green bricks for it to sell is required")
            else:
                instance = Renko_SA(strategyTicker, strategyAggregation, int(optionalArg1))
                return instance 

        elif strategyName == RegisteredStrategyNames.RENKO_BAH:
            instance = Renko_BAH(strategyTicker, strategyAggregation)
            return instance 

        elif strategyName == RegisteredStrategyNames.RENKO_BAH_SA:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Renko BAH SA first optional parameter of how many green bricks for it to sell is required")
            else:
                instance = Renko_BAH_SA(strategyTicker, strategyAggregation, int(optionalArg1))
                return instance 

        elif strategyName == RegisteredStrategyNames.RENKO_CaV:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Renko CaV first optional parameter of SMA Length is required")
            else:
                instance = Renko_CaV(strategyTicker, strategyAggregation, int(optionalArg1))
                return instance 

        elif strategyName == RegisteredStrategyNames.RENKO_CON_SA:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Renko CaV SA first optional parameter of SMA Length is required")
            elif optionalArg2 == None:
                print(TerminalStrings.ERROR + " Renko CaV SA second optional parameter of how many green bricks for it to sell is required")
            else:
                instance = Renko_CON_SA(strategyTicker, strategyAggregation, int(optionalArg1), int(optionalArg2))
                return instance 

        elif strategyName == RegisteredStrategyNames.RENKO_CON_VS:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Renko CON SA first optional parameter of SMA Length is required")
            elif optionalArg2 == None:
                print(TerminalStrings.ERROR + " Renko CON SA second optional parameter of how many red bricks for it to sell is required")
            else:
                instance = Renko_CON_VS(strategyTicker, strategyAggregation, int(optionalArg1), int(optionalArg2))
                return instance 

        elif strategyName == RegisteredStrategyNames.RENKO_WCONTEXT_VS:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Renko WC VS first optional parameter of context aggregation is required")
            elif optionalArg2 == None:
                print(TerminalStrings.ERROR + " Renko WC VS second optional parameter of how many red bricks for it to sell is required")
            else:
                instance = Renko_WC_VS(strategyTicker, strategyAggregation, int(optionalArg1), int(optionalArg2))
                return instance 

        elif strategyName == RegisteredStrategyNames.RENKO_WCONTEXTSMI_VS:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Renko WCSMI VS first optional parameter of context aggregation is required")
            elif optionalArg2 == None:
                print(TerminalStrings.ERROR + " Renko WCSMI VS second optional parameter of how many red bricks for it to sell is required")
            else:
                instance = Renko_WCSMI_VS(strategyTicker, strategyAggregation, int(optionalArg1), int(optionalArg2))
                return instance 

        elif strategyName == RegisteredStrategyNames.RENKO_SMI:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Renko SMI first optional parameter of percent D Length is required")
            elif optionalArg2 == None:
                print(TerminalStrings.ERROR + " Renko SMI second optional parameter of percent K Length is required")
            else:
                instance = Renko_SMI(strategyTicker, strategyAggregation, int(optionalArg1), int(optionalArg2))
                return instance 

        elif strategyName == RegisteredStrategyNames.RENKO_HL:
            if optionalArg1 == None:
                print(TerminalStrings.ERROR + " Renko HL first optional parameter of include double bottoms is required")
            else:
                instance = Renko_HL(strategyTicker, strategyAggregation, int(optionalArg1))
                return instance 

        # elif strategyName == RegisteredStrategyNames.RENKO_TSFH:
        #     if optionalArg1 == None:
        #         print(TerminalStrings.ERROR + " Renko TSFH first optional parameter of sellOutX (cents float amount for trailing stoploss) is required")
        #     else:
        #         instance = Renko_TSFH(strategyTicker, strategyAggregation, float(optionalArg1))
        #         return instance 

        # elif strategyName == RegisteredStrategyNames.RENKO_BAH_TSFH:
        #     if optionalArg1 == None:
        #         print(TerminalStrings.ERROR + " Renko BAH TSFH first optional parameter of sellOutX (cents float amount for trailing stoploss) is required")
        #     else:
        #         instance = Renko_BAH_TSFH(strategyTicker, strategyAggregation, float(optionalArg1))
        #         return instance 

        # elif strategyName == RegisteredStrategyNames.RENKO_CON_TSFH:
        #     if optionalArg1 == None:
        #         print(TerminalStrings.ERROR + " Renko CON TSFH first optional parameter of sma length is required")
        #     elif optionalArg2 == None:
        #         print(TerminalStrings.ERROR + " Renko CON TSFH second optional parameter of sellOutX (cents float amount for trailing stoploss) is required")
        #     else:
        #         instance = Renko_CON_TSFH(strategyTicker, strategyAggregation, int(optionalArg1), float(optionalArg2))
        #         return instance 

        else:
            print(TerminalStrings.ERROR + " strategy name \"" + strategyName + "\" not found!")



        
def isStrategyName(name):
    return name in acceptableStrategyNames
