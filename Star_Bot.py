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

account = config["account"]
privateKey = config["privateKey"]
daysToCompound = config["daysToCompound"]
compoundTimeHour = config["compoundTimeHour"]
compoundTimeMins = config["compoundTimeMins"]
minCompound = config["minCompound"]

w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com/'))
with open('starMasterchefABI.json', 'r') as f:
    starMasterchefAbi =json.load(f)
starMasterchefAddress = '0x16E76500f1E6C943FEd150bF56403d91A91dCD55'

starMasterchefContract = w3.eth.contract(address=starMasterchefAddress ,abi=starMasterchefAbi)

async def collectRewards():
    global nodes
    global balance
    blocktime = w3.eth.get_block('latest')
    blocktime = blocktime.timestamp
    gasPrice = w3.eth.gasPrice

    pendingStar = starMasterchefContract.functions.pendingStar(6,account).call()
    
    if(pendingStar >= minCompound):
        print("collecting reward")
        tx = starMasterchefContract.functions.compound(6).buildTransaction({'nonce': w3.eth.getTransactionCount(account), "from": account, "gasPrice":gasPrice})
        signed_tx = w3.eth.account.signTransaction(tx, private_key=privateKey)
        raw_tx = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

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
    claimMins = (compoundTimeHour*60)+compoundTimeMins
    print(hours,":",mins)
    if(((hours*60)+mins)>=claimMins):
        await collectRewards()
        print("collect")
    else:
        delayHours = compoundTimeHour-hours
        delayMins = compoundTimeMins-mins
        if(delayMins < 0):
            delayHours -= 1
            delayMins = 60+delayMins
        print("waiting: "  ,delayHours ,":",delayMins)
        time.sleep((delayHours*360)+(delayMins*60))
        await checkTime()
    

async def main():
    await checkTime()
    

asyncio.run(main())

