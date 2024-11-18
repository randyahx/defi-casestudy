import asyncio
import aiohttp
from web3.providers import AsyncHTTPProvider
from web3 import AsyncWeb3
import ssl
import time

# ETH Node  
NODE_ENDPOINT = ""
# 1Inch API  
ONEINCH_API_URL = "https://api.1inch.dev/swap/v6.0/1/quote"
ONEINCH_API_KEY = ""    
# Uniswap ETH/USDC V2 Pair Contract Address (Reduce latency from contract calls to check for address)
UNISWAP_PAIR_ADDRESS = AsyncWeb3.to_checksum_address("0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc")
# Minimal Uniswap ETH/USDC V2 Pair ABI 
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
    }
]
# Minimal ERC20 ABI  
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
WETH_ADDRESS = AsyncWeb3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27ead9083C756Cc2")
USDC_ADDRESS = AsyncWeb3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
# Token Decimals (Reduce latency from contract calls to check for decimals)  
WETH_DECIMALS = 18
USDC_DECIMALS = 6
# Token Amount  
TOKEN_AMOUNT = 10

# Initialize async Web3 (Reduce latency from waiting for sequential calls)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async_w3 = AsyncWeb3(
    AsyncHTTPProvider(
        NODE_ENDPOINT,
        request_kwargs={'ssl': ssl_context}
    )
)

async def get_uniswap_v2_price_async():
    start_time = time.time()
    
    pair_contract = async_w3.eth.contract(address=UNISWAP_PAIR_ADDRESS, abi=UNISWAP_PAIR_ABI)
    reserves = await pair_contract.functions.getReserves().call()
    
    usdc_reserve = reserves[0]
    eth_reserve = reserves[1]
    
    adjusted_usdc_reserve = usdc_reserve / (10**USDC_DECIMALS)
    adjusted_eth_reserve = eth_reserve / (10**WETH_DECIMALS)
    
    price = adjusted_usdc_reserve / adjusted_eth_reserve
    execution_time = (time.time() - start_time) * 1000  # Time in ms  
    
    return price, execution_time

async def get_1inch_price_async():
    start_time = time.time()
    
    params = {
        "src": WETH_ADDRESS,
        "dst": USDC_ADDRESS,
        "amount": AsyncWeb3.to_wei(1, 'ether')
    }
    
    headers = {
        "Authorization": f"Bearer {ONEINCH_API_KEY}",
        "Accept": "application/json"
    }
   
    async with aiohttp.ClientSession() as session:
        async with session.get(ONEINCH_API_URL, params=params, headers=headers, ssl=ssl_context) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"1inch API Error: Status {response.status} - {text}")
                
            data = await response.json()
            price = int(data["dstAmount"]) / 10 ** USDC_DECIMALS
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return price, execution_time

async def main():
    while True:  # Continuous loop
        try:
            start_time = time.time()  
            
            # Get prices and execution times in parallel
            (uniswap_price, uniswap_time), (oneinch_price, oneinch_time) = await asyncio.gather(
                get_uniswap_v2_price_async(),
                get_1inch_price_async()
            )
            
            uniswap_total = uniswap_price * TOKEN_AMOUNT
            oneinch_total = oneinch_price * TOKEN_AMOUNT

            optimal_platform = "Uniswap V2" if uniswap_total > oneinch_total else "1inch"
            price_difference = abs(uniswap_total - oneinch_total)

            total_execution_time = (time.time() - start_time) * 1000  # Time in ms
            
            print("")
            print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Uniswap V2 Sell Price for {TOKEN_AMOUNT} ETH: {round(uniswap_total, 2)} USDC (Execution: {round(uniswap_time, 2)}ms)")
            print(f"1inch Sell Price for {TOKEN_AMOUNT} ETH: {round(oneinch_total, 2)} USDC (Execution: {round(oneinch_time, 2)}ms)")
            print(f"Price Difference: {round(price_difference, 2)} USDC, Optimal Platform: {optimal_platform}")
            print(f"Total Execution Time: {round(total_execution_time, 2)}ms")
            
            interval = max(0, 0.5 - (total_execution_time/1000))  # Time in seconds  
            await asyncio.sleep(interval)

        except Exception as err:
            print(f"Error: {str(err)}")
            await asyncio.sleep(0.5)  
        except KeyboardInterrupt:
            print("\nScript stopped by user")
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript stopped by user")
