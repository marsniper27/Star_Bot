import asyncio
import hjson
import json
import platform
import time
import windowsTask
from web3 import Web3
from datetime import datetime
os = platform.system()
print(os)

with open('config.hjson', 'r') as f:
    config = hjson.load(f)

compound = config["compound"]
account = config["account"]
privateKey = config["privateKey"]
daysToClaim = config["daysToClaim"]
claimTimeHour = config["claimTimeHour"]
claimTimeMins = config["claimTimeMins"]
namePrefix = config["namePrefix"]

w3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools/'))
with open('hnrAbi.json', 'r') as f:
    hnrAbi =json.load(f)
hnrAddress = '0x36667966c79dEC0dCDA0E2a41370fb58857F5182'

hnrContract = w3.eth.contract(address=hnrAddress ,abi=hnrAbi)
balance = hnrContract.functions.balanceOf(account).call()
nodes = hnrContract.functions.getNodeNumberOf(account).call()

async def collectRewards():
    global nodes
    global balance
    blocktime = w3.eth.get_block('latest')
    blocktime = blocktime.timestamp
    gasPrice = w3.eth.gasPrice

    poolBalance = hnrContract.functions.balanceOf('0xBAd99C80Cfa1a51b36A7D250fD8CcEbd2496fe51').call()
    mushaReward = hnrContract.functions.getMushaReward().call()
    totalRewards = nodes*mushaReward
    
    if(poolBalance > nodes*mushaReward and poolBalance > 2000000000000000000000):
        print("collecting reward")
        tx = hnrContract.functions.cashoutAll().buildTransaction({'nonce': w3.eth.getTransactionCount(account), "from": account, "gasPrice":gasPrice})
        signed_tx = w3.eth.account.signTransaction(tx, private_key=privateKey)
        raw_tx = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        balance += totalRewards

        mushaPrice = hnrContract.functions.getMushaPrice().call()

        if(compound == True and balance >= mushaPrice):
            name = namePrefix + str(nodes+1)
        
            tx = hnrContract.functions.createNodeWithTokens(name,'MUSHA').buildTransaction({'nonce': w3.eth.getTransactionCount(account), "from": account, "gasPrice":gasPrice})
            signed_tx = w3.eth.account.signTransaction(tx, private_key=privateKey)
            raw_tx = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

            nodes+=1
            balance -= mushaPrice
        if(config["scheduleClaim"] == True):
            match os:
                case "Windows":
                    windowsTask.createSchedule()
                case "Linux":
                    print("need to implement Linux task scheduling")
                case "Darwin":
                    print("need to implement MacOs task scheduling")
        

async def checkTime():
    now = datetime.now()
    hours = int(now.strftime("%H"))
    mins = int(now.strftime("%M"))
    claimMins = (claimTimeHour*60)+claimTimeMins
    print(hours,":",mins)
    if(((hours*60)+mins)>=claimMins):
        await collectRewards()
        print("collect")
    else:
        delayHours = claimTimeHour-hours
        delayMins = claimTimeMins-mins
        if(delayMins < 0):
            delayHours -= 1
            delayMins = 60+delayMins
        print("waiting: "  ,delayHours ,":",delayMins)
        time.sleep((delayHours*360)+(delayMins*60))
        await checkTime()
    

async def main():
    await checkTime()
    

asyncio.run(main())

