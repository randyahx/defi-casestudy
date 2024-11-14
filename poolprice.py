import requests
from web3 import Web3

# ETH Node  
NODE_ENDPOINT = "NODE_ENDPOINT"
# 1Inch API  
ONEINCH_API_URL = "API_URL"
ONEINCH_API_KEY = "YOUR_API_KEY"  
# Uniswap V2 Contract Address    
UNISWAP_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"  

# Uniswap V2 Factory ABI  
UNISWAP_FACTORY_ABI = '''[{
    "constant": true,
    "inputs": [
        {"internalType": "address", "name": "tokenA", "type": "address"},
        {"internalType": "address", "name": "tokenB", "type": "address"}
    ],
    "name": "getPair",
    "outputs": [{"internalType": "address", "name": "pair", "type": "address"}],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
}]'''

# Uniswap V2 Pair ABI
UNISWAP_PAIR_ABI = '''[{
    "constant": true,
    "inputs": [],
    "name": "getReserves",
    "outputs": [
        {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
        {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
        {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"}
    ],
    "payable": false,
    "stateMutability": "view",
    "type": "function"
}]'''

# Token Address  
WETH_ADDRESS = Web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27ead9083C756Cc2")
USDC_ADDRESS = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

TOKEN_AMOUNT = 10

# Initialize Web3
web3 = Web3(Web3.HTTPProvider("NODE_ENDPOINT"))

# Uniswap V2 Price - ETH/USDC
def get_uniswap_v2_price():
    # Get ETH/USDC pair address  
    factory_contract = web3.eth.contract(address=UNISWAP_FACTORY_ADDRESS, abi=UNISWAP_FACTORY_ABI)
    pair_address = factory_contract.functions.getPair(WETH_ADDRESS, USDC_ADDRESS).call()

    # Get reserves from ETH/USDC pair  
    pair_contract = web3.eth.contract(address=pair_address, abi=UNISWAP_PAIR_ABI)
    reserves = pair_contract.functions.getReserves().call()

    reserve_weth, reserve_usdc = reserves[0], reserves[1]  

    # Calculate price for TOKEN_AMOUNT of ETH
    price = (reserve_usdc * TOKEN_AMOUNT) / (reserve_weth * 10**-12)  # Adjust for USDC decimal
    print(price)
    return price

# 1inch Price - ETH/USDC
def get_1inch_price():
    # Get ETH/USDC pair    
    params = {
        "src": WETH_ADDRESS,
        "dst": USDC_ADDRESS,
        "amount": Web3.to_wei(TOKEN_AMOUNT, 'ether')
    }
    
    headers = {
        "Authorization": f"Bearer {ONEINCH_API_KEY}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(ONEINCH_API_URL, params=params, headers=headers)
        print(f"1inch API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"1inch API Response: {response.text}")  
            raise Exception(f"1inch API Error: Status {response.status_code} - {response.text}")
            
        data = response.json()
        return int(data["toAmount"]) / 10 ** 6  # Convert USDC (6 decimals)
    except requests.exceptions.RequestException as e:
        raise Exception(f"1inch API Request Failed: {str(e)}")
    except ValueError as e:
        raise Exception(f"1inch API Invalid Response: {str(e)}")
    except Exception as e:
        raise Exception(f"1inch API Error: {str(e)}")

# Main  
try:
    uniswap_price = get_uniswap_v2_price()
    oneinch_price = get_1inch_price()

    print(f"Uniswap V2 ETH/USDC Price for {TOKEN_AMOUNT} ETH: {uniswap_price} USDC")
    print(f"1inch ETH/USDC Price for {TOKEN_AMOUNT} ETH: {oneinch_price} USDC")

    price_difference = abs(uniswap_price - oneinch_price)
    print(f"Price Difference: {price_difference} USDC")

except Exception as err:
    print(f"Error: {str(err)}")
