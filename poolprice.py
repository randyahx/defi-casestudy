import requests
from web3 import Web3

# ETH Node  
NODE_ENDPOINT = "https://eth-mainnet.g.alchemy.com/v2/Flo-r4CfzjM_7oqSvamjWP6I_uswnZLx"
# 1Inch API  
ONEINCH_API_URL = "https://api.1inch.dev/swap/v6.0/1/quote"
ONEINCH_API_KEY = "kD4WQzyzYvcLdx3V3MN29hNx0BTokMNC"  
# Uniswap V2 Pair Contract Address (ETH/USDC)
UNISWAP_PAIR_ADDRESS = Web3.to_checksum_address("0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc")
# Uniswap V2 Pair ABI (ETH/USDC)
UNISWAP_PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"},
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]
# ERC20 ABI  
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]
# Token Address  
WETH_ADDRESS = Web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27ead9083C756Cc2")
USDC_ADDRESS = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
# Token Amount  
TOKEN_AMOUNT = 10

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(NODE_ENDPOINT))

# Uniswap V2 Price - ETH/USDC
def get_uniswap_v2_price():
     # Initialize pair contract
    pair_contract = web3.eth.contract(address=UNISWAP_PAIR_ADDRESS, abi=UNISWAP_PAIR_ABI)

    # Fetch reserves
    reserves = pair_contract.functions.getReserves().call()
    reserve0 = reserves[0]
    reserve1 = reserves[1]

    # Fetch token addresses from the pair contract
    token0_address = pair_contract.functions.token0().call()
    token1_address = pair_contract.functions.token1().call()

    # Initialize tokens contracts
    token0_contract = web3.eth.contract(address=token0_address, abi=ERC20_ABI)
    token1_contract = web3.eth.contract(address=token1_address, abi=ERC20_ABI)  

    # Get decimals
    decimals0 = token0_contract.functions.decimals().call()
    decimals1 = token1_contract.functions.decimals().call()

    # Adjust reserves for decimals
    adjusted_reserve0 = reserve0 / (10**decimals0)
    adjusted_reserve1 = reserve1 / (10**decimals1)

    # Calculate price (USDC per ETH)
    if token0_address.lower() == USDC_ADDRESS.lower():  # USDC address
        eth_price = adjusted_reserve0 / adjusted_reserve1
        usdc_per_eth = eth_price
    else:
        eth_price = adjusted_reserve1 / adjusted_reserve0
        usdc_per_eth = eth_price

    return usdc_per_eth 

# 1inch Price - ETH/USDC
def get_1inch_price():
    # Get ETH/USDC pair    
    params = {
        "src": WETH_ADDRESS,
        "dst": USDC_ADDRESS,
        "amount": Web3.to_wei(1, 'ether')
    }
    
    headers = {
        "Authorization": f"Bearer {ONEINCH_API_KEY}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(ONEINCH_API_URL, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"1inch API Response: {response.text}")  
            raise Exception(f"1inch API Error: Status {response.status_code} - {response.text}")
            
        data = response.json()
        return int(data["dstAmount"]) / 10 ** 6   
    except requests.exceptions.RequestException as e:
        raise Exception(f"1inch API Request Failed: {str(e)}")
    except ValueError as e:
        raise Exception(f"1inch API Invalid Response: {str(e)}")
    except Exception as e:
        raise Exception(f"1inch API Error: {str(e)}")

# Main  
try:
    uniswap_price = get_uniswap_v2_price() * TOKEN_AMOUNT
    oneinch_price = get_1inch_price() * TOKEN_AMOUNT

    print(f"Uniswap V2 ETH/USDC Price for {TOKEN_AMOUNT} ETH: {round(uniswap_price, 2)} USDC")
    print(f"1inch ETH/USDC Price for {TOKEN_AMOUNT} ETH: {round(oneinch_price, 2)} USDC")

    price_difference = abs(uniswap_price - oneinch_price)  
    print(f"Price Difference: {round(price_difference, 2)} USDC")

except Exception as err:
    print(f"Error: {str(err)}")
