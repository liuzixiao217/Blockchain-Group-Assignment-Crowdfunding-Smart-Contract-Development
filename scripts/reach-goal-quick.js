const { ethers } = require("hardhat");

async function main() {
  console.log("💰 Robust Donation Test");
  
  try {
    const contractAddress = "0x25D1Cb8E516750F8265329e86cD51d35D6C9C9D4";
    
    const [deployer] = await ethers.getSigners();
    console.log("✅ Using Account:", deployer.address);
    
    const balance = await ethers.provider.getBalance(deployer.address);
    console.log("💰 Account Balance:", ethers.formatEther(balance), "ETH");
    
    const Crowdfunding = await ethers.getContractFactory("CompleteCrowdfunding");
    const contract = Crowdfunding.attach(contractAddress);
    
    console.log("🔗 Connected to Contract:", contractAddress);
    
    console.log("\n📊 Comprehensive Status Check:");
    
    const creator = await contract.creator();
    const goal = await contract.goal();
    const currentRaised = await contract.amountRaised();
    const goalReached = await contract.goalReached();
    const deadline = await contract.deadline();
    const status = await contract.getStatus();
    
    console.log("Creator:", creator);
    console.log("Goal Amount:", ethers.formatEther(goal), "ETH");
    console.log("Amount Raised:", ethers.formatEther(currentRaised), "ETH");
    console.log("Goal Reached:", goalReached);
    console.log("Status:", status);
    
    const currentTime = Math.floor(Date.now() / 1000);
    const timeLeft = Number(deadline) - currentTime;
    console.log("Time Remaining:", Math.max(0, timeLeft), "seconds");
    
    if (timeLeft <= 0) {
      throw new Error("❌ Contract expired, please redeploy");
    }
    
    if (status !== "ACTIVE") {
      throw new Error(`❌ Contract status is not ACTIVE: ${status}`);
    }
    
    if (goalReached) {
      throw new Error("❌ Goal already reached, no need for donation");
    }
    
    const needed = goal - currentRaised;
    console.log("\n🎯 Required Donation:", ethers.formatEther(needed), "ETH");
    
    if (needed <= 0) {
      throw new Error("❌ No donation needed, amount calculation error");
    }
    
    if (balance < needed) {
      throw new Error(`❌ Insufficient balance, need ${ethers.formatEther(needed)} ETH but only have ${ethers.formatEther(balance)} ETH`);
    }
    
    console.log("\n💸 Executing Donation...");
    const tx = await contract.fund({ value: needed });
    console.log("⏳ Waiting for transaction confirmation...");
    const receipt = await tx.wait();
    
    console.log("✅ Donation Successful!");
    console.log("📝 Transaction Hash:", receipt.hash);
    console.log("🔗 Transaction Link: https://sepolia.etherscan.io/tx/" + receipt.hash);
    
    console.log("\n🔍 Verifying Donation Result:");
    const newRaised = await contract.amountRaised();
    const newGoalReached = await contract.goalReached();
    const newStatus = await contract.getStatus();
    const contractBalance = await contract.getContractBalance();
    
    console.log("Updated Amount Raised:", ethers.formatEther(newRaised), "ETH");
    console.log("Updated Goal Reached:", newGoalReached);
    console.log("Updated Status:", newStatus);
    console.log("Contract Balance:", ethers.formatEther(contractBalance), "ETH");
    
    if (newGoalReached) {
      console.log("\n🎉 Goal Reached! Now you can test withdrawal");
      console.log("⏩ Next Command: npx hardhat run test-withdraw-final.js --network sepolia");
    } else {
      console.log("\n⚠️ Goal not reached, please check contract status");
    }
    
  } catch (error) {
    console.error("❌ Donation Failed:", error.message);
    process.exit(1);
  }
}

main();