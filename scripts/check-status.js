const { ethers } = require("hardhat");

async function main() {
  const contractAddress = "0x25D1Cb8E516750F8265329e86cD51d35D6C9C9D4";
  const Crowdfunding = await ethers.getContractFactory("CompleteCrowdfunding");
  const contract = Crowdfunding.attach(contractAddress);
  
  console.log("🔄 Real-time Status Check:");
  console.log("Address:", contractAddress);
  console.log("Status:", await contract.getStatus());
  console.log("Raised:", ethers.formatEther(await contract.amountRaised()), "/", ethers.formatEther(await contract.goal()), "ETH");
  console.log("Goal Reached:", await contract.goalReached());
  console.log("Contract Balance:", ethers.formatEther(await contract.getContractBalance()), "ETH");
  
  const deadline = await contract.deadline();
  const currentTime = Math.floor(Date.now() / 1000);
  const timeLeft = Number(deadline) - currentTime;
  
  if (timeLeft > 0) {
    console.log("Time Remaining:", Math.floor(timeLeft / 60), "minutes", timeLeft % 60, "seconds");
  } else {
    console.log("Ended", Math.abs(Math.floor(timeLeft / 60)), "minutes ago");
  }
}

main().catch(console.error);