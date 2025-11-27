const { ethers } = require("hardhat");

async function main() {
  console.log("🚀 Deploying CompleteCrowdfunding Contract");
  
  const [deployer] = await ethers.getSigners();
  console.log("Deployer:", deployer.address);
  
  // Check balance
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", ethers.formatEther(balance), "ETH");
  
  // Set goal and duration (30 days)
  const goal = ethers.parseEther("0.001");
  const duration = 30 * 24 * 60 * 60; // 30 days
  
  console.log("📝 Contract Parameters:");
  console.log("Goal:", ethers.formatEther(goal), "ETH");
  console.log("Duration: 30 days");
  
  const Crowdfunding = await ethers.getContractFactory("CompleteCrowdfunding");
  console.log("⏳ Deploying...");
  
  const contract = await Crowdfunding.deploy(goal, duration);
  await contract.waitForDeployment();
  
  const address = await contract.getAddress();
  
  console.log("\n🎉 Contract Deployed Successfully!");
  console.log("📍 Contract Address:", address);
  console.log("🎯 Goal Amount:", ethers.formatEther(goal), "ETH");
  console.log("👤 Creator:", await contract.creator());
  
  // Verify deployment
  const deployedGoal = await contract.goal();
  const deadline = await contract.deadline();
  const status = await contract.getStatus();
  
  console.log("\n✅ Deployment Verification:");
  console.log("Confirmed Goal:", ethers.formatEther(deployedGoal), "ETH");
  console.log("Deadline:", new Date(Number(deadline) * 1000).toLocaleString());
  console.log("Initial Status:", status);
  
  console.log("\n🌐 View on Etherscan:");
  console.log("https://sepolia.etherscan.io/address/" + address);
  
  console.log("\n💡 Next Steps:");
  console.log("1. Update contract address in frontend/backend");
  console.log("2. Test funding functionality");
  console.log("3. Test withdrawal after goal reached");
  
  return address;
}

main().catch((error) => {
  console.error("❌ Deployment Failed:", error);
  process.exitCode = 1;
});