const { ethers } = require("ethers");

// Fraxlend Contract Address    
const FRAXLEND_CONTRACT_ADDRESS = "0xdbe88dbac39263c47629ebba02b3ef4cf0752a72";
// Fraxlend Contract ABI
const FRAXLEND_CONTRACT_ABI = [
    "function getUserSnapshot(address user) view returns (uint256, uint256, uint256)"
];
// User Address 
const USER_ADDRESS = "0x30A20b0281Df39e6337c3cbE5865E6fdCDcCe3f1";
// Block Number
const BLOCK_NUMBER = 18724090;

// Node Endpoint
const endpoint = new ethers.JsonRpcProvider("NODE_ENDPOINT");
const fraxlendContract = new ethers.Contract(FRAXLEND_CONTRACT_ADDRESS, FRAXLEND_CONTRACT_ABI, endpoint);

// Fetch user data at block number  
(async () => {
    const [assetShares, borrowShares, collateralBalance] = await fraxlendContract.getUserSnapshot(USER_ADDRESS, {
        blockTag: BLOCK_NUMBER
    });
    console.log(`Asset Shares: ${assetShares}`);
    console.log(`Borrow Shares: ${borrowShares}`);
    console.log(`Collateral Balance: ${collateralBalance}`);
})();