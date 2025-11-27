async function main() {
  console.log("Testing connection...");
  
  const { ethers } = require("hardhat");
  const provider = ethers.provider;
  
  try {
    const network = await provider.getNetwork();
    console.log("Network:", network.name, "Chain ID:", network.chainId);
     
    const block = await provider.getBlockNumber();
    console.log("Current block:", block);
    
    console.log("✅ Connection successful!");
  } catch (error) {
    console.log("❌ Connection failed:", error.message);
  }
}

main();