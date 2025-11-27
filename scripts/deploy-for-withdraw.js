const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying Robust Crowdfunding Contract (10 minutes)");
  
  try {
    const [deployer] = await ethers.getSigners();
    console.log("✅ Deployer Address:", deployer.address);
    
    const balance = await ethers.provider.getBalance(deployer.address);
    console.log("💰 Account Balance:", ethers.formatEther(balance), "ETH");
    
    if (balance < ethers.parseEther("0.01")) {
      throw new Error("Insufficient account balance, please get test ETH first");
    }
    
    const goal = ethers.parseEther("0.0003");
    const duration = 10 * 60; // 10 minutes
    
    console.log("📝 Contract Parameters:");
    console.log("Goal Amount:", ethers.formatEther(goal), "ETH");
    console.log("Duration: 10 minutes");
    
    const Crowdfunding = await ethers.getContractFactory("CompleteCrowdfunding");
    console.log("⏳ Deploying...");
    
    const contract = await Crowdfunding.deploy(goal, duration);
    await contract.waitForDeployment();
    
    const address = await contract.getAddress();
    
    console.log("🎉 Contract Deployed Successfully!");
    console.log("📍 Contract Address:", address);
    console.log("👤 Creator:", await contract.creator());
    
    const deployedGoal = await contract.goal();
    const deployedDeadline = await contract.deadline();
    const status = await contract.getStatus();
    
    console.log("\n✅ Deployment Verification:");
    console.log("Confirmed Goal:", ethers.formatEther(deployedGoal), "ETH");
    console.log("Deadline:", new Date(Number(deployedDeadline) * 1000).toLocaleString());
    console.log("Initial Status:", status);
    
    console.log("\n🌐 View Links:");
    console.log("Etherscan: https://sepolia.etherscan.io/address/" + address);
    
    console.log("\n⏰ Next Commands:");
    console.log("npx hardhat run reach-goal-quick.js --network sepolia");
    
    return address;
    
  } catch (error) {
    console.error("❌ Deployment Failed:", error.message);
    process.exit(1);
  }
}

main();