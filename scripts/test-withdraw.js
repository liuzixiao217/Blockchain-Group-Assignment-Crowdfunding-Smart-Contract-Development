const { ethers } = require("hardhat");

async function main() {
  console.log("=== Funds Withdrawal Test ===");
  
  const contractAddress = "0x25D1Cb8E516750F8265329e86cD51d35D6C9C9D4";
  
  const Crowdfunding = await ethers.getContractFactory("CompleteCrowdfunding");
  const contract = Crowdfunding.attach(contractAddress);
  
  const [deployer] = await ethers.getSigners();
  
  console.log("Contract Address:", contractAddress);
  console.log("Tester:", deployer.address);
  
  // Check pre-withdrawal status
  console.log("\n📊 Pre-Withdrawal Status:");
  const creator = await contract.creator();
  const goalReached = await contract.goalReached();
  const fundsWithdrawn = await contract.fundsWithdrawn();
  const contractBalance = await contract.getContractBalance();
  const deployerBalanceBefore = await ethers.provider.getBalance(deployer.address);
  
  console.log("Creator:", creator);
  console.log("Goal Reached:", goalReached);
  console.log("Funds Withdrawn:", fundsWithdrawn);
  console.log("Contract Balance:", ethers.formatEther(contractBalance), "ETH");
  console.log("Creator Balance:", ethers.formatEther(deployerBalanceBefore), "ETH");
  
  // Check withdrawal conditions
  if (deployer.address.toLowerCase() === creator.toLowerCase() && 
      goalReached && 
      !fundsWithdrawn && 
      contractBalance > 0) {
    
    console.log("\n💸 Starting Withdrawal...");
    
    try {
      const withdrawTx = await contract.withdrawFunds();
      console.log("Waiting for transaction confirmation...");
      const receipt = await withdrawTx.wait();
      
      console.log("✅ Withdrawal Successful!");
      console.log("Transaction Hash:", receipt.hash);
      
      // Check post-withdrawal status
      console.log("\n📊 Post-Withdrawal Status:");
      const fundsWithdrawnAfter = await contract.fundsWithdrawn();
      const contractBalanceAfter = await contract.getContractBalance();
      const deployerBalanceAfter = await ethers.provider.getBalance(deployer.address);
      
      console.log("Funds Withdrawn Status:", fundsWithdrawnAfter);
      console.log("Contract Balance:", ethers.formatEther(contractBalanceAfter), "ETH");
      console.log("Creator Balance:", ethers.formatEther(deployerBalanceAfter), "ETH");
      
    } catch (error) {
      console.log("❌ Withdrawal Failed:", error.message);
    }
    
  } else {
    console.log("\n❌ Withdrawal Conditions Not Met:");
    if (deployer.address.toLowerCase() !== creator.toLowerCase()) {
      console.log(" - Current account is not the creator");
    }
    if (!goalReached) {
      console.log(" - Goal not reached");
    }
    if (fundsWithdrawn) {
      console.log(" - Funds already withdrawn");
    }
    if (contractBalance === 0n) {
      console.log(" - Contract balance is zero");
    }
  }
  
  console.log("\n🌐 View Links:");
  console.log("Contract: https://sepolia.etherscan.io/address/" + contractAddress);
}

main().catch(console.error);