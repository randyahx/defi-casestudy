# DeFi Casestudy  

This repository contains a python script to query the prices for ETH/USDC on Uniswap V2 and 1inch. It also contains an additional script used for the Fraxlend question.  

**Key Optimizations**
1. Async was used instead of sequential execution to query from both protocols to reduce latency  
2. Decimal values were included in the script to reduce latency from having to get the values from a contract call
3. Minimal ABI with only the required functions  
