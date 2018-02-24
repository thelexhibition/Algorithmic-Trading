# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import numpy as np
import decimal as d


class ChannelsAlgorithm(QCAlgorithm):

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2017, 1, 1)  #Set Start Date
        self.SetEndDate(2018, 2, 22)    #Set End Date
        self.SetCash(10000)             #Set Strategy Cash
        # Find more symbols here: http://quantconnect.com/data
        self.SetBrokerageModel(BrokerageName.GDAX, AccountType.Cash)
        
        self.symbols = []
        self.symbols.append("BTCUSD"), self.symbols.append("LTCUSD"), self.symbols.append("ETHUSD"), self.symbols.append("BTCEUR")
        
        for crypto in self.symbols:
            self.AddCrypto(crypto, Resolution.Daily)
        
        self.SetBenchmark("BTCUSD")
        
        # Initilize Indicator
        self.indicator = {}
        for asset in self.symbols:
            self.indicator[asset] = self.PSAR(asset,0.01,0.3,0.2,Resolution.Daily)

        self.previous = None


    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.'''
        # a couple things to notice in this method:
        #  1. We never need to 'update' our indicators with the data, the engine takes care of this for us
        #  2. We can use indicators directly in math expressions
        #  3. We can easily plot many indicators at the same time
        
        # only once per day
        if self.previous is not None and self.previous.date() == self.Time.date():
            return

        # Loop through list of crypto coins
        for sec in self.symbols:
            
            # Check to see if we own any of this coin in the portfolio
            holdings = self.Portfolio[sec].Quantity
            
            # If we don't own any, check to see if we should
            if holdings <= 0:
                
                # if the price is greater than the buy indiator, we'll go long
                if float(self.Securities[sec].Price) > self.indicator[sec].Current.Value:
                    self.Log("BUY  >> {0}".format(self.Securities[sec].Price))
                    
                    # We will buy 25% of the size of the portfolio for this position
                    self.SetHoldings(sec, 0.25)
    
            # we only want to liquidate if we're currently long & the price is no longer greater than the indicator value
            if holdings > 0 and self.Securities[sec].Price < self.indicator[sec].Current.Value:
                self.Log("SELL >> {0}".format(self.Securities[sec].Price))
                self.Liquidate(sec)
    
            self.previous = self.Time
